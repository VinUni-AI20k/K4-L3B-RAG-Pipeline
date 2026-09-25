"""
Task 3 — Chuẩn hóa dữ liệu sang Markdown.

Hướng dẫn:
    1. Dùng MarkItDown để convert PDF/DOC/DOCX.
    2. Đọc JSON và giữ metadata ở đầu file Markdown.
    3. Giữ cấu trúc thư mục legal/ và news/.
    4. Không tạo file rỗng hoặc file trùng khi chạy lại.

Cài đặt:
    Dependency MarkItDown đã được khai báo trong pyproject.toml.

-> Hoặc dùng công cụ nào bạn quen khác MarkItDown.
"""

import json
import os
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from markitdown import MarkItDown


# =========================
# Cấu hình đường dẫn
# =========================

ROOT_DIR = Path(__file__).parent.parent

LANDING_DIR = ROOT_DIR / "data" / "landing"
OUTPUT_DIR = ROOT_DIR / "data" / "standardized"


# =========================
# Convert Legal Documents
# =========================

def ocr_scanned_pdf(path: Path) -> str:
    """Extract real text from scanned pages using local Vietnamese/English OCR."""
    import pypdfium2 as pdfium

    executable = shutil.which("tesseract")
    if not executable:
        installed = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Tesseract-OCR/tesseract.exe"
        if installed.is_file():
            executable = str(installed)
    if not executable:
        raise RuntimeError("Scanned PDF requires Tesseract OCR with vie and eng language data")
    data_dir = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "Tesseract-OCR/tessdata"
    data_args = ["--tessdata-dir", str(data_dir)] if data_dir.is_dir() else []
    languages = subprocess.run(
        [executable, *data_args, "--list-langs"], capture_output=True, text=True, check=True,
    ).stdout.splitlines()
    if "vie" not in languages or "eng" not in languages:
        raise RuntimeError("Install Tesseract vie.traineddata and eng.traineddata for scanned PDFs")

    def recognize(image: Path) -> str:
        result = subprocess.run(
            [executable, str(image), "stdout", *data_args, "-l", "vie+eng"],
            capture_output=True, encoding="utf-8", check=True, timeout=180,
            env={**os.environ, "OMP_THREAD_LIMIT": "1"},
        )
        image.unlink()
        return result.stdout.strip()

    with tempfile.TemporaryDirectory(prefix="legal-ocr-") as folder:
        with ThreadPoolExecutor(max_workers=4) as pool:
            pending = []
            document = pdfium.PdfDocument(str(path))
            try:
                print(f"OCR: {path.name} ({len(document)} pages)", flush=True)
                for number in range(len(document)):
                    page = document[number]
                    bitmap = page.render(scale=3)
                    image = bitmap.to_pil()
                    target = Path(folder) / f"page-{number + 1}.png"
                    try:
                        image.save(target)
                    finally:
                        image.close()
                        bitmap.close()
                        page.close()
                    pending.append(pool.submit(recognize, target))
            finally:
                document.close()
            pages = []
            for number, future in enumerate(pending, 1):
                text = future.result()
                if not text:
                    raise RuntimeError(f"OCR returned no text for {path.name}, page {number}")
                pages.append(f"## Page {number}\n\n{text}")
                print(f"OCR page {number}/{len(pending)} complete", flush=True)
    return "\n\n".join(pages)


def convert_legal_docs() -> None:
    """
    Convert các tài liệu PDF/DOC/DOCX trong data/landing/legal
    sang Markdown và lưu tại data/standardized/legal.
    """

    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"

    # Kiểm tra thư mục đầu vào
    if not legal_dir.exists():
        print(f"Legal directory does not exist: {legal_dir}")
        return

    # Tạo thư mục output
    output_dir.mkdir(parents=True, exist_ok=True)

    converter = MarkItDown()

    supported_extensions = {".pdf", ".doc", ".docx"}

    for path in sorted(legal_dir.iterdir()):

        # Bỏ qua folder và các file không được hỗ trợ
        if not path.is_file():
            continue

        if path.suffix.lower() not in supported_extensions:
            continue

        try:
            print(f"Converting legal document: {path.name}")

            result = converter.convert(str(path))

            # Lấy nội dung được MarkItDown convert
            content = result.text_content or ""
            if not content.strip() and path.suffix.lower() == ".pdf":
                content = ocr_scanned_pdf(path)

            if content is None:
                print(f"Skipped empty document: {path.name}")
                continue

            content = content.strip()

            # Không tạo file Markdown rỗng
            if not content:
                print(f"Skipped empty document: {path.name}")
                continue

            output_path = output_dir / f"{path.stem}.md"

            # write_text sẽ ghi đè file cùng tên khi chạy lại,
            # vì vậy không sinh ra các bản sao.
            output_path.write_text(
                content + "\n",
                encoding="utf-8",
            )

            print(f"Saved: {output_path}")

        except Exception as error:
            print(f"Failed to convert {path.name}: {error}")


# =========================
# Convert News JSON
# =========================

def convert_news_articles() -> None:
    """
    Convert các JSON trong data/landing/news thành Markdown.

    Metadata được giữ ở đầu file:
        - title
        - url
        - date_crawled
    """

    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"

    # Kiểm tra thư mục đầu vào
    if not news_dir.exists():
        print(f"News directory does not exist: {news_dir}")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    required_fields = {
        "url",
        "title",
        "date_crawled",
        "content_markdown",
    }

    for path in sorted(news_dir.glob("*.json")):

        try:
            print(f"Converting news article: {path.name}")

            # Đọc JSON
            data = json.loads(
                path.read_text(encoding="utf-8")
            )

            # Kiểm tra đủ metadata
            missing_fields = required_fields - data.keys()

            if missing_fields:
                print(
                    f"Skipped {path.name}: "
                    f"missing fields {sorted(missing_fields)}"
                )
                continue

            # Lấy dữ liệu
            title = str(data["title"]).strip()
            url = str(data["url"]).strip()
            date_crawled = str(data["date_crawled"]).strip()
            content = str(data["content_markdown"]).strip()

            # Không tạo file nếu dữ liệu quan trọng bị rỗng
            if not all([title, url, date_crawled, content]):
                print(
                    f"Skipped {path.name}: "
                    "required metadata/content is empty"
                )
                continue

            # Metadata header
            header = (
                f"# {title}\n\n"
                f"**Source:** {url}\n\n"
                f"**Crawled:** {date_crawled}\n\n"
                "---\n\n"
            )

            markdown = header + content + "\n"

            output_path = output_dir / f"{path.stem}.md"

            # Ghi đè cùng tên nếu chạy lại
            output_path.write_text(
                markdown,
                encoding="utf-8",
            )

            print(f"Saved: {output_path}")

        except json.JSONDecodeError as error:
            print(f"Invalid JSON {path.name}: {error}")

        except Exception as error:
            print(f"Failed to convert {path.name}: {error}")


# =========================
# Convert toàn bộ Corpus
# =========================

def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing sang standardized."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Converting legal documents...")
    print("=" * 60)

    convert_legal_docs()

    print()

    print("=" * 60)
    print("Converting news articles...")
    print("=" * 60)

    convert_news_articles()

    print()

    print(f"Saved Markdown to: {OUTPUT_DIR}")


# =========================
# Main
# =========================

if __name__ == "__main__":
    convert_all()