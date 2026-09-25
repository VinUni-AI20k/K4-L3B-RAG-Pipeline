"""
Task 2 — Crawl bài viết/thông báo.

Chủ đề nhóm: Tuyển sinh Đại học Quốc gia Hà Nội (ĐHQGHN) 2026 — phương thức
xét tuyển, chỉ tiêu, học phí, điểm chuẩn.

Crawl bằng Playwright (render JS) rồi chuyển phần nội dung chính sang Markdown
bằng markdownify. Mỗi bài lưu thành một JSON trong data/landing/news/ với
url, title, date_crawled, content_markdown (+ date_published nếu trang có).

Trình duyệt:
    Mặc định dùng Microsoft Edge có sẵn trên máy (BROWSER_CHANNEL=msedge).
    Đặt BROWSER_CHANNEL=chrome, hoặc BROWSER_CHANNEL= (rỗng) để dùng Chromium
    của Playwright sau khi chạy `python -m playwright install chromium`.
"""

import asyncio
import json
import os
import re
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup
from markdownify import markdownify
from playwright.async_api import async_playwright


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

BROWSER_CHANNEL = os.getenv("BROWSER_CHANNEL", "msedge") or None

ARTICLE_URLS = [
    # Quy chế tuyển sinh chung của Bộ GD&ĐT 2026 (áp dụng cho ĐHQGHN)
    "https://moet.gov.vn/tin-tuc/tin-tong-hop2/ban-hanh-quy-che-tuyen-sinh-dai-hoc-nam-2026.html",
    "https://xaydungchinhsach.chinhphu.vn/nhung-diem-moi-trong-quy-che-tuyen-sinh-dai-hoc-2026-119260215183555963.htm",
    # Phương thức xét tuyển — quy chế tuyển sinh ĐHQGHN
    "https://baochinhphu.vn/dai-hoc-quoc-gia-ha-noi-ban-hanh-quy-che-tuyen-sinh-moi-tu-2026-102260320180414717.htm",
    # Chỉ tiêu
    "https://education.vnu.edu.vn/tin-tuc/hoat-dong-truong-dai-hoc-giao-duc/tin-tuc-tuyen-sinh/nam-2026-truong-dai-hoc-giao-duc-dhqghn-du-kien-tuyen-2000-chi-tieu-cho-16-nganh-dao-tao/",
    "https://tienphong.vn/dh-quoc-gia-ha-noi-tuyen-bo-sung-680-chi-tieu-dai-hoc-chinh-quy-nam-2026-post1873523.tpo",
    # Học phí
    "https://vnexpress.net/hoc-phi-12-truong-thuoc-dai-hoc-quoc-gia-ha-noi-nam-2026-chi-tiet-nhat-5079708.html",
    # Điểm chuẩn
    "https://xaydungchinhsach.chinhphu.vn/diem-chuan-dai-hoc-quoc-gia-ha-noi-2026-119260809163517452.htm",
]

# Vùng nội dung chính của các báo/cổng thông tin; fallback về <article>/<main>.
CONTENT_SELECTORS = [
    "div.detail-content",      # baochinhphu, xaydungchinhsach
    "article.fck_detail",      # vnexpress
    "div.article__body",       # tienphong
    "div.entry-content",       # website WordPress của các trường
    "article",
    "main",
]

NOISE_SELECTORS = [
    "script", "style", "noscript", "iframe", "form", "nav", "header", "footer",
    "aside", "figure.video", ".box-relate", ".relate-container", ".social",
    ".detail-tab", ".banner", "[class*='ads']",
    "[type=RelatedNewsBox]",   # khối "Tham khảo thêm" của baochinhphu/xaydungchinhsach
    ".button-dowload-img",     # nút "Tải xuống" ảnh
    ".detail-comment", ".comment-wrapper", ".box-comment",
    ".box-zone-thread", ".detail-author-bot", ".audio-player",
    "video", "[class*='player' i]", "[id*='player' i]", "[class*='vidcrunch' i]",
]

MIN_CONTENT_CHARS = 300


def meta_content(soup: BeautifulSoup, **attrs) -> str | None:
    meta = soup.find("meta", attrs=attrs)
    if meta and meta.get("content", "").strip():
        return meta["content"].strip()
    return None


def extract_title(soup: BeautifulSoup) -> str:
    # og:title đôi khi bị cắt ngắn -> chọn bản đầy đủ hơn giữa og:title và <h1>.
    h1 = soup.find("h1")
    candidates = [
        meta_content(soup, property="og:title"),
        h1.get_text(" ", strip=True) if h1 else None,
    ]
    candidates = [c for c in candidates if c]
    if candidates:
        return max(candidates, key=len)
    return soup.title.get_text(strip=True) if soup.title else "Unknown"


def extract_lead(soup: BeautifulSoup) -> str | None:
    """Sapo/mô tả bài viết — một số báo đặt ngoài vùng nội dung chính."""
    return meta_content(soup, property="og:description") or meta_content(soup, name="description")


def extract_published(soup: BeautifulSoup) -> str | None:
    return (
        meta_content(soup, property="article:published_time")
        or meta_content(soup, name="pubdate")
        or meta_content(soup, itemprop="datePublished")
    )


def extract_content_markdown(soup: BeautifulSoup) -> str:
    for selector in NOISE_SELECTORS:
        for node in soup.select(selector):
            node.decompose()

    # Chọn vùng nội dung dài nhất trong các selector khớp.
    candidates = [node for selector in CONTENT_SELECTORS for node in soup.select(selector)]
    best = max(candidates, key=lambda n: len(n.get_text(strip=True)), default=None)
    if best is None or len(best.get_text(strip=True)) < MIN_CONTENT_CHARS:
        best = soup.body or soup

    markdown = markdownify(str(best), heading_style="ATX", strip=["img", "a"])
    markdown = re.sub(r"[ \t]+\n", "\n", markdown)
    markdown = re.sub(r"\n{3,}", "\n\n", markdown)
    return markdown.strip()


async def crawl_article(url: str, browser) -> dict:
    page = await browser.new_page(locale="vi-VN")
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=90_000)
        try:
            await page.wait_for_load_state("networkidle", timeout=15_000)
        except Exception:
            pass  # trang có quảng cáo tải liên tục -> dùng DOM hiện tại
        html = await page.content()
    finally:
        await page.close()

    soup = BeautifulSoup(html, "html.parser")
    title = extract_title(soup)
    published = extract_published(soup)
    lead = extract_lead(soup)
    content = extract_content_markdown(soup)
    if lead and lead[:60] not in content:
        content = f"**{lead}**\n\n{content}"
    if len(content) < MIN_CONTENT_CHARS:
        raise ValueError(f"content too short ({len(content)} chars) — có thể bị chặn")

    return {
        "url": url,
        "title": title,
        "date_crawled": datetime.now().isoformat(timespec="seconds"),
        "date_published": published,
        "content_markdown": content,
    }


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(channel=BROWSER_CHANNEL, headless=True)
        try:
            for index, url in enumerate(ARTICLE_URLS, 1):
                try:
                    article = await crawl_article(url, browser)
                    output = DATA_DIR / f"article_{index:02d}.json"
                    output.write_text(
                        json.dumps(article, ensure_ascii=False, indent=2),
                        encoding="utf-8",
                    )
                    print(f"Saved: {output.name} ({len(article['content_markdown'])} chars) — {article['title']}")
                except Exception as error:
                    print(f"Failed: {url} — {error}")
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(crawl_all())
