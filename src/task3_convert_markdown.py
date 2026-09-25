"""
Task 3 — Chuẩn hóa dữ liệu sang Markdown.

- PDF/DOCX trong landing/legal/ -> MarkItDown -> standardized/legal/<stem>.md
- JSON trong landing/news/      -> standardized/news/<stem>.md

Mỗi file Markdown mở đầu bằng YAML front matter (title, source, url, doc_type, ...)
để Task 4 đọc lại metadata. Chạy lại sẽ ghi đè cùng tên file và xoá file .md
không còn nguồn tương ứng, nên không sinh file trùng; tài liệu không trích được
text (vd. PDF scan) bị bỏ qua thay vì tạo file rỗng.
"""

import json
import re
from pathlib import Path

from src.task1_collect_legal_docs import SOURCES as LEGAL_URLS, TITLES as LEGAL_TITLES


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"

LEGAL_EXTENSIONS = {".pdf", ".doc", ".docx"}
MIN_CONTENT_CHARS = 200


def front_matter(metadata: dict) -> str:
    lines = ["---"]
    for key, value in metadata.items():
        if value is not None:
            lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def clean_text(text: str) -> str:
    """Dọn text trích từ PDF: bỏ khoảng trắng thừa, dòng chỉ có số trang, dòng trống lặp."""
    text = text.replace(" ", " ").replace("\f", "\n")
    lines = [line.rstrip() for line in text.splitlines()]
    lines = [line for line in lines if not re.fullmatch(r"\s*(-\s*)?\d{1,3}(\s*-)?\s*", line)]
    text = "\n".join(lines)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def write_markdown(output_dir: Path, stem: str, metadata: dict, body: str) -> Path | None:
    if len(body) < MIN_CONTENT_CHARS:
        print(f"Skip (no text): {stem} — {len(body)} chars")
        return None
    target = output_dir / f"{stem}.md"
    target.write_text(front_matter(metadata) + body + "\n", encoding="utf-8")
    print(f"Saved: {target.relative_to(OUTPUT_DIR)} ({len(body)} chars)")
    return target


def remove_stale(output_dir: Path, written: list[Path]) -> None:
    keep = {path.name for path in written}
    for path in output_dir.glob("*.md"):
        if path.name not in keep:
            path.unlink()
            print(f"Removed stale: {path.relative_to(OUTPUT_DIR)}")


def convert_legal_docs() -> None:
    from markitdown import MarkItDown

    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)
    converter = MarkItDown()

    written = []
    for path in sorted(legal_dir.iterdir()):
        if path.suffix.lower() not in LEGAL_EXTENSIONS:
            continue
        try:
            body = clean_text(converter.convert(str(path)).text_content)
        except Exception as error:
            print(f"Failed: {path.name} — {error}")
            continue
        metadata = {
            "title": LEGAL_TITLES.get(path.name, path.stem),
            "source": path.name,
            "url": LEGAL_URLS.get(path.name),
            "doc_type": "legal",
        }
        if target := write_markdown(output_dir, path.stem, metadata, body):
            written.append(target)
    remove_stale(output_dir, written)


def convert_news_articles() -> None:
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    written = []
    for path in sorted(news_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        metadata = {
            "title": data["title"],
            "source": path.name,
            "url": data["url"],
            "doc_type": "news",
            "date_published": data.get("date_published"),
            "date_crawled": data["date_crawled"],
        }
        body = f"# {data['title']}\n\n{clean_text(data['content_markdown'])}"
        if target := write_markdown(output_dir, path.stem, metadata, body):
            written.append(target)
    remove_stale(output_dir, written)


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"Saved Markdown to: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
