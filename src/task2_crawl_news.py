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
load_dotenv(Path(__file__).parent.parent / ".env")

ARTICLE_URLS = [
    "https://vnexpress.net/cam-nang-du-lich-tp-hcm-4608205.html"
]


async def crawl_article(url: str) -> dict:
    """Scrape one article with Firecrawl and return the landing-page schema."""
    try:
        from firecrawl import AsyncFirecrawl
    except ImportError:
        from firecrawl import AsyncFirecrawlApp as AsyncFirecrawl

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise RuntimeError(
            "FIRECRAWL_API_KEY is missing. Add it to the repository .env file."
        )

    firecrawl = AsyncFirecrawl(api_key=api_key)
    if hasattr(firecrawl, "scrape"):
        result = await firecrawl.scrape(url, formats=["markdown"])
    else:
        result = await firecrawl.scrape_url(url, formats=["markdown"])

    if isinstance(result, dict):
        markdown = result.get("markdown")
        metadata = result.get("metadata") or {}
        title = metadata.get("title") if isinstance(metadata, dict) else None
    else:
        markdown = getattr(result, "markdown", None)
        metadata = getattr(result, "metadata", None)
        title = getattr(metadata, "title", None) if metadata else None

    if not isinstance(markdown, str) or not markdown.strip():
        raise ValueError(f"Firecrawl returned no markdown content for {url}")

    return {
        "url": url,
        "title": title or "Unknown",
        "date_crawled": datetime.now(timezone.utc).isoformat(),
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
