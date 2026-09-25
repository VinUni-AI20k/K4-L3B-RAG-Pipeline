"""Task 2 — Crawl bài viết và tài nguyên IELTS Writing công khai.

Chạy bằng ``python -m src.task2_crawl_news``. Mỗi URL được lưu thành một JSON
trong ``data/landing/news/`` với các trường mà Task 3 yêu cầu.
"""

from __future__ import annotations

import asyncio
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

import requests


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"
REQUEST_TIMEOUT_SECONDS = 30
MIN_CONTENT_LENGTH = 200

# Nguồn IELTS public, bổ trợ cho bộ tài liệu dự án. Hai trang British Council
# trong danh sách nguồn trả về 403 từ môi trường crawl này, nên dùng các trang
# IELTS.org công khai thay thế thay vì cố vượt cơ chế chặn truy cập.
ARTICLE_URLS = [
    "https://ielts.org/news-and-insights/ielts-writing-band-descriptors-and-key-assessment-criteria",
    "https://ielts.org/take-a-test/preparation-resources/writing-test-resources",
    "https://ielts.org/take-a-test/preparation-resources/sample-test-questions/academic-test",
    "https://ielts.org/take-a-test/test-types/ielts-academic-test/ielts-academic-format-writing",
    "https://ielts.org/news-and-insights/10-steps-to-writing-high-scoring-ielts-essays",
]


class _ArticleParser(HTMLParser):
    """Trích tiêu đề và các khối nội dung chính mà không lấy menu/footer."""

    _SKIP_TAGS = {"script", "style", "noscript", "svg", "nav", "footer", "header", "aside", "form"}
    _BLOCK_TAGS = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "blockquote"}
    _CONTENT_TAGS = {"main", "article"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.metadata: dict[str, str] = {}
        self.blocks: list[str] = []
        self._skip_depth = 0
        self._content_depth = 0
        self._title_depth = 0
        self._block_tag: str | None = None
        self._block_parts: list[str] = []
        self._has_main = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = {key.lower(): value or "" for key, value in attrs}
        if tag == "meta":
            key = (attrs_map.get("property") or attrs_map.get("name") or "").lower()
            value = attrs_map.get("content", "").strip()
            if key and value:
                self.metadata[key] = value
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return
        if tag == "title":
            self._title_depth += 1
        if tag in self._CONTENT_TAGS:
            self._has_main = True
            self._content_depth += 1
        if tag in self._BLOCK_TAGS and self._block_tag is None:
            self._block_tag = tag
            self._block_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP_TAGS and self._skip_depth:
            self._skip_depth -= 1
            return
        if self._skip_depth:
            return
        if tag == "title" and self._title_depth:
            self._title_depth -= 1
        if tag in self._CONTENT_TAGS and self._content_depth:
            self._content_depth -= 1
        if tag == self._block_tag:
            text = _clean_text("".join(self._block_parts))
            if text:
                self.blocks.append(_format_block(tag, text))
            self._block_tag = None
            self._block_parts = []

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if self._title_depth:
            self.title += data
        if self._block_tag and (not self._has_main or self._content_depth):
            self._block_parts.append(data)


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _format_block(tag: str, text: str) -> str:
    if tag.startswith("h") and len(tag) == 2 and tag[1].isdigit():
        return f"{'#' * int(tag[1])} {text}"
    if tag == "li":
        return f"- {text}"
    if tag == "blockquote":
        return f"> {text}"
    return text


def _content_markdown(html: str, page_url: str) -> tuple[str, str]:
    parser = _ArticleParser()
    parser.feed(html)
    heading_title = next(
        (block[2:].strip() for block in parser.blocks if block.startswith("# ")),
        "",
    )
    title = (
        heading_title
        or parser.metadata.get("og:title")
        or parser.metadata.get("twitter:title")
        or _clean_text(parser.title)
    )
    content = "\n\n".join(dict.fromkeys(parser.blocks)).strip()
    if not title:
        title = urlparse(page_url).path.rstrip("/").split("/")[-1].replace("-", " ").title()
    return title, content


def _filename_for_url(index: int, url: str) -> str:
    slug = urlparse(url).path.rstrip("/").split("/")[-1] or "article"
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", slug).strip("_-") or "article"
    return f"article_{index:02d}_{slug[:70]}.json"


async def crawl_article(url: str) -> dict[str, str]:
    """Tải và trích một trang HTML công khai thành bản ghi landing chuẩn."""
    response = await asyncio.to_thread(
        requests.get,
        url,
        timeout=REQUEST_TIMEOUT_SECONDS,
        headers={"User-Agent": "Mozilla/5.0 (compatible; IELTSWritingRAG/1.0)"},
    )
    response.raise_for_status()
    content_type = response.headers.get("Content-Type", "").lower()
    if "html" not in content_type and "text/" not in content_type:
        raise ValueError(f"Expected an HTML page, got Content-Type={content_type!r}")

    title, content = _content_markdown(response.text, response.url)
    if len(content) < MIN_CONTENT_LENGTH:
        raise ValueError(f"Extracted content is too short ({len(content)} characters)")

    return {
        "url": response.url,
        "title": title,
        "date_crawled": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "content_markdown": content,
    }


async def crawl_all() -> None:
    """Crawl danh sách URL, lưu file JSON và báo lỗi theo từng URL."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []

    for index, url in enumerate(ARTICLE_URLS, 1):
        try:
            article = await crawl_article(url)
            output = DATA_DIR / _filename_for_url(index, url)
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(f"Saved: {output} ({len(article['content_markdown'])} chars)")
        except Exception as error:
            failures.append(url)
            print(f"Failed: {url} — {error}")

    if failures:
        raise RuntimeError(f"Crawling failed for {len(failures)} of {len(ARTICLE_URLS)} URLs")


if __name__ == "__main__":
    asyncio.run(crawl_all())
