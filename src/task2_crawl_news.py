"""
Task 2 — Crawl bài viết/hướng dẫn hỗ trợ khách hàng về thương mại điện tử.

Hướng dẫn:
    1. Crawl/thu thập tối thiểu 5 bài viết từ trung tâm trợ giúp của sàn TMĐT.
    2. Lưu output vào data/landing/news/
    3. Mỗi bài lưu 1 file JSON với metadata (url, title, date_crawled, content_markdown).
"""

import sys
import json
from datetime import datetime
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).parent.parent
SOURCE_DIR = PROJECT_ROOT / "data" / "shoppe_warranty"
LANDING_NEWS_DIR = PROJECT_ROOT / "data" / "landing" / "news"


def setup_directory():
    """Tạo thư mục data/landing/news/ nếu chưa có."""
    LANDING_NEWS_DIR.mkdir(parents=True, exist_ok=True)


ARTICLES_META = [
    {
        "filename": "dispute-process.json",
        "source_md": "dispute-process.md",
        "url": "https://help.shopee.vn/portal/4/article/77251-quy-trinh-giai-quyet-tranh-chap",
        "title": "Quy trình xử lý khiếu nại và tranh chấp trên Shopee",
    },
    {
        "filename": "return-refund-process.json",
        "source_md": "return-refund-process.md",
        "url": "https://help.shopee.vn/portal/4/article/77252-quy-trinh-tra-hang-hoan-tien",
        "title": "Hướng dẫn các bước yêu cầu Trả hàng và Hoàn tiền Shopee",
    },
    {
        "filename": "seller-listing-policy.json",
        "source_md": "seller-listing-policy.md",
        "url": "https://banhang.shopee.vn/edu/article/1852",
        "title": "Quy định đăng bán sản phẩm và tiêu chuẩn cộng đồng Shopee",
    },
    {
        "filename": "shopee-guarantee.json",
        "source_md": "shopee-guarantee.md",
        "url": "https://help.shopee.vn/portal/4/article/77248-chinh-sach-shopee-dam-bao",
        "title": "Chính sách Shopee Đảm Bảo bảo vệ quyền lợi người mua",
    },
    {
        "filename": "shopee-mall-terms.json",
        "source_md": "shopee-mall-terms.md",
        "url": "https://help.shopee.vn/portal/4/article/77255-dieu-khoan-dich-vu-shopee-mall",
        "title": "Điều khoản dịch vụ và cam kết hàng chính hãng Shopee Mall",
    },
]


def collect_news_articles():
    """Thu thập 5 bài viết trợ giúp khách hàng vào data/landing/news/."""
    setup_directory()

    for item in ARTICLES_META:
        md_path = SOURCE_DIR / item["source_md"]
        if not md_path.exists():
            continue

        content = md_path.read_text(encoding="utf-8")
        article_data = {
            "url": item["url"],
            "title": item["title"],
            "date_crawled": datetime.now().isoformat(),
            "content_markdown": content,
        }

        output_path = LANDING_NEWS_DIR / item["filename"]
        output_path.write_text(json.dumps(article_data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✓ Đã lưu bài viết: {output_path} ({output_path.stat().st_size} bytes)")


if __name__ == "__main__":
    collect_news_articles()
