"""
Task 1 — Thu thập tài liệu chính sách/quy định.

Chủ đề nhóm: Hướng dẫn trò chơi — Liên Quân Mobile (Arena of Valor).

Tài liệu chính sách/quy định của chủ đề (nguồn chính thức của Garena /
Hội Đồng Liên Quân Mobile, đều tải được bằng requests):

    1. Điều khoản dịch vụ Garena (tos.html)
    2. Các hành vi bị xử phạt và thời hạn khóa (Hội Đồng Liên Quân)
    3. Cập nhật hành vi bị xử phạt và thời hạn khóa từ 1/1/2026

Tài liệu lưu dạng HTML vào data/landing/legal/ (task 3 sẽ chuyển Markdown).
Tên file không dấu, thể hiện đúng nội dung.
"""

import json
from datetime import datetime
from pathlib import Path

import requests

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

SOURCES = {
    "garena-dieu-khoan-dich-vu.html":
        "https://cdn.vn.garenanow.com/web/ddt/legal/tos.html",
    "lienquan-cac-hanh-vi-bi-xu-phat-va-thoi-han-khoa.html":
        "https://lienquan.garena.vn/cac-hanh-vi-bi-xu-phat-va-thoi-han-khoa/",
    "lienquan-cap-nhat-hanh-vi-bi-xu-phat-tu-01012026.html":
        "https://lienquan.garena.vn/cap-nhat-cac-hanh-vi-bi-xu-phat-va-thoi-han-khoa-tu-1-1-2026/",
}


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def download_documents() -> None:
    """Tải từng tài liệu, lưu nội dung + metadata nguồn."""
    manifest = {}
    for filename, url in SOURCES.items():
        try:
            response = requests.get(url, timeout=30, headers={"User-Agent": USER_AGENT})
            response.raise_for_status()
            (DATA_DIR / filename).write_bytes(response.content)
            manifest[filename] = {
                "url": url,
                "date_crawled": datetime.now().isoformat(),
                "size_bytes": len(response.content),
            }
            print(f"Saved: {filename} ({len(response.content)} bytes)")
        except requests.RequestException as error:
            print(f"Failed: {url} — {error}")

    manifest_path = DATA_DIR / "sources.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Saved: {manifest_path}")


if __name__ == "__main__":
    setup_directory()
    download_documents()
