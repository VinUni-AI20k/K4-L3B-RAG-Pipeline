"""
Task 7 — Reciprocal Rank Fusion.

RRF gộp nhiều bảng xếp hạng mà không cộng trực tiếp cosine score với BM25
score. Công thức: RRF(d) = sum(1 / (k + rank)), rank bắt đầu từ 1.

Lưu ý: RRF score chỉ phản ánh thứ hạng, không dùng để quyết định fallback.
"""


def rerank_rrf(
    ranked_lists: list[list[dict]],
    top_k: int = 5,
    k: int = 60,
) -> list[dict]:
    """Fuse nhiều ranked lists và trả hybrid SearchResult."""
    if top_k <= 0 or not ranked_lists:
        return []
    if k < 0:
        raise ValueError("k must be non-negative")

    scores: dict[str, float] = {}
    items: dict[str, dict] = {}

    for ranked_list in ranked_lists:
        seen_in_list: set[str] = set()
        for rank, item in enumerate(ranked_list, start=1):
            item_id = item["id"]

            # Một ID chỉ được đóng góp điểm một lần trong mỗi danh sách.
            if item_id in seen_in_list:
                continue
            seen_in_list.add(item_id)

            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank)
            items.setdefault(item_id, item)

    ranked_ids = sorted(
        scores,
        key=lambda item_id: scores[item_id],
        reverse=True,
    )

    results = []
    for item_id in ranked_ids[:top_k]:
        result = dict(items[item_id])
        result["score"] = scores[item_id]
        result["retrieval_method"] = "hybrid"
        results.append(result)
    return results


if __name__ == "__main__":
    import json
    from pathlib import Path

    mock_path = Path(__file__).parent.parent / "data" / "task7_mock_input.json"
    mock = json.loads(mock_path.read_text(encoding="utf-8"))
    for result in rerank_rrf(
        mock["ranked_lists"],
        top_k=mock["top_k"],
        k=mock["k"],
    ):
        print(result["id"], result["score"], result["retrieval_method"])
