"""
Task 2 — Crawl bài viết/thông báo.

Chủ đề: thuế và nghĩa vụ kê khai của hộ kinh doanh cá thể.

7 bài viết (>=5 yêu cầu), phủ cả chế độ thuế cũ và cải cách hiện hành
(quyết định cùng người dùng: giữ cả hai vì "thuế môn bài" và "phương pháp
khoán" đã bị bãi bỏ từ 01/01/2026 nhưng vẫn là kiến thức nền cần thiết):
    - Cải cách 2026: bỏ thuế khoán, bỏ lệ phí môn bài, cách tính thuế mới.
    - Nền/lịch sử: cách tính thuế khoán (trước 2026) để đối chiếu.
    - Vận hành: hoá đơn điện tử, phạt chậm nộp hồ sơ khai thuế.

Cài browser trước khi chạy:
    python -m playwright install chromium
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    # Cai cach 2026: bo ap dung thue khoan.
    "https://www.vietnamplus.vn/bo-ap-dung-thue-khoan-ho-kinh-doanh-buoc-vao-cuoc-choi-moi-post1042297.vnp",
    # Cai cach 2026: chinh thuc bo le phi mon bai.
    "https://einvoice.vn/tin-tuc/bo-thue-mon-bai",
    # Cai cach 2026: tong quan noi dung moi ND68/2026 + TT18/2026 (chinhphu.vn).
    "https://xaydungchinhsach.chinhphu.vn/noi-dung-moi-cua-nghi-dinh-68-2026-nd-cp-va-thong-tu-18-2026-tt-btc-nguoi-nop-thue-can-luu-y-119260312140920747.htm",
    # Cai cach 2026: cach tinh thue ho kinh doanh theo quy dinh moi.
    "https://sme.misa.vn/334301/thue-ho-kinh-doanh/",
    # Nen/lich su: cach tinh thue khoan truoc 2026, de doi chieu.
    "https://www.meinvoice.vn/tin-tuc/17722/cach-tinh-thue-khoan-ho-kinh-doanh/",
    # Van hanh: hoa don dien tu cho ho kinh doanh.
    "https://easybooks.vn/hoa-don-ho-kinh-doanh/",
    # Van hanh: muc phat cham nop ho so khai thue tu 2026.
    "https://einvoice.vn/tin-tuc/muc-phat-cham-nop-ho-so-khai-thue",
]


async def crawl_article(url: str) -> dict:
    from crawl4ai import AsyncWebCrawler

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        if not result.success or (result.status_code or 200) >= 400:
            raise ValueError(f"Crawl failed for {url}: {result.error_message}")
        title = (result.metadata or {}).get("title") or url
        markdown = str(result.markdown) if result.markdown else ""
        if not markdown.strip():
            raise ValueError(f"Empty markdown for {url}")
        return {
            "url": url,
            "title": title,
            "date_crawled": datetime.now().isoformat(),
            "content_markdown": markdown,
        }


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for index, url in enumerate(ARTICLE_URLS, 1):
        try:
            article = await crawl_article(url)
            output = DATA_DIR / f"article_{index:02d}.json"
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"Saved: {output}")
        except Exception as error:
            print(f"Failed: {url} — {error}")


if __name__ == "__main__":
    asyncio.run(crawl_all())
