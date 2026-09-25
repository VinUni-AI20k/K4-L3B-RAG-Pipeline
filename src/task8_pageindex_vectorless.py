"""Task 8 — Optional PageIndex Cloud vectorless fallback over source PDFs."""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from functools import lru_cache
from pathlib import Path

import requests
from dotenv import load_dotenv

from .contracts import validate_search_results


load_dotenv()

ROOT_DIR = Path(__file__).parent.parent
PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "").strip()
PAGEINDEX_API_BASE = "https://api.pageindex.ai"
PAGEINDEX_TIMEOUT_SECONDS = 45
PAGEINDEX_POLL_INTERVAL_SECONDS = 2
PAGEINDEX_MAX_WAIT_SECONDS = 90
STANDARDIZED_DIR = ROOT_DIR / "data" / "standardized"
TEMP_PDF_DIR = ROOT_DIR / "data" / "_tmp_pdf"
DOCUMENT_IDS_PATH = ROOT_DIR / "pageindex_doc_ids.json"


def _api_key() -> str:
    return os.getenv("PAGEINDEX_API_KEY", PAGEINDEX_API_KEY).strip()


def _read_mapping() -> dict:
    if not DOCUMENT_IDS_PATH.exists():
        return {"version": 1, "documents": {}}
    try:
        data = json.loads(DOCUMENT_IDS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"version": 1, "documents": {}}
    if not isinstance(data, dict) or not isinstance(data.get("documents"), dict):
        return {"version": 1, "documents": {}}
    return data


def _write_mapping(mapping: dict) -> None:
    temporary = DOCUMENT_IDS_PATH.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(DOCUMENT_IDS_PATH)


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _source_markdown() -> list[Path]:
    return sorted(path for path in STANDARDIZED_DIR.rglob("*.md") if path.is_file())


