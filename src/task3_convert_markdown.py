"""Chuẩn hóa PDF và JSON thành Markdown có metadata truy vết được."""

from __future__ import annotations

import json
import html
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).parent.parent
LANDING_DIR = ROOT / "data" / "landing"
OUTPUT_DIR = ROOT / "data" / "standardized"


def _front_matter(metadata: dict) -> str:
    lines = ["---"]
    for key, value in metadata.items():
        escaped = str(value if value is not None else "").replace('"', '\\"')
        lines.append(f'{key}: "{escaped}"')
    lines.extend(["---", ""])
    return "\n".join(lines)


class _LegalHTMLParser(HTMLParser):
    ignored_tags = {"script", "style", "svg", "noscript", "form", "iframe"}
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

    def handle_endtag(self, tag: str) -> None:
        if tag in self.ignored_tags and self.ignored_depth:
            self.ignored_depth -= 1
        elif not self.ignored_depth and tag in self.block_tags:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.ignored_depth:
            self.parts.append(data)

    def text(self) -> str:
        raw = html.unescape("".join(self.parts)).replace("\xa0", " ")
        lines = [re.sub(r"\s+", " ", line).strip() for line in raw.splitlines()]
        return "\n\n".join(line for line in lines if line)


def _fetch_full_text(url: str) -> str:
    try:
        import truststore

        truststore.inject_into_ssl()
    except ImportError:
        pass
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; K4-RAG-Lab/1.0)"})
    with urlopen(request, timeout=60) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        raw_html = response.read().decode(charset, errors="replace")
    parser = _LegalHTMLParser()
    parser.feed(raw_html)
    return parser.text()


def _convert_pdf(path: Path, full_text_url: str) -> str:
    try:
        from markitdown import MarkItDown
    except ImportError:
        try:
            from pypdf import PdfReader
        except ImportError as error:
            raise RuntimeError(
                'Thiếu công cụ đọc PDF; chạy: python -m pip install -e ".[dev]"'
            ) from error
        reader = PdfReader(str(path))
        text = "\n\n".join((page.extract_text() or "").strip() for page in reader.pages).strip()
    else:
        text = MarkItDown().convert(str(path)).text_content.strip()
    if len(text) < 200:
        text = _fetch_full_text(full_text_url)
    if len(text) < 200:
        raise ValueError(f"Không trích xuất đủ nội dung từ {path.name} hoặc trang toàn văn")
    return text


def convert_legal_docs() -> None:
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = legal_dir / "legal_sources.json"
    if not manifest_path.exists():
        raise FileNotFoundError("Thiếu legal_sources.json; hãy chạy Task 1 trước")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    for item in manifest:
        source_path = legal_dir / item["filename"]
        if not source_path.exists():
            raise FileNotFoundError(source_path)
        body = _convert_pdf(source_path, item["full_text_url"])
        metadata = {
            "title": item["title"],
            "source": item["filename"],
            "doc_type": "legal",
            "url": item["source_page"],
            "document_number": item["document_number"],
            "issuer": item["issuer"],
            "issued_date": item["issued_date"],
            "effective_date": item["effective_date"],
            "status": item["status"],
            "version_note": item["version_note"],
            "collected_at": item["collected_at"],
        }
        output = output_dir / f"{source_path.stem}.md"
        output.write_text(_front_matter(metadata) + f"# {item['title']}\n\n" + body + "\n", encoding="utf-8")
        print(f"Saved: {output}")


def convert_news_articles() -> None:
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(news_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        required = {"url", "title", "date_crawled", "content_markdown"}
        missing = required - data.keys()
        if missing:
            raise ValueError(f"{path.name} thiếu metadata: {sorted(missing)}")
        body = str(data["content_markdown"]).strip()
        if len(body) < 200:
            raise ValueError(f"Nội dung {path.name} quá ngắn")
        metadata = {
            "title": data["title"],
            "source": path.name,
            "doc_type": "news",
            "url": data["url"],
            "publisher": data.get("publisher", ""),
            "date_crawled": data["date_crawled"],
        }
        output = output_dir / f"{path.stem}.md"
        output.write_text(_front_matter(metadata) + f"# {data['title']}\n\n" + body + "\n", encoding="utf-8")
        print(f"Saved: {output}")


def convert_all() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"Saved Markdown to: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
