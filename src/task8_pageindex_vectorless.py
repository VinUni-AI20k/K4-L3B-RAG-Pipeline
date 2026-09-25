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
CACHE_FILE = Path(__file__).parent.parent / "data" / "pageindex_doc_ids.json"


def _load_doc_id_cache() -> dict[str, str]:
    """Đọc cache mapping source_path -> document_id."""
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return {}


def _save_doc_id_cache(cache: dict[str, str]) -> None:
    """Lưu cache mapping source_path -> document_id."""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    if not PAGEINDEX_API_KEY:
        print("PAGEINDEX_API_KEY not set. Skipping upload.")
        return

    import pageindex  # type: ignore

    client = pageindex.Client(api_key=PAGEINDEX_API_KEY)
    cache = _load_doc_id_cache()
    changed = False

    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        key = path.relative_to(STANDARDIZED_DIR).as_posix()
        if key in cache:
            print(f"Already uploaded, skipping: {key}")
            continue
        print(f"Uploading: {key}")
        try:
            content = path.read_text(encoding="utf-8")
            response = client.documents.create(
                name=path.stem,
                content=content,
                content_type="text/markdown",
            )
            # Kiểm tra tên field từ response thật của SDK
            doc_id = response.id if hasattr(response, "id") else response["id"]
            cache[key] = doc_id
            changed = True
            print(f"Uploaded: {key} → {doc_id}")
        except Exception as error:
            print(f"Upload failed for {key}: {error}")

    if changed:
        _save_doc_id_cache(cache)


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult."""
    if not PAGEINDEX_API_KEY:
        return []

    import pageindex  # type: ignore

    cache = _load_doc_id_cache()
    if not cache:
        print("No uploaded documents found. Run upload_documents() first.")
        return []

    try:
        client = pageindex.Client(api_key=PAGEINDEX_API_KEY)
        doc_ids = list(cache.values())

        response = client.documents.query(
            query=query,
            document_ids=doc_ids,
            top_k=top_k,
        )

        results = []
        nodes = response.nodes if hasattr(response, "nodes") else response.get("nodes", [])
        for rank, node in enumerate(nodes[:top_k], 1):
            # Gán score giảm dần theo rank nếu API không trả score
            score = getattr(node, "score", None) or node.get("score", None)
            if score is None:
                score = 1.0 / rank

            content = getattr(node, "text", None) or node.get("text", "") or node.get("content", "")
            node_id = getattr(node, "id", None) or node.get("id", f"pageindex-{rank}")
            source = getattr(node, "document_name", None) or node.get("document_name", "pageindex")

            results.append({
                "id": str(node_id),
                "content": content,
                "score": float(score),
                "metadata": {
                    "source": source,
                    "title": source,
                    "doc_type": "legal",
                    "url": None,
                    "chunk_index": rank - 1,
                },
                "retrieval_method": "pageindex",
            })

        # Đảm bảo sort giảm dần theo score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    except Exception as error:
        print(f"PageIndex search failed: {error}")
        return []


if __name__ == "__main__":
    upload_documents()
