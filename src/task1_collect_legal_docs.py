"""Task 1 - collect and validate the legal corpus for Vietnamese tourism."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "landing" / "legal"
MANIFEST_PATH = DATA_DIR / "sources.json"
MIN_FILE_SIZE = 1024


def load_sources() -> list[dict[str, str]]:
    """Load provenance and download information for every legal document."""
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Missing legal source manifest: {MANIFEST_PATH}")

    sources = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(sources, list) or len(sources) < 3:
        raise ValueError("sources.json must describe at least 3 legal documents")
    return sources


def setup_directory() -> None:
    """Create landing folders used by the legal corpus."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "text_sources").mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def download_text_sources(sources: list[dict[str, str]]) -> None:
    """Download official text-layer copies used for Markdown conversion."""
    import requests

    for source in sources:
        output = DATA_DIR / source["text_file"]
        if output.exists() and output.stat().st_size > MIN_FILE_SIZE:
            print(f"Already exists: {output}")
            continue

        output.parent.mkdir(parents=True, exist_ok=True)
        response = requests.get(source["text_download_url"], timeout=60)
        response.raise_for_status()
        output.write_bytes(response.content)
        print(f"Downloaded: {output}")


def validate_documents(sources: list[dict[str, str]]) -> None:
    """Require both signed originals and usable official text-layer copies."""
    problems: list[str] = []
    for source in sources:
        for field in ("original_file", "text_file"):
            path = DATA_DIR / source[field]
            if not path.is_file() or path.stat().st_size <= MIN_FILE_SIZE:
                problems.append(f"missing or too small: {path}")

        for field in ("title", "document_number", "official_page_url"):
            if not str(source.get(field, "")).strip():
                problems.append(f"{source.get('id', '<unknown>')}: empty {field}")

    if problems:
        raise RuntimeError("Legal corpus validation failed:\n- " + "\n- ".join(problems))

    print(f"Ready: {len(sources)} signed originals + official text-layer copies")


def download_documents() -> None:
    """Download missing conversion copies and validate the legal corpus."""
    setup_directory()
    sources = load_sources()
    download_text_sources(sources)
    validate_documents(sources)


if __name__ == "__main__":
    download_documents()
