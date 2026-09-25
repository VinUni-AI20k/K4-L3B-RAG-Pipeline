"""
Task 8 — PageIndex vectorless fallback.

Hướng dẫn:
    1. Đọc PAGEINDEX_API_KEY từ .env.
    2. Upload tài liệu ở định dạng PageIndex hỗ trợ.
    3. Cache document IDs để không upload lại.
    4. Parse kết quả thành SearchResult có method pageindex.

PageIndex là dịch vụ ngoài: cần timeout và xử lý lỗi để pipeline không crash.
"""

import os
import json
import tempfile
import time
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CACHE_PATH = Path(__file__).parent.parent / ".pageindex_cache.json"


def _client():
    if not PAGEINDEX_API_KEY:
        raise RuntimeError("PAGEINDEX_API_KEY is not configured")
    from pageindex import PageIndexClient

    return PageIndexClient(api_key=PAGEINDEX_API_KEY)


def _load_cache() -> dict:
    if not CACHE_PATH.exists():
        return {}
    try:
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_cache(cache: dict) -> None:
    CACHE_PATH.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _markdown_as_pdf(path: Path, target: Path) -> None:
    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    unicode_font = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / "arial.ttf"
    if unicode_font.exists():
        pdf.add_font("ArialUnicode", fname=str(unicode_font))
        pdf.set_font("ArialUnicode", size=10)
        unicode_output = True
    else:
        pdf.set_font("Helvetica", size=10)
        unicode_output = False
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line if unicode_output else line.encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 5, text or " ")
    pdf.output(str(target))


def _response_items(response) -> list[dict]:
    if isinstance(response, list):
        return [item for item in response if isinstance(item, dict)]
    if not isinstance(response, dict):
        return []
    for key in ("results", "nodes", "retrieved_nodes", "items", "data"):
        value = response.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict):
            nested = _response_items(value)
            if nested:
                return nested
    return [response] if any(key in response for key in ("text", "content", "summary")) else []


def _item_text(item: dict) -> str:
    for key in ("content", "text", "summary", "node_text", "snippet"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    client = _client()
    cache = _load_cache()
    changed = False
    with tempfile.TemporaryDirectory() as temporary_dir:
        for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
            source = path.relative_to(STANDARDIZED_DIR).as_posix()
            fingerprint = f"{path.stat().st_size}:{path.stat().st_mtime_ns}"
            cached = cache.get(source, {})
            if cached.get("fingerprint") == fingerprint and cached.get("doc_id"):
                continue
            pdf_path = Path(temporary_dir) / f"{path.stem}.pdf"
            _markdown_as_pdf(path, pdf_path)
            response = client.submit_document(str(pdf_path))
            document_id = response.get("doc_id")
            if not document_id:
                raise RuntimeError(f"PageIndex upload returned no doc_id for {source}")
            cache[source] = {"doc_id": document_id, "fingerprint": fingerprint}
            changed = True
    if changed:
        _write_cache(cache)


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult."""
    if not query.strip() or top_k <= 0:
        return []
    client = _client()
    cache = _load_cache()
    if not cache:
        upload_documents()
        cache = _load_cache()

    results = []
    for source, entry in sorted(cache.items()):
        response = client.submit_query(entry["doc_id"], query)
        retrieval_id = response.get("retrieval_id")
        if not retrieval_id:
            continue
        retrieval = client.get_retrieval(retrieval_id)
        if retrieval.get("status") in {"pending", "processing", "queued"}:
            for _ in range(10):
                time.sleep(1)
                retrieval = client.get_retrieval(retrieval_id)
                if retrieval.get("status") not in {"pending", "processing", "queued"}:
                    break
        for rank, item in enumerate(_response_items(retrieval), 1):
            content = _item_text(item)
            if not content:
                continue
            score = item.get("score", item.get("relevance_score"))
            try:
                score = float(score)
            except (TypeError, ValueError):
                score = 1.0 / rank
            results.append({
                "id": f"{source}::pageindex-{rank}",
                "content": content,
                "score": score,
                "metadata": {
                    "source": source,
                    "title": Path(source).stem,
                    "doc_type": Path(source).parts[0],
                    "url": None,
                    "chunk_index": rank - 1,
                },
                "retrieval_method": "pageindex",
            })
    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    upload_documents()
