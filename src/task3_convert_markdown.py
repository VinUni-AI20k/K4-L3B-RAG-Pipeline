"""Task 3 - normalize legal documents and crawled articles to Markdown."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
LANDING_DIR = ROOT / "data" / "landing"
OUTPUT_DIR = ROOT / "data" / "standardized"
MIN_CONTENT_LENGTH = 200


def load_legal_manifest() -> list[dict[str, str]]:
    manifest = LANDING_DIR / "legal" / "sources.json"
    sources = json.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(sources, list) or len(sources) < 3:
        raise ValueError("Legal source manifest must contain at least 3 documents")
    return sources


def convert_legal_docs() -> None:
    """Convert official text-layer copies while retaining signed-file provenance."""
    from markitdown import MarkItDown

    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)
    converter = MarkItDown()

    for source in load_legal_manifest():
        source_path = legal_dir / source["text_file"]
        if not source_path.is_file():
            raise FileNotFoundError(f"Missing text source: {source_path}")

        content = converter.convert(str(source_path)).text_content.strip()
        if len(content) < MIN_CONTENT_LENGTH:
            raise ValueError(
                f"{source_path.name} produced only {len(content)} characters; "
                "use a text-layer document or OCR it first"
            )

        header = (
            f"# {source['title']}\n\n"
            f"**Số hiệu:** {source['document_number']}\n\n"
            f"**Ngày ban hành:** {source['issued_date']}\n\n"
            f"**Nguồn chính thức:** {source['official_page_url']}\n\n"
            f"**Bản ký số lưu tại:** {source['original_file']}\n\n"
            "---\n\n"
        )
        output = output_dir / f"{source['id']}.md"
        output.write_text(header + content + "\n", encoding="utf-8")
        print(f"Converted: {source_path.name} -> {output} ({len(content)} chars)")


def convert_news_articles() -> None:
    """Validate article metadata and preserve it at the top of each Markdown file."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)
    required_fields = {"url", "title", "date_crawled", "content_markdown"}

    for path in sorted(news_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        missing = required_fields - data.keys()
        if missing:
            raise ValueError(f"{path.name} is missing fields: {sorted(missing)}")

        empty = [field for field in required_fields if not str(data[field]).strip()]
        if empty:
            raise ValueError(f"{path.name} has empty fields: {sorted(empty)}")

        content = str(data["content_markdown"]).strip()
        if len(content) < MIN_CONTENT_LENGTH:
            raise ValueError(
                f"{path.name} contains only {len(content)} content characters"
            )

        header = (
            f"# {str(data['title']).strip()}\n\n"
            f"**Nguồn:** {str(data['url']).strip()}\n\n"
            f"**Thời điểm crawl (UTC):** {str(data['date_crawled']).strip()}\n\n"
            "---\n\n"
        )
        output = output_dir / f"{path.stem}.md"
        output.write_text(header + content + "\n", encoding="utf-8")
        print(f"Converted: {path.name} -> {output} ({len(content)} chars)")


def convert_all() -> None:
    """Convert the full landing corpus."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"Saved Markdown to: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
