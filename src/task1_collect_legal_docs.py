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


LEGAL_SOURCES = {
    "quy_che_dao_tao_dhqghn_3626.pdf": "https://vnu.edu.vn/upload/2022/10/3626-QD-DHQGHN.pdf",
    "quy_dinh_hoc_bong_dhqghn_4618.pdf": "https://vnu.edu.vn/upload/2022/12/4618-QD-DHQGHN.pdf",
    "quy_trinh_canh_bao_hoc_vu_dhqghn.pdf": "https://vnu.edu.vn/upload/2023/canh-bao-hoc-vu.pdf",
}


def download_documents() -> None:
    """Tải ít nhất 3 PDF/DOCX từ nguồn công khai hoặc kiểm tra các file đã thu thập."""
    import requests

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print("Checking and collecting legal documents...")
    for filename, url in LEGAL_SOURCES.items():
        file_path = DATA_DIR / filename
        if file_path.exists() and file_path.stat().st_size > 1024:
            print(f"[OK] Document already exists: {filename} ({file_path.stat().st_size:,} bytes)")
            continue

        print(f"Downloading {filename} from {url}...")
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            file_path.write_bytes(response.content)
            print(f"[Downloaded] {filename} ({file_path.stat().st_size:,} bytes)")
        except Exception as error:
            print(f"[Warning] Could not download from {url}: {error}")
            if not file_path.exists():
                print(f"[Notice] Please place {filename} manually in {DATA_DIR}")

    # Kiểm tra số lượng tài liệu hợp lệ trong thư mục
    valid_files = [
        f for f in DATA_DIR.iterdir()
        if f.is_file() and not f.name.startswith(".") and f.suffix.lower() in {".pdf", ".doc", ".docx"} and f.stat().st_size > 1024
    ]
    if len(valid_files) < 3:
        raise RuntimeError(f"Yêu cầu tối thiểu 3 tài liệu legal hợp lệ, hiện có: {len(valid_files)}")
    print(f"[Done] Task 1: Verified {len(valid_files)} legal documents at {DATA_DIR}")


if __name__ == "__main__":
    setup_directory()
    download_documents()
