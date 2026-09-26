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
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from http.client import HTTPException
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    "https://vietnam.travel/vi/place-to-go",
    "https://vietnam.travel/vi/plan-your-trip/vietnam-itineraries",
    "https://vietnam.travel/vi/things-to-do/",
    "https://www.vietnam.travel/things-to-do/vietnam-foodie-guide-region",
    "https://www.vietnam.travel/things-to-do/explore-food-hoi-an",
]


class ContentParser(HTMLParser):
    """Extract the site's Drupal content block, excluding shared page chrome."""

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
    SKIP = {"script", "style", "noscript", "iframe", "form", "button", "svg", "nav", "footer"}
    BLOCK = {"p", "div", "section", "article", "ul", "ol", "blockquote", "table", "tr"}

    def __init__(self, url: str):
        super().__init__(convert_charrefs=True)
        self.url = url
        self.stack = []
        self.parts = []
        self.title_parts = []
        self.found_content = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        parent = self.stack[-1] if self.stack else None
        active = bool(parent and parent[1]) or attrs.get("id") == "block-vietnamtourism-content"
        skip = bool(parent and parent[2]) or tag in self.SKIP
        skip |= "breadcrumb-container" in attrs.get("class", "").split()
        skip |= attrs.get("id") == "also-like" and "/things-to-do/" in urlsplit(self.url).path and not urlsplit(self.url).path.startswith("/vi/")
        self.found_content |= active
        href = urljoin(self.url, attrs.get("href", "")) if tag == "a" else ""
        if urlsplit(href).scheme not in {"http", "https"} or attrs.get("href", "").startswith("#"):
            href = ""
        if active and not skip:
            if re.fullmatch(r"h[1-6]", tag):
                self.parts.append("\n\n" + "#" * int(tag[1]) + " ")
            elif tag in self.BLOCK:
                self.parts.append("\n\n")
            elif tag == "li":
                self.parts.append("\n- ")
            elif tag == "br":
                self.parts.append("\n")
            elif tag == "a" and href:
                self.parts.append("[")
        if tag not in self.VOID:
            self.stack.append((tag, active, skip, href))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        index = next((i for i in range(len(self.stack) - 1, -1, -1) if self.stack[i][0] == tag), None)
        if index is None:
            return
        _, active, skip, href = self.stack[index]
        del self.stack[index:]
        if active and not skip:
            if tag == "a" and href:
                self.parts.append(f"]({href})")
            elif tag in self.BLOCK or re.fullmatch(r"h[1-6]", tag):
                self.parts.append("\n\n")

    def handle_data(self, data):
        if any(item[0] == "title" for item in self.stack):
            self.title_parts.append(data)
        if self.stack and self.stack[-1][1] and not self.stack[-1][2]:
            self.parts.append(re.sub(r"\s+", " ", data))

    def markdown(self):
        text = "".join(self.parts)
        text = re.sub(r"\[([^\[\]]*)\]\(([^\n]*?)\)",
                      lambda m: "[" + re.sub(r"\s+", " ", m[1]).strip().lstrip("# ") + "](" + m[2] + ")", text)
        text = re.sub(r"\[\s*\]\([^\n]*?\)", "", text)
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
        text = "\n".join(line for line in lines if not re.fullmatch(r"[-#]+", line)
                         and "Sign up for our newsletter" not in line)
        return re.sub(r"\n{3,}", "\n\n", text).strip()


def fetch_article(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "RAGCourseCollector/1.0", "Accept": "text/html"})
    with urlopen(request, timeout=120) as response:
        if response.headers.get_content_type() != "text/html":
            raise ValueError(f"Expected HTML: {url}")
        resolved_url = response.geturl()
        html = response.read().decode(response.headers.get_content_charset() or "utf-8")
    parser = ContentParser(resolved_url)
    parser.feed(html)
    content = parser.markdown()
    title = "".join(parser.title_parts).strip()
    if not parser.found_content or len(content) < 200 or not title:
        raise ValueError(f"Missing/empty main content; inspect page layout or access error: {url}")
    return {
        "url": url,
        "title": title,
        "date_crawled": datetime.now(timezone.utc).isoformat(),
        "content_markdown": content,
        "resolved_url": resolved_url,
        "language": "vi" if urlsplit(resolved_url).path.startswith("/vi/") else "en",
    }


async def crawl_article(url: str) -> dict:
    """Use standard-library HTTP for server-rendered pages; no browser needed."""
    for attempt in range(3):
        try:
            return await asyncio.to_thread(fetch_article, url)
        except HTTPError:
            # Do not retry access restrictions or try to bypass a WAF.
            raise
        except (URLError, HTTPException, TimeoutError, ConnectionError):
            if attempt == 2:
                raise
            await asyncio.sleep(2 ** attempt)


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    failures = []
    for index, url in enumerate(ARTICLE_URLS, 1):
        try:
            article = await crawl_article(url)
            output = DATA_DIR / f"article_{index:02d}.json"
            temporary = output.with_suffix(".json.part")
            temporary.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            temporary.replace(output)
            print(f"Saved: {output}")
        except Exception as error:
            failures.append(url)
            print(f"Failed: {url} — {error}")
    if failures:
        raise RuntimeError(f"Failed to crawl {len(failures)}/{len(ARTICLE_URLS)} URLs; existing files preserved.")


if __name__ == "__main__":
    asyncio.run(crawl_all())
