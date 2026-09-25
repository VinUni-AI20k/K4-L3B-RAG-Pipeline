"""Task 7 — Reciprocal Rank Fusion for independent ranked result lists."""

from __future__ import annotations

from .contracts import validate_search_results


def rerank_rrf(
    ranked_lists: list[list[dict]],
    top_k: int = 5,
    k: int = 60,
) -> list[dict]:
    """Fuse rankings using ``sum(1 / (k + rank))`` (rank starts at one)."""
    if top_k <= 0 or not ranked_lists:
        return []
    if k <= 0:
        raise ValueError("k must be positive")

    scores: dict[str, float] = {}
    items: dict[str, dict] = {}
    for ranked_list in ranked_lists:
        seen_in_list: set[str] = set()
        for rank, item in enumerate(ranked_list, start=1):
            item_id = item.get("id")
            if not isinstance(item_id, str) or not item_id or item_id in seen_in_list:
                continue
            seen_in_list.add(item_id)
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank)
            # Preserve original content and metadata; only score/method change.
            items[item_id] = item

    ranked_ids = sorted(scores, key=lambda item_id: (-scores[item_id], item_id))[:top_k]
    results: list[dict] = []
    for item_id in ranked_ids:
        result = dict(items[item_id])
        result["metadata"] = dict(result["metadata"])
        result["metadata"].setdefault("url", None)
        result["score"] = scores[item_id]
        result["retrieval_method"] = "hybrid"
        results.append(result)
    validate_search_results(results, top_k=top_k, expected_method="hybrid")
    return results


if __name__ == "__main__":
    print("Run src.task7_reranking from the retrieval pipeline or pass ranked lists.")
