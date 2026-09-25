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
    "https://vi.wikipedia.org/wiki/Gi%C3%A1o_d%E1%BB%A5c_Vi%E1%BB%87t_Nam",
    "https://vi.wikipedia.org/wiki/B%E1%BB%99_Gi%C3%A1o_d%E1%BB%A5c_v%C3%A0_%C4%90%C3%A0o_t%E1%BA%A1o_(Vi%E1%BB%87t_Nam)",
    "https://vi.wikipedia.org/wiki/Gi%C3%A1o_d%E1%BB%A5c_%C4%91%E1%BA%A1i_h%E1%BB%8Dc_t%E1%BA%A1i_Vi%E1%BB%87t_Nam",
    "https://vi.wikipedia.org/wiki/Danh_s%C3%A1ch_tr%C6%B0%E1%BB%9Dng_%C4%91%E1%BA%A1i_h%E1%BB%8Dc,_h%E1%BB%8Dc_vi%E1%BB%87n_v%C3%A0_cao_%C4%91%E1%BA%B3ng_t%E1%BA%A1i_Vi%E1%BB%87t_Nam",
    "https://vi.wikipedia.org/wiki/K%E1%BB%B3_thi_tuy%E1%BB%83n_sinh_%C4%91%E1%BA%A1i_h%E1%BB%8Dc_v%C3%A0_cao_%C4%91%E1%BA%B3ng_(Vi%E1%BB%87t_Nam)"
]


async def crawl_article(url: str) -> dict:
    from datetime import datetime
    from crawl4ai import AsyncWebCrawler

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        return {
            "url": url,
            "title": result.metadata.get("title", "Unknown") if result.metadata else "Unknown",
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
