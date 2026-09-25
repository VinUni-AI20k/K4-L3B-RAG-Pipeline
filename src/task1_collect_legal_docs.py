"""
Task 1 — Thu thập tài liệu chính sách/quy định.

Hướng dẫn:
    1. Chọn chủ đề của nhóm.
    2. Tìm tối thiểu 3 tài liệu PDF/DOCX từ nguồn công khai.
    3. Lưu file gốc vào data/landing/legal/.
    4. Đặt tên không dấu và thể hiện đúng nội dung.

Ví dụ tài liệu: học phí, học bổng, ký túc xá, quy trình đăng ký.
Nếu website chặn crawler, hãy chọn nguồn công khai khác; không vượt WAF.
"""

import json
import os
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests
from dotenv import load_dotenv


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"
load_dotenv()


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def download_documents() -> None:
    """Tải ít nhất 3 PDF/DOCX từ nguồn công khai."""
    raw_sources = os.getenv("LEGAL_DOCUMENTS_JSON", "{}").strip()
    try:
        sources = json.loads(raw_sources)
    except json.JSONDecodeError as error:
        raise ValueError("LEGAL_DOCUMENTS_JSON must be valid JSON") from error
    if not isinstance(sources, dict) or not sources:
        raise ValueError(
            "Set LEGAL_DOCUMENTS_JSON to a JSON object mapping filenames to URLs"
        )
    if len(sources) < 3:
        raise ValueError("LEGAL_DOCUMENTS_JSON must contain at least 3 documents")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for configured_name, url in sources.items():
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            raise ValueError(f"Invalid public URL for {configured_name!r}")
        filename = str(configured_name).strip() or Path(
            unquote(urlparse(url).path)
        ).name
        if Path(filename).name != filename or Path(filename).suffix.lower() not in {
            ".pdf", ".doc", ".docx"
        }:
            raise ValueError(f"Unsupported or unsafe filename: {filename!r}")

        response = requests.get(url, timeout=(10, 60))
        response.raise_for_status()
        if len(response.content) < 1024:
            raise ValueError(f"Downloaded file is unexpectedly small: {filename}")
        output = DATA_DIR / filename
        output.write_bytes(response.content)
        print(f"Saved: {output}")


if __name__ == "__main__":
    setup_directory()
    download_documents()
