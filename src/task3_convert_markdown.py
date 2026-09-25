"""
Task 3 — Chuẩn hóa dữ liệu sang Markdown.

Legal docs (.docx) được convert bằng cách đọc thẳng word/document.xml
trong gói zip OOXML (chỉ dùng zipfile + xml.etree của thư viện chuẩn),
KHÔNG dùng MarkItDown cho .docx: pyproject.toml chỉ khai báo extra
`markitdown[pdf]`, không có `[docx]`, và thêm extra sẽ vi phạm ràng buộc
"không thêm dependency mới khi chưa được team duyệt". `.pdf`/`.doc` (nếu
có) vẫn dùng MarkItDown, vốn đã sẵn có qua extra `[pdf]`.

News JSON được convert sang Markdown kèm header Source + Crawled.
"""

from pathlib import Path

from src.task1_collect_legal_docs import SOURCE_PAGES as LEGAL_SOURCE_PAGES


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def _paragraph_text(paragraph, ns: str) -> str:
    """Flatten one w:p's own flow text (runs, tabs, breaks).

    Recurses into everything except w:drawing subtrees: a drawing (image or
    text box) can nest its own w:p elements, which the top-level walk in
    `_docx_to_text` already visits on their own. Descending into a drawing
    here would swallow that nested text into the host paragraph too and
    duplicate it.
    """
    parts: list[str] = []

    def walk(element) -> None:
        for child in element:
            if child.tag == ns + "drawing":
                continue
            if child.tag == ns + "t":
                parts.append(child.text or "")
            elif child.tag == ns + "tab":
                parts.append("\t")
            elif child.tag == ns + "br":
                parts.append("\n")
            else:
                walk(child)

    walk(paragraph)
    return "".join(parts)


def _docx_to_text(path: Path) -> str:
    """Extract plain text from a .docx (OOXML zip) using only the stdlib."""
    import zipfile
    from xml.etree import ElementTree as ET

    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        # Some government-issued .docx files use backslash-separated
        # zip entry names (Windows-authored), not the usual forward slash.
        key = "word/document.xml" if "word/document.xml" in names else "word\\document.xml"
        xml_content = archive.read(key)

    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    mc_ns = "{http://schemas.openxmlformats.org/markup-compatibility/2006}"
    tree = ET.fromstring(xml_content)

    # mc:AlternateContent wraps two equivalent copies of the same content
    # (a modern w:drawing text box in mc:Choice, a legacy VML fallback in
    # mc:Fallback). Drop the Fallback copy so its text isn't extracted twice.
    for alternate in tree.iter(mc_ns + "AlternateContent"):
        for fallback in alternate.findall(mc_ns + "Fallback"):
            alternate.remove(fallback)

    paragraphs = []
    for paragraph in tree.iter(ns + "p"):
        text = _paragraph_text(paragraph, ns)
        if text.strip():
            paragraphs.append(text)
    return "\n\n".join(paragraphs)


def _should_convert(source: Path, target: Path) -> bool:
    """Whether `source` needs (re)converting into `target`.

    A size-only skip check treats any non-trivial existing output as final,
    so re-running task1/task2 with fresh source data (a new crawl, a
    re-downloaded document) silently leaves stale markdown in place. Also
    reconvert when the target is empty/too small, regardless of mtimes.
    """
    if not target.exists() or target.stat().st_size <= 200:
        return True
    return source.stat().st_mtime > target.stat().st_mtime


def convert_legal_docs() -> None:
    """Convert PDF/DOC/DOCX vào standardized/legal."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    for path in sorted(legal_dir.iterdir()):
        suffix = path.suffix.lower()
        if suffix not in {".pdf", ".doc", ".docx"}:
            continue
        target = output_dir / f"{path.stem}.md"
        if not _should_convert(path, target):
            print(f"Skip existing: {target.name}")
            continue

        if suffix == ".docx":
            text = _docx_to_text(path)
        else:
            from markitdown import MarkItDown

            text = MarkItDown().convert(str(path)).text_content

        source_url = LEGAL_SOURCE_PAGES.get(path.name, "")
        header = f"**Source:** {source_url}\n\n**Type:** legal\n\n---\n\n" if source_url else ""
        target.write_text(header + text, encoding="utf-8")
        print(f"Converted: {target.name}")


def convert_news_articles() -> None:
    """Convert JSON vào standardized/news."""
    import json

    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    for path in sorted(news_dir.glob("*.json")):
        target = output_dir / f"{path.stem}.md"
        if not _should_convert(path, target):
            print(f"Skip existing: {target.name}")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        header = (
            f"# {data['title']}\n\n"
            f"**Source:** {data['url']}\n\n"
            f"**Crawled:** {data['date_crawled']}\n\n---\n\n"
        )
        target.write_text(header + data["content_markdown"], encoding="utf-8")
        print(f"Converted: {target.name}")


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"Saved Markdown to: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
