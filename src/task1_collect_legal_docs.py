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

from pathlib import Path

import requests


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"

# Danh sách tài liệu cần tải: (tên file, URL công khai)
# TODO: Thay thế bằng URL thực tế phù hợp với chủ đề của nhóm.
DOCUMENT_SOURCES: dict[str, str] = {
    # Ví dụ (thay bằng URL thực):
    # "hoc-phi-2024.pdf": "https://example.edu/hoc-phi-2024.pdf",
    # "quy-che-hoc-bong.pdf": "https://example.edu/hoc-bong.pdf",
    # "noi-quy-ky-tuc-xa.pdf": "https://example.edu/noi-quy-ktx.pdf",
}


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def download_documents() -> None:
    """Tải ít nhất 3 PDF/DOCX từ nguồn công khai."""
    if not DOCUMENT_SOURCES:
        raise ValueError(
            "DOCUMENT_SOURCES trống. Hãy thêm ít nhất 3 URL tài liệu vào DOCUMENT_SOURCES."
        )

    for filename, url in DOCUMENT_SOURCES.items():
        dest = DATA_DIR / filename
        if dest.exists():
            print(f"Already exists, skipping: {dest.name}")
            continue
        print(f"Downloading: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        dest.write_bytes(response.content)
        print(f"Saved: {dest}")

    downloaded = list(DATA_DIR.iterdir())
    print(f"\nTotal files in {DATA_DIR}: {len(downloaded)}")


if __name__ == "__main__":
    setup_directory()
    download_documents()
