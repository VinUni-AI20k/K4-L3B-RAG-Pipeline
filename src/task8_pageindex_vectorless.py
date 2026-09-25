"""
Task 8 — PageIndex vectorless fallback.

Hướng dẫn:
    1. Đọc PAGEINDEX_API_KEY từ .env.
    2. Upload tài liệu ở định dạng PageIndex hỗ trợ.
    3. Cache document IDs để không upload lại.
    4. Parse kết quả thành SearchResult có method pageindex.

PageIndex là dịch vụ ngoài: cần timeout và xử lý lỗi để pipeline không crash.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CACHE_FILE = Path(__file__).parent.parent / "pageindex_doc_ids.json"


def _load_cache() -> dict[str, str]:
    """Đọc mapping source -> document_id từ cache file."""
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_cache(mapping: dict[str, str]) -> None:
    CACHE_FILE.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")


def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    if not PAGEINDEX_API_KEY:
        print("PAGEINDEX_API_KEY không được cấu hình — bỏ qua upload.")
        return

    try:
        from pageindex import PageIndex  # type: ignore

        client = PageIndex(api_key=PAGEINDEX_API_KEY)
        cache = _load_cache()

        md_files = list(STANDARDIZED_DIR.rglob("*.md"))
        for md_path in md_files:
            source_key = str(md_path.relative_to(STANDARDIZED_DIR))
            if source_key in cache:
                continue
            content = md_path.read_text(encoding="utf-8")
            response = client.documents.create(content=content, name=md_path.stem)
            doc_id = response.id if hasattr(response, "id") else str(response)
            cache[source_key] = doc_id
            print(f"Uploaded: {source_key} -> {doc_id}")

        _save_cache(cache)
    except Exception as exc:
        print(f"PageIndex upload lỗi (bỏ qua): {exc}")


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult. Trả [] nếu không có API key hoặc lỗi."""
    if not PAGEINDEX_API_KEY:
        return []

    try:
        from pageindex import PageIndex  # type: ignore

        client = PageIndex(api_key=PAGEINDEX_API_KEY)
        cache = _load_cache()
        doc_ids = list(cache.values())
        if not doc_ids:
            return []

        response = client.documents.query(query=query, document_ids=doc_ids, top_k=top_k)
        nodes = getattr(response, "nodes", None) or getattr(response, "results", [])

        results = []
        for rank, node in enumerate(nodes[:top_k], start=1):
            content = getattr(node, "content", "") or getattr(node, "text", "")
            node_id = getattr(node, "id", f"pageindex-{rank}")
            score_raw = getattr(node, "score", None)
            score = float(score_raw) if score_raw is not None else 1.0 / rank
            metadata_raw = getattr(node, "metadata", {}) or {}
            results.append({
                "id": str(node_id),
                "content": str(content),
                "score": score,
                "metadata": {
                    "source": metadata_raw.get("source", "pageindex"),
                    "title": metadata_raw.get("name", metadata_raw.get("title", "PageIndex Result")),
                    "doc_type": metadata_raw.get("doc_type", "news"),
                    "url": metadata_raw.get("url", None),
                    "chunk_index": rank - 1,
                },
                "retrieval_method": "pageindex",
            })

        return sorted(results, key=lambda x: x["score"], reverse=True)

    except Exception as exc:
        print(f"PageIndex search lỗi (fallback về hybrid): {exc}")
        return []


if __name__ == "__main__":
    upload_documents()
