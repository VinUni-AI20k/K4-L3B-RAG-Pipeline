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


import asyncio
import json
import re
import sys
import urllib.request
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    "https://www.hutech.edu.vn/tuyensinh/tin-tuyen-sinh/14630721-hutech-cong-bo-phuong-an-tuyen-sinh-dai-hoc-chinh-quy-du-kien-nam-2026",
    "https://www.hutech.edu.vn/tuyensinh/tin-tuyen-sinh/14630823-hutech-cong-bo-chinh-sach-hoc-bong-tuyen-sinh-khoa-2026",
    "https://www.hutech.edu.vn/tuyensinh/tin-tuc/tin-tuyen-sinh/14610630-quy-che-tuyen-sinh-trinh-do-dai-hoc-chinh-quy",
    "https://www.hutech.edu.vn/tuyensinh/tin-tuc/tin-tuyen-sinh/14610627-quy-che-to-chuc-thi-cac-mon-nang-khieu-tai-truong-dai-hoc-cong-nghe-tp-ho-chi-minh",
    "https://www.hutech.edu.vn/e-hutech/thong-bao-tuyen-sinh/14578229-mau-ho-so-du-tuyen-va-nhap-hoc",
    "https://www.hutech.edu.vn/tuyensinh/dai-hoc-nganh-dao-tao",
]


class HTMLToMarkdownParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self.in_title = False
        self.page_title = ""
        self.in_script = False
        self.in_style = False
        self.in_link = False
        self.link_href = ""
        self.link_text = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag in ("script", "style", "noscript"):
            self.in_script = True
        elif tag == "title":
            self.in_title = True
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(tag[1])
            self.result.append(f"\n\n{'#' * level} ")
        elif tag == "p":
            self.result.append("\n\n")
        elif tag == "br":
            self.result.append("\n")
        elif tag == "li":
            self.result.append("\n- ")
        elif tag == "tr":
            self.result.append("\n")
        elif tag in ("td", "th"):
            self.result.append(" | ")
        elif tag == "a":
            self.in_link = True
            self.link_href = attrs_dict.get("href", "")
            self.link_text = []

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self.in_script = False
        elif tag == "title":
            self.in_title = False
        elif tag in ("p", "h1", "h2", "h3", "h4", "h5", "h6"):
            self.result.append("\n")
        elif tag == "a":
            self.in_link = False
            text = "".join(self.link_text).strip()
            if text and self.link_href and not self.link_href.startswith(("#", "javascript:")):
                self.result.append(f" [{text}]({self.link_href}) ")
            elif text:
                self.result.append(f" {text} ")

    def handle_data(self, data):
        if self.in_script or self.in_style:
            return
        if self.in_title:
            self.page_title += data
            return
        if self.in_link:
            self.link_text.append(data)
        else:
            self.result.append(data)

    def get_markdown(self) -> str:
        raw = "".join(self.result)
        # Normalize multiple empty lines and excessive spaces
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in raw.split("\n")]
        text = "\n".join(lines)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        return text


async def crawl_article(url: str) -> dict:
    """Crawl bài viết từ URL và trích xuất title + content markdown."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)

    loop = asyncio.get_event_loop()
    html_content = await loop.run_in_executor(
        None, lambda: urllib.request.urlopen(req, timeout=30).read().decode("utf-8", errors="ignore")
    )

    # Trích xuất title từ OpenGraph hoặc title tag
    title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html_content)
    if not title_match:
        title_match = re.search(r"<title>(.*?)</title>", html_content, re.DOTALL)
    title = title_match.group(1).strip() if title_match else "HUTECH Thông tin Tuyển sinh"
    title = re.sub(r"\s+", " ", title)

    # Ưu tiên lấy phần thân bài viết từ panel#contentnews hoặc khối nội dung
    panel_match = re.search(r'<panel id="contentnews">(.*?)</panel>', html_content, re.DOTALL)
    if not panel_match:
        panel_match = re.search(r'<div class="content noidung[^"]*">(.*?)<div class="footer', html_content, re.DOTALL)
    content_to_parse = panel_match.group(1) if panel_match else html_content

    parser = HTMLToMarkdownParser()
    parser.feed(content_to_parse)
    markdown_content = parser.get_markdown()

    # Thêm tiêu đề nếu chưa có ở đầu
    if not markdown_content.startswith("#"):
        markdown_content = f"# {title}\n\n{markdown_content}"

    return {
        "url": url,
        "title": title,
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": markdown_content,
    }


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for index, url in enumerate(ARTICLE_URLS, 1):
        try:
            print(f"Crawling ({index}/{len(ARTICLE_URLS)}): {url}...")
            article = await crawl_article(url)
            output = DATA_DIR / f"article_{index:02d}.json"
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"Saved: {output} - '{article['title']}' ({len(article['content_markdown'])} chars)")
        except Exception as error:
            print(f"Failed: {url} — {error}")


if __name__ == "__main__":
    asyncio.run(crawl_all())

