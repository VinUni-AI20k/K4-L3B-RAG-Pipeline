"""
Task 2 — Crawl bài viết/thông báo.

Chủ đề: Du lịch Việt Nam — lịch trình, địa điểm, ẩm thực, quy định địa phương.
7 URL (đủ dư so với mức tối thiểu 5) trải đều 4 nhóm nội dung trên, để RAG
sau này trả lời được nhiều loại câu hỏi khác nhau.

Cài browser trước khi chạy:
    python -m playwright install chromium
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from crawl4ai import AsyncWebCrawler

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    # Lịch trình / địa điểm
    "https://www.vietnamairlines.com/bh/en/plan-book/travel/travel-guide/places-to-visit-in-hoi-an",
    # Ẩm thực
    "https://www.authenticfoodquest.com/guide-best-food-in-hoi-an-restaurants/",
    "https://www.willflyforfood.net/hoi-an-food-guide/",
    # Lễ hội / văn hóa
    "https://hanoitimes.vn/google-celebrates-hoi-an-lantern-full-moon-festival-45382.html",
    # Quy định địa phương
    "https://hoianheritage.danang.gov.vn/en/news/news-events/announcement-of-the-visiting-in-hoi-an-ancient-town-125.html",
    "https://en.baobacninhtv.vn/hoi-an-launches-tour-group-entry-fees.bbg",
    "https://tuoitrenews.vn/news/ttnewsstyle/20250107/hoi-an-wants-to-offer-free-entry-into-ancient-town-to-more-visitor-groups/83776.html",
]


async def crawl_article(crawler: AsyncWebCrawler, url: str) -> dict:
    result = await crawler.arun(url=url)
    return {
        "url": url,
        "title": result.metadata.get("title", "Unknown"),
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": result.markdown,
    }


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Mở 1 trình duyệt dùng chung cho cả batch thay vì mở/đóng mỗi URL —
    # nhanh hơn nhiều lần và là cách dùng đúng của AsyncWebCrawler.
    async with AsyncWebCrawler() as crawler:
        for index, url in enumerate(ARTICLE_URLS, 1):
            try:
                article = await crawl_article(crawler, url)
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