"""Task 3 — Convert landing HTML/PDF/DOCX/JSON to clean, source-aware Markdown.

Run offline with: python -m src.task3_convert_markdown
"""

import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from markdownify import markdownify

LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"
HEADING = re.compile(r"^(#{1,6})\s+(.+)$")


def _clean_prose(text: str, url: str | None) -> str:
    """Clean non-code blocks without flattening tables or nested lists."""
    blocks = re.split(r"\n\s*\n", text.strip())
    cleaned = []
    for block in blocks:
        if block == "Stub" or block.startswith("*This article is a [stub]"):
            continue
        # Fandom's broken navigation table has only an entry for category Tướng.
        # Match the whole block, never remove a section containing real content.
        rows = block.splitlines()
        if rows and all(row.strip().startswith("|") for row in rows):
            meaningful = [row for row in rows if re.sub(r"[|\s:\-]", "", row)]
            if not meaningful:
                continue
            if (len(meaningful) == 1
                    and re.fullmatch(r'\|\s*\*\*\[Tướng\]\([^\n]+\)\*\*\s*\|\s*\|?', meaningful[0])
                    and ("Th%E1%BB%83_lo%E1%BA%A1i:" in meaningful[0]
                         or "Thể_loại:" in meaningful[0])):
                continue
        if url:
            block = re.sub(r"(\]\()(/[^\s)]*)", lambda m: m[1] + urljoin(url, m[2]), block)
        cleaned.append(block)
    return "\n\n".join(cleaned)


