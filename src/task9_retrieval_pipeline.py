"""
Task 9 — Retrieval pipeline hoàn chỉnh.

Luồng xử lý:
    1. Chạy semantic_search và lexical_search.
    2. Fuse hai danh sách bằng RRF đúng một lần.
    3. Lấy best cosine score gốc từ dense results.
    4. Nếu score dưới threshold, thử PageIndex fallback.
    5. Nếu fallback lỗi, trả hybrid results thay vì crash.

Không so sánh threshold với RRF score vì hai thang đo khác nhau.
"""

import math
import os

from .task5_semantic_search import semantic_search
from .task6_lexical_search import lexical_search
from .task7_reranking import rerank_rrf
from .task8_pageindex_vectorless import pageindex_search


def _configured_threshold() -> float:
    raw = os.getenv("SCORE_THRESHOLD", "").strip()
    if not raw:
        return 0.3
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError("SCORE_THRESHOLD must be numeric") from exc
    if not math.isfinite(value):
        raise ValueError("SCORE_THRESHOLD must be finite")
    return value


SCORE_THRESHOLD = _configured_threshold()
DEFAULT_TOP_K = 5


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    use_reranking: bool = True,
) -> list[dict]:
    """Trả về hybrid hoặc pageindex SearchResult."""
    if not isinstance(query, str):
        raise ValueError("query must be a string")
    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 0:
        raise ValueError("top_k must be a non-negative integer")
    if isinstance(score_threshold, bool) or not isinstance(score_threshold, (int, float)):
        raise ValueError("score_threshold must be numeric")
    if not math.isfinite(float(score_threshold)):
        raise ValueError("score_threshold must be finite")
    if not isinstance(use_reranking, bool):
        raise ValueError("use_reranking must be boolean")
    if top_k == 0 or not query.strip():
        return []

    candidate_k = top_k * 2
    dense = semantic_search(query, top_k=candidate_k)
    sparse = lexical_search(query, top_k=candidate_k)
    hybrid = rerank_rrf([dense, sparse], top_k=top_k) if use_reranking else dense[:top_k]

    # Only the original cosine similarity is calibrated against this threshold.
    best_dense_score = dense[0]["score"] if dense else 0.0
    if best_dense_score < float(score_threshold):
        try:
            fallback = pageindex_search(query, top_k=top_k)
            if fallback:
                return fallback
        except Exception:
            # PageIndex is optional and external. Preserve the local result.
            pass
    return hybrid[:top_k]


if __name__ == "__main__":
    for result in retrieve("test query", top_k=3):
        print(result)
