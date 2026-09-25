"""
Task 2 — Crawl bài viết/thông báo.

Hướng dẫn:
    1. Điền tối thiểu 5 URL công khai vào ARTICLE_URLS.
    2. Crawl từng URL bằng Crawl4AI.
    3. Lưu mỗi bài thành một JSON trong data/landing/news/.
    4. Giữ đủ url, title, date_crawled và content_markdown.

Cài browser trước khi chạy:
    python -m playwright install chromium

Có thể dùng Firecrawl hoặc công cụ tương đương.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from crawl4ai import AsyncWebCrawler


# Thư mục lưu dữ liệu crawl được
DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"


# Danh sách các bài viết công khai cần crawl
ARTICLE_URLS = [
    "https://bocongan.gov.vn/chinh-sach-phap-luat/bai-viet/chinh-phu-ban-hanh-nghi-dinh-bao-ve-du-lieu-ca-nhan-d3-t982",
    "https://baochinhphu.vn/bien-phap-dieu-kien-bao-dam-bao-ve-du-lieu-ca-nhan-102230417185238022.htm",
    "https://baochinhphu.vn/luat-bao-ve-du-lieu-ca-nhan-chinh-thuc-co-hieu-luc-tu-ngay-mai-1-1-2026-102251231155609721.htm",
    "https://xaydungchinhsach.chinhphu.vn/quy-dinh-bao-ve-du-lieu-ca-nhan-doi-voi-thong-tin-suc-khoe-va-trong-hoat-dong-kinh-doanh-bao-hiem-119250725170233556.htm",
    "https://dichvucong.bocongan.gov.vn/public/link-to/chi-tiet-thu-tuc?ma-thu-tuc=54853",
]


async def crawl_article(url: str, crawler: AsyncWebCrawler | None = None) -> dict:
    """
    Crawl một URL và trả về dữ liệu bài viết.
    """

    if crawler is None:
        async with AsyncWebCrawler() as owned_crawler:
            return await crawl_article(url, owned_crawler)

    result = await crawler.arun(url=url)

    # Kiểm tra crawl có thành công không
    if not result.success:
        raise RuntimeError(
            f"Không thể crawl URL: {url}. "
            f"Error: {result.error_message}"
        )

    # Lấy metadata
    metadata = result.metadata or {}

    # Lấy title
    title = metadata.get("title", "Unknown")

    # Lấy nội dung markdown
    content_markdown = result.markdown

    # Một số phiên bản Crawl4AI có thể trả về object Markdown
    if not isinstance(content_markdown, str):
        if hasattr(content_markdown, "raw_markdown"):
            content_markdown = content_markdown.raw_markdown
        else:
            content_markdown = str(content_markdown)

    # Kiểm tra nội dung
    if not content_markdown.strip():
        raise RuntimeError(
            f"Crawl thành công nhưng không lấy được nội dung: {url}"
        )

    return {
        "url": url,
        "title": title,
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": content_markdown,
    }


async def crawl_all() -> None:
    """
    Crawl tất cả URL trong ARTICLE_URLS
    và lưu mỗi bài thành một file JSON.
    """

    # Tạo thư mục nếu chưa tồn tại
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    async with AsyncWebCrawler() as crawler:
        for index, url in enumerate(ARTICLE_URLS, 1):
            try:
                print(f"\nCrawling [{index}/{len(ARTICLE_URLS)}]: {url}")

                article = await crawl_article(url, crawler)

                # article_01.json, article_02.json,...
                output = DATA_DIR / f"article_{index:02d}.json"

                output.write_text(
                    json.dumps(
                        article,
                        ensure_ascii=False,
                        indent=2,
                    ),
                    encoding="utf-8",
                )

                print(f"Saved: {output}")

            except Exception as error:
                print(f"Failed: {url}")
                print(f"Error: {error}")


if __name__ == "__main__":
    asyncio.run(crawl_all())