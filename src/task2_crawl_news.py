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


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    "https://admissions.vinuni.edu.vn/vi/dai-hoc/gioi-thieu/",
    "https://admissions.vinuni.edu.vn/vi/dai-hoc/ung-tuyen-vao-vinuni/ung-vien-nam-nhat/",
    "https://admissions.vinuni.edu.vn/vi/dai-hoc/ung-tuyen-vao-vinuni/sinh-vien-chuyen-tiep/",
    "https://admissions.vinuni.edu.vn/vi/dai-hoc/ung-tuyen-vao-vinuni/sinh-vien-quoc-te/",
    "https://admissions.vinuni.edu.vn/vi/dai-hoc/cau-hoi-thuong-gap/tuyen-sinh/",
    "https://admissions.vinuni.edu.vn/vi/hoc-phi/cu-nhan/",
    "https://admissions.vinuni.edu.vn/vi/dai-hoc/ung-tuyen-vao-vinuni/ung-vien-nam-nhat/tieu-chi-tuyen-sinh/",
    "https://vinuni.edu.vn/vi/huong-dan-nop-ho-so-dai-hoc/",
]


async def crawl_article(url: str) -> dict:
    # Keep Crawl4AI's cache and logs in the repository workspace rather than
    # writing to the user's home directory (which may be restricted).
    os.environ.setdefault("CRAWL4_AI_BASE_DIRECTORY", str(DATA_DIR.parents[2]))
    from crawl4ai import AsyncWebCrawler

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
    if not result.success:
        raise RuntimeError(result.error_message or "Crawler failed")
    markdown = (result.markdown or "").strip()
    if len(markdown) < 100:
        raise ValueError("Page returned too little readable content")
    metadata = result.metadata or {}
    return {
        "url": url,
        "title": metadata.get("title") or url.rstrip("/").rsplit("/", 1)[-1],
        "date_crawled": datetime.now(timezone.utc).isoformat(),
        "content_markdown": markdown,
    }


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    successes = 0
    for index, url in enumerate(ARTICLE_URLS, 1):
        try:
            article = await crawl_article(url)
            slug = url.rstrip("/").rsplit("/", 1)[-1] or "article"
            output = DATA_DIR / f"article_{index:02d}_{slug}.json"
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"Saved: {output}")
            successes += 1
        except Exception as error:
            print(f"Failed: {url} — {error}")
    if successes < 5:
        raise RuntimeError(f"Only {successes} articles crawled successfully; at least 5 are required")


if __name__ == "__main__":
    asyncio.run(crawl_all())
