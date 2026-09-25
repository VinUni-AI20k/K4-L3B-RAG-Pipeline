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
    
    # TODO: Thay thế các URL dưới đây bằng link tài liệu thực tế nhóm bạn tìm được
    sources = {
        "luat-giao-duc-2019.pdf": "https://datafiles.chinhphu.vn/cpp/files/vbpq/2019/07/43.signed.pdf",
        "quy-che-dao-tao-dai-hoc.pdf": "https://datafiles.chinhphu.vn/cpp/files/vbpq/2021/04/08-bgd.signed.pdf",
        "nghi-dinh-81-hoc-phi.pdf": "https://datafiles.chinhphu.vn/cpp/files/vbpq/2021/08/81.signed.pdf",
    }
    
    print("Bat dau tai tai lieu...")
    for filename, url in sources.items():
        print(f"Dang tai {filename}...")
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            (DATA_DIR / filename).write_bytes(response.content)
            print(f"-> Da tai thanh cong: {filename}")
        except Exception as e:
            print(f"-> Loi khi tai {filename}: {e}")


if __name__ == "__main__":
    setup_directory()
    download_documents()
