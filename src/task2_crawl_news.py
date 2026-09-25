"""Task 2 — Thu thập bài viết du lịch Ninh Bình."""

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    "https://dulichninhbinh.com.vn/item/3076",
    "https://dulichninhbinh.com.vn/item/2864",
    "https://dulichninhbinh.com.vn/item/3021",
    "https://dulichninhbinh.com.vn/item/2760",
    "https://dulichninhbinh.com.vn/item/1431",
]


async def crawl_article(url: str) -> dict:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
    from crawl4ai.content_filter_strategy import PruningContentFilter
    from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

    run_config = CrawlerRunConfig(
        excluded_tags=["nav", "header", "footer", "aside"],
        exclude_external_images=True,
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(
                threshold=0.45,
                threshold_type="dynamic",
                min_word_threshold=5,
            )
        ),
    )

    # Dùng Chromium đầy đủ đã tải trên máy, không cần headless shell.
    async with AsyncWebCrawler(config=BrowserConfig(headless=False)) as crawler:
        result = await crawler.arun(url=url, config=run_config)

        if not result.success:
            raise RuntimeError(f"Không crawl được: {url}")

        content = result.markdown.fit_markdown
        if not content or len(content.strip()) < 200:
            raise ValueError(f"Nội dung sau khi lọc quá ngắn: {url}")

        return {
            "url": url,
            "title": (result.metadata or {}).get("title") or url,
            "date_crawled": datetime.now(timezone.utc).isoformat(),
            "content_markdown": content.strip(),
        }


async def crawl_all() -> None:
    """Thu thập và lưu mỗi bài vào một file JSON."""
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