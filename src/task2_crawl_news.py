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
from datetime import datetime
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

# TODO: Thay bằng ít nhất 5 URL bài viết/thông báo công khai liên quan đến chủ đề nhóm.
ARTICLE_URLS = [
    # Ví dụ:
    # "https://example.edu/news/article-1",
    # "https://example.edu/news/article-2",
    # "https://example.edu/news/article-3",
    # "https://example.edu/news/article-4",
    # "https://example.edu/news/article-5",
]


async def crawl_article(url: str) -> dict:
    """Crawl một URL và trả về dict với url, title, date_crawled, content_markdown."""
    from crawl4ai import AsyncWebCrawler

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        return {
            "url": url,
            "title": result.metadata.get("title", "Unknown") if result.metadata else "Unknown",
            "date_crawled": datetime.now().isoformat(),
            "content_markdown": result.markdown or "",
        }


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    if not ARTICLE_URLS:
        raise ValueError(
            "ARTICLE_URLS trống. Hãy thêm ít nhất 5 URL bài viết vào ARTICLE_URLS."
        )

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for index, url in enumerate(ARTICLE_URLS, 1):
        output = DATA_DIR / f"article_{index:02d}.json"
        if output.exists():
            print(f"Already exists, skipping: {output.name}")
            continue
        try:
            article = await crawl_article(url)
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"Saved: {output}")
        except Exception as error:
            print(f"Failed: {url} — {error}")

    saved = list(DATA_DIR.glob("*.json"))
    print(f"\nTotal articles in {DATA_DIR}: {len(saved)}")


if __name__ == "__main__":
    asyncio.run(crawl_all())