def _markdown_to_pdf(source: Path) -> Path:
    """Create a temporary text PDF for PageIndex's PDF-only processing API."""
    from fpdf import FPDF

    TEMP_PDF_DIR.mkdir(parents=True, exist_ok=True)
    source_relative = source.relative_to(STANDARDIZED_DIR).as_posix()
    suffix = hashlib.sha256(source_relative.encode("utf-8")).hexdigest()[:12]
    output = TEMP_PDF_DIR / f"{source.stem}_{suffix}.pdf"
    raw = source.read_text(encoding="utf-8-sig")
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", raw)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"[*_`]+", "", text)
    # Core PDF fonts use Windows-1252. Preserve common IELTS punctuation and
    # replace any unsupported character rather than aborting the fallback.
    text = text.encode("cp1252", errors="replace").decode("cp1252")

    pdf = FPDF()
    pdf.set_title(source.stem.replace("_", " "))
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)
    for paragraph in text.splitlines():
        paragraph = paragraph.strip()
        pdf.multi_cell(0, 5, paragraph or " ")
    pdf.output(str(output))
    return output


def upload_documents() -> None:
    """Upload changed PDF sources once and persist their PageIndex document IDs."""
    api_key = _api_key()
    if not api_key:
        print("PageIndex disabled: set PAGEINDEX_API_KEY to enable PDF fallback.")
        return

    sources = _source_markdown()
    if not sources:
        print(f"PageIndex has no standardized Markdown sources under {STANDARDIZED_DIR}.")
        return

    mapping = _read_mapping()
    documents = mapping["documents"]
    failures: list[str] = []
    for path in sources:
        relative_path = path.relative_to(STANDARDIZED_DIR).as_posix()
        fingerprint = _file_sha256(path)
        previous = documents.get(relative_path, {})
        if previous.get("sha256") == fingerprint and previous.get("doc_id"):
            continue
        try:
            upload_path = _markdown_to_pdf(path)
            with upload_path.open("rb") as pdf_file:
                response = requests.post(
                    f"{PAGEINDEX_API_BASE}/doc/",
                    headers={"api_key": api_key},
                    files={"file": (upload_path.name, pdf_file, "application/pdf")},
                    timeout=PAGEINDEX_TIMEOUT_SECONDS,
                )
            response.raise_for_status()
            payload = response.json()
            doc_id = payload.get("doc_id") if isinstance(payload, dict) else None
            if not isinstance(doc_id, str) or not doc_id:
                raise ValueError("PageIndex upload response did not include doc_id")
            documents[relative_path] = {
                "doc_id": doc_id,
                "sha256": fingerprint,
                "title": path.stem.replace("_", " "),
            }
            _write_mapping(mapping)
            print(f"Uploaded to PageIndex: {relative_path}")
        except Exception as error:
            failures.append(f"{relative_path}: {error}")
            print(f"PageIndex upload failed: {relative_path} — {error}")

    if failures and not any(
        item.get("doc_id") for item in documents.values()
    ):
        raise RuntimeError("No PDF could be uploaded to PageIndex: " + "; ".join(failures))


@lru_cache(maxsize=64)
def _fetch_tree(doc_id: str, api_key: str) -> list[dict]:
    deadline = time.monotonic() + PAGEINDEX_MAX_WAIT_SECONDS
    while True:
        response = requests.get(
            f"{PAGEINDEX_API_BASE}/doc/{doc_id}/",
            headers={"api_key": api_key},
            params={"type": "tree"},
            timeout=PAGEINDEX_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError(f"Unexpected PageIndex response for {doc_id}")
        status = str(payload.get("status", "")).lower()
        if status == "completed":
            result = payload.get("result", [])
            if isinstance(result, dict):
                result = result.get("structure", result.get("nodes", []))
            return result if isinstance(result, list) else []
        if status in {"failed", "error", "cancelled"}:
            raise RuntimeError(f"PageIndex processing status is {status} for {doc_id}")
        if time.monotonic() >= deadline:
            raise TimeoutError(f"PageIndex tree is not ready for {doc_id}")
        time.sleep(PAGEINDEX_POLL_INTERVAL_SECONDS)


def _flatten_tree(nodes: list[dict], document_title: str, source: str) -> list[dict]:
    flattened: list[dict] = []

    def visit(node: object) -> None:
        if not isinstance(node, dict):
            return
        title = str(node.get("title") or document_title).strip()
        text = str(node.get("text") or node.get("summary") or "").strip()
        if text:
            node_id = str(node.get("node_id") or node.get("id") or len(flattened))
            page = node.get("page_index")
            try:
                chunk_index = max(0, int(page) - 1) if page is not None else len(flattened)
            except (TypeError, ValueError):
                chunk_index = len(flattened)
            flattened.append({
                "id": f"pageindex::{source}::{node_id}",
                "content": text,
                "score": 0.0,
                "metadata": {
                    "source": source,
                    "title": title,
                    "doc_type": "legal",
                    "url": None,
                    "chunk_index": chunk_index,
                },
                "retrieval_method": "pageindex",
            })
        children = node.get("nodes", node.get("children", []))
        if isinstance(children, list):
            for child in children:
                visit(child)

    for item in nodes:
        visit(item)
    return flattened


def _query_tokens(query: str) -> set[str]:
    return set(re.findall(r"[\w]+(?:[-'][\w]+)*", query.casefold(), flags=re.UNICODE))


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Retrieve relevant tree nodes from PageIndex Cloud without vector search."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")
    if top_k <= 0:
        return []
    api_key = _api_key()
    if not api_key:
        return []

    upload_documents()
    documents = _read_mapping()["documents"]
    query_tokens = _query_tokens(query)
    if not query_tokens:
        return []

    candidates: list[dict] = []
    for source, entry in sorted(documents.items()):
        doc_id = entry.get("doc_id")
        if not doc_id:
            continue
        tree = _fetch_tree(doc_id, api_key)
        candidates.extend(_flatten_tree(tree, entry.get("title", Path(source).stem), source))

    scored: list[dict] = []
    for item in candidates:
        words = _query_tokens(item["content"])
        overlap = len(query_tokens & words)
        if not overlap:
            continue
        # A simple overlap score is used only to order PageIndex tree nodes;
        # Task 9's confidence threshold always uses the original dense score.
        item = dict(item)
        item["score"] = overlap / (len(query_tokens) + 0.25 * len(words))
        scored.append(item)
    scored.sort(key=lambda item: (-item["score"], item["id"]))
    results = scored[:top_k]
    validate_search_results(results, top_k=top_k, expected_method="pageindex")
    return results


if __name__ == "__main__":
    upload_documents()
