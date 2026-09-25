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
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"


import json

CACHE_FILE = Path(__file__).parent.parent / "data" / "pageindex_cache.json"


def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    if not PAGEINDEX_API_KEY:
        print("PAGEINDEX_API_KEY không được thiết lập trong .env. Bỏ qua upload.")
        return

    try:
        from pageindex import PageIndexClient
        client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
    except Exception as e:
        print(f"Không thể khởi tạo PageIndexClient: {e}")
        return

    cache: dict[str, str] = {}
    if CACHE_FILE.exists():
        try:
            cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            cache = {}

    legal_dir = Path(__file__).parent.parent / "data" / "landing" / "legal"
    if not legal_dir.exists():
        return

    for file_path in legal_dir.glob("*.pdf"):
        if file_path.name in cache:
            continue
        try:
            print(f"Đang upload {file_path.name} lên PageIndex...")
            res = client.submit_document(file_path=str(file_path))
            if "doc_id" in res:
                cache[file_path.name] = res["doc_id"]
                print(f"Đã upload {file_path.name} -> doc_id: {res['doc_id']}")
        except Exception as e:
            print(f"Lỗi khi upload {file_path.name}: {e}")

    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult."""
    if not query.strip():
        return []

    if not PAGEINDEX_API_KEY:
        return []

    try:
        from pageindex import PageIndexClient
        client = PageIndexClient(api_key=PAGEINDEX_API_KEY)

        if not CACHE_FILE.exists():
            return []

        cache: dict[str, str] = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        if not cache:
            return []

        results: list[dict] = []
        rank = 0
        for filename, doc_id in cache.items():
            if len(results) >= top_k:
                break
            try:
                res = client.submit_query(doc_id=doc_id, query=query)
                answer_text = res.get("answer") or res.get("response") or res.get("content")
                if answer_text:
                    rank += 1
                    results.append({
                        "id": f"pageindex::{doc_id}::{rank}",
                        "content": str(answer_text),
                        "score": float(max(0.1, 1.0 - rank * 0.1)),
                        "metadata": {
                            "source": filename,
                            "title": filename.replace(".pdf", ""),
                            "doc_type": "legal",
                            "url": None,
                            "chunk_index": rank - 1,
                        },
                        "retrieval_method": "pageindex",
                    })
            except Exception:
                continue

        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:top_k]
    except Exception:
        return []


if __name__ == "__main__":
    upload_documents()
