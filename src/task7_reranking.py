"""Task 7 — Gộp các bảng xếp hạng bằng Reciprocal Rank Fusion (RRF)."""


def rerank_rrf(
    ranked_lists: list[list[dict]],
    top_k: int = 5,
    k: int = 60,
) -> list[dict]:
    """Trả về kết quả hybrid, không lặp ID, theo điểm RRF giảm dần."""
    if top_k <= 0:
        return []

    scores: dict[str, float] = {}
    items: dict[str, dict] = {}

    for ranked_list in ranked_lists:
        seen = set()

        for rank, item in enumerate(ranked_list, start=1):
            item_id = item["id"]
            if item_id in seen:
                continue

            seen.add(item_id)
            scores[item_id] = scores.get(item_id, 0.0) + 1 / (k + rank)
            items.setdefault(item_id, item)

    ranked_ids = sorted(
        scores,
        key=lambda item_id: (-scores[item_id], item_id),
    )

    return [
        {
            **items[item_id],
            "score": scores[item_id],
            "retrieval_method": "hybrid",
        }
        for item_id in ranked_ids[:top_k]
    ]