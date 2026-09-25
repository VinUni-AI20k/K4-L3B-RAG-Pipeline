"""Task 3 — Chuẩn hóa dữ liệu sang Markdown.

Tài liệu pháp lý được chuyển đổi bằng MarkItDown. Bài viết đã crawl được
đọc từ JSON và giữ metadata ở đầu file Markdown. Đầu ra giữ cấu trúc
``standardized/legal`` và ``standardized/news``.
"""

import json
from pathlib import Path


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def convert_legal_docs() -> None:
    """Convert PDF/DOC/DOCX trong landing/legal sang Markdown."""
    from markitdown import MarkItDown

    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    converter = MarkItDown()
    supported_extensions = {".pdf", ".doc", ".docx"}

    for path in sorted(legal_dir.iterdir()):
        if (
            not path.is_file()
            or path.name.startswith(".")
            or path.suffix.lower() not in supported_extensions
        ):
            continue

        try:
            result = converter.convert(str(path))
            markdown = result.text_content.strip()
            if not markdown:
                print(f"Skipped empty document: {path}")
                continue

            # Tên cố định giúp lần chạy sau cập nhật đúng file, không tạo bản sao.
            output_path = output_dir / f"{path.stem}.md"
            content = f"{markdown}\n"
            if (
                output_path.exists()
                and output_path.read_text(encoding="utf-8") == content
            ):
                print(f"Unchanged: {output_path}")
                continue

            output_path.write_text(content, encoding="utf-8")
            print(f"Saved: {output_path}")
        except Exception as error:
            print(f"Failed: {path} — {error}")


def convert_news_articles() -> None:
    """Convert JSON trong landing/news sang Markdown và giữ metadata."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    required_fields = ("url", "title", "date_crawled", "content_markdown")

    for path in sorted(news_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            if not isinstance(data, dict):
                raise ValueError("JSON root must be an object")

            missing_fields = [
                field
                for field in required_fields
                if not isinstance(data.get(field), str) or not data[field].strip()
            ]
            if missing_fields:
                raise ValueError(
                    f"Missing or empty fields: {', '.join(missing_fields)}"
                )

            header = (
                f"# {data['title'].strip()}\n\n"
                f"**Source:** {data['url'].strip()}\n\n"
                f"**Crawled:** {data['date_crawled'].strip()}\n\n"
                "---\n\n"
            )
            content = f"{header}{data['content_markdown'].strip()}\n"
            output_path = output_dir / f"{path.stem}.md"

            if (
                output_path.exists()
                and output_path.read_text(encoding="utf-8") == content
            ):
                print(f"Unchanged: {output_path}")
                continue

            output_path.write_text(content, encoding="utf-8")
            print(f"Saved: {output_path}")
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
            print(f"Failed: {path} — {error}")


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing sang Markdown."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"Saved Markdown to: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
