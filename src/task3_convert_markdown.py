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
    tree = ET.fromstring(xml_content)
    paragraphs = []
    for paragraph in tree.iter(ns + "p"):
        text = "".join(node.text or "" for node in paragraph.iter(ns + "t"))
        if text.strip():
            paragraphs.append(text)
    return "\n\n".join(paragraphs)


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
        if target.exists() and target.stat().st_size > 200:
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
        if target.exists() and target.stat().st_size > 200:
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
