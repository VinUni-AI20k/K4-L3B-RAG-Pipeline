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
import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


load_dotenv()

logger = logging.getLogger(__name__)

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CACHE_FILE = Path(__file__).parent.parent / "data" / "pageindex_cache.json"
TIMEOUT_SECONDS = 10


def upload_documents() -> dict[str, str]:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    api_key = os.getenv("PAGEINDEX_API_KEY", PAGEINDEX_API_KEY)
    if not api_key:
        logger.warning("PAGEINDEX_API_KEY chưa được cấu hình. Bỏ qua upload.")
        return {}

    # Load cache nếu đã upload trước đó
    cache: dict[str, str] = {}
    if CACHE_FILE.exists():
        try:
            cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning("Không thể đọc cache PageIndex: %s", e)

    # Đọc các file JSON tài liệu chuẩn hóa
    json_files = sorted(STANDARDIZED_DIR.glob("*/*.json"))
    if not json_files:
        logger.warning("Không tìm thấy tài liệu chuẩn hóa trong %s", STANDARDIZED_DIR)
        return cache

    try:
        import pageindex  # type: ignore

        client = pageindex.PageIndex(api_key=api_key) if hasattr(pageindex, "PageIndex") else None
    except ImportError:
        logger.warning("Thư viện pageindex chưa được cài đặt.")
        return cache

    updated = False
    for path in json_files:
        doc_id = path.stem
        if doc_id in cache:
            continue

        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            content = data.get("content", "")
            title = data.get("metadata", {}).get("title", doc_id)
            if client and hasattr(client, "upload_document"):
                res = client.upload_document(title=title, content=content)
                remote_id = res.get("id") or res.get("doc_id") or doc_id
                cache[doc_id] = str(remote_id)
                updated = True
        except Exception as err:
            logger.warning("Lỗi khi upload tài liệu %s lên PageIndex: %s", doc_id, err)

    if updated:
        try:
            CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as err:
            logger.warning("Không thể lưu cache PageIndex: %s", err)

    return cache


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult."""
    if top_k <= 0 or not query.strip():
        return []

    api_key = os.getenv("PAGEINDEX_API_KEY", PAGEINDEX_API_KEY)
    if not api_key:
        logger.info("PAGEINDEX_API_KEY trống; bỏ qua PageIndex fallback.")
        return []

    try:
        # Nếu thư viện pageindex có sẵn, gọi qua client SDK
        try:
            import pageindex  # type: ignore

            if hasattr(pageindex, "PageIndex"):
                client = pageindex.PageIndex(api_key=api_key)
                if hasattr(client, "search"):
                    raw_results = client.search(query=query, top_k=top_k)
                    results = []
                    seen_ids = set()
                    for index, item in enumerate(raw_results):
                        item_id = str(item.get("id", f"pageindex-{index}"))
                        if item_id in seen_ids:
                            continue
                        seen_ids.add(item_id)
                        content = item.get("content", item.get("text", ""))
                        score = float(item.get("score", 1.0 - index * 0.05))
                        meta = dict(item.get("metadata", {}))
                        meta.setdefault("source", "pageindex")
                        meta.setdefault("title", item.get("title", "Tài liệu PageIndex"))
                        meta.setdefault("doc_type", "legal")
                        meta.setdefault("url", None)
                        meta.setdefault("chunk_index", index)
                        results.append({
                            "id": item_id,
                            "content": content,
                            "score": score,
                            "metadata": meta,
                            "retrieval_method": "pageindex",
                        })
                    results.sort(key=lambda x: x["score"], reverse=True)
                    return results[:top_k]
        except ImportError:
            pass

        # Nếu không có SDK hoặc không có method search, gọi qua REST API
        import requests

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        resp = requests.post(
            "https://api.pageindex.ai/v1/search",
            headers=headers,
            json={"query": query, "top_k": top_k},
            timeout=TIMEOUT_SECONDS,
        )
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("results", data.get("nodes", []))
            results = []
            seen_ids = set()
            for index, item in enumerate(items):
                item_id = str(item.get("id", f"pageindex-{index}"))
                if item_id in seen_ids:
                    continue
                seen_ids.add(item_id)
                content = item.get("content", item.get("text", ""))
                score = float(item.get("score", 1.0 - index * 0.05))
                meta = dict(item.get("metadata", {}))
                meta.setdefault("source", "pageindex")
                meta.setdefault("title", item.get("title", "Tài liệu PageIndex"))
                meta.setdefault("doc_type", "legal")
                meta.setdefault("url", None)
                meta.setdefault("chunk_index", index)
                results.append({
                    "id": item_id,
                    "content": content,
                    "score": score,
                    "metadata": meta,
                    "retrieval_method": "pageindex",
                })
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:top_k]
        else:
            raise RuntimeError(f"PageIndex API status {resp.status_code}: {resp.text}")

    except Exception as exc:
        logger.error("Lỗi tìm kiếm PageIndex: %s", exc)
        raise RuntimeError(f"PageIndex provider error: {exc}") from exc


if __name__ == "__main__":
    test_query = "Thông tin liên hệ tuyển sinh NEU"
    print(f"Testing pageindex_search: query='{test_query}'")
    try:
        res = pageindex_search(test_query, top_k=3)
        print(f"Result count: {len(res)}")
    except Exception as err:
        print(f"Caught expected/handled error: {err}")
