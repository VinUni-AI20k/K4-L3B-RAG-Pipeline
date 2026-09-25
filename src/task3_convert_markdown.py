"""Task 3 — Chuẩn hóa dữ liệu landing sang Markdown.

- PDF/DOC/DOCX được chuyển bằng MarkItDown sang ``data/standardized/legal/``.
- JSON bài viết được chuyển sang ``data/standardized/news/`` và giữ metadata
  ở đầu nội dung.
- Đường dẫn đầu ra ổn định nên chạy lại sẽ cập nhật file cũ, không nhân bản.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"
LEGAL_EXTENSIONS = {".pdf", ".doc", ".docx"}
NEWS_REQUIRED_FIELDS = {"url", "title", "date_crawled", "content_markdown"}


def _safe_markdown_value(value: Any) -> str:
    """Make a single-line metadata value safe to place in Markdown headers."""
    return re.sub(r"\s+", " ", str(value)).strip().replace("|", "\\|")


def _write_markdown(output: Path, content: str) -> bool:
    """Write a non-empty Markdown document; return False for blank content."""
    content = content.strip()
    if not content:
        return False
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content + "\n", encoding="utf-8")
    return True


def _remove_repeated_title(body: str, title: str) -> str:
    """Avoid repeating a document's first heading after adding our metadata."""
    lines = body.strip().splitlines()
    if lines and lines[0].lstrip("# ").strip().casefold() == title.casefold():
        return "\n".join(lines[1:]).strip()
    return body.strip()


def convert_legal_docs() -> None:
    """Convert supported legal files and preserve their relative directories."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    files = (
        sorted(
            path
            for path in legal_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in LEGAL_EXTENSIONS
        )
        if legal_dir.is_dir()
        else []
    )
    if not files:
        print(f"No PDF/DOC/DOCX files found in {legal_dir}; skipping legal conversion.")
        return

    try:
        from markitdown import MarkItDown
    except ImportError as error:
        raise RuntimeError(
            "Legal files were found, but MarkItDown is not installed. "
            'Install project dependencies with: python -m pip install -e ".[dev]"'
        ) from error

    converter = MarkItDown()
    failures: list[str] = []
    converted = 0
    for path in files:
        relative_path = path.relative_to(legal_dir)
        output = (output_dir / relative_path).with_suffix(".md")
        try:
            result = converter.convert(str(path))
            body = str(getattr(result, "text_content", "") or "").strip()
            if not body:
                failures.append(f"{path}: converter returned empty text")
                print(f"Skipped empty conversion: {path}")
                continue

            title = _safe_markdown_value(
                getattr(result, "title", None) or path.stem.replace("_", " ")
            )
            body = _remove_repeated_title(body, title)
            source = _safe_markdown_value(relative_path.as_posix())
            markdown = (
                f"# {title}\n\n"
                f"**Source:** `{source}`  \n"
                "**Document type:** legal\n\n"
                "---\n\n"
                f"{body}"
            )
            if not _write_markdown(output, markdown):
                failures.append(f"{path}: converted document is blank")
                print(f"Skipped empty conversion: {path}")
                continue
            converted += 1
            print(f"Saved: {output}")
        except Exception as error:
            failures.append(f"{path}: {error}")
            print(f"Failed: {path} — {error}")

    print(f"Legal documents converted: {converted}/{len(files)}")
    if failures:
        raise RuntimeError("Legal conversion failed: " + "; ".join(failures))


def _load_news_record(path: Path) -> dict[str, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Cannot read valid UTF-8 JSON: {error}") from error
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")

    missing = NEWS_REQUIRED_FIELDS - data.keys()
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(sorted(missing))}")
    normalized = {key: str(data[key]).strip() for key in NEWS_REQUIRED_FIELDS}
    empty = [key for key, value in normalized.items() if not value]
    if empty:
        raise ValueError(f"Empty required fields: {', '.join(sorted(empty))}")
    return normalized


def convert_news_articles() -> None:
    """Convert landing JSON articles to Markdown with source metadata first."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    files = sorted(news_dir.rglob("*.json")) if news_dir.is_dir() else []
    if not files:
        print(f"No JSON article files found in {news_dir}; skipping news conversion.")
        return

    failures: list[str] = []
    converted = 0
    for path in files:
        relative_path = path.relative_to(news_dir)
        output = (output_dir / relative_path).with_suffix(".md")
        try:
            article = _load_news_record(path)
            body = article["content_markdown"].strip()
            if not body:
                failures.append(f"{path}: content_markdown is blank")
                print(f"Skipped empty article: {path}")
                continue

            title = _safe_markdown_value(article["title"])
            body = _remove_repeated_title(body, title)
            url = _safe_markdown_value(article["url"])
            crawled = _safe_markdown_value(article["date_crawled"])
            markdown = (
                f"# {title}\n\n"
                f"**Source:** <{url}>  \n"
                f"**Crawled:** {crawled}  \n"
                "**Document type:** news\n\n"
                "---\n\n"
                f"{body}"
            )
            if not _write_markdown(output, markdown):
                failures.append(f"{path}: generated Markdown is blank")
                print(f"Skipped empty article: {path}")
                continue
            converted += 1
            print(f"Saved: {output}")
        except Exception as error:
            failures.append(f"{path}: {error}")
            print(f"Failed: {path} — {error}")

    print(f"News articles converted: {converted}/{len(files)}")
    if failures:
        raise RuntimeError("News conversion failed: " + "; ".join(failures))


def convert_all() -> None:
    """Convert legal and news landing data, reporting errors after both run."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []
    for converter in (convert_legal_docs, convert_news_articles):
        try:
            converter()
        except RuntimeError as error:
            failures.append(str(error))

    print(f"Markdown output directory: {OUTPUT_DIR}")
    if failures:
        raise RuntimeError("Some source files could not be converted: " + " | ".join(failures))


if __name__ == "__main__":
    convert_all()
