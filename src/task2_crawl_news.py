"""Task 2 - crawl five public Vietnamese tourism articles with Crawl4AI."""

from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "landing" / "news"

# Keep Crawl4AI's cache inside the project instead of the user's home folder.
os.environ.setdefault("CRAWL4_AI_BASE_DIRECTORY", str(ROOT))

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator


ARTICLES = [
    {
        "id": "cam-nang-du-lich-ha-noi",
        "url": "https://vnexpress.net/cam-nang-du-lich-ha-noi-4459188.html",
    },
    {
        "id": "cam-nang-du-lich-ninh-binh",
        "url": "https://vnexpress.net/cam-nang-du-lich-ninh-binh-4127327.html",
    },
    {
        "id": "cam-nang-du-lich-hue",
        "url": "https://vnexpress.net/cam-nang-du-lich-hue-4126937.html",
    },
    {
        "id": "am-thuc-ba-mien",
        "url": "https://mytour.vn/vi/blog/bai-viet/kham-pha-am-thuc-va-trai-nghiem-huong-vi-ba-mien.html",
    },
    {
        "id": "mon-an-ngon-viet-nam",
        "url": "https://mytour.vn/vi/blog/bai-viet/top-15-mon-an-ngon-nhat-viet-nam-theo-danh-gia-cua-du-khach.html",
    },
]

# Backwards-compatible list for notebooks or teammates importing the old name.
ARTICLE_URLS = [article["url"] for article in ARTICLES]


def markdown_text(result: object) -> str:
    """Return Crawl4AI's filtered Markdown, falling back to raw Markdown."""
    markdown = getattr(result, "markdown", "")
    if isinstance(markdown, str):
        return markdown.strip()
    return (
        getattr(markdown, "fit_markdown", "")
        or getattr(markdown, "raw_markdown", "")
        or ""
    ).strip()


async def crawl_article(
    crawler: AsyncWebCrawler,
    article: dict[str, str],
    run_config: CrawlerRunConfig,
) -> dict[str, str]:
    """Crawl and validate one article."""
    result = await crawler.arun(url=article["url"], config=run_config)
    if not result.success:
        raise RuntimeError(result.error_message or f"HTTP {result.status_code}")

    metadata = result.metadata or {}
    title = str(metadata.get("title") or "").strip()
    content = markdown_text(result)
    if not title:
        raise ValueError("page has no title")
    if len(content) < 200:
        raise ValueError(f"article content is too short ({len(content)} characters)")

    return {
        "url": article["url"],
        "title": title,
        "date_crawled": datetime.now(timezone.utc).isoformat(),
        "content_markdown": content,
    }


async def crawl_all() -> None:
    """Crawl all configured articles and save one validated JSON per article."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    browser_config = BrowserConfig(
        browser_type="chromium",
        chrome_channel=os.getenv("CRAWL4AI_CHROME_CHANNEL", "chrome"),
        headless=True,
        verbose=False,
    )
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(threshold=0.4),
        ),
        remove_overlay_elements=True,
        exclude_all_images=True,
        page_timeout=60_000,
    )

    failures: list[str] = []
    async with AsyncWebCrawler(config=browser_config) as crawler:
        for article_config in ARTICLES:
            try:
                article = await crawl_article(crawler, article_config, run_config)
                output = DATA_DIR / f"{article_config['id']}.json"
                output.write_text(
                    json.dumps(article, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                print(f"Saved: {output} ({len(article['content_markdown'])} chars)")
            except Exception as error:  # Keep crawling the remaining independent URLs.
                error_text = str(error).encode("ascii", "backslashreplace").decode()
                failures.append(f"{article_config['url']}: {error_text}")
                print(f"Failed: {article_config['url']} - {error_text}")

    if failures:
        raise RuntimeError("Some articles could not be crawled:\n- " + "\n- ".join(failures))


if __name__ == "__main__":
    asyncio.run(crawl_all())
