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
    "https://uet.vnu.edu.vn/ke-hoach-ket-thuc-khoa-hoc-cua-cac-lop-qh-2021-k66-chuong-trinh-ky-su-cac-khoa-cu-va-tn-truoc-han-dot-xet-thang-01-2026/",
    "https://uet.vnu.edu.vn/thong-bao-so-5-ve-trien-khai-cho-sinh-vien-tham-gia-bhyt-nam-2026/",
    "https://uet.vnu.edu.vn/tham-gia-cuoc-thi-hoc-sinh-sinh-vien-voi-y-tuong-khoi-nghiep/",
    "https://uet.vnu.edu.vn/thong-tin-ve-chuong-trinh-hoc-bong-khoa-hoc-cong-nghe-dao-tao-thac-si-tien-si-du-hoc-nuoc-ngoai-cua-tap-doan-vingroup/",
    "https://uet.vnu.edu.vn/tong-hop-ve-hoc-bong-bac-sau-dai-hoc-tai-uet-nam-2021/",
    "https://uet.vnu.edu.vn/thong-tin-hoc-bong-vingroup/",
]


async def crawl_article(url: str) -> dict:
    """Crawl một bài viết qua Crawl4AI và trả về metadata cùng nội dung markdown."""
    from datetime import datetime
    from crawl4ai import AsyncWebCrawler

    async with AsyncWebCrawler(verbose=False) as crawler:
        result = await crawler.arun(url=url)
        title = "Thông báo UET"
        if result.metadata and result.metadata.get("title"):
            title = result.metadata["title"].strip()
        markdown_content = result.markdown or ""
        
        return {
            "url": url,
            "title": title,
            "date_crawled": datetime.now().isoformat(),
            "content_markdown": markdown_content,
        }


async def crawl_all(force: bool = False) -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for index, url in enumerate(ARTICLE_URLS, 1):
        output = DATA_DIR / f"article_{index:02d}.json"
        if not force and output.exists() and output.stat().st_size > 100:
            print(f"Skipping existing: {output.name} (use force=True to re-crawl)")
            continue
        try:
            print(f"Crawling ({index}/{len(ARTICLE_URLS)}): {url}")
            article = await crawl_article(url)
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"Saved: {output}")
        except Exception as error:
            print(f"Failed: {url} — {error}")


if __name__ == "__main__":
    asyncio.run(crawl_all())
