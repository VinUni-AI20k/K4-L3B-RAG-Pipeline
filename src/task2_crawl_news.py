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
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"
load_dotenv()

ARTICLE_URLS = [
    url.strip() for url in os.getenv("ARTICLE_URLS", "").split(",") if url.strip()
]


async def crawl_article(url: str) -> dict:
    if not url.startswith(("http://", "https://")):
        raise ValueError(f"Invalid public URL: {url!r}")
    from crawl4ai import AsyncWebCrawler

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
    if getattr(result, "success", True) is False:
        raise RuntimeError(getattr(result, "error_message", "crawl failed"))
    metadata = getattr(result, "metadata", None) or {}
    markdown = getattr(result, "markdown", "")
    if not isinstance(markdown, str):
        markdown = getattr(markdown, "raw_markdown", str(markdown))
    if not markdown.strip():
        raise ValueError(f"Crawler returned empty content for {url}")
    return {
        "url": url,
        "title": str(metadata.get("title") or url),
        "date_crawled": datetime.now(timezone.utc).isoformat(),
        "content_markdown": markdown.strip(),
    }


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if len(ARTICLE_URLS) < 5:
        raise ValueError("ARTICLE_URLS must contain at least 5 public URLs")

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
