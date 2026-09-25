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
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"
# Ghi lại filename -> url gốc để Task 3 nhúng vào metadata Markdown.
# Nếu không có bước này, sau khi convert sang .md sẽ KHÔNG còn cách nào
# đối chiếu ngược một tài liệu đã chuẩn hoá với nguồn công khai của nó.
MANIFEST_PATH = DATA_DIR / "_manifest.json"


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def download_documents() -> None:
    """Tải ít nhất 3 PDF/DOCX từ nguồn công khai và ghi manifest url."""
    import requests

    sources = {
        "phap_luat_ve_ho_kinh_doanh_vn.pdf": "https://fdvn.vn/wp-content/uploads/2025/05/luu-ban-nhap-tu-dong-9-5.pdf",
        "so_tay_thue.pdf": "https://cdn.thuvienphapluat.vn/uploads/khoinghiep/2026/03/10/SO-TAY-HO-KINH-DOANH.pdf",
        "dia_vi_phap_ly.pdf": "https://economica.vn/Content/files/PUBL%20%26%20REP/Dia%20vi%20Phap%20ly%20cua%20Ho%20Kinh%20doanh%20-%20Thuc%20trang%20và%20Giai%20phap.pdf",
    }

    manifest = _load_manifest()
    for filename, url in sources.items():
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        (DATA_DIR / filename).write_bytes(response.content)
        manifest[filename] = url
        print(f"Downloaded: {filename}")
    _write_manifest(manifest)


def _load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        return {}
    try:
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_manifest(manifest: dict) -> None:
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    setup_directory()
    download_documents()
