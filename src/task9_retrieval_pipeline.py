"""Task 9 — Kết hợp dense, BM25, RRF và xử lý fallback an toàn."""

from .task5_semantic_search import semantic_search
from .task6_lexical_search import lexical_search
from .task7_reranking import rerank_rrf
from .task8_pageindex_vectorless import pageindex_search

SCORE_THRESHOLD = 0.3
DEFAULT_TOP_K = 5


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    use_reranking: bool = True,
) -> list[dict]:
    if not query.strip() or top_k <= 0:
        return []

    dense = semantic_search(query, top_k=top_k * 2)

    if use_reranking:
        sparse = lexical_search(query, top_k=top_k * 2)
        results = rerank_rrf([dense, sparse], top_k=top_k)
    else:
        results = dense[:top_k]

    # So với điểm cosine của dense, không so với điểm RRF.
    best_dense_score = dense[0]["score"] if dense else 0.0
    if best_dense_score < score_threshold:
        try:
            fallback = pageindex_search(query, top_k=top_k)
            if fallback:
                return fallback[:top_k]
        except Exception:
            pass

    return results[:top_k]