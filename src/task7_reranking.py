"""
Task 7 — Reciprocal Rank Fusion.

RRF gộp nhiều bảng xếp hạng mà không cộng trực tiếp cosine score
với BM25 score.

Công thức:

    RRF(d) = sum(1 / (k + rank))

rank bắt đầu từ 1.

RRF score chỉ phản ánh thứ hạng, không dùng để quyết định fallback.
"""


def rerank_rrf(
    ranked_lists: list[list[dict]],
    top_k: int = 5,
    k: int = 60,
) -> list[dict]:
    """Fuse nhiều ranked lists và trả hybrid SearchResult."""

    if top_k <= 0:
        return []

    if k <= 0:
        raise ValueError("RRF parameter k must be greater than 0.")

    scores: dict[str, float] = {}
    items: dict[str, dict] = {}

    for ranked_list in ranked_lists:
        if not ranked_list:
            continue

        for rank, item in enumerate(ranked_list, start=1):
            item_id = item.get("id")

            if item_id is None:
                continue

            # RRF chỉ dùng rank, KHÔNG dùng score gốc.
            rrf_score = 1.0 / (k + rank)

            scores[item_id] = scores.get(item_id, 0.0) + rrf_score

            # Giữ object đầy đủ từ retrieval result.
            if item_id not in items:
                items[item_id] = item.copy()

    ranked_ids = sorted(
        scores,
        key=lambda item_id: scores[item_id],
        reverse=True,
    )

    results: list[dict] = []

    for item_id in ranked_ids[:top_k]:
        result = items[item_id].copy()

        # Score của output là RRF score.
        result["score"] = float(scores[item_id])
        result["retrieval_method"] = "hybrid"

        results.append(result)

    return results


if __name__ == "__main__":
    dense = [
        {"id": "A", "content": "A", "score": 0.95},
        {"id": "B", "content": "B", "score": 0.80},
        {"id": "C", "content": "C", "score": 0.70},
    ]

    bm25 = [
        {"id": "B", "content": "B", "score": 8.2},
        {"id": "A", "content": "A", "score": 7.5},
        {"id": "D", "content": "D", "score": 6.0},
    ]

    results = rerank_rrf(
        [dense, bm25],
        top_k=4,
    )

    for result in results:
        print(result)