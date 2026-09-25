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

Đặc biệt:
    - HTML rendered dùng để lấy nội dung bài viết.
    - Wikitext dùng để khôi phục các template có cấu trúc:
        {{Ngọc|...}}
        {{Phù hiệu|...}}
        {{pbt|...}}

Rate limit:
    - Nghỉ 2 giây giữa các request.
    - Nếu API trả 403:
        retry 3 lần
        backoff: 3s / 6s / 9s
    - Nếu vẫn 403 sau retry:
        fallback sang HTML public.
"""

import asyncio
import json
import re
import time
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
# RATE LIMIT / RETRY CONFIG
# ============================================================

# Nghỉ giữa các article
REQUEST_DELAY = 2

# Số lần retry khi API bị rate-limit
MAX_RETRIES = 3

# Thời gian backoff cho từng lần retry
RETRY_BACKOFF = [
    3,
    6,
    9,
]


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
    # Tướng
    # --------------------------------------------------------

    "https://arenaofvalor.fandom.com/vi/wiki/Valhein",
    "https://arenaofvalor.fandom.com/vi/wiki/Violet",
    "https://arenaofvalor.fandom.com/vi/wiki/Florentino",
    "https://arenaofvalor.fandom.com/vi/wiki/Aleister",
    "https://arenaofvalor.fandom.com/vi/wiki/Alice",
]


# ============================================================
# GEM MAPPING
# ============================================================

RED_GEMS = {
    "cp": "CP",
    "cvl": "CVL",
    "cvlxg": "CVL-XG",
    "cvlhm": "CVL-HM",
    "tlstcm": "TLCM-STCM",
    "tdmg": "TĐ-M-G",
    "cpxgp": "CP-XGP",
    "cptd": "CP-TĐ",
    "tlcm": "TLCM",
    "tdtlcm": "TĐ-TLCM",
}


PURPLE_GEMS = {
    "m": "MTĐ",
    "hmp": "HMP",
    "hm": "HM",
    "tlcmm": "TLCM-MTĐ",
    "mhm": "MTĐ-Hồi",
    "hmgp": "HM-GP",
    "cphmp": "CP-HMP",
    "mhmtc": "M-HM-TC",
    "cvltc": "CVL-TC",
    "tdtc": "TĐ-TC",
}


GREEN_GEMS = {
    "g": "G",
    "ggp": "G-GP",
    "mhc": "MTĐ-GHC",
    "gp": "GP",
    "cphc": "CP-GHC",
    "cvlxg": "CVL-XG",
    "tdxgp": "TĐ-XGP",
    "hc": "GHC",
    "hmpg": "HMP-G",
    "ggphc": "G-GP-HC",
}


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

    API trả về:
        - title
        - text
        - wikitext

    text:
        HTML đã render.

    wikitext:
        Nội dung wiki gốc, dùng để parse:
        - {{Ngọc}}
        - {{Phù hiệu}}
        - {{pbt}}
    """

    page_name = get_page_name(url)

    params = {
        "action": "parse",
        "page": page_name,
        "prop": "text|wikitext",
        "format": "json",
        "formatversion": "2",
    }

    print(
        f"    API page: {page_name}"
    )

    for attempt in range(MAX_RETRIES + 1):

        try:

            response = requests.get(
                API_URL,
                params=params,
                headers={
                    "User-Agent": USER_AGENT,
                },
                timeout=30,
            )

            # =================================================
            # SUCCESS
            # =================================================

            if response.status_code == 200:

                data = response.json()

                if "error" in data:
                    raise RuntimeError(
                        "MediaWiki API error: "
                        f"{data['error']}"
                    )

                parse_data = data.get(
                    "parse"
                )

                if not parse_data:
                    raise RuntimeError(
                        f"Không có dữ liệu parse "
                        f"cho: {page_name}"
                    )

                return parse_data

            # =================================================
            # 403 RATE LIMIT
            # =================================================

            if response.status_code == 403:

                if attempt < MAX_RETRIES:

                    delay = RETRY_BACKOFF[
                        attempt
                    ]

                    print(
                        "    403 rate-limit — "
                        "Fandom chặn khi gọi API "
                        "liên tiếp."
                    )

                    print(
                        f"    Retry "
                        f"{attempt + 1}/{MAX_RETRIES} "
                        f"sau {delay}s..."
                    )

                    time.sleep(delay)

                    continue

                # ------------------------------------------------
                # Đã retry đủ 3 lần
                # ------------------------------------------------

                print(
                    "    403 rate-limit — "
                    "đã retry 3 lần."
                )

                response.raise_for_status()

            # =================================================
            # HTTP ERROR KHÁC
            # =================================================

            response.raise_for_status()

        except requests.RequestException as error:

            if attempt >= MAX_RETRIES:
                raise

            delay = RETRY_BACKOFF[
                attempt
            ]

            print(
                f"    Request lỗi: {error}"
            )

            print(
                f"    Retry "
                f"{attempt + 1}/{MAX_RETRIES} "
                f"sau {delay}s..."
            )

            time.sleep(delay)

    raise RuntimeError(
        f"Không thể lấy API: {page_name}"
    )