def clean_markdown(text: str, url: str | None = None) -> str:
    """Normalize prose and remove empty sections; preserve fenced code verbatim."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Split off fenced code before any whitespace/Unicode/link transformations.
    parts = re.split(r"(^[ \t]*```[^\n]*\n.*?^[ \t]*```[ \t]*$|^[ \t]*~~~[^\n]*\n.*?^[ \t]*~~~[ \t]*$)", text, flags=re.M | re.S)
    for index in range(0, len(parts), 2):
        prose = unicodedata.normalize("NFC", parts[index])
        prose = prose.replace("\ufeff", "").replace("\u200b", "").replace("\xa0", " ")
        # Preserve two-space Markdown hard breaks and indentation of nested lists.
        prose = "\n".join(line.rstrip() + ("  " if line.endswith("  ") and line.strip() else "") for line in prose.splitlines())
        parts[index] = _clean_prose(prose, url)
    text = "\n\n".join(part for part in parts if part.strip())
    # Walk backwards so a parent with only empty subsections is also removed.
    lines = text.splitlines()
    in_code = False
    headings = set()
    for index, line in enumerate(lines):
        if re.match(r"^\s*(`{3,}|~{3,})", line):
            in_code = not in_code
        elif not in_code and HEADING.match(line):
            headings.add(index)
    for index in sorted(headings, reverse=True):
        level = len(HEADING.match(lines[index])[1])
        end = index + 1
        while end < len(lines):
            match = HEADING.match(lines[end]) if end in headings else None
            if match and len(match[1]) <= level:
                break
            end += 1
        if not any(line.strip() for line in lines[index + 1:end]):
            lines[index] = ""
    # Collapse blank lines only outside fenced code.
    result = []
    in_code = False
    for line in lines:
        if re.match(r"^\s*(`{3,}|~{3,})", line):
            in_code = not in_code
        if line.strip() or in_code or (result and result[-1].strip()):
            result.append(line)
    return "\n".join(result).strip()


def html_to_markdown(path: Path, url: str | None) -> tuple[str, str, str | None]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8-sig"), "html.parser")
    title_node = soup.select_one("h1, .content .title > p") or soup.title
    title = title_node.get_text(" ", strip=True) if title_node else path.stem
    published = soup.select_one(".p-news__single--meta")
    date_published = published.get_text(" ", strip=True) if published else None
    body = soup.select_one("article, .entry-content") or soup.select_one("main, .content") or soup.body or soup
    for tag in body.select("script, style, noscript, nav, footer, header, form, iframe, .mw-editsection, .toc"):
        tag.decompose()
    if title_node and title_node in body.descendants:
        title_node.decompose()
    # The Garena terms export represents its numbered section titles as lists.
    for section in body.select("ol.lst-kix_list_12-0"):
        heading = soup.new_tag("h2")
        heading.string = f"{section.get('start', '1')}. {section.get_text(' ', strip=True)}"
        section.replace_with(heading)
    for tag in body.select("a[href], img[src]"):
        attr = "href" if tag.name == "a" else "src"
        if url:
            tag[attr] = urljoin(url, tag[attr])
    for node in list(body.find_all(string=True)):
        if not node.find_parent(["pre", "code"]):
            node.replace_with(re.sub(r"\s+", " ", str(node)))
    return title, markdownify(str(body), heading_style="ATX", bullets="-", table_infer_header=True), date_published


def write_document(path: Path, doc_type: str, title: str, body: str, metadata: dict) -> None:
    title = " ".join(title.split())
    if not title:
        raise ValueError(f"{path.name}: empty title")
    body = clean_markdown(body, metadata.get("url"))
    if body.splitlines() and body.splitlines()[0] == f"# {title}":
        body = body.partition("\n")[2].strip()
    if not body:
        raise ValueError(f"{path.name}: empty content after cleaning")
    target = OUTPUT_DIR / doc_type / f"{path.stem}.md"
    fields = {
        "id": f"{doc_type}/{target.name}",
        "source": f"{doc_type}/{path.name}",
        "title": title,
        "doc_type": doc_type,
        "url": metadata.get("url"),
        "date_crawled": metadata.get("date_crawled"),
    }
    if metadata.get("date_published"):
        fields["date_published"] = metadata["date_published"]
    # JSON-quoted scalars are valid YAML, including titles containing colons.
    header = "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in fields.items())
    output = f"---\n{header}\n---\n\n# {title}\n\n{body}\n"
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.read_text(encoding="utf-8") == output:
        print(f"Unchanged: {doc_type}/{target.name}")
        return
    temporary = target.with_suffix(".md.tmp")
    temporary.write_text(output, encoding="utf-8")
    temporary.replace(target)
    print(f"Saved: {doc_type}/{target.name}")


def convert_legal_docs() -> None:
    directory = LANDING_DIR / "legal"
    manifest_path = directory / "sources.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    if not isinstance(manifest, dict):
        raise ValueError("sources.json must be an object keyed by filename")
    paths = sorted(p for p in directory.iterdir() if p.is_file() and p.suffix.lower() in {".html", ".htm", ".pdf", ".docx"})
    if len({p.stem for p in paths}) != len(paths):
        raise ValueError("Duplicate legal stems: rename input files to avoid overwriting")
    if list(directory.glob("*.doc")):
        raise ValueError("Convert legacy .doc files to .docx before running Task 3")
    for path in paths:
        metadata = dict(manifest.get(path.name, {}))
        if path.suffix.lower() in {".html", ".htm"}:
            title, body, published = html_to_markdown(path, metadata.get("url"))
            metadata["date_published"] = published
        else:
            from markitdown import MarkItDown

            result = MarkItDown().convert(str(path))
            title, body = result.title or path.stem, result.text_content
        write_document(path, "legal", title, body, metadata)


def convert_news_articles() -> None:
    for path in sorted((LANDING_DIR / "news").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(data, dict):
            raise ValueError(f"{path.name}: expected a JSON object")
        for key in ("title", "url", "date_crawled", "content_markdown"):
            if not isinstance(data.get(key), str) or not data[key].strip():
                raise ValueError(f"{path.name}: {key} must be a non-empty string")
        write_document(path, "news", data["title"], data["content_markdown"], data)


def convert_all() -> None:
    """Fail visibly on invalid inputs; completed files remain safe to rerun."""
    convert_legal_docs()
    convert_news_articles()
    print(f"Saved Markdown to: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
