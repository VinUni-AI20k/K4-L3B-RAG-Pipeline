"""
Task 2 — Crawl bài viết/thông báo.

Hướng dẫn:
    1. Điền tối thiểu 5 URL công khai vào ARTICLE_URLS.
    2. Crawl từng URL bằng Crawl4AI.
    3. Lưu mỗi bài thành một JSON trong data/landing/news/.
    4. Giữ đủ url, title, date_crawled và content_markdown.

Cài browser trước khi chạy:
    python -m playwright install chromium
    
-> Dùng Firecrawl or bất cứ công cụ nào bạn quen    
"""

import asyncio
import json
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    "https://vinuni.edu.vn/aithucchien/",
    "https://vinuni.edu.vn/vi/thong-tin-tuyen-sinh-chuong-trinh-dao-tao-nhan-tai-ai-thuc-chien-khoa-co-ban/",
    "https://vinuni.edu.vn/vi/vingroup-khai-giang-khoa-dau-tien-chuong-trinh-dao-tao-20-000-nhan-tai-ai-thuc-chien/",
    "https://vinuni.edu.vn/vi/3-ngay-thi-ai-thuc-chien-hanh-trinh-cua-nhung-nguoi-dam-thu-thach/",
    "https://vinuni.edu.vn/vi/chinh-thuc-mo-cong-nhan-ho-so-tuyen-sinh-khoa-2-3-chuong-trinh-dao-tao-20-000-nhan-tai-ai-thu-chien/",
    "https://phoenix.note.transformerlabs.ai/technical-book/chapter-02",
]


async def crawl_article(url: str) -> dict:
    # TODO: Implement crawling logic.
    #
    from datetime import datetime
    from crawl4ai import AsyncWebCrawler
    
    async with AsyncWebCrawler() as crawler:
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
