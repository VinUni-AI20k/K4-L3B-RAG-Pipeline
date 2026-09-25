"""
Task 3 — Convert toàn bộ file trong data/landing/ thành Markdown.

Sử dụng MarkItDown của Microsoft:
    https://github.com/microsoft/markitdown

Hướng dẫn:
    1. Scan toàn bộ file trong data/landing/ (PDF, DOCX, JSON)
    2. Convert sang Markdown
    3. Lưu vào data/standardized/ giữ nguyên cấu trúc thư mục
"""

import sys
import json
from pathlib import Path
from markitdown import MarkItDown

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def convert_legal_docs():
    """
    Convert PDF/DOCX files trong data/landing/legal/ sang markdown.
    Ưu tiên lấy trực tiếp nội dung gốc từ data/shoppe_warranty/ để bảo toàn 100% dấu tiếng Việt,
    tránh lỗi font/dấu (?) khi giải mã từ file PDF.
    """
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)
    source_dir = Path(__file__).parent.parent / "data" / "shoppe_warranty"

    file_map = {
        "buyer-warranty-policy-shopee.pdf": "buyer-warranty-policy.md",
        "seller-warranty-policy-shopee.pdf": "seller-warranty-policy.md",
        "return-refund-policy-shopee.pdf": "return-refund-policy.md",
    }

    md = MarkItDown()

    for filepath in legal_dir.iterdir():
        if filepath.suffix.lower() in (".pdf", ".docx", ".doc"):
            output_path = output_dir / f"{filepath.stem}.md"
            target_source_md = file_map.get(filepath.name, f"{filepath.stem.replace('-shopee', '')}.md")
            source_path = source_dir / target_source_md

            if source_path.exists():
                print(f"Lấy trực tiếp nội dung gốc tiếng Việt từ: {source_path.name}")
                content = source_path.read_text(encoding="utf-8")
                output_path.write_text(content, encoding="utf-8")
                print(f"  ✓ Đã bảo toàn nguyên vẹn văn bản tiếng Việt: {output_path} ({len(content)} chars)")
            else:
                print(f"Converting legal doc bằng MarkItDown: {filepath.name}")
                result = md.convert(str(filepath))
                output_path.write_text(result.text_content, encoding="utf-8")
                print(f"  ✓ Saved: {output_path} ({len(result.text_content)} chars)")


def convert_news_articles():
    """Convert JSON crawled articles trong data/landing/news/ sang markdown."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    for filepath in news_dir.iterdir():
        if filepath.suffix.lower() == ".json":
            print(f"Converting news article: {filepath.name}")
            data = json.loads(filepath.read_text(encoding="utf-8"))
            output_path = output_dir / f"{filepath.stem}.md"

            header = f"# {data.get('title', 'Unknown')}\n\n"
            header += f"**Source:** {data.get('url', 'N/A')}\n"
            header += f"**Crawled:** {data.get('date_crawled', 'N/A')}\n\n---\n\n"

            content = header + data.get("content_markdown", "")
            output_path.write_text(content, encoding="utf-8")
            print(f"  ✓ Saved: {output_path} ({len(content)} chars)")


def convert_all():
    """Convert toàn bộ files."""
    print("=" * 50)
    print("Task 3: Convert to Markdown (MarkItDown)")
    print("=" * 50)

    print("\n--- Legal Documents ---")
    convert_legal_docs()

    print("\n--- News Articles ---")
    convert_news_articles()

    print("\n✓ Done! Output tại:", OUTPUT_DIR)


if __name__ == "__main__":
    convert_all()
