"""Collect real NEU article bodies; keep raw HTML and archive previous JSON."""
import argparse
import asyncio
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data/landing/news"
MANIFEST = ROOT / "data/sources.json"


def extract_article(html: str) -> tuple[str, str, str | None]:
    soup = BeautifulSoup(html, "html.parser")
    heading = soup.select_one(".title-news h1")
    body = soup.select_one("#post-content > div")
    if heading is None or body is None:
        raise ValueError("NEU article selector missing; refusing navigation/error pages")
    for tag in body.select("script, style, nav, form, button, .tags, .share-widget"):
        tag.decompose()
    content = markdownify(str(body), heading_style="ATX", strip=["img"]).strip()
    content = re.sub(r"\n{3,}", "\n\n", content)
    if len(content) < 300:
        raise ValueError("Article body too short; manual review required")
    date = re.search(r"(\d{2}) tháng (\d{2}) (2026)", soup.get_text(" ", strip=True))
    published = f"{date[3]}-{date[2]}-{date[1]}" if date else None
    return heading.get_text(" ", strip=True), content, published


def fetch_article(item: dict) -> dict:
    response = requests.get(item["url"], timeout=(15, 45))
    response.raise_for_status()
    response.encoding = "utf-8"
    title, content, published = extract_article(response.text)
    raw = ROOT / "data/landing/raw_html" / f"{item['id']}.html"
    raw.parent.mkdir(parents=True, exist_ok=True)
    raw.write_bytes(response.content)
    return {**item, "title": title, "date_crawled": datetime.now(timezone.utc).isoformat(),
            "date_published": published, "content_markdown": content,
            "raw_html_path": raw.relative_to(ROOT).as_posix(),
            "raw_sha256": hashlib.sha256(response.content).hexdigest(),
            "collection_method": "requests+beautifulsoup+markdownify", "content_status": "collected"}


async def crawl_article(url: str) -> dict:
    items = json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    return await asyncio.to_thread(fetch_article, next(x for x in items if x["url"] == url))


def validate_article(item: dict) -> None:
    for key in ("url", "title", "date_crawled", "content_markdown"):
        if not isinstance(item.get(key), str) or not item[key].strip():
            raise ValueError(f"Missing article field: {key}")
    if item.get("content_status") != "collected":
        raise ValueError("Unverified/placeholder article must not enter the corpus")


async def crawl_all(refresh: bool = False) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    items = [x for x in json.loads(MANIFEST.read_text(encoding="utf-8-sig")) if x["doc_type"] == "news"]
    failures = []
    for item in items:
        path = ROOT / item["local_path"]
        if path.exists() and not refresh:
            old = json.loads(path.read_text(encoding="utf-8-sig"))
            if old.get("url") == item["url"] and old.get("content_status") == "collected":
                validate_article(old)
                print(f"Cached: {path.name}")
                continue
        try:
            article = await asyncio.to_thread(fetch_article, item)
            validate_article(article)
            if path.exists():
                old_bytes = path.read_bytes()
                archive = ROOT / "data/archive/news" / f"{path.stem}_{hashlib.sha256(old_bytes).hexdigest()[:12]}.json"
                archive.parent.mkdir(parents=True, exist_ok=True)
                archive.write_bytes(old_bytes)
            temporary = path.with_suffix(".tmp")
            temporary.write_text(json.dumps(article, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            temporary.replace(path)
            print(f"Collected: {path.name} ({len(article['content_markdown'])} characters)")
        except Exception as error:
            failures.append(f"{item['url']}: {error}")
    if failures:
        raise RuntimeError("Crawl incomplete; previous files preserved:\n" + "\n".join(failures))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    asyncio.run(crawl_all(parser.parse_args().refresh))
