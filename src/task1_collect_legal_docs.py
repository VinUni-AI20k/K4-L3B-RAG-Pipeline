"""
Task 1 — Thu thập tài liệu chính sách/quy định.

Chủ đề nhóm: Tuyển sinh Đại học Quốc gia Hà Nội (ĐHQGHN) 2026 — phương thức
xét tuyển, chỉ tiêu, học phí, điểm chuẩn.

Nguồn: quy chế tuyển sinh chung của Bộ GD&ĐT, quy chế và thông tin tuyển sinh
chính thức năm 2026 của ĐHQGHN. File gốc lưu vào data/landing/legal/.
Nếu website chặn crawler, hãy chọn nguồn công khai khác; không vượt WAF.
"""

import time
from pathlib import Path

import requests


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/153.0 Safari/537.36"
    )
}

# filename -> URL công khai
SOURCES = {
    # Thông tư 06/2026/TT-BGDĐT — Quy chế tuyển sinh đại học (phương thức, điểm sàn, nguyện vọng)
    "thong-tu-06-2026-quy-che-tuyen-sinh-dai-hoc.pdf":
        "https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/3/06-bgddt.pdf",
    # Quyết định 955/QĐ-ĐHQGHN — Quy chế tuyển sinh đại học của ĐHQG Hà Nội (từ 2026)
    "quy-che-tuyen-sinh-dhqg-ha-noi-2026.pdf":
        "https://xdcs.cdnchinhphu.vn/446259493575335936/2026/3/20/955-qd-dhqghn-2026-17739997160011924597755.pdf",
    # Thông tin tuyển sinh 2026 — Trường ĐH Giáo dục (thành viên ĐHQGHN):
    # chỉ tiêu, phương thức, tổ hợp, học phí
    "thong-tin-tuyen-sinh-2026-dh-giao-duc-dhqghn.pdf":
        "https://cdn.thuvienphapluat.vn/uploads/Hoidapphapluat/2026/CNT/Thang-6-2026/20-6-2026/TTTS-%C4%90HQGHN-2026.pdf",
    # Thông tin tuyển sinh 2026 — Trường ĐH Khoa học Tự nhiên (thành viên ĐHQGHN)
    "thong-tin-tuyen-sinh-2026-dh-khoa-hoc-tu-nhien-dhqghn.pdf":
        "https://cdn.tuyensinh247.com/picture/2026/0610/1860-signedsigned10-qd-ban-hanh-thong-tin-ts-2026-finalsigned.pdf",
}


# Tiêu đề hiển thị/citation cho từng tài liệu (Task 3 ghi vào metadata).
TITLES = {
    "thong-tu-06-2026-quy-che-tuyen-sinh-dai-hoc.pdf":
        "Thông tư 06/2026/TT-BGDĐT — Quy chế tuyển sinh trình độ đại học",
    "quy-che-tuyen-sinh-dhqg-ha-noi-2026.pdf":
        "Quyết định 955/QĐ-ĐHQGHN — Quy chế tuyển sinh đại học của ĐHQG Hà Nội",
    "thong-tin-tuyen-sinh-2026-dh-giao-duc-dhqghn.pdf":
        "Thông tin tuyển sinh đại học năm 2026 — Trường ĐH Giáo dục, ĐHQGHN",
    "thong-tin-tuyen-sinh-2026-dh-khoa-hoc-tu-nhien-dhqghn.pdf":
        "Thông tin tuyển sinh đại học năm 2026 — Trường ĐH Khoa học Tự nhiên, ĐHQGHN",
}


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def download_file(url: str, retries: int = 3) -> bytes:
    """Tải file, thử lại khi mạng chập chờn."""
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=120)
            response.raise_for_status()
            if not response.content.startswith((b"%PDF", b"PK")):
                raise ValueError("response is not a PDF/DOCX file")
            return response.content
        except (requests.RequestException, ValueError):
            if attempt == retries:
                raise
            time.sleep(2 * attempt)
    raise RuntimeError("unreachable")


def download_documents() -> None:
    """Tải các PDF/DOCX; bỏ qua file đã có để chạy lại không tải trùng."""
    for filename, url in SOURCES.items():
        target = DATA_DIR / filename
        if target.exists() and target.stat().st_size > 1024:
            print(f"Skip (exists): {filename}")
            continue
        try:
            target.write_bytes(download_file(url))
            print(f"Saved: {filename} ({target.stat().st_size // 1024} KB)")
        except Exception as error:
            print(f"Failed: {url} — {error}")


if __name__ == "__main__":
    setup_directory()
    download_documents()
