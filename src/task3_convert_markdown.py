"""Normalize NEU PDFs/articles with page provenance and reusable OCR cache."""
import csv
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from src.task2_crawl_news import validate_article

ROOT = Path(__file__).resolve().parents[1]
LANDING_DIR = ROOT / "data/landing"
OUTPUT_DIR = ROOT / "data/standardized"
OCR_DIR = ROOT / "data/ocr"
MANIFEST = ROOT / "data/sources.json"


def normalize(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x0c", "")
    return re.sub(r"\n{3,}", "\n\n", "\n".join(line.rstrip() for line in text.splitlines())).strip()


def tesseract_command() -> str:
    local = ROOT / "data/_tmp_pdf/tesseract/tesseract.exe"
    command = os.environ.get("TESSERACT_CMD") or shutil.which("tesseract")
    if not command and local.exists():
        command = str(local)
    if not command:
        raise RuntimeError("Scanned PDF needs Tesseract + vie.traineddata. Set TESSERACT_CMD; see docs/DATA_HANDOFF.md.")
    return command


def ocr_page(page) -> tuple[str, float | None]:
    command = tesseract_command()
    temporary_root = ROOT / "data/_tmp_pdf"
    temporary_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="neu_ocr_", dir=temporary_root) as directory:
        image = Path(directory) / "page.png"
        page.to_image(resolution=300).save(str(image))
        output = Path(directory) / "result"
        env = {**os.environ, "OMP_THREAD_LIMIT": "2"}
        subprocess.run([command, str(image), str(output), "-l", "vie+eng",
                        "--psm", "3", "-c", "preserve_interword_spaces=1", "txt", "tsv"],
                       check=True, capture_output=True, timeout=180, env=env)
        text = normalize(output.with_suffix(".txt").read_text(encoding="utf-8"))
        rows = csv.DictReader(io.StringIO(output.with_suffix(".tsv").read_text(encoding="utf-8")), delimiter="\t")
        scores = [float(row["conf"]) for row in rows if row.get("text", "").strip() and float(row["conf"]) >= 0]
        return text, round(sum(scores) / len(scores), 2) if scores else None


def extract_pdf(path: Path, document_id: str) -> list[dict]:
    import pdfplumber
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    cache = OCR_DIR / f"{document_id}.json"
    if cache.exists():
        saved = json.loads(cache.read_text(encoding="utf-8"))
        if saved.get("sha256") == digest and saved.get("extractor_version") == 1:
            return saved["pages"]
    pages = []
    with pdfplumber.open(path) as pdf:
        for number, page in enumerate(pdf.pages, 1):
            text = normalize(page.extract_text(layout=True) or "")
            method, confidence = "pdf_text", None
            if len(text) < 80:
                text, confidence = ocr_page(page)
                method = "tesseract_vie_eng"
            if len(text) < 80:
                raise ValueError(f"{path.name}, page {number}: no usable text after OCR")
            pages.append({"page": number, "text": text, "extraction_method": method,
                          "ocr_mean_confidence": confidence})
            print(f"{document_id}: page {number}/{len(pdf.pages)} ({method})", flush=True)
    OCR_DIR.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({"sha256": digest, "extractor_version": 1, "pages": pages},
                               ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return pages


def save_document(item: dict, content: str, extra: dict) -> None:
    directory = OUTPUT_DIR / item["doc_type"]
    directory.mkdir(parents=True, exist_ok=True)
    metadata = {**item, **extra, "source": item["local_path"]}
    header = "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in metadata.items())
    markdown = f"---\n{header}\n---\n\n# {item['title']}\n\n{normalize(content)}\n"
    (directory / f"{item['id']}.md").write_text(markdown, encoding="utf-8")
    document = {"id": item["id"], "content": normalize(content), "metadata": metadata}
    (directory / f"{item['id']}.json").write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def convert_legal_docs() -> None:
    for item in json.loads(MANIFEST.read_text(encoding="utf-8-sig")):
        if item["doc_type"] != "legal":
            continue
        path = ROOT / item["local_path"]
        if path.suffix.lower() == ".pdf":
            pages = extract_pdf(path, item["id"])
            reviewed_pages = []
            review_directory = ROOT / "data/reviewed" / item["id"]
            review_manifest = review_directory / "review.json"
            if review_manifest.exists():
                review = json.loads(review_manifest.read_text(encoding="utf-8"))
                if review["source_sha256"] != hashlib.sha256(path.read_bytes()).hexdigest():
                    raise ValueError(f"Reviewed pages are stale: {item['id']}")
                for p in pages:
                    reviewed = review_directory / f"page_{p['page']:02d}.md"
                    if reviewed.exists():
                        p["text"] = normalize(reviewed.read_text(encoding="utf-8"))
                        reviewed_pages.append(p["page"])
            content = "\n\n".join(f"## Trang {p['page']}\n\n{p['text']}" for p in pages)
            save_document(item, content, {"page_count": len(pages),
                "visually_reviewed_pages": reviewed_pages,
                "extraction_method": ",".join(sorted({p["extraction_method"] for p in pages})),
                "review_status": "ocr_requires_numeric_and_table_review"})
        elif path.suffix.lower() == ".docx":
            from markitdown import MarkItDown
            content = normalize(MarkItDown().convert(str(path)).text_content)
            if not content:
                raise ValueError(f"Empty DOCX: {path}")
            save_document(item, content, {"extraction_method": "markitdown"})
        else:
            raise ValueError(f"Unsupported legal document: {path}")


def convert_news_articles() -> None:
    for item in json.loads(MANIFEST.read_text(encoding="utf-8-sig")):
        if item["doc_type"] != "news":
            continue
        article = json.loads((ROOT / item["local_path"]).read_text(encoding="utf-8-sig"))
        validate_article(article)
        if article["url"] != item["url"]:
            raise ValueError(f"Manifest URL mismatch: {item['id']}")
        metadata = {k: v for k, v in article.items() if k != "content_markdown"}
        save_document(metadata, article["content_markdown"], {"extraction_method": "html_to_markdown"})


def convert_all() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"Saved Markdown and contract JSON to {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
