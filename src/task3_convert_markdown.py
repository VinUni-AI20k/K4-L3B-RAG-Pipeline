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
    import json
    import fitz
    import pytesseract

    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    sources_path = legal_dir / "sources.json"
    sources = json.loads(sources_path.read_text(encoding="utf-8")) if sources_path.exists() else {}

    for path in sorted(legal_dir.glob("*.pdf")):
        info = sources.get(path.name, {})
        pages = []

        with fitz.open(path) as pdf:
            for page_number, page in enumerate(pdf, start=1):
                text = page.get_text("text").strip()

                # PDF scan ảnh: OCR từng trang để tránh nạp cả tài liệu vào RAM.
                if len(text) < 30:
                    pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                    from PIL import Image
                    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    text = pytesseract.image_to_string(image, lang="vie+eng").strip()

                if text:
                    pages.append(f"## Trang {page_number}\n\n{text}")

        if not pages:
            print(f"KHÔNG ĐỌC ĐƯỢC: {path.name}")
            continue

        header = (
            f"# {info.get('title', path.stem)}\n\n"
            f"**Source:** {info.get('url', '')}\n\n"
            f"**Issuer:** {info.get('issuer', '')}\n\n"
        )
        output_path = output_dir / f"{path.stem}.md"
        output_path.write_text(header + "\n\n".join(pages), encoding="utf-8")
        print(f"Converted {path.name}: {len(pages)} pages")


def convert_news_articles() -> None:
    """Convert JSON vào standardized/news."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not news_dir.exists():
        print("No news landing directory found")
        return

    for path in sorted(news_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            title = data.get("title", "Untitled")
            url = data.get("url", "")
            date_crawled = data.get("date_crawled", "")
            content = data.get("content_markdown", "")

            header = (
                f"# {title}\n\n"
                f"**Source:** {url}\n\n"
                f"**Crawled:** {date_crawled}\n\n---\n\n"
            )
            output_path = output_dir / f"{path.stem}.md"
            output_path.write_text(
                header + content, encoding="utf-8"
            )
            print(f"Converted news: {output_path}")
        except Exception as e:
            print(f"Failed to convert {path.name}: {e}")


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"Saved Markdown to: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
