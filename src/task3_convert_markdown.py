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


def _yaml_escape(value: str) -> str:
    """Escape đơn giản để giá trị an toàn trong YAML front-matter một dòng."""
    return str(value).replace("\\", "\\\\").replace('"', '\\"')


def _front_matter(fields: dict) -> str:
    lines = ["---"]
    for key, value in fields.items():
        if value is None:
            lines.append(f"{key}: null")
        else:
            lines.append(f'{key}: "{_yaml_escape(value)}"')
    lines.append("---\n")
    return "\n".join(lines)


def convert_legal_docs() -> None:
    """Convert PDF/DOCX vào standardized/legal, kèm front-matter có url gốc."""
    from markitdown import MarkItDown

    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)
    converter = MarkItDown()

    manifest_path = legal_dir / "_manifest.json"
    manifest = {}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            manifest = {}

    for path in sorted(legal_dir.iterdir()):
        if path.suffix.lower() not in {".pdf", ".doc", ".docx"}:
            continue

        result = converter.convert(str(path))
        content = (result.text_content or "").strip()
        if not content:
            print(f"Skipped (empty content): {path.name}")
            continue

        url = manifest.get(path.name)
        if url is None:
            print(
                f"Warning: no source url in _manifest.json for {path.name}; "
                "add it manually so the document stays traceable."
            )

        front_matter = _front_matter({
            "title": path.stem.replace("_", " "),
            "source": path.name,
            "url": url,
            "doc_type": "legal",
        })
        (output_dir / f"{path.stem}.md").write_text(
            front_matter + "\n" + content, encoding="utf-8"
        )
        print(f"Converted: {path.name} -> {path.stem}.md")


def convert_news_articles() -> None:
    """Convert JSON vào standardized/news, kèm front-matter có url gốc."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    for path in sorted(news_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        content = (data.get("content_markdown") or "").strip()
        if not content:
            print(f"Skipped (empty content): {path.name}")
            continue

        front_matter = _front_matter({
            "title": data["title"],
            "url": data["url"],
            "date_crawled": data["date_crawled"],
            "doc_type": "news",
        })
        (output_dir / f"{path.stem}.md").write_text(
            front_matter + "\n" + content, encoding="utf-8"
        )
        print(f"Converted: {path.name} -> {path.stem}.md")


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"Saved Markdown to: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
