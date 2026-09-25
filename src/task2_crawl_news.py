"""Crawl public news/articles into data/landing/news as JSON."""
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"
ARTICLE_URLS = [
    "https://xaydungchinhsach.chinhphu.vn/phuong-thuc-nganh-chuong-trinh-tuyen-sinh-dai-hoc-nam-2025-cua-dai-hoc-kinh-te-quoc-dan-1192501040836584.htm",
    "https://daotao.neu.edu.vn/vi/dang-ky-ho-so-xet-tuyen-dai-hoc-chinh-quy/giai-dap-ho-tro-ve-dang-ky-ho-so-xet-tuyen-dai-hoc-chinh-quy-dhktq",
    "https://trangedu.com/truong/dai-hoc-kinh-te-quoc-dan/#cac-nganh-tuyen-sinh",
    "https://daibieunhandan.vn/nam-2025-dai-hoc-kinh-te-quoc-dan-tuyen-sinh-theo-3-phuong-thuc-10356249.html",
    "https://daotao.neu.edu.vn/vi/tin-tuc-1689/tuyen-sinh-dai-hoc-2026-nhung-luu-y-dac-biet-4050",
]

async def crawl_article(url: str) -> dict:
    from crawl4ai import AsyncWebCrawler
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        metadata = result.metadata or {}
        content = result.markdown or result.cleaned_html or ""
        if not content.strip():
            raise RuntimeError("Trang không trả về nội dung văn bản")
        return {"url": url, "title": metadata.get("title", "Unknown"), "date_crawled": datetime.now(timezone.utc).isoformat(), "content_markdown": content.strip()}

async def crawl_all() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for index, url in enumerate(ARTICLE_URLS, 1):
        try:
            article = await crawl_article(url)
            output = DATA_DIR / f"article_{index:02d}.json"
            output.write_text(json.dumps(article, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"Saved: {output}")
        except Exception as error:
            print(f"Failed: {url} — {error}")

if __name__ == "__main__":
    asyncio.run(crawl_all())
