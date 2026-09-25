"""Task 9 — Hybrid retrieval, one RRF pass, and optional PageIndex fallback."""

from __future__ import annotations

import os

from .task5_semantic_search import semantic_search
from .task6_lexical_search import lexical_search
from .task7_reranking import rerank_rrf
from .task8_pageindex_vectorless import pageindex_search


_threshold_value = os.getenv("SCORE_THRESHOLD", "").strip()
SCORE_THRESHOLD = float(_threshold_value) if _threshold_value else 0.3
DEFAULT_TOP_K = 5


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    use_reranking: bool = True,
) -> list[dict]:
    """Return hybrid results, or PageIndex nodes when dense confidence is low."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")
    if top_k <= 0:
        return []

    dense: list[dict] = []
    sparse: list[dict] = []
    try:
        dense = semantic_search(query, top_k=top_k * 2)
    except Exception as error:
        # Sparse retrieval may still provide useful evidence if embeddings or
        # the vector store are temporarily unavailable.
        print(f"Dense retrieval unavailable: {error}")
    try:
        sparse = lexical_search(query, top_k=top_k * 2)
    except Exception as error:
        print(f"BM25 retrieval unavailable: {error}")

    if use_reranking:
        try:
            hybrid = rerank_rrf([dense, sparse], top_k=top_k)
        except Exception as error:
            print(f"RRF unavailable; using available ranked results: {error}")
            hybrid = (dense or sparse)[:top_k]
    else:
        hybrid = dense[:top_k] if dense else sparse[:top_k]

    # Dense results are sorted by the original cosine similarity. Never compare
    # the unrelated RRF or BM25 scale to this threshold.
    best_dense_score = float(dense[0]["score"]) if dense else 0.0
    if best_dense_score < score_threshold:
        try:
            fallback = pageindex_search(query, top_k=top_k)
            if fallback:
                return fallback[:top_k]
        except Exception as error:
            print(f"PageIndex fallback unavailable; returning hybrid results: {error}")

    return hybrid[:top_k]


if __name__ == "__main__":
    for result in retrieve("IELTS Writing band descriptors", top_k=3):
        print(result)
