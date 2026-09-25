"""
Task 1 — Thu thập tài liệu chính sách/quy định.

Chủ đề: thuế và nghĩa vụ kê khai của hộ kinh doanh cá thể.

Nguồn: bản DOCX chính thức từ Công báo Chính phủ (congbao.chinhphu.vn),
không phải bản PDF ký số quét ảnh (bản "signed.pdf" ở vanban.chinhphu.vn
không có lớp text, xác minh bằng markitdown/pdfminer trả về 0 ký tự).
DOCX công báo cùng nguồn chính phủ, có text thật, tải trực tiếp không bị
chặn crawler.

Lưu ý về hiệu lực (tính đến 2026-09-25): Thông tư 40/2021/TT-BTC và
Thông tư 100/2021/TT-BTC đã được thay thế hoàn toàn bởi Thông tư
18/2026/TT-BTC (05/03/2026). Nghị định 123/2020/NĐ-CP về hoá đơn đã được
thay thế bởi Nghị định 254/2026/NĐ-CP (hiệu lực 01/07/2026). Bộ tài liệu
dưới đây dùng văn bản hiện hành để nội dung nhất quán với luật hiện hành.
"""

from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"

SOURCES = {
    # Thong tu 18/2026/TT-BTC: ho so, thu tuc quan ly thue ho kinh doanh
    # (thay the TT 40/2021 va TT 100/2021).
    "tt18-2026-quan-ly-thue-ho-kinh-doanh.docx": (
        "https://g7.cdnchinhphu.vn/api/download/stream?Url=tm-8mq6BhNw0NbrKRhTDAaHMpvrqWaeHuYm7lW3HNfzTzww8Myg35dDL_fJB4izwth3Z8MXJWj0Y0b1097zzz-yVSCh9FwVBAjjddI_8iBRW-UbSXKjlthf3_nL_itW4sXquQM4bz56haJOFTUxaqQ~~"
        "&file_name=2026_159_18%2f2026%2fTT-BTC.docx"
    ),
    # Nghi dinh 68/2026/ND-CP: chinh sach thue GTGT/TNCN va quan ly thue
    # ho kinh doanh (phuong phap tinh thue, nguong doanh thu hien hanh).
    "nd68-2026-chinh-sach-thue-ho-kinh-doanh.docx": (
        "https://g7.cdnchinhphu.vn/api/download/stream?Url=tm-8mq6BhNw0NbrKRhTDAaHMpvrqWaeHuYm7lW3HNfzTzww8Myg35dDL_fJB4izwVtxmiC9gRLYk2b9Cs-E1hZsYgY567JTjjZQILPhOmGI83wBGrdMTcT__Vcu3d5sA9U-roOrTIWu79TeJQ2hFcg~~"
        "&file_name=2026_152_68%2f2026%2fN%c4%90-CP.docx"
    ),
    # Nghi dinh 254/2026/ND-CP: hoa don dien tu, chung tu dien tu
    # (thay the Nghi dinh 123/2020/ND-CP tu 01/07/2026).
    "nd254-2026-hoa-don-dien-tu.docx": (
        "https://g7.cdnchinhphu.vn/api/download/stream?Url=tm-8mq6BhNw0NbrKRhTDAaHMpvrqWaeHuYm7lW3HNfzTzww8Myg35dDL_fJB4izwaJVtTUJPtqt6_lxqg89MBHuMxBLIIvAw_GQuw0oHHffIwUJTeMiG7wiqZEEK9AYSs5aPmnoI9c-qYRHg-YOeWw~~"
        "&file_name=2026_402_254%2f2026%2fN%c4%90-CP.docx"
    ),
}


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def download_documents() -> None:
    """Tải các văn bản luật hiện hành từ Công báo Chính phủ."""
    import subprocess

    # g7.cdnchinhphu.vn's server-sent certificate chain is missing an
    # intermediate, which Python's bundled certifi store rejects
    # (requests raises SSLError there). System curl still verifies TLS
    # normally and succeeds because it consults the OS trust store, which
    # already has that intermediate cached. Shelling out to curl keeps
    # certificate verification on; it does not weaken or bypass it.
    for filename, url in SOURCES.items():
        target = DATA_DIR / filename
        if target.exists() and target.stat().st_size > 1024:
            print(f"Skip existing: {filename}")
            continue
        subprocess.run(
            [
                "curl", "-fsSL", "-A", "Mozilla/5.0",
                "--max-time", "40",
                "-o", str(target),
                url,
            ],
            check=True,
        )
        print(f"Downloaded: {filename} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    setup_directory()
    download_documents()
