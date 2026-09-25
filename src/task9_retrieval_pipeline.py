"""
Task 9 — Retrieval Pipeline Hoàn Chỉnh.

Kết hợp Semantic Search + Lexical Search (BM25) + Reranking + PageIndex Fallback.

Quy trình:
    1. Chạy semantic_search và lexical_search
    2. Kiểm tra điểm Cosine Similarity gốc từ dense_results so với score_threshold
    3. Nếu best_score < score_threshold → Kích hoạt PageIndex Vectorless Fallback
    4. Nếu đạt ngưỡng → Gộp thứ hạng bằng RRF và Rerank kết quả
    5. Trả về top_k kết quả hoàn chỉnh
"""

import sys
from .task5_semantic_search import semantic_search
from .task6_lexical_search import lexical_search
from .task7_reranking import rerank, rerank_rrf
from .task8_pageindex_vectorless import pageindex_search

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# =============================================================================
# CONFIGURATION
# =============================================================================

# Ngưỡng cosine similarity gốc để kích hoạt fallback (theo hướng dẫn Lab Guide)
SCORE_THRESHOLD = 0.48
DEFAULT_TOP_K = 5
RERANK_METHOD = "rrf"


def retrieve_with_debug(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    use_reranking: bool = True,
) -> tuple[list[dict], dict]:
    """
    Retrieval pipeline hoàn chỉnh trả về kết quả và chi tiết từng bước debug.
    """
    if not query or not query.strip():
        return [], {}

    # 1. Chạy song song Dense Search và Sparse Search
    dense_results = semantic_search(query, top_k=top_k)
    sparse_results = lexical_search(query, top_k=top_k)

    # 2. Kiểm tra điều kiện Fallback dựa trên điểm Cosine Similarity gốc
    best_dense_score = dense_results[0]["score"] if dense_results else 0.0
    fallback_triggered = best_dense_score < score_threshold
    fallback_method = "none"
    final_results = []

    if fallback_triggered:
        try:
            fallback_results = pageindex_search(query, top_k=top_k)
            if fallback_results:
                fallback_method = "pageindex"
                final_results = fallback_results[:top_k]
        except Exception:
            pass

    # 3. Nếu không kích hoạt fallback hoặc fallback rỗng, gộp bằng RRF
    if not final_results:
        if use_reranking:
            final_results = rerank_rrf([dense_results, sparse_results], top_k=top_k)
        else:
            final_results = dense_results[:top_k]

    debug_info = {
        "query": query,
        "dense_results": dense_results,
        "sparse_results": sparse_results,
        "best_dense_score": best_dense_score,
        "score_threshold": score_threshold,
        "fallback_triggered": fallback_triggered,
        "fallback_method": fallback_method,
        "fusion_results": final_results,
    }

    return final_results, debug_info


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    use_reranking: bool = True,
) -> list[dict]:
    """
    Retrieval pipeline hoàn chỉnh với logic fallback thông minh.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả cuối cùng cần lấy
        score_threshold: Ngưỡng điểm cosine similarity gốc tối thiểu của semantic search
        use_reranking: Có áp dụng reranking hay không (mặc định dùng RRF)

    Returns:
        List of SearchResult dictionaries tuân thủ schema hợp đồng.
    """
    results, _ = retrieve_with_debug(
        query,
        top_k=top_k,
        score_threshold=score_threshold,
        use_reranking=use_reranking,
    )
    return results


if __name__ == "__main__":
    test_queries = [
        "Chính sách đổi trả và hoàn tiền trên Shopee?",
        "Các phương thức thanh toán được hỗ trợ?",
        "xyzabc123nonsensequerynotexist",  # Test fallback trigger
    ]

    for q in test_queries:
        print(f"\nQuery: {q}")
        print("-" * 60)
        results = retrieve(q, top_k=3)
        for i, r in enumerate(results, 1):
            print(f"  {i}. [{r['score']:.4f}] [{r['source']}] {r['content'][:70]}...")
