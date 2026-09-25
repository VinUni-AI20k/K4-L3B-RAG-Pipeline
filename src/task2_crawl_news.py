"""Collect Shopee help articles into one JSON file per article.

The supplied Markdown files are previously collected page snapshots. The
default run packages those snapshots with their original retrieval dates.
Pass ``--refresh`` to fetch the public URLs again with Crawl4AI.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "landing" / "news"
REQUIRED_FIELDS = ("doc_id", "title", "source_url", "retrieved_at")


def _read_snapshot(path: Path) -> tuple[dict[str, str], str]:
    """Read metadata and article body from a supplied UTF-8 Markdown file."""
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"Missing front matter: {path.name}")

    try:
        closing = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration as error:
        raise ValueError(f"Unclosed front matter: {path.name}") from error

    metadata: dict[str, str] = {}
    for line in lines[1:closing]:
        if not line.strip():
            continue
        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"Invalid metadata line in {path.name}: {line}")
        metadata[key.strip()] = value.strip().strip('"')

    for field in REQUIRED_FIELDS:
        if not metadata.get(field):
            raise ValueError(f"Missing {field} in {path.name}")
    if metadata["doc_id"] != path.stem:
        raise ValueError(f"doc_id does not match filename: {path.name}")
    parsed = urlparse(metadata["source_url"])
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"Invalid source_url in {path.name}")
    try:
        date.fromisoformat(metadata["retrieved_at"])
    except ValueError as error:
        raise ValueError(f"Invalid retrieved_at in {path.name}") from error

    body = "\n".join(lines[closing + 1 :]).strip()
    if len(body) < 200:
        raise ValueError(f"Article content is too short: {path.name}")
    return metadata, body


def _source_files() -> list[Path]:
    files = sorted(DATA_DIR.glob("*.md"))
    if len(files) < 5:
        raise ValueError(f"At least five Markdown article snapshots are required; found {len(files)}")
    return files


def _article_from_snapshot(metadata: dict[str, str], body: str) -> dict[str, str]:
    """Keep the original crawl date rather than inventing a new one."""
    return {
        "url": metadata["source_url"],
        "title": metadata["title"],
        "date_crawled": metadata["retrieved_at"],
        "content_markdown": body,
        "doc_id": metadata["doc_id"],
        "category": metadata.get("category", ""),
        "language": metadata.get("language", "vi"),
    }


async def crawl_article(url: str) -> dict[str, str]:
    """Fetch a public article with Crawl4AI when a live refresh is requested."""
    if urlparse(url).scheme != "https":
        raise ValueError("Article URL must use HTTPS")
    try:
        from crawl4ai import AsyncWebCrawler
    except ImportError as error:
        raise RuntimeError("Install the project's Crawl4AI dependency to use --refresh") from error

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
    if not result.success:
        raise RuntimeError(f"Crawl failed: {result.error_message}")
    markdown = result.markdown
    if not isinstance(markdown, str):
        markdown = getattr(markdown, "fit_markdown", None) or getattr(markdown, "raw_markdown", "")
    if not markdown or len(markdown.strip()) < 200:
        raise ValueError(f"Crawl returned too little content: {url}")
    title = (result.metadata or {}).get("title")
    if not title:
        raise ValueError(f"Crawl returned no title: {url}")
    return {
        "url": url,
        "title": title.strip(),
        "date_crawled": datetime.now(timezone.utc).date().isoformat(),
        "content_markdown": markdown.strip(),
    }


async def crawl_all(refresh: bool = False) -> list[Path]:
    """Write one stable, UTF-8 JSON file for each supplied article."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    files = _source_files()
    output_files: list[Path] = []
    failures: list[str] = []
    for path in files:
        try:
            metadata, body = _read_snapshot(path)
            article = await crawl_article(metadata["source_url"]) if refresh else _article_from_snapshot(metadata, body)
            article["doc_id"] = metadata["doc_id"]
            article["category"] = metadata.get("category", "")
            article["language"] = metadata.get("language", "vi")
            output = DATA_DIR / f"{path.stem}.json"
            serialized = json.dumps(article, ensure_ascii=False, indent=2) + "\n"
            if not output.exists() or output.read_text(encoding="utf-8") != serialized:
                output.write_text(serialized, encoding="utf-8")
                print(f"Saved: {output.name}")
            else:
                print(f"Current: {output.name}")
            output_files.append(output)
        except (OSError, ValueError, RuntimeError) as error:
            failures.append(f"{path.name}: {error}")

    for failure in failures:
        print(f"Failed: {failure}")
    if failures or len(output_files) < 5:
        raise RuntimeError(
            f"Task 2 incomplete: {len(output_files)} articles saved, {len(failures)} failed"
        )
    print(f"Task 2 complete: {len(output_files)} article JSON files in {DATA_DIR}")
    return output_files


ARTICLE_URLS = [_read_snapshot(path)[0]["source_url"] for path in _source_files()]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="Crawl the public pages again with Crawl4AI")
    arguments = parser.parse_args()
    asyncio.run(crawl_all(refresh=arguments.refresh))
