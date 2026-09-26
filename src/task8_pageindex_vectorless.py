"""
Task 8 — PageIndex vectorless fallback.

Hướng dẫn:
    1. Đọc PAGEINDEX_API_KEY từ .env.
    2. Upload tài liệu ở định dạng PageIndex hỗ trợ.
    3. Cache document IDs để không upload lại.
    4. Parse kết quả thành SearchResult có method pageindex.

PageIndex là dịch vụ ngoài: cần timeout và xử lý lỗi để pipeline không crash.
"""

import hashlib
import json
import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
ROOT = Path(__file__).resolve().parent.parent
LANDING_LEGAL_DIR = ROOT / "data" / "landing" / "legal"
DOCUMENT_IDS_PATH = ROOT / "pageindex_doc_ids.json"
API_BASE = os.getenv("PAGEINDEX_API_BASE", "https://api.pageindex.ai").rstrip("/")
REQUEST_TIMEOUT = float(os.getenv("PAGEINDEX_TIMEOUT", "60"))


def _read_mapping() -> dict[str, dict]:
    if not DOCUMENT_IDS_PATH.is_file():
        return {}
    try:
        value = json.loads(DOCUMENT_IDS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _write_mapping(mapping: dict[str, dict]) -> None:
    temporary = DOCUMENT_IDS_PATH.with_suffix(".json.part")
    temporary.write_text(
        json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(DOCUMENT_IDS_PATH)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    if not PAGEINDEX_API_KEY:
        raise RuntimeError("PAGEINDEX_API_KEY is not configured")
    import requests

    mapping = _read_mapping()
    pdfs = sorted(LANDING_LEGAL_DIR.glob("*.pdf"))
    if not pdfs:
        raise RuntimeError(f"No PDF documents found in {LANDING_LEGAL_DIR}")

    for path in pdfs:
        source_hash = _sha256(path)
        cached = mapping.get(path.name, {})
        if cached.get("sha256") == source_hash and cached.get("doc_id"):
            continue
        with path.open("rb") as stream:
            response = requests.post(
                f"{API_BASE}/doc/",
                headers={"api_key": PAGEINDEX_API_KEY},
                files={"file": (path.name, stream, "application/pdf")},
                timeout=REQUEST_TIMEOUT,
            )
        response.raise_for_status()
        payload = response.json()
        doc_id = payload.get("doc_id")
        if not isinstance(doc_id, str) or not doc_id:
            raise RuntimeError(f"PageIndex did not return doc_id for {path.name}")
        mapping[path.name] = {"doc_id": doc_id, "sha256": source_hash}
        # Persist after each upload so an interrupted run remains resumable.
        _write_mapping(mapping)


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult."""
    if not isinstance(query, str):
        raise ValueError("query must be a string")
    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 0:
        raise ValueError("top_k must be a non-negative integer")
    if top_k == 0 or not query.strip() or not PAGEINDEX_API_KEY:
        return []

    mapping = _read_mapping()
    if not mapping:
        return []
    import requests

    by_doc_id = {
        value["doc_id"]: source
        for source, value in mapping.items()
        if isinstance(value, dict) and isinstance(value.get("doc_id"), str)
    }
    if not by_doc_id:
        return []
    response = requests.post(
        f"{API_BASE}/chat/completions",
        headers={"api_key": PAGEINDEX_API_KEY, "Content-Type": "application/json"},
        json={
            "doc_id": list(by_doc_id),
            "messages": [{"role": "user", "content": query}],
            "stream": False,
            "enable_citations": True,
            "temperature": 0.0,
        },
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    choices = payload.get("choices") or []
    answer = ""
    if choices and isinstance(choices[0], dict):
        answer = str((choices[0].get("message") or {}).get("content") or "").strip()
    if not answer:
        return []

    citations = payload.get("citations") or []
    results = []
    for index, citation in enumerate(citations[:top_k]):
        if not isinstance(citation, dict):
            continue
        doc_id = citation.get("doc_id") or citation.get("document_id")
        source = citation.get("doc") or citation.get("filename") or by_doc_id.get(doc_id)
        source = str(source or "PageIndex")
        page = citation.get("page") or citation.get("page_index")
        text = citation.get("text") or citation.get("content") or answer
        metadata = {
            "source": source,
            "title": str(citation.get("title") or Path(source).stem),
            "doc_type": "legal",
            "url": None,
            "chunk_index": index,
        }
        if isinstance(page, int):
            metadata["page"] = page
        results.append({
            "id": f"pageindex::{doc_id or source}::{page or index}::{index}",
            "content": str(text),
            "score": 1.0 / (index + 1),
            "metadata": metadata,
            "retrieval_method": "pageindex",
        })

    if not results:
        source = next(iter(mapping))
        results = [{
            "id": "pageindex::answer",
            "content": answer,
            "score": 1.0,
            "metadata": {
                "source": source,
                "title": Path(source).stem,
                "doc_type": "legal",
                "url": None,
                "chunk_index": 0,
            },
            "retrieval_method": "pageindex",
        }]

    # Import lazily to keep the optional fallback lightweight.
    from .contracts import validate_search_results

    validate_search_results(results, top_k=top_k, expected_method="pageindex")
    return results


if __name__ == "__main__":
    upload_documents()
