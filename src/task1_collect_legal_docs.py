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
    """Tải ít nhất 3 PDF/DOCX từ nguồn công khai của HUTECH."""
    import urllib.request

    sources = {
        "quy_che_tuyen_sinh_dhcq_2026.pdf": "https://www.hutech.edu.vn/download/tuyensinh/74031",
        "thong_tin_tuyen_sinh_dhcq_2026.pdf": "https://www.hutech.edu.vn/download/tuyensinh/74376",
        "phieu_dang_ky_tuyen_sinh_hutech.doc": "https://www.hutech.edu.vn/download/e-hutech/42865",
        "ly_lich_sinh_vien_hutech.doc": "https://www.hutech.edu.vn/download/e-hutech/42864",
    }

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    for filename, url in sources.items():
        file_path = DATA_DIR / filename
        if file_path.exists() and file_path.stat().st_size > 0:
            print(f"Already exists: {filename} ({file_path.stat().st_size} bytes)")
            continue

        print(f"Downloading: {filename} from {url}...")
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as response:
                content = response.read()
                if content:
                    file_path.write_bytes(content)
                    print(f"Saved: {filename} ({len(content)} bytes)")
                else:
                    print(f"Warning: {filename} received empty content.")
        except Exception as exc:
            print(f"Failed to download {filename}: {exc}")


if __name__ == "__main__":
    setup_directory()
    download_documents()

