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

from pathlib import Path


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def convert_legal_docs() -> None:
    """Convert PDF/DOCX từ data/landing/legal vào data/standardized/legal."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        from markitdown import MarkItDown
        converter = MarkItDown()
        for path in legal_dir.iterdir():
            if path.suffix.lower() in {".pdf", ".doc", ".docx"}:
                target_md = output_dir / f"{path.stem}.md"
                print(f"Converting {path.name} to Markdown using MarkItDown...")
                try:
                    result = converter.convert(str(path))
                    target_md.write_text(result.text_content, encoding="utf-8")
                    print(f"Saved: {target_md}")
                except Exception as exc:
                    print(f"Error converting {path.name}: {exc}")
    except ImportError:
        # Fallback using pypdfium2 / pypdf / pdfminer if MarkItDown not available
        print("MarkItDown not yet imported, trying alternative PDF converter...")
        for path in legal_dir.iterdir():
            if path.suffix.lower() == ".pdf":
                target_md = output_dir / f"{path.stem}.md"
                try:
                    import pypdf
                    reader = pypdf.PdfReader(str(path))
                    pages_text = [page.extract_text() or "" for page in reader.pages]
                    content = f"# {path.stem}\n\n" + "\n\n".join(pages_text)
                    target_md.write_text(content, encoding="utf-8")
                    print(f"Saved: {target_md}")
                except Exception as exc:
                    print(f"Fallback extraction failed for {path.name}: {exc}")


def convert_news_articles() -> None:
    """Convert JSON từ data/landing/news vào data/standardized/news."""
    import json

    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    for path in news_dir.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            header = (
                f"# {data['title']}\n\n"
                f"**Source:** {data['url']}\n\n"
                f"**Crawled:** {data['date_crawled']}\n\n---\n\n"
            )
            target_md = output_dir / f"{path.stem}.md"
            target_md.write_text(header + data.get("content_markdown", ""), encoding="utf-8")
            print(f"Saved: {target_md}")
        except Exception as exc:
            print(f"Error converting {path.name}: {exc}")


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"Saved Markdown to: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()

