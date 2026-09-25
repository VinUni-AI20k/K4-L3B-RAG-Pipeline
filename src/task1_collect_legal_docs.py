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


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def download_documents() -> None:
    """Tải ít nhất 3 PDF/DOCX từ nguồn công khai."""

    import requests
    
    sources = {
        "chienluoc-marketing-dulich-vietnam.pdf": "https://images.vietnamtourism.gov.vn/vn/dmdocuments/2023/qdpheduyetchienluocmarketing.pdf",
        "sotay-dulich-congdong-vietnam.pdf": "https://images.vietnamtourism.gov.vn/vn/dmdocuments/CBTHandbookVNonepage.pdf",
        "camnang-dulich-saigon.pdf": "https://sodulich.hochiminhcity.gov.vn/UPLOADS/TINTUC/FILE/2022/7/202207291137205728.pdf",
    }
    for filename, url in sources.items():
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        (DATA_DIR / filename).write_bytes(response.content)

if __name__ == "__main__":
    setup_directory()
    download_documents()
