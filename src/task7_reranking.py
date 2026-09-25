"""
Task 7 — Reciprocal Rank Fusion.

RRF gộp nhiều bảng xếp hạng mà không cộng trực tiếp cosine score với BM25
score. Công thức: RRF(d) = sum(1 / (k + rank)), rank bắt đầu từ 1.

Lưu ý: RRF score chỉ phản ánh thứ hạng, không dùng để quyết định fallback.
"""

from .contracts import validate_search_results


def rerank_rrf(
    ranked_lists: list[list[dict]],
    top_k: int = 5,
    k: int = 60,
) -> list[dict]:
    """Fuse nhiều ranked lists và trả hybrid SearchResult theo RRF."""
    if not ranked_lists or top_k <= 0:
        return []

    scores: dict[str, float] = {}
    items: dict[str, dict] = {}

    for ranked_list in ranked_lists:
        if not ranked_list:
            continue
        for rank, item in enumerate(ranked_list, start=1):
            item_id = str(item["id"])
            rrf_score = 1.0 / (k + rank)
            scores[item_id] = scores.get(item_id, 0.0) + rrf_score
            if item_id not in items:
                items[item_id] = item

    if not scores:
        return []

    ranked_ids = sorted(scores.keys(), key=lambda doc_id: scores[doc_id], reverse=True)

    results: list[dict] = []
    for item_id in ranked_ids[:top_k]:
        result = dict(items[item_id])
        result["score"] = float(scores[item_id])
        result["retrieval_method"] = "hybrid"
        results.append(result)

    validate_search_results(results, top_k=top_k, expected_method="hybrid")
    return results


if __name__ == "__main__":
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    from .task5_semantic_search import semantic_search
    from .task6_lexical_search import lexical_search

    query = "học bổng khuyến khích học tập"
    dense_res = semantic_search(query, top_k=5)
    sparse_res = lexical_search(query, top_k=5)

    fused = rerank_rrf([dense_res, sparse_res], top_k=5)
    print(f"RRF Hybrid search results for: '{query}'")
    for r in fused:
        print(f"[{r['score']:.5f}] {r['id']} - {r['metadata']['title']}")
