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
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from pathlib import Path
from typing import Any, Callable

from dotenv import load_dotenv


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
PROJECT_DIR = Path(__file__).parent.parent
LEGAL_DIR = PROJECT_DIR / "data" / "landing" / "legal"
CACHE_PATH = PROJECT_DIR / "data" / "pageindex_cache.json"

API_CALL_TIMEOUT = 30.0
RETRIEVAL_TIMEOUT = 30.0
POLL_INTERVAL = 1.0
SUPPORTED_SUFFIXES = {".pdf", ".docx"}


def _load_cache() -> dict[str, str]:
    """Đọc mapping source -> doc_id; cache lỗi được xem như cache rỗng."""
    if not CACHE_PATH.exists():
        return {}
    try:
        raw = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(raw, dict):
        return {}
    return {
        str(source): str(doc_id)
        for source, doc_id in raw.items()
        if source and doc_id
    }


def _save_cache(cache: dict[str, str]) -> None:
    """Ghi cache sau mỗi lần upload thành công để có thể chạy tiếp."""
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _call_with_timeout(
    function: Callable[..., Any],
    *args: Any,
    timeout: float = API_CALL_TIMEOUT,
) -> Any:
    """Giới hạn thời gian chờ một lời gọi SDK PageIndex."""
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(function, *args)
    try:
        return future.result(timeout=timeout)
    except FutureTimeoutError as error:
        future.cancel()
        raise TimeoutError(
            f"PageIndex did not respond within {timeout:.0f} seconds"
        ) from error
    finally:
        executor.shutdown(wait=False, cancel_futures=True)


def _legal_files() -> list[Path]:
    """Liệt kê các tài liệu pháp lý mà PageIndex cloud có thể nhận."""
    if not LEGAL_DIR.exists():
        return []
    return [
        path
        for path in sorted(LEGAL_DIR.iterdir())
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    ]


def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    if not PAGEINDEX_API_KEY:
        return

    try:
        from pageindex import PageIndexClient
    except ImportError as error:
        print(f"PageIndex SDK is unavailable: {error}")
        return

    client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
    cache = _load_cache()

    for path in _legal_files():
        source = path.name
        if source in cache:
            continue
        try:
            response = _call_with_timeout(client.submit_document, str(path))
            doc_id = response.get("doc_id") if isinstance(response, dict) else None
            if not doc_id:
                raise ValueError("PageIndex response does not contain doc_id")
            cache[source] = str(doc_id)
            _save_cache(cache)
        except Exception as error:
            # Một tài liệu lỗi không được làm hỏng các tài liệu còn lại.
            print(f"PageIndex upload failed for {source}: {error}")


def _wait_for_retrieval(client: Any, retrieval_id: str) -> dict:
    """Poll retrieval cho đến khi hoàn tất hoặc hết thời gian."""
    deadline = time.monotonic() + RETRIEVAL_TIMEOUT

    while time.monotonic() < deadline:
        remaining = deadline - time.monotonic()
        response = _call_with_timeout(
            client.get_retrieval,
            retrieval_id,
            timeout=min(API_CALL_TIMEOUT, max(remaining, 0.1)),
        )
        if not isinstance(response, dict):
            raise ValueError("PageIndex retrieval response must be a dict")

        status = response.get("status")
        if status == "completed":
            return response
        if status == "failed":
            raise RuntimeError(f"PageIndex retrieval failed: {retrieval_id}")

        time.sleep(min(POLL_INTERVAL, max(remaining, 0.0)))

    raise TimeoutError(
        f"PageIndex retrieval exceeded {RETRIEVAL_TIMEOUT:.0f} seconds"
    )


def _parse_retrieval(response: dict, source: str, doc_id: str) -> list[dict]:
    """Đổi retrieved_nodes của PageIndex thành SearchResult chuẩn."""
    results = []
    nodes = response.get("retrieved_nodes") or []

    for node in nodes:
        if not isinstance(node, dict):
            continue
        node_id = str(node.get("node_id") or len(results))
        title = str(node.get("title") or Path(source).stem)

        for content_item in node.get("relevant_contents") or []:
            if not isinstance(content_item, dict):
                continue
            content = (
                content_item.get("relevant_content")
                or content_item.get("content")
                or content_item.get("text")
                or ""
            )
            if not isinstance(content, str) or not content.strip():
                continue

            rank = len(results) + 1
            page_index = content_item.get("page_index")
            raw_score = content_item.get("score", node.get("score"))
            score = (
                float(raw_score)
                if isinstance(raw_score, (int, float))
                and not isinstance(raw_score, bool)
                else 1.0 / rank
            )
            results.append(
                {
                    "id": (
                        f"pageindex::{doc_id}::{node_id}::"
                        f"{page_index}::{rank}"
                    ),
                    "content": content.strip(),
                    "score": score,
                    "metadata": {
                        "source": source,
                        "title": title,
                        "doc_type": "legal",
                        "url": None,
                        "chunk_index": rank - 1,
                    },
                    "retrieval_method": "pageindex",
                }
            )
    return results


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult."""
    if not PAGEINDEX_API_KEY or top_k <= 0 or not query.strip():
        return []

    try:
        from pageindex import PageIndexClient

        # Upload lazy: chỉ chạy khi dense score yêu cầu fallback.
        upload_documents()
        cache = _load_cache()
        if not cache:
            return []

        client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
        results = []

        for source, doc_id in cache.items():
            try:
                ready = _call_with_timeout(client.is_retrieval_ready, doc_id)
                if not ready:
                    continue

                submission = _call_with_timeout(
                    client.submit_query,
                    doc_id,
                    query,
                )
                retrieval_id = (
                    submission.get("retrieval_id")
                    if isinstance(submission, dict)
                    else None
                )
                if not retrieval_id:
                    continue

                response = _wait_for_retrieval(client, str(retrieval_id))
                results.extend(_parse_retrieval(response, source, doc_id))
            except Exception as error:
                print(f"PageIndex search failed for {source}: {error}")

        results.sort(key=lambda item: item["score"], reverse=True)
        unique_results = []
        seen_ids: set[str] = set()
        for result in results:
            if result["id"] in seen_ids:
                continue
            seen_ids.add(result["id"])
            unique_results.append(result)
        return unique_results[:top_k]
    except Exception as error:
        print(f"pageindex_search failed: {error}")
        return []


if __name__ == "__main__":
    upload_documents()
