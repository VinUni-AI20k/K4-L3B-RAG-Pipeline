"""
Task 2 — Crawl bài viết/thông báo.

Chủ đề nhóm: hỗ trợ tra cứu kiến thức migration lên AWS.

Năm trang AWS Prescriptive Guidance bao phủ các câu hỏi vận hành hay gặp:
migrate VM lên EC2, migrate PostgreSQL lên Aurora, migrate shared file system,
communication gate trong governance, và checklist giai đoạn cutover.

Cài browser trước khi chạy:
    python -m playwright install chromium

Chạy:
    python -m src.task2_crawl_news
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

# URL công khai, đã bỏ tham số tracking để citation trỏ đúng trang gốc.
ARTICLE_URLS = [
    "https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/migrate-an-on-premises-vm-to-amazon-ec2-by-using-aws-application-migration-service.html",
    "https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/migrate-an-on-premises-postgresql-database-to-aurora-postgresql.html",
    "https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/migrate-shared-file-systems-in-an-aws-large-migration.html",
    "https://docs.aws.amazon.com/prescriptive-guidance/latest/large-migration-governance-playbook/task-create-communication-gates.html",
    "https://docs.aws.amazon.com/prescriptive-guidance/latest/best-practices-migration-cutover/cutover-stage.html",
]

# Nội dung thật của trang docs.aws.amazon.com nằm trong #main-col-body.
# Dùng target_elements (không phải css_selector) để markdown chỉ lấy phần này
# mà vẫn giữ HTML đầy đủ cho metadata — <title> nằm ngoài selector.
CONTENT_SELECTOR = "#main-col-body"

MIN_CONTENT_CHARS = 500


def _clean_title(raw_title: str, url: str) -> str:
    """Bỏ hậu tố site name trong <title>; rỗng thì fallback theo slug URL."""
    title = re.sub(r"\s*-\s*AWS Prescriptive Guidance\s*$", "", raw_title or "").strip()
    if title:
        return title
    slug = url.rstrip("/").rsplit("/", 1)[-1].removesuffix(".html")
    return slug.replace("-", " ").strip().capitalize() or "Unknown"


def _slug(url: str) -> str:
    return url.rstrip("/").rsplit("/", 1)[-1].removesuffix(".html")


def _extract_markdown(result: object) -> str:
    """Crawl4AI trả về MarkdownGenerationResult hoặc str tuỳ cấu hình."""
    markdown = getattr(result, "markdown", "") or ""
    raw = getattr(markdown, "raw_markdown", None)
    return (raw if raw is not None else str(markdown)).strip()


async def crawl_article(crawler: AsyncWebCrawler, url: str) -> dict:
    """Crawl một URL và trả về record theo schema của landing/news."""
    config = CrawlerRunConfig(
        target_elements=[CONTENT_SELECTOR],
        cache_mode=CacheMode.BYPASS,
        wait_until="domcontentloaded",
        page_timeout=90_000,
    )
    result = await crawler.arun(url=url, config=config)

    if not getattr(result, "success", False):
        raise RuntimeError(getattr(result, "error_message", "crawl failed"))

    content_markdown = _extract_markdown(result)
    if len(content_markdown) < MIN_CONTENT_CHARS:
        raise RuntimeError(
            f"nội dung quá ngắn ({len(content_markdown)} ký tự), có thể sai selector"
        )

    metadata = getattr(result, "metadata", None) or {}
    return {
        "url": url,
        "title": _clean_title(metadata.get("title", ""), url),
        "date_crawled": datetime.now().isoformat(timespec="seconds"),
        "content_markdown": content_markdown,
    }


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    browser_config = BrowserConfig(headless=True, verbose=False)
    failures: list[str] = []

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for index, url in enumerate(ARTICLE_URLS, 1):
            try:
                article = await crawl_article(crawler, url)
            except Exception as error:
                failures.append(url)
                print(f"Failed: {url} — {error}")
                continue

            output = DATA_DIR / f"article_{index:02d}_{_slug(url)}.json"
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(
                f"Saved: {output.name} — {len(article['content_markdown']):,} chars "
                f"— {article['title']}"
            )

    ok = len(ARTICLE_URLS) - len(failures)
    print(f"\nCrawled {ok}/{len(ARTICLE_URLS)} articles into {DATA_DIR}")
    if failures:
        print("Cần crawl lại:\n  " + "\n  ".join(failures))


if __name__ == "__main__":
    asyncio.run(crawl_all())
