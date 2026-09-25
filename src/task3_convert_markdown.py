"""Task 3 — Chuẩn hóa dữ liệu sang Markdown."""

import json
from pathlib import Path


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"
LEGAL_EXTENSIONS = {".pdf", ".doc", ".docx"}


def ocr_pdf(path: Path) -> str:
    """OCR PDF scan bằng Tesseract khi PDF không có lớp văn bản."""
    try:
        import fitz
        import pytesseract
        from PIL import Image
    except ImportError as error:
        raise RuntimeError(
            "Thieu dependency OCR. Cai: python -m pip install pymupdf pytesseract pillow"
        ) from error

    try:
        languages = pytesseract.get_languages(config="")
    except pytesseract.TesseractNotFoundError as error:
        raise RuntimeError(
            "Khong tim thay Tesseract OCR. Hay cai Tesseract va goi ngon ngu Vietnamese (vie)."
        ) from error

    language = "vie+eng" if "vie" in languages else "eng"
    pages: list[str] = []
    document = fitz.open(path)
    try:
        for page in document:
            pixmap = page.get_pixmap(dpi=300, alpha=False)
            image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
            text = pytesseract.image_to_string(image, lang=language).strip()
            if text:
                pages.append(text)
    finally:
        document.close()

    return "\n\n---\n\n".join(pages)


def convert_legal_docs() -> None:
    """Chuyển các PDF/DOCX pháp lý ở landing sang Markdown."""
    from markitdown import MarkItDown

    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not legal_dir.exists():
        print(f"Khong tim thay thu muc: {legal_dir}")
        return

    converter = MarkItDown()
    for path in legal_dir.iterdir():
        if not path.is_file() or path.suffix.lower() not in LEGAL_EXTENSIONS:
            continue

        try:
            content = converter.convert(str(path)).text_content.strip()
            if not content and path.suffix.lower() == ".pdf":
                print(f"PDF scan, dang OCR: {path.name}")
                content = ocr_pdf(path)
            if not content:
                print(f"Bo qua file rong: {path.name}")
                continue

            output_path = output_dir / f"{path.stem}.md"
            output_path.write_text(content + "\n", encoding="utf-8")
            print(f"Saved: {output_path}")
        except Exception as error:
            print(f"Failed: {path.name} — {error}")


def convert_news_articles() -> None:
    """Chuyển các JSON bài viết ở landing sang Markdown, giữ metadata."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not news_dir.exists():
        print(f"Khong tim thay thu muc: {news_dir}")
        return

    required_fields = {"title", "url", "date_crawled", "content_markdown"}
    for path in news_dir.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            missing_fields = required_fields - data.keys()
            content = str(data.get("content_markdown", "")).strip()
            if missing_fields or not content:
                detail = f"thieu truong: {', '.join(sorted(missing_fields))}" if missing_fields else "noi dung rong"
                print(f"Bo qua {path.name}: {detail}")
                continue

            header = (
                f"# {data['title']}\n\n"
                f"**Source:** {data['url']}\n\n"
                f"**Crawled:** {data['date_crawled']}\n\n---\n\n"
            )
            output_path = output_dir / f"{path.stem}.md"
            output_path.write_text(header + content + "\n", encoding="utf-8")
            print(f"Saved: {output_path}")
        except (json.JSONDecodeError, OSError) as error:
            print(f"Failed: {path.name} — {error}")


def convert_all() -> None:
    """Chuyển toàn bộ dữ liệu landing sang Markdown."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"Saved Markdown to: {OUTPUT_DIR}")


if __name__ == "__main__":    convert_all()