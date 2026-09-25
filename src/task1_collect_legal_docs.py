"""Task 1: collect original legal documents in data/landing/legal/.

Existing manually collected files are supported. To add public documents:
python -m src.task1_collect_legal_docs --source ten_tai_lieu.pdf=https://host/file.pdf
Repeat --source for additional documents. Do not bypass blocked websites.
"""

import argparse
import hashlib
import io
import re
import tempfile
from pathlib import Path
from urllib.parse import urlsplit
from zipfile import BadZipFile, ZipFile

import requests

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "landing" / "legal"
EXTENSIONS = {".pdf", ".doc", ".docx"}


def setup_directory() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def document_digest(filename: str, content: bytes) -> str:
    """Reject HTML/error pages and undersized files, including renamed downloads."""
    suffix = Path(filename).suffix.lower()
    if len(content) <= 1024:
        raise ValueError(f"{filename}: document must be larger than 1024 bytes")
    valid = False
    if suffix == ".pdf":
        valid = content.startswith(b"%PDF-") and b"%%EOF" in content[-4096:]
    elif suffix == ".doc":
        valid = content.startswith(bytes.fromhex("D0CF11E0A1B11AE1"))
    elif suffix == ".docx":
        try:
            with ZipFile(io.BytesIO(content)) as archive:
                valid = {"[Content_Types].xml", "word/document.xml"} <= set(archive.namelist())
        except BadZipFile:
            pass
    if not valid:
        raise ValueError(f"{filename}: invalid {suffix} document")
    return hashlib.sha256(content).hexdigest()


def download_documents(sources: dict[str, str] | None = None) -> None:
    """Download supplied sources; retain valid files and avoid duplicate content."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    known: dict[str, Path] = {}
    for path in sorted(DATA_DIR.iterdir()):
        if path.is_file() and not path.name.startswith(".") and path.suffix.lower() in EXTENSIONS:
            digest = document_digest(path.name, path.read_bytes())
            known.setdefault(digest, path)
            print(f"Existing: {path.name}")

    for filename, url in (sources or {}).items():
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", filename):
            raise ValueError("Use a plain ASCII filename without directories")
        if Path(filename).suffix.lower() not in EXTENSIONS:
            raise ValueError(f"{filename}: expected PDF, DOC or DOCX")
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(f"{filename}: expected a public HTTP(S) URL")
        target = DATA_DIR / filename
        if target.exists():
            print(f"Skip existing: {filename}")
            continue
        # A blocked source is an error; no alternate credentials or WAF bypass.
        with requests.get(url, timeout=(10, 60)) as response:
            response.raise_for_status()
            content = response.content
        digest = document_digest(filename, content)
        if digest in known:
            print(f"Skip duplicate: {filename} (same content as {known[digest].name})")
            continue
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=DATA_DIR, suffix=".part", delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(content)
            temporary.replace(target)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        known[digest] = target
        print(f"Downloaded: {filename} ({len(content)} bytes)")

    if len(known) < 3:
        raise ValueError(
            f"Only {len(known)} distinct valid legal documents; need at least 3. "
            "Add files manually or supply --source filename.pdf=https://host/document.pdf"
        )
    print(f"OK: {len(known)} distinct legal documents in {DATA_DIR}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", action="append", default=[], metavar="FILENAME=URL")
    args = parser.parse_args()
    sources: dict[str, str] = {}
    for value in args.source:
        filename, separator, url = value.partition("=")
        if not separator or filename in sources:
            parser.error("Each --source must be a distinct FILENAME=URL")
        sources[filename] = url
    setup_directory()
    try:
        download_documents(sources)
    except (OSError, ValueError, requests.RequestException) as exc:
        parser.exit(1, f"ERROR: {exc}\n")


if __name__ == "__main__":
    main()

