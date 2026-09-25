"""Collect and validate the supplied Shopee policy documents.

The three DOCX files are already present in ``data/landing/legal``. Their
embedded ``source_url`` values point to public HTML articles, so this module
does not claim to download original DOCX files from those URLs.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile


DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "landing" / "legal"
DOCUMENT_IDS = (
    "general-return-refund-rules",
    "restricted-return-products",
    "return-by-change-of-mind",
)
MIN_FILE_SIZE = 1024
MIN_CONTENT_LENGTH = 200
WORD_NAMESPACE = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def setup_directory() -> None:
    """Ensure the legal landing directory exists."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _read_docx_paragraphs(path: Path) -> list[str]:
    """Extract visible text and reject invalid or empty Word packages."""
    try:
        with ZipFile(path) as archive:
            required = {"[Content_Types].xml", "word/document.xml"}
            if not required.issubset(archive.namelist()):
                raise ValueError(f"Invalid DOCX package: {path.name}")
            root = ElementTree.fromstring(archive.read("word/document.xml"))
    except (BadZipFile, ElementTree.ParseError, OSError) as error:
        raise ValueError(f"Cannot read DOCX {path.name}: {error}") from error

    return [
        "".join(node.text or "" for node in paragraph.findall(".//w:t", WORD_NAMESPACE)).strip()
        for paragraph in root.findall(".//w:p", WORD_NAMESPACE)
    ]


def _metadata(paragraphs: list[str]) -> dict[str, str]:
    """Read provenance fields from the document's Markdown front matter."""
    fields: dict[str, str] = {}
    for paragraph in paragraphs:
        if paragraph.startswith("## "):
            break
        key, separator, value = paragraph.partition(":")
        if separator and key in {"doc_id", "title", "source_url", "retrieved_at"}:
            fields[key] = value.strip()
    return fields


def validate_document(path: Path, expected_id: str) -> dict[str, str]:
    """Check one supplied DOCX for readable content and source provenance."""
    if not path.is_file():
        raise FileNotFoundError(f"Required policy document is missing: {path}")
    if path.stat().st_size < MIN_FILE_SIZE:
        raise ValueError(f"Policy document is too small: {path.name}")
    if path.stem != expected_id or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", path.stem):
        raise ValueError(f"Unexpected or non-ASCII document name: {path.name}")

    paragraphs = _read_docx_paragraphs(path)
    fields = _metadata(paragraphs)
    for key in ("doc_id", "title", "source_url", "retrieved_at"):
        if not fields.get(key):
            raise ValueError(f"Missing {key} metadata in {path.name}")
    if fields["doc_id"] != expected_id:
        raise ValueError(f"doc_id does not match filename: {path.name}")
    source = urlparse(fields["source_url"])
    if source.scheme != "https" or not source.netloc:
        raise ValueError(f"Invalid source_url in {path.name}")
    try:
        date.fromisoformat(fields["retrieved_at"])
    except ValueError as error:
        raise ValueError(f"Invalid retrieved_at in {path.name}") from error
    if len(" ".join(paragraphs).strip()) < MIN_CONTENT_LENGTH:
        raise ValueError(f"Policy document has too little text: {path.name}")
    return fields


def download_documents() -> list[Path]:
    """Register the three already collected documents after validation.

    The function name is retained for compatibility with the original Task 1
    entry point. No network request is needed for user supplied DOCX files.
    """
    setup_directory()
    documents: list[Path] = []
    for document_id in DOCUMENT_IDS:
        path = DATA_DIR / f"{document_id}.docx"
        metadata = validate_document(path, document_id)
        print(
            f"Ready: {path.name} ({path.stat().st_size} bytes; "
            f"source: {urlparse(metadata['source_url']).hostname})"
        )
        documents.append(path)
    print(f"Task 1 complete: {len(documents)} policy DOCX files in {DATA_DIR}")
    return documents


if __name__ == "__main__":
    download_documents()
