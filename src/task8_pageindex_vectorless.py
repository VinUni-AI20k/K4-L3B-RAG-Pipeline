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

from .contracts import validate_search_results


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CACHE_FILE = Path(__file__).parent.parent / "data" / "pageindex_cache.json"


def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    api_key = os.getenv("PAGEINDEX_API_KEY", PAGEINDEX_API_KEY)
    if not api_key:
        print("PAGEINDEX_API_KEY is not set in .env. Skipping upload.")
        return

    try:
        from pageindex import PageIndexClient

        client = PageIndexClient(api_key=api_key)
        doc_cache: dict[str, str] = {}
        if CACHE_FILE.exists():
            try:
                doc_cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            except Exception:
                doc_cache = {}

        md_files = list(STANDARDIZED_DIR.rglob("*.md"))
        print(f"Found {len(md_files)} markdown files to check for upload.")

        for file_path in md_files:
            rel_name = file_path.name
            if rel_name in doc_cache:
                continue

            try:
                res = client.submit_document(file_path=str(file_path))
                doc_id = res.get("doc_id") or res.get("id")
                if doc_id:
                    doc_cache[rel_name] = doc_id
                    print(f"Uploaded {rel_name} -> doc_id: {doc_id}")
            except Exception as upload_err:
                print(f"Failed to upload {rel_name}: {upload_err}")

        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(json.dumps(doc_cache, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Cached {len(doc_cache)} documents to {CACHE_FILE.name}")

    except Exception as err:
        print(f"Error during upload_documents: {err}")


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult."""
    if not query or not query.strip() or top_k <= 0:
        return []

    api_key = os.getenv("PAGEINDEX_API_KEY", PAGEINDEX_API_KEY)
    if not api_key:
        return []

    try:
        from pageindex import PageIndexClient

        client = PageIndexClient(api_key=api_key)

        doc_ids: list[str] = []
        if CACHE_FILE.exists():
            try:
                data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
                doc_ids = list(data.values())
            except Exception:
                doc_ids = []

        if not doc_ids:
            return []

        response = client.submit_query(query=query, doc_ids=doc_ids)
        raw_results = response.get("results", []) or response.get("nodes", [])

        results: list[dict] = []
        seen_ids: set[str] = set()

        for idx, item in enumerate(raw_results):
            item_id = str(item.get("id") or item.get("node_id") or f"pageindex-{idx}")
            if item_id in seen_ids:
                continue
            seen_ids.add(item_id)

            content = item.get("content") or item.get("text") or ""
            score = float(item.get("score") if item.get("score") is not None else (1.0 / (idx + 1)))

            metadata = item.get("metadata") or {}
            if not isinstance(metadata, dict):
                metadata = {}
            if "source" not in metadata:
                metadata["source"] = item.get("source") or "pageindex_document"
            if "title" not in metadata:
                metadata["title"] = item.get("title") or "PageIndex Doc"
            if "doc_type" not in metadata:
                metadata["doc_type"] = "legal"
            if "url" not in metadata:
                metadata["url"] = None
            if "chunk_index" not in metadata:
                metadata["chunk_index"] = idx

            results.append(
                {
                    "id": item_id,
                    "content": content,
                    "score": score,
                    "metadata": metadata,
                    "retrieval_method": "pageindex",
                }
            )
            if len(results) >= top_k:
                break

        results.sort(key=lambda x: x["score"], reverse=True)
        validate_search_results(results, top_k=top_k, expected_method="pageindex")
        return results

    except Exception as err:
        print(f"PageIndex search error (caught safely): {err}")
        return []


if __name__ == "__main__":
    upload_documents()
