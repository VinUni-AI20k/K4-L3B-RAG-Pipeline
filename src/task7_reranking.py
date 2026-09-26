"""
Task 7 — Reciprocal Rank Fusion.

RRF gộp nhiều bảng xếp hạng mà không cộng trực tiếp cosine score với BM25
score. Công thức: RRF(d) = sum(1 / (k + rank)), rank bắt đầu từ 1.

Lưu ý: RRF score chỉ phản ánh thứ hạng, không dùng để quyết định fallback.

-> Dùng Jina hoặc self host hoặc bất cứ công cụ nào bạn quen
"""

from .contracts import validate_search_results


def rerank_rrf(
    ranked_lists: list[list[dict]],
    top_k: int = 5,
    k: int = 60,
) -> list[dict]:
    """Fuse nhiều ranked lists và trả hybrid SearchResult."""
    if not isinstance(ranked_lists, list):
        raise ValueError("ranked_lists must be a list")
    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 0:
        raise ValueError("top_k must be a non-negative integer")
    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise ValueError("k must be a positive integer")
    if top_k == 0:
        return []

    scores: dict[str, float] = {}
    items: dict[str, dict] = {}
    first_seen: dict[str, int] = {}
    order = 0
    for ranked_list in ranked_lists:
        if not isinstance(ranked_list, list):
            raise ValueError("each ranked list must be a list")
        # A provider occasionally returning a duplicate must not receive two
        # votes from the same ranking.
        seen_in_list: set[str] = set()
        for rank, item in enumerate(ranked_list, start=1):
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                raise ValueError("ranked items must be SearchResult dictionaries")
            item_id = item["id"]
            if item_id in seen_in_list:
                continue
            seen_in_list.add(item_id)
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank)
            if item_id not in items:
                items[item_id] = item
                first_seen[item_id] = order
                order += 1

    ranked_ids = sorted(scores, key=lambda item_id: (-scores[item_id], first_seen[item_id]))
    results = []
    for item_id in ranked_ids[:top_k]:
        result = {**items[item_id], "score": scores[item_id], "retrieval_method": "hybrid"}
        result["metadata"] = dict(items[item_id]["metadata"])
        results.append(result)
    validate_search_results(results, top_k=top_k, expected_method="hybrid")
    return results


if __name__ == "__main__":
    print("RRF module ready. Run: pytest tests/test_contracts.py -q")
