"""Thu thập bài viết từ các cổng thông tin du lịch chính thức."""

from __future__ import annotations

import asyncio
import html
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_SOURCES = [
    {
        "slug": "hue-diem-den-noi-bat",
        "title": "Những điểm đến nổi bật tại Huế",
        "content_anchor": "Top 10 địa điểm “chụp ảnh đẹp không muốn về” ngay tại Huế",
        "url": "https://visithue.vn/Top-10-dia-diem-%E2%80%9Cchup-anh-dep-khong-muon-ve%E2%80%9D-ngay-tai-Hue.html/?pid=MTkyMTR8Y3NkbGRs0",
        "publisher": "Cổng thông tin du lịch thành phố Huế",
    },
    {
        "slug": "da-nang-ngu-hanh-son",
        "title": "Danh thắng Ngũ Hành Sơn",
        "content_anchor": "Danh thắng Ngũ Hành Sơn",
        "url": "https://danangfantasticity.com/cn/danh-thang-ngu-hanh-son",
        "publisher": "Cổng thông tin du lịch thành phố Đà Nẵng",
    },
    {
        "slug": "hoi-an-hoat-dong-van-hoa",
        "title": "Bảy trải nghiệm văn hóa tại Hội An",
        "content_anchor": "Top 7 things to do in Asia’s leading cultural destination of Hoi An",
        "url": "https://www.vietnam.travel/things-to-do/7-things-to-do-hoi-an",
        "publisher": "Cục Du lịch Quốc gia Việt Nam",
    },
    {
        "slug": "hue-am-thuc-dac-trung",
        "title": "Mười món ăn đặc trưng nên thử tại Huế",
        "content_anchor": "10 món ăn ngon phải thử ít nhất một lần khi đến Huế",
        "url": "https://visithue.vn/10-mon-an-ngon-phai-thu-it-nhat-mot-lan-khi-den-Hue.html/?pid=MTkzNjB8Y3NkbGRs0",
        "publisher": "Cổng thông tin du lịch thành phố Huế",
    },
    {
        "slug": "mien-trung-hanh-trinh-di-san",
        "title": "Trải nghiệm và di chuyển tại miền Trung Việt Nam",
        "content_anchor": "Top things to do in Central Vietnam",
        "url": "https://www.vietnam.travel/things-to-do/top-things-do-central-vietnam",
        "publisher": "Cục Du lịch Quốc gia Việt Nam",
    },
]

ARTICLE_URLS = [item["url"] for item in ARTICLE_SOURCES]


class _ReadableHTMLParser(HTMLParser):
    """Bộ chuyển HTML nhỏ, ưu tiên phần văn bản có ích cho retrieval."""

    ignored_tags = {
        "script", "style", "svg", "noscript", "form", "iframe",
        "nav", "header", "footer", "aside",
    }
    block_tags = {"p", "div", "article", "section", "br", "li", "tr", "h1", "h2", "h3", "h4"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ignored_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in self.ignored_tags:
            self.ignored_depth += 1
        elif not self.ignored_depth and tag in self.block_tags:
            self.parts.append("\n")
            if tag == "li":
                self.parts.append("- ")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.ignored_tags and self.ignored_depth:
            self.ignored_depth -= 1
        elif not self.ignored_depth and tag in self.block_tags:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.ignored_depth:
            self.parts.append(data)

    def markdown(self) -> str:
        text = html.unescape("".join(self.parts)).replace("\xa0", " ")
        lines = []
        for raw_line in text.splitlines():
            line = re.sub(r"\s+", " ", raw_line).strip()
            if line and (not lines or line != lines[-1]):
                lines.append(line)
        return "\n\n".join(lines)


def _fetch_article(source: dict) -> dict:
    request = Request(
        source["url"],
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; K4-RAG-Lab/1.0)",
            "Accept-Language": "vi-VN,vi;q=0.9",
        },
    )
    with urlopen(request, timeout=60) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        raw_html = response.read().decode(charset, errors="replace")

    parser = _ReadableHTMLParser()
    parser.feed(raw_html)
    content = parser.markdown()
    anchor = source.get("content_anchor", source["title"])
    anchor_position = content.find(anchor)
    if anchor_position >= 0:
        content = content[anchor_position:]
    for footer_marker in ("Bài viết khác", "TIN LIÊN QUAN", "RELATED POSTS", "Subscribe"):
        footer_position = content.find(footer_marker, 500)
        if footer_position >= 0:
            content = content[:footer_position].rstrip()
    if len(content) < 200:
        raise ValueError(f"Nội dung sau làm sạch quá ngắn: {source['url']}")
    return {
        "url": source["url"],
        "title": source["title"],
        "publisher": source["publisher"],
        "date_crawled": datetime.now(timezone.utc).isoformat(),
        "content_markdown": content,
    }


async def crawl_article(url: str) -> dict:
    source = next((item for item in ARTICLE_SOURCES if item["url"] == url), None)
    if source is None:
        source = {"url": url, "title": url, "publisher": "Chưa xác định"}
    return await asyncio.to_thread(_fetch_article, source)


async def crawl_all() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    failures = []
    for source in ARTICLE_SOURCES:
        try:
            article = await crawl_article(source["url"])
            output = DATA_DIR / f"{source['slug']}.json"
            output.write_text(json.dumps(article, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"Saved: {output}")
        except Exception as error:
            failures.append(f"{source['url']}: {error}")
            print(f"Failed {source['slug']}: {type(error).__name__}")
    if failures:
        raise RuntimeError("Không crawl đủ nguồn:\n" + "\n".join(failures))


if __name__ == "__main__":
    asyncio.run(crawl_all())
