"""
Task 1 — Thu thập tài liệu chính sách/quy định.

Chủ đề nhóm: hỗ trợ tra cứu kiến thức migration lên AWS.

Nguồn: AWS Prescriptive Guidance (tài liệu công khai, bản PDF chính thức).
Ba playbook bao phủ ba giai đoạn của một đợt large migration:
    - foundation: nền tảng, tổ chức và điều kiện cần trước khi migrate.
    - portfolio: kiểm kê ứng dụng, phân tích và xếp wave.
    - migration: thực thi migrate theo từng wave.

Chạy:
    python -m src.task1_collect_legal_docs
"""

from pathlib import Path

import requests


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"

# Tên file không dấu, phản ánh đúng nội dung tài liệu.
SOURCES: dict[str, str] = {
    "aws-large-migration-foundation-playbook.pdf": (
        "https://docs.aws.amazon.com/pdfs/prescriptive-guidance/latest/"
        "large-migration-foundation-playbook/large-migration-foundation-playbook.pdf"
    ),
    "aws-large-migration-portfolio-playbook.pdf": (
        "https://docs.aws.amazon.com/pdfs/prescriptive-guidance/latest/"
        "large-migration-portfolio-playbook/large-migration-portfolio-playbook.pdf"
    ),
    "aws-large-migration-migration-playbook.pdf": (
        "https://docs.aws.amazon.com/pdfs/prescriptive-guidance/latest/"
        "large-migration-migration-playbook/large-migration-migration-playbook.pdf"
    ),
}

# docs.aws.amazon.com trả 403 cho user-agent mặc định của requests.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    )
}

MIN_PDF_BYTES = 10_000


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def download_documents() -> None:
    """Tải các PDF trong SOURCES về data/landing/legal/.

    File đã tải đủ lớn thì bỏ qua, nên chạy lại script không tải trùng.
    """
    for filename, url in SOURCES.items():
        target = DATA_DIR / filename

        if target.exists() and target.stat().st_size >= MIN_PDF_BYTES:
            print(f"Skip (exists): {filename} — {target.stat().st_size:,} bytes")
            continue

        try:
            response = requests.get(url, headers=HEADERS, timeout=120)
            response.raise_for_status()
        except requests.RequestException as error:
            print(f"Failed: {filename} — {error}")
            continue

        content = response.content
        if not content.startswith(b"%PDF"):
            print(f"Failed: {filename} — nội dung trả về không phải PDF")
            continue

        target.write_bytes(content)
        print(f"Saved: {target} — {len(content):,} bytes")


if __name__ == "__main__":
    setup_directory()
    download_documents()
