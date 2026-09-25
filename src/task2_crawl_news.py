"""
Task 2 — Crawl bài viết/thông báo.

Nguồn dữ liệu:
    Arena of Valor Fandom Wiki

Cách lấy dữ liệu:
    MediaWiki API

Output:
    data/landing/news/article_01.json
    data/landing/news/article_02.json
    ...

Mỗi JSON gồm:
    - url
    - title
    - date_crawled
    - content_markdown
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md


# ============================================================
# CONFIG
# ============================================================

DATA_DIR = (
    Path(__file__).parent.parent
    / "data"
    / "landing"
    / "news"
)

API_URL = (
    "https://arenaofvalor.fandom.com/vi/api.php"
)

USER_AGENT = (
    "K4-L3B-RAG-Pipeline/1.0 "
    "(Educational RAG Lab)"
)


# ============================================================
# ARTICLE SOURCES
# ============================================================

ARTICLE_URLS = [
    # --------------------------------------------------------
    # Hệ thống
    # --------------------------------------------------------

    "https://arenaofvalor.fandom.com/vi/wiki/Ngọc",
    "https://arenaofvalor.fandom.com/vi/wiki/Phù_hiệu",
    "https://arenaofvalor.fandom.com/vi/wiki/Trang_bị",

    # --------------------------------------------------------
    # 5 tướng
    # --------------------------------------------------------

    "https://arenaofvalor.fandom.com/vi/wiki/Moren",
    "https://arenaofvalor.fandom.com/vi/wiki/Violet",
    "https://arenaofvalor.fandom.com/vi/wiki/Errol",
    "https://arenaofvalor.fandom.com/vi/wiki/Aleister",
    "https://arenaofvalor.fandom.com/vi/wiki/Arum",
]


# ============================================================
# URL → PAGE NAME
# ============================================================

def get_page_name(url: str) -> str:
    """
    Chuyển URL wiki thành page name dùng cho MediaWiki API.

    Ví dụ:

        https://arenaofvalor.fandom.com/vi/wiki/Florentino

    → Florentino
    """

    parsed = urlparse(url)

    path = parsed.path.rstrip("/")

    if "/wiki/" not in path:
        raise ValueError(
            f"URL không đúng format Fandom wiki: {url}"
        )

    page_name = path.split(
        "/wiki/",
        1
    )[1]

    return unquote(page_name)


# ============================================================
# CALL MEDIAWIKI API
# ============================================================

def fetch_page_from_api(url: str) -> dict:
    """
    Lấy nội dung một trang bằng MediaWiki API.

    Không sử dụng Selenium/Crawl4AI.
    """

    page_name = get_page_name(url)

    params = {
        "action": "parse",
        "page": page_name,

        # text = HTML đã render từ wiki
        # wikitext = nội dung wiki gốc
        "prop": "text|wikitext",

        "format": "json",
        "formatversion": "2",
    }

    print(
        f"    API page: {page_name}"
    )

    response = requests.get(
        API_URL,
        params=params,
        headers={
            "User-Agent": USER_AGENT
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    if "error" in data:
        raise RuntimeError(
            "MediaWiki API error: "
            f"{data['error']}"
        )

    parse_data = data.get("parse")

    if not parse_data:
        raise RuntimeError(
            f"Không có dữ liệu parse cho: "
            f"{page_name}"
        )

    return parse_data


# ============================================================
# CLEAN HTML
# ============================================================

def clean_html(html: str) -> str:
    """
    Loại bỏ các thành phần không cần thiết
    trước khi chuyển HTML → Markdown.
    """

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    # --------------------------------------------------------
    # Script / style
    # --------------------------------------------------------

    for tag in soup.find_all(
        [
            "script",
            "style",
            "noscript",
        ]
    ):
        tag.decompose()

    # --------------------------------------------------------
    # Images
    # --------------------------------------------------------

    for tag in soup.find_all("img"):
        tag.decompose()

    # --------------------------------------------------------
    # Gallery
    # --------------------------------------------------------

    for selector in [
        ".gallery",
        ".gallerybox",
        ".wikia-gallery",
    ]:
        for tag in soup.select(selector):
            tag.decompose()

    # --------------------------------------------------------
    # TOC
    # --------------------------------------------------------

    for selector in [
        ".toc",
        "#toc",
        ".mw-editsection",
    ]:
        for tag in soup.select(selector):
            tag.decompose()

    # --------------------------------------------------------
    # Một số thành phần giao diện Fandom
    # --------------------------------------------------------

    for selector in [
        ".page-header__actions",
        ".page-header__contribution",
        ".WikiaArticleFooter",
        ".mw-jump",
    ]:
        for tag in soup.select(selector):
            tag.decompose()

    return str(soup)


# ============================================================
# HTML → MARKDOWN
# ============================================================

def html_to_markdown(html: str) -> str:
    """
    Chuyển HTML đã làm sạch thành Markdown.
    """

    clean_html_content = clean_html(
        html
    )

    markdown = md(
        clean_html_content,
        heading_style="ATX",
    )

    return clean_markdown(
        markdown
    )


# ============================================================
# CLEAN MARKDOWN
# ============================================================

def clean_markdown(markdown: str) -> str:
    """
    Chuẩn hóa Markdown cơ bản.
    """

    lines = []

    for line in markdown.splitlines():

        line = line.rstrip()

        # Bỏ các dòng chỉ chứa khoảng trắng
        if not line.strip():
            lines.append("")
        else:
            lines.append(line)

    markdown = "\n".join(lines)

    # Không để quá nhiều dòng trống
    markdown = re.sub(
        r"\n{3,}",
        "\n\n",
        markdown,
    )

    return markdown.strip()


# ============================================================
# CRAWL ONE ARTICLE
# ============================================================

def crawl_article(url: str) -> dict:
    """
    Crawl một article từ Fandom API.

    Return đúng schema của Task 2.
    """

    parse_data = fetch_page_from_api(
        url
    )

    title = parse_data.get(
        "title",
        get_page_name(url),
    )

    html = parse_data.get(
        "text",
        "",
    )

    if not html:
        raise RuntimeError(
            f"API không trả về nội dung: {url}"
        )

    content_markdown = html_to_markdown(
        html
    )

    if not content_markdown:
        raise RuntimeError(
            f"Markdown rỗng: {url}"
        )

    return {
        "url": url,
        "title": title,
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": content_markdown,
    }


# ============================================================
# CRAWL ALL ARTICLES
# ============================================================

async def crawl_all() -> None:
    """
    Crawl toàn bộ ARTICLE_URLS.

    Mỗi URL:
        → article_01.json
        → article_02.json
        → ...
    """

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 70)
    print("TASK 2 — ARENA OF VALOR FANDOM API CRAWLER")
    print("=" * 70)

    print(
        f"\nTotal articles: "
        f"{len(ARTICLE_URLS)}"
    )

    success_count = 0
    failed_count = 0

    for index, url in enumerate(
        ARTICLE_URLS,
        start=1,
    ):

        print("\n" + "-" * 70)

        print(
            f"[{index}/{len(ARTICLE_URLS)}]"
        )

        print(
            f"URL: {url}"
        )

        try:

            article = await asyncio.to_thread(
                crawl_article,
                url,
            )

            output_file = (
                DATA_DIR
                / f"article_{index:02d}.json"
            )

            output_file.write_text(
                json.dumps(
                    article,
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            content_length = len(
                article[
                    "content_markdown"
                ]
            )

            print(
                f"✓ Saved: {output_file}"
            )

            print(
                f"  Title: "
                f"{article['title']}"
            )

            print(
                f"  Characters: "
                f"{content_length:,}"
            )

            success_count += 1

        except Exception as error:

            failed_count += 1

            print(
                f"✗ Failed: {url}"
            )

            print(
                f"  Error: {error}"
            )

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n" + "=" * 70)
    print("TASK 2 SUMMARY")
    print("=" * 70)

    print(
        f"Total:   {len(ARTICLE_URLS)}"
    )

    print(
        f"Success: {success_count}"
    )

    print(
        f"Failed:  {failed_count}"
    )

    print(
        f"\nOutput directory:"
    )

    print(
        DATA_DIR
    )

    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    asyncio.run(crawl_all())