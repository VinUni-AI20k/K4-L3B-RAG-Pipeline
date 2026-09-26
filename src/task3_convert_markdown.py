"""Task 3: PDF/DOCX and news JSON to Markdown with source metadata.

Uses PyMuPDF with Vietnamese OCR for scanned PDFs, MarkItDown for DOCX,
and the standard library for JSON. See docs/TASK3.md for isolated setup.
Original landing documents are never changed.
"""

import argparse
import hashlib
import json
import os
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANDING_DIR = ROOT / "data" / "landing"
OUTPUT_DIR = ROOT / "data" / "standardized"
CACHE_DIR = ROOT / ".cache" / "task3-ocr"
TESSDATA_DIR = Path(os.environ.get("TESSDATA_PREFIX", ROOT / ".cache" / "tessdata-fast"))
CONVERTER_VERSION = "2"


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text).replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\x00", "").replace("\xa0", " ")
    return re.sub(r"\n{3,}", "\n\n", "\n".join(line.rstrip() for line in text.splitlines())).strip()


def atomic_write(path: Path, text: str) -> None:
    if not text.strip():
        raise ValueError(f"Refusing empty output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return
    temporary = path.with_suffix(path.suffix + ".part")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def markdown_document(metadata: dict, body: str) -> str:
    body = normalize(body)
    if not body:
        raise ValueError("No extracted document content")
    # JSON-quoted values are valid YAML scalars and preserve URLs and colons.
    header = "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in metadata.items())
    return f"---\n{header}\n---\n\n# {metadata['title']}\n\n{body}\n"


def legal_headings(text: str) -> str:
    lines = []
    for line in normalize(text).splitlines():
        stripped = line.strip()
        if re.match(r"^Điều\s+\d+\b", stripped):
            line = "### " + stripped
        elif re.match(r"^(?:CHƯƠNG|Chương)\s+[IVXLCDM\d]+\b", stripped):
            line = "## " + stripped
        lines.append(line)
    return "\n".join(lines)


def ocr_text(textpage) -> str:
    """Keep OCR word boundaries: plain extraction may glue adjacent spans."""
    paragraphs = []
    for block in textpage.extractDICT()["blocks"]:
        lines = []
        for line in block.get("lines", []):
            words = [span["text"].strip() for span in line["spans"] if span["text"].strip()]
            if words:
                lines.append(" ".join(words))
        if lines:
            paragraphs.append("\n".join(lines))
    return normalize("\n\n".join(paragraphs))


def pdf_text(path: Path, digest: str) -> tuple[str, dict]:
    import pymupdf

    model = TESSDATA_DIR / "vie.traineddata"
    model_hash = hashlib.sha256(model.read_bytes()).hexdigest() if model.exists() else "missing"
    settings = f"{CONVERTER_VERSION}:{pymupdf.VersionBind}:vie:300:{model_hash}"
    key = hashlib.sha256(f"{digest}:{settings}".encode()).hexdigest()
    cache = CACHE_DIR / key
    pages, ocr_pages = [], []
    with pymupdf.open(path) as document:
        if not len(document):
            raise ValueError(f"PDF has no pages: {path}")
        for index, page in enumerate(document, 1):
            text = normalize(page.get_text(sort=True))
            method = "text"
            # Signed scans may expose only the digital-signature caption as text.
            # A large page image plus a short caption still requires full OCR.
            scan_image = any(
                pymupdf.Rect(image["bbox"]).get_area() > page.rect.get_area() * 0.5
                for image in page.get_image_info()
            )
            if len(re.sub(r"\s", "", text)) < 50 or (scan_image and len(text) < 500):
                method = "ocr"
                ocr_pages.append(index)
                cached = cache / f"page_{index:03d}.txt"
                if cached.exists() and cached.read_text(encoding="utf-8").strip():
                    text = cached.read_text(encoding="utf-8")
                else:
                    if not model.is_file():
                        raise RuntimeError(f"Vietnamese OCR model missing: {model}; see docs/TASK3.md")
                    textpage = page.get_textpage_ocr(language="vie", dpi=300, full=True, tessdata=str(TESSDATA_DIR.resolve()))
                    text = ocr_text(textpage)
                    if len(re.sub(r"\s", "", text)) < 30:
                        raise ValueError(f"Empty/insufficient OCR: {path.name}, page {index}")
                    atomic_write(cached, text + "\n")
            pages.append(f"## Trang {index}\n\n{legal_headings(text)}")
            print(f"  {path.name}: page {index}/{len(document)} ({method})", flush=True)
    return "\n\n".join(pages), {
        "page_count": len(pages), "ocr_pages": ocr_pages,
        "conversion_method": "pymupdf+tesseract-vie" if ocr_pages else "pymupdf-text",
        "ocr_dpi": 300 if ocr_pages else None,
        "ocr_model_sha256": model_hash if ocr_pages else None,
        "review_status": "OCR output; not fully manually proofread" if ocr_pages else "automatically extracted",
    }


def convert_legal_docs() -> None:
    legal_dir = LANDING_DIR / "legal"
    manifest_path = legal_dir / "sources.json"
    sources = {}
    if manifest_path.exists():
        sources = {item["filename"]: item for item in json.loads(manifest_path.read_text(encoding="utf-8"))["documents"]}
    paths = sorted(p for p in legal_dir.iterdir() if p.suffix.lower() in {".pdf", ".docx"})
    if len({p.stem.casefold() for p in paths}) != len(paths):
        raise ValueError("Legal files have colliding output names")
    for path in paths:
        source = sources.get(path.name, {})
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if source.get("sha256") and source["sha256"] != digest:
            raise ValueError(f"Source checksum mismatch: {path.name}")
        metadata = {
            "title": source.get("title", path.stem), "source": path.name,
            "doc_type": "legal", "url": source.get("source_url"),
            "download_url": source.get("download_url"), "source_sha256": digest,
            "language": "vi", "converter_version": CONVERTER_VERSION,
        }
        if path.suffix.lower() == ".pdf":
            body, details = pdf_text(path, digest)
            metadata.update(details)
        else:
            from markitdown import MarkItDown
            body = MarkItDown().convert(str(path)).text_content
            metadata["conversion_method"] = "markitdown"
        output = OUTPUT_DIR / "legal" / f"{path.stem}.md"
        atomic_write(output, markdown_document(metadata, body))
        print(f"Saved: {output}", flush=True)


def convert_news_articles() -> None:
    for path in sorted((LANDING_DIR / "news").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for key in ("url", "title", "date_crawled", "content_markdown"):
            if not isinstance(data.get(key), str) or not data[key].strip():
                raise ValueError(f"Missing or empty {key}: {path}")
        metadata = {
            "title": data["title"], "source": path.name, "doc_type": "news",
            "url": data["url"], "date_crawled": data["date_crawled"],
            "language": data.get("language"), "resolved_url": data.get("resolved_url"),
            "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "conversion_method": "json-markdown", "converter_version": CONVERTER_VERSION,
        }
        output = OUTPUT_DIR / "news" / f"{path.stem}.md"
        atomic_write(output, markdown_document(metadata, data["content_markdown"]))
        print(f"Saved: {output}", flush=True)


def convert_all() -> None:
    """Convert news first, independently of optional OCR dependencies."""
    convert_news_articles()
    convert_legal_docs()
    print(f"Saved Markdown to: {OUTPUT_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=("all", "news", "legal"), default="all")
    args = parser.parse_args()
    {"all": convert_all, "news": convert_news_articles, "legal": convert_legal_docs}[args.only]()
