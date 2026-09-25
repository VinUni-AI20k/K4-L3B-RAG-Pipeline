"""
Task 3 — Chuẩn hóa dữ liệu sang Markdown.

Hướng dẫn:
    1. Dùng MarkItDown để convert PDF/DOCX.
    2. Đọc JSON và giữ metadata ở đầu file Markdown.
    3. Giữ cấu trúc thư mục legal/ và news/.
    4. Không tạo file rỗng hoặc file trùng khi chạy lại.

Cài đặt:
    Dependency MarkItDown đã được khai báo trong pyproject.toml.
    
-> Hoặc dùng công cụ nào bạn quen khác Markitdown
"""

import json
from pathlib import Path


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def convert_legal_docs() -> None:
    """Convert PDF/DOCX vào standardized/legal."""
    from markitdown import MarkItDown

    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"

    if not legal_dir.exists() or not any(legal_dir.iterdir()):
        print(f"No legal documents found in {legal_dir}. Skipping.")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    converter = MarkItDown()

    for path in sorted(legal_dir.iterdir()):
        if path.suffix.lower() not in {".pdf", ".doc", ".docx"}:
            continue
        dest = output_dir / f"{path.stem}.md"
        if dest.exists():
            print(f"Already exists, skipping: {dest.name}")
            continue
        print(f"Converting: {path.name}")
        result = converter.convert(str(path))
        content = result.text_content.strip()
        if not content:
            print(f"WARNING: Empty content for {path.name}, skipping.")
            continue
        dest.write_text(content, encoding="utf-8")
        print(f"Saved: {dest}")


def convert_news_articles() -> None:
    """Convert JSON vào standardized/news."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"

    if not news_dir.exists() or not any(news_dir.glob("*.json")):
        print(f"No news JSON files found in {news_dir}. Skipping.")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    for path in sorted(news_dir.glob("*.json")):
        dest = output_dir / f"{path.stem}.md"
        if dest.exists():
            print(f"Already exists, skipping: {dest.name}")
            continue
        print(f"Converting: {path.name}")
        data = json.loads(path.read_text(encoding="utf-8"))
        content_md = data.get("content_markdown", "").strip()
        if not content_md:
            print(f"WARNING: Empty content_markdown in {path.name}, skipping.")
            continue
        header = (
            f"# {data.get('title', 'Untitled')}\n\n"
            f"**Source:** {data.get('url', '')}\n\n"
            f"**Crawled:** {data.get('date_crawled', '')}\n\n---\n\n"
        )
        dest.write_text(header + content_md, encoding="utf-8")
        print(f"Saved: {dest}")


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"\nSaved Markdown to: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