# ============================================================
# FALLBACK HTML
# ============================================================

def fetch_page_from_html(
    url: str,
) -> dict:
    """
    Fallback khi MediaWiki API vẫn bị chặn.

    Lưu ý:
        HTML không có Wikitext nên các template:
            {{Ngọc}}
            {{Phù hiệu}}
            {{pbt}}

        sẽ không thể parse từ Wikitext.
    """

    print(
        "    API không truy cập được."
    )

    print(
        "    → Fallback sang HTML public."
    )

    response = requests.get(
        url,
        headers={
            "User-Agent": USER_AGENT,
        },
        timeout=30,
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    # ========================================================
    # TITLE
    # ========================================================

    title = get_page_name(url)

    h1 = soup.find("h1")

    if h1:

        title = h1.get_text(
            " ",
            strip=True,
        )

    elif soup.title:

        title = soup.title.get_text(
            " ",
            strip=True,
        )

    # ========================================================
    # MAIN CONTENT
    # ========================================================

    content = (
        soup.select_one(".mw-parser-output")
        or soup.select_one(".WikiaArticle")
        or soup.select_one("#mw-content-text")
        or soup.body
    )

    if content is None:

        raise RuntimeError(
            f"Không tìm thấy nội dung HTML: {url}"
        )

    return {
        "title": title,
        "text": str(content),
        "wikitext": "",
    }


# ============================================================
# FETCH PAGE
# ============================================================

def fetch_page(
    url: str,
) -> dict:
    """
    Ưu tiên MediaWiki API.

    Nếu API bị 403 sau toàn bộ retry,
    fallback sang HTML public.
    """

    try:

        return fetch_page_from_api(
            url
        )

    except requests.HTTPError as error:

        status_code = (
            error.response.status_code
            if error.response is not None
            else None
        )

        if status_code == 403:

            print(
                "    HTTP 403 từ MediaWiki API."
            )

            return fetch_page_from_html(
                url
            )

        raise

    except requests.RequestException as error:

        print(
            "    API request lỗi:"
            f" {error}"
        )

        print(
            "    → Fallback sang HTML public."
        )

        return fetch_page_from_html(
            url
        )


# ============================================================
# PARSE {{Ngọc}}
# ============================================================

def parse_gem_template(
    template: str,
) -> dict:
    """
    Parse template:

        {{Ngọc|red1=cp|purple1=m|green1=g|...}}

    thành dictionary.
    """

    content = template[
        len("{{Ngọc|"):-2
    ]

    values = {}

    for part in content.split("|"):

        if "=" not in part:
            continue

        key, value = part.split(
            "=",
            1,
        )

        values[
            key.strip()
        ] = value.strip()

    return values


def parse_gems(
    wikitext: str,
) -> str:
    """
    Lấy các template {{Ngọc|...}} từ Wikitext
    và chuyển thành Markdown.
    """

    if not wikitext:
        return ""

    pattern = r"\{\{Ngọc\|.*?\}\}"

    templates = re.findall(
        pattern,
        wikitext,
        flags=re.DOTALL,
    )

    if not templates:
        return ""

    result = []

    result.append(
        "## Bảng ngọc"
    )

    result.append("")

    for index, template in enumerate(
        templates,
        start=1,
    ):

        data = parse_gem_template(
            template
        )

        result.append(
            f"### Bộ ngọc {index}"
        )

        result.append("")

        # ====================================================
        # NGỌC ĐỎ
        # ====================================================

        for i in [1, 2]:

            gem_id = data.get(
                f"red{i}"
            )

            desc = data.get(
                f"desc{i if i == 1 else 4}"
            )

            if gem_id:

                name = RED_GEMS.get(
                    gem_id,
                    gem_id,
                )

                result.append(
                    f"- **Ngọc đỏ:** Đỏ III {name}"
                )

                if desc:

                    result.append(
                        f"  - Số lượng: {desc}"
                    )

        # ====================================================
        # NGỌC TÍM
        # ====================================================

        for i in [1, 2]:

            gem_id = data.get(
                f"purple{i}"
            )

            desc = data.get(
                f"desc{2 if i == 1 else 5}"
            )

            if gem_id:

                name = PURPLE_GEMS.get(
                    gem_id,
                    gem_id,
                )

                result.append(
                    f"- **Ngọc tím:** Tím III {name}"
                )

                if desc:

                    result.append(
                        f"  - Số lượng: {desc}"
                    )

        # ====================================================
        # NGỌC LỤC
        # ====================================================

        for i in [1, 2]:

            gem_id = data.get(
                f"green{i}"
            )

            desc = data.get(
                f"desc{3 if i == 1 else 6}"
            )

            if gem_id:

                name = GREEN_GEMS.get(
                    gem_id,
                    gem_id,
                )

                result.append(
                    f"- **Ngọc lục:** Lục III {name}"
                )

                if desc:

                    result.append(
                        f"  - Số lượng: {desc}"
                    )

        result.append("")

    return "\n".join(
        result
    ).strip()


# ============================================================
# PARSE {{Phù hiệu}}
# ============================================================

def parse_enchantment(
    wikitext: str,
) -> str:
    """
    Parse:

        {{Phù hiệu|...}}

    thành Markdown.

    Ví dụ:

        {{Phù hiệu|canh gác|bơm máu|mộc giáp|...}}

    →
        ## Phù hiệu

        - **Nhánh 1:** canh gác
        - **Nhánh 2:** bơm máu
        - **Nhánh 3:** mộc giáp
    """

    if not wikitext:
        return ""

    pattern = (
        r"\{\{Phù hiệu\|([^}]*)\}\}"
    )

    match = re.search(
        pattern,
        wikitext,
        flags=re.DOTALL,
    )

    if not match:
        return ""

    values = [
        value.strip()
        for value in match.group(1).split("|")
        if value.strip()
    ]

    if not values:
        return ""

    result = []

    result.append(
        "## Phù hiệu"
    )

    result.append("")

    for index, value in enumerate(
        values,
        start=1,
    ):

        result.append(
            f"- **Nhánh {index}:** {value}"
        )

    return "\n".join(
        result
    )


# ============================================================
# PARSE {{pbt}}
# ============================================================

def parse_summoner_spell(
    wikitext: str,
) -> str:
    """
    Parse:

        {{pbt|...}}

    thành Markdown.

    Ví dụ:

        {{pbt|Tốc biến}}

    →
        ## Phép bổ trợ

        - **Tốc biến**
    """

    if not wikitext:
        return ""

    pattern = (
        r"\{\{pbt\|([^}]*)\}\}"
    )

    match = re.search(
        pattern,
        wikitext,
        flags=re.DOTALL,
    )

    if not match:
        return ""

    spell = match.group(1).strip()

    if not spell:
        return ""

    return (
        "## Phép bổ trợ\n\n"
        f"- **{spell}**"
    )


# ============================================================
# CLEAN HTML
# ============================================================

def clean_html(
    html: str,
) -> str:
    """
    Loại bỏ các thành phần không cần thiết
    trước khi chuyển HTML → Markdown.
    """

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    # ========================================================
    # SCRIPT / STYLE
    # ========================================================

    for tag in soup.find_all(
        [
            "script",
            "style",
            "noscript",
        ]
    ):
        tag.decompose()

    # ========================================================
    # IMAGES
    # ========================================================

    for tag in soup.find_all("img"):
        tag.decompose()

    # ========================================================
    # GALLERY
    # ========================================================

    for selector in [
        ".gallery",
        ".gallerybox",
        ".wikia-gallery",
    ]:

        for tag in soup.select(
            selector
        ):
            tag.decompose()

    # ========================================================
    # TOC
    # ========================================================

    for selector in [
        ".toc",
        "#toc",
        ".mw-editsection",
    ]:

        for tag in soup.select(
            selector
        ):
            tag.decompose()

    # ========================================================
    # FANDOM UI
    # ========================================================

    for selector in [
        ".page-header__actions",
        ".page-header__contribution",
        ".WikiaArticleFooter",
        ".mw-jump",
    ]:

        for tag in soup.select(
            selector
        ):
            tag.decompose()

    return str(soup)


# ============================================================
# HTML → MARKDOWN
# ============================================================

def html_to_markdown(
    html: str,
) -> str:
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
# REMOVE OLD EMPTY SECTIONS
# ============================================================

def remove_empty_sections(
    markdown: str,
) -> str:
    """
    Xóa các heading đặc biệt do HTML render ra.

    Các section này sẽ được thêm lại bằng dữ liệu
    lấy từ Wikitext nếu template tương ứng tồn tại.
    """

    sections = [
        "Bảng ngọc",
        "Phù hiệu",
        "Phép bổ trợ",
    ]

    for section in sections:

        # Match các dạng:
        #
        # ## Bảng ngọc
        #
        # ### Bảng ngọc
        #
        # ### [Bảng ngọc](...)
        #

        pattern = (
            rf"(?im)^#{2,6}\s*"
            rf"(?:\[)?"
            rf"{re.escape(section)}"
            rf".*"
            rf"\n?"
        )

        markdown = re.sub(
            pattern,
            "",
            markdown,
            count=1,
        )

    return markdown.strip()


# ============================================================
# CLEAN MARKDOWN
# ============================================================

def clean_markdown(
    markdown: str,
) -> str:
    """
    Chuẩn hóa Markdown cơ bản.
    """

    lines = []

    for line in markdown.splitlines():

        line = line.rstrip()

        if not line.strip():

            lines.append("")

        else:

            lines.append(line)

    markdown = "\n".join(
        lines
    )

    # Không để quá nhiều dòng trống.
    markdown = re.sub(
        r"\n{3,}",
        "\n\n",
        markdown,
    )

    return markdown.strip()


# ============================================================
# CRAWL ONE ARTICLE
# ============================================================

def crawl_article(
    url: str,
) -> dict:
    """
    Crawl một article từ Fandom.

    Quy trình:

        URL
         ↓
        MediaWiki API
         ↓
        HTML + Wikitext
         ↓
        HTML → Markdown
         ↓
        Parse {{Ngọc}}
         ↓
        Parse {{Phù hiệu}}
         ↓
        Parse {{pbt}}
         ↓
        Ghép dữ liệu
         ↓
        JSON
    """

    # ========================================================
    # 1. FETCH
    # ========================================================

    parse_data = fetch_page(
        url
    )

    # ========================================================
    # 2. TITLE
    # ========================================================

    title = parse_data.get(
        "title",
        get_page_name(url),
    )

    # ========================================================
    # 3. HTML
    # ========================================================

    html = parse_data.get(
        "text",
        "",
    )

    if not html:

        raise RuntimeError(
            f"API không trả về HTML: {url}"
        )

    # ========================================================
    # 4. HTML → MARKDOWN
    # ========================================================

    content_markdown = html_to_markdown(
        html
    )

    # ========================================================
    # 5. WIKITEXT
    # ========================================================

    wikitext = parse_data.get(
        "wikitext",
        "",
    )

    # Một số format API có thể trả:
    #
    # {
    #     "*": "..."
    # }
    #
    # nên xử lý cả hai trường hợp.

    if isinstance(
        wikitext,
        dict,
    ):

        wikitext = wikitext.get(
            "*",
            "",
        )

    # ========================================================
    # 6. PARSE DỮ LIỆU ĐẶC BIỆT
    # ========================================================

    gem_markdown = parse_gems(
        wikitext
    )

    enchantment_markdown = (
        parse_enchantment(
            wikitext
        )
    )

    spell_markdown = (
        parse_summoner_spell(
            wikitext
        )
    )

    # ========================================================
    # 7. XÓA SECTION RỖNG
    # ========================================================

    content_markdown = (
        remove_empty_sections(
            content_markdown
        )
    )

    # ========================================================
    # 8. GHÉP CÁC SECTION ĐẶC BIỆT
    # ========================================================

    extra_sections = []

    if enchantment_markdown:

        extra_sections.append(
            enchantment_markdown
        )

    if gem_markdown:

        extra_sections.append(
            gem_markdown
        )

    if spell_markdown:

        extra_sections.append(
            spell_markdown
        )

    if extra_sections:

        content_markdown += (
            "\n\n"
            + "\n\n".join(
                extra_sections
            )
        )

    # ========================================================
    # 9. CLEAN FINAL MARKDOWN
    # ========================================================

    content_markdown = clean_markdown(
        content_markdown
    )

    # ========================================================
    # 10. VALIDATE
    # ========================================================

    if not content_markdown:

        raise RuntimeError(
            f"Markdown rỗng: {url}"
        )

    # ========================================================
    # 11. RETURN TASK 2 SCHEMA
    # ========================================================

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

    print(
        "TASK 2 — ARENA OF VALOR FANDOM API CRAWLER"
    )

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

            # =================================================
            # KIỂM TRA DỮ LIỆU ĐẶC BIỆT
            # =================================================

            if "## Bảng ngọc" in article[
                "content_markdown"
            ]:

                print(
                    "  ✓ Đã lấy Bảng ngọc"
                )

            if "## Phù hiệu" in article[
                "content_markdown"
            ]:

                print(
                    "  ✓ Đã lấy Phù hiệu"
                )

            if "## Phép bổ trợ" in article[
                "content_markdown"
            ]:

                print(
                    "  ✓ Đã lấy Phép bổ trợ"
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

        # ====================================================
        # DELAY GIỮA CÁC ARTICLE
        # ====================================================

        if index < len(ARTICLE_URLS):

            print(
                f"\n  Nghỉ {REQUEST_DELAY}s "
                "trước request tiếp theo..."
            )

            time.sleep(
                REQUEST_DELAY
            )

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n" + "=" * 70)

    print(
        "TASK 2 SUMMARY"
    )

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
        "\nOutput directory:"
    )

    print(
        DATA_DIR
    )

    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    asyncio.run(
        crawl_all()
    )