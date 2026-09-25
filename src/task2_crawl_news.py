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
    # TODO: Thêm ít nhất 5 public URL.
    "https://nplaw.vn/quy-dinh-phap-luat-ve-ho-kinh-doanh.html",
    "https://pbgdpl.hanoi.gov.vn/chi-tiet-tim-kiem/-/asset_publisher/kyB8zPQFRdzV/content/phan-tich-cac-quy-inh-cua-phap-luat-ve-ho-kinh-doanh",
    "https://luattinminh.vn/ho-kinh-doanh-la-gi",
    "https://tapchitoaan.vn/dia-vi-phap-ly-cua-ho-kinh-doanh-theo-phap-luat-viet-nam15367.html",
    "https://einvoice.vn/tin-tuc/cac-van-ban-phap-luat-cho-ho-kinh-doanh"
]


def _markdown_to_text(markdown) -> str:
    """crawl4ai có thể trả result.markdown là str hoặc MarkdownGenerationResult
    (tuỳ version), nên phải chuẩn hoá về str trước khi lưu JSON."""
    if isinstance(markdown, str):
        return markdown
    for attr in ("fit_markdown", "raw_markdown"):
        value = getattr(markdown, attr, None)
        if isinstance(value, str) and value.strip():
            return value
    return str(markdown) if markdown is not None else ""


async def crawl_article(url: str) -> dict:
    from datetime import datetime
    from crawl4ai import AsyncWebCrawler

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        if not getattr(result, "success", True):
            raise RuntimeError(
                f"Crawl failed for {url}: {getattr(result, 'error_message', 'unknown error')}"
            )

        content_markdown = _markdown_to_text(result.markdown).strip()
        if not content_markdown:
            raise RuntimeError(f"Crawl returned empty content for {url}")

        metadata = result.metadata or {}
        return {
            "url": url,
            "title": metadata.get("title") or "Unknown",
            "date_crawled": datetime.now().isoformat(),
            "content_markdown": content_markdown,
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
