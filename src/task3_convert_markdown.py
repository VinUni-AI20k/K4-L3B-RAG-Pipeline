"""Standardize legal documents and article JSON as UTF-8 Markdown.

The supplied DOCX files contain Markdown text. Extracting their Word paragraphs
preserves the original headings and tables; other PDF/DOCX files use MarkItDown.
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile


ROOT_DIR = Path(__file__).resolve().parent.parent
LANDING_DIR = ROOT_DIR / "data" / "landing"
OUTPUT_DIR = ROOT_DIR / "data" / "standardized"
WORD_NAMESPACE = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
LEGAL_EXTENSIONS = {".pdf", ".doc", ".docx"}


def _write_if_changed(path: Path, content: str) -> bool:
    """Write atomically only when the normalized document changed."""
    if len(content.strip()) < 200:
        raise ValueError(f"Refusing to write empty or short document: {path.name}")
    if path.is_file() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=path.parent,
            suffix=".tmp", delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()
    return True


def _docx_paragraphs(path: Path) -> str:
    """Read Word paragraph text without adding markup around existing Markdown."""
    try:
        with ZipFile(path) as archive:
            if "word/document.xml" not in archive.namelist():
                raise ValueError(f"Missing document.xml in {path.name}")
            root = ElementTree.fromstring(archive.read("word/document.xml"))
    except (BadZipFile, ElementTree.ParseError, OSError) as error:
        raise ValueError(f"Cannot read {path.name}: {error}") from error
    paragraphs = [
        "".join(node.text or "" for node in paragraph.findall(".//w:t", WORD_NAMESPACE))
        for paragraph in root.findall(".//w:p", WORD_NAMESPACE)
    ]
    return "\n".join(paragraphs).replace("\u00a0", " ").strip()


def _markitdown_text(path: Path) -> str:
    try:
        from markitdown import MarkItDown
        result = MarkItDown().convert(str(path))
    except Exception as error:
        raise RuntimeError(f"Cannot convert {path.name} with MarkItDown: {error}") from error
    return (result.text_content or "").strip()


def _front_matter(metadata: dict[str, str]) -> str:
    """Serialize metadata with JSON quoted scalars, which YAML also accepts."""
    lines = ["---"]
    for key, value in metadata.items():
        if value:
            lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
    lines.append("---")
    return "\n".join(lines)


def _normalize_legal_text(text: str, path: Path) -> str:
    """Preserve embedded Markdown and repair incomplete front matter."""
    text = text.replace("\r\n", "\n").replace("\u00a0", " ").strip()
    if len(text) < 200:
        raise ValueError(f"Legal document is too short: {path.name}")
    lines = text.splitlines()
    if lines[0].strip() != "---":
        return _front_matter({"doc_id": path.stem, "title": path.stem, "source_file": path.name}) + "\n\n" + text + "\n"

    closing = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if closing is None:
        heading = next((i for i in range(1, len(lines)) if lines[i].lstrip().startswith("#")), None)
        if heading is None:
            raise ValueError(f"Cannot locate policy body in {path.name}")
        metadata_lines = [line for line in lines[1:heading] if line.strip()]
        body = "\n".join(lines[heading:]).strip()
        text = "---\n" + "\n".join(metadata_lines) + "\n---\n\n" + body
    return text.strip() + "\n"


def convert_legal_docs() -> list[Path]:
    """Convert every source PDF/DOCX to one Markdown document by stem."""
    source_dir = LANDING_DIR / "legal"
    files = sorted(path for path in source_dir.iterdir() if path.is_file() and path.suffix.lower() in LEGAL_EXTENSIONS)
    if len(files) < 3:
        raise ValueError(f"Task 3 requires at least three legal documents; found {len(files)}")
    if len({path.stem for path in files}) != len(files):
        raise ValueError("Two legal source files have the same stem")

    output_dir = OUTPUT_DIR / "legal"
    outputs: list[Path] = []
    for path in files:
        if path.suffix.lower() == ".docx":
            extracted = _docx_paragraphs(path)
            text = extracted if extracted.startswith("---") else _markitdown_text(path)
        else:
            text = _markitdown_text(path)
        output = output_dir / f"{path.stem}.md"
        changed = _write_if_changed(output, _normalize_legal_text(text, path))
        print(f"{'Saved' if changed else 'Current'}: legal/{output.name}")
        outputs.append(output)
    return outputs


def _article_markdown(path: Path) -> str:
    try:
        article = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Cannot read article JSON {path.name}: {error}") from error
    if not isinstance(article, dict):
        raise ValueError(f"Article JSON must be an object: {path.name}")
    required = ("url", "title", "date_crawled", "content_markdown")
    if any(not isinstance(article.get(key), str) or not article[key].strip() for key in required):
        raise ValueError(f"Missing article metadata or content: {path.name}")
    if urlparse(article["url"]).scheme != "https":
        raise ValueError(f"Article URL must use HTTPS: {path.name}")
    try:
        date.fromisoformat(article["date_crawled"])
    except ValueError as error:
        raise ValueError(f"Invalid crawl date: {path.name}") from error
    body = article["content_markdown"].strip()
    if len(body) < 200:
        raise ValueError(f"Article content is too short: {path.name}")
    if article.get("doc_id", path.stem) != path.stem:
        raise ValueError(f"doc_id does not match filename: {path.name}")

    metadata = {
        "doc_id": path.stem,
        "title": article["title"].strip(),
        "source_url": article["url"].strip(),
        "retrieved_at": article["date_crawled"].strip(),
    }
    for key in ("document_version", "audience", "category", "language"):
        value = article.get(key)
        if isinstance(value, str) and value.strip():
            metadata[key] = value.strip()
    return _front_matter(metadata) + "\n\n" + body + "\n"


def convert_news_articles() -> list[Path]:
    """Convert article JSON, retaining source metadata at the top."""
    source_dir = LANDING_DIR / "news"
    files = sorted(source_dir.glob("*.json"))
    if len(files) < 5:
        raise ValueError(f"Task 3 requires at least five article JSON files; found {len(files)}")
    output_dir = OUTPUT_DIR / "news"
    outputs: list[Path] = []
    for path in files:
        output = output_dir / f"{path.stem}.md"
        changed = _write_if_changed(output, _article_markdown(path))
        print(f"{'Saved' if changed else 'Current'}: news/{output.name}")
        outputs.append(output)
    return outputs


def convert_all() -> None:
    """Standardize both landing source types."""
    legal = convert_legal_docs()
    news = convert_news_articles()
    print(f"Task 3 complete: {len(legal)} legal and {len(news)} news Markdown files in {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
