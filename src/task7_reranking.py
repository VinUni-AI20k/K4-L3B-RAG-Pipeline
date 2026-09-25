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
    """Fuse các danh sách đã xếp hạng, không thay đổi dữ liệu đầu vào.

    Mỗi ID chỉ đóng góp ở lần xuất hiện đầu trong mỗi danh sách; rank là
    vị trí gốc, bắt đầu từ 1. Giữ nội dung/metadata của lần gặp ID đầu tiên.
    Khi bằng điểm, ưu tiên ID gặp trước. ``k`` phải không âm;
    ``top_k <= 0`` trả danh sách rỗng.
    """
    if k < 0:
        raise ValueError("k must be non-negative")
    if top_k <= 0:
        return []

    scores: dict[str, float] = {}
    items: dict[str, dict] = {}
    for ranked_list in ranked_lists:
        seen: set[str] = set()
        for rank, item in enumerate(ranked_list, start=1):
            item_id = item["id"]
            if item_id in seen:
                continue
            seen.add(item_id)
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank)
            items.setdefault(item_id, item)

    ranked_ids = sorted(scores, key=scores.__getitem__, reverse=True)
    return [
        {**items[item_id], "score": scores[item_id], "retrieval_method": "hybrid"}
        for item_id in ranked_ids[:top_k]
    ]


if __name__ == "__main__":
    print("Run: python -m pytest tests/test_rrf.py -q")
