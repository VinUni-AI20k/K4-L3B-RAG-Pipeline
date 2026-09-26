"""Task 8 - PageIndex fallback with an offline local fallback."""

from __future__ import annotations

import json
import math
import os
import re
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = ROOT / "data" / "standardized"
CACHE_PATH = ROOT / "pageindex_cache.json"
PDF_DIR = ROOT / "pageindex_pdfs"
PAGEINDEX_TIMEOUT = float(os.getenv("PAGEINDEX_TIMEOUT", "30"))
STOPWORDS = {
    "ai", "bao", "bi", "cach", "cho", "co", "cua", "duoc", "gi", "gia",
    "hay", "hom", "khi", "la", "mot", "nao", "nay", "nhung", "o", "tai",
    "the", "thi", "va", "ve", "voi", "được", "cách", "cho", "có", "của",
    "gì", "giá", "hôm", "khi", "là", "một", "nào", "nay", "những", "ở",
    "tại", "thế", "thì", "và", "về", "với",
}
DOMAIN_TERMS = {
    "ẩm", "thực", "ăn", "món", "khách", "sạn", "tour", "visa", "vé",
    "du", "lịch", "lữ", "hành", "luật", "nghị", "định", "phạt", "quyền",
    "hà", "nội", "ninh", "bình", "huế", "việt", "nam", "điểm", "đến",
    "travel", "tourism", "hotel", "restaurant",
}


def _query_terms(query: str) -> set[str]:
    return {
        term for term in re.findall(r"\w+", query.lower())
        if len(term) > 2 and term not in STOPWORDS
    }


def _metadata(path: Path) -> dict[str, Any]:
    return {
        "source": path.name,
        "title": path.stem,
        "doc_type": "legal" if "legal" in path.parts else "news",
        "url": None,
        "chunk_index": 0,
    }


def _load_cache() -> dict[str, Any]:
    if not CACHE_PATH.exists():
        return {}
    try:
        value = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _save_cache(cache: dict[str, Any]) -> None:
    CACHE_PATH.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _markdown_to_pdf(path: Path) -> Path:
    """Create a simple PDF accepted by PageIndex from Markdown."""
    output = PDF_DIR / f"{path.relative_to(STANDARDIZED_DIR).with_suffix('.pdf')}"
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and output.stat().st_mtime >= path.stat().st_mtime:
        return output

    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.encode("latin-1", "replace").decode("latin-1")
        if not text:
            pdf.ln(5)
            continue
        for start in range(0, len(text), 40):
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(pdf.epw, 5, text[start : start + 40])
    pdf.output(str(output))
    return output


def upload_documents() -> None:
    """Upload standardized documents and cache PageIndex document IDs."""
    cache = _load_cache()
    documents = sorted(STANDARDIZED_DIR.rglob("*.md"))

    if not PAGEINDEX_API_KEY:
        for path in documents:
            cache.setdefault(path.name, {"source_path": path.as_posix()})
        _save_cache(cache)
        print("PAGEINDEX_API_KEY is not configured; wrote local document manifest.")
        return

    from pageindex import PageIndexClient

    client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
    for path in documents:
        entry = cache.get(path.name, {})
        if isinstance(entry, dict) and entry.get("doc_id"):
            continue
        try:
            response = client.submit_document(str(_markdown_to_pdf(path)))
            doc_id = response.get("doc_id")
            if not doc_id:
                raise RuntimeError(f"PageIndex response has no doc_id: {response}")
            cache[path.name] = {
                "doc_id": doc_id,
                "source_path": path.as_posix(),
            }
            _save_cache(cache)
            print(f"Uploaded {path.name}: {doc_id}")
        except Exception as error:
            print(f"PageIndex upload failed for {path.name}: {error}")


def _local_search(query: str, top_k: int) -> list[dict]:
    terms = _query_terms(query)
    if not terms & DOMAIN_TERMS:
        return []
    minimum_overlap = max(1, math.ceil(len(terms) * 0.6))
    results = []
    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        content = path.read_text(encoding="utf-8").strip()
        words = set(re.findall(r"\w+", content.lower()))
        score = float(len(terms & words))
        if score >= minimum_overlap:
            results.append(
                {
                    "id": path.relative_to(STANDARDIZED_DIR).as_posix() + "::pageindex",
                    "content": content,
                    "score": score,
                    "metadata": _metadata(path),
                    "retrieval_method": "pageindex",
                }
            )
    results.sort(key=lambda item: (-item["score"], item["id"]))
    return results[:top_k]


def _poll_retrieval(client: Any, retrieval_id: str) -> dict[str, Any]:
    deadline = time.monotonic() + PAGEINDEX_TIMEOUT
    latest: dict[str, Any] = {}
    while time.monotonic() < deadline:
        response = client.get_retrieval(retrieval_id)
        if isinstance(response, dict):
            latest = response
            status = str(response.get("status", "")).lower()
            if status in {"completed", "complete", "success", "failed", "error"}:
                break
        time.sleep(1)
    return latest


def _texts(value: Any) -> list[str]:
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    if isinstance(value, list):
        output: list[str] = []
        for item in value:
            output.extend(_texts(item))
        return output
    if isinstance(value, dict):
        output: list[str] = []
        for key in ("content", "text", "snippet", "node_content", "retrieved_content"):
            if key in value:
                output.extend(_texts(value[key]))
        if output:
            return output
        for item in value.values():
            output.extend(_texts(item))
        return output
    return []


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Query PageIndex and return SearchResult-compatible records."""
    if top_k <= 0:
        return []
    if not _query_terms(query) & DOMAIN_TERMS:
        return []
    if not PAGEINDEX_API_KEY:
        return _local_search(query, top_k)

    from pageindex import PageIndexClient

    cache = _load_cache()
    client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
    results: list[dict] = []
    seen: set[str] = set()
    for source, entry in cache.items():
        if not isinstance(entry, dict) or not entry.get("doc_id"):
            continue
        try:
            submitted = client.submit_query(entry["doc_id"], query)
            retrieval_id = submitted.get("retrieval_id")
            if not retrieval_id:
                continue
            response = _poll_retrieval(client, retrieval_id)
            source_path = Path(entry.get("source_path", source))
            metadata = _metadata(source_path)
            for rank, content in enumerate(_texts(response), start=1):
                result_id = f"{entry['doc_id']}::{rank}"
                if result_id in seen:
                    continue
                seen.add(result_id)
                results.append(
                    {
                        "id": result_id,
                        "content": content,
                        "score": 1.0 / rank,
                        "metadata": metadata,
                        "retrieval_method": "pageindex",
                    }
                )
        except Exception:
            continue
    results.sort(key=lambda item: (-item["score"], item["id"]))
    return results[:top_k] or _local_search(query, top_k)


if __name__ == "__main__":
    upload_documents()
