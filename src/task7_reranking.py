"""
Task 7 — Reciprocal Rank Fusion (RRF).

RRF gộp nhiều bảng xếp hạng (Dense + BM25) mà không cộng trực tiếp điểm số khác thang đo.
Công thức chuẩn: RRF(d) = sum(1 / (k + rank)), trong đó rank bắt đầu từ 1.
Kết quả trả về danh sách SearchResult với retrieval_method="hybrid", sắp xếp giảm dần theo điểm RRF.
"""


def rerank_rrf(
    ranked_lists: list[list[dict]],
    top_k: int = 5,
    k: int = 60,
) -> list[dict]:
    """Fuse nhiều ranked lists và trả hybrid SearchResult theo RRF."""
    if top_k <= 0 or not ranked_lists:
        return []

    scores: dict[str, float] = {}
    items: dict[str, dict] = {}

    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, start=1):
            item_id = item["id"]
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank)
            if item_id not in items:
                items[item_id] = item

    # Sắp xếp các chunk theo điểm RRF giảm dần
    ranked_ids = sorted(scores.keys(), key=lambda item_id: scores[item_id], reverse=True)

    results = []
    for item_id in ranked_ids[:top_k]:
        res = dict(items[item_id])
        res["score"] = float(scores[item_id])
        res["retrieval_method"] = "hybrid"
        results.append(res)

    return results


if __name__ == "__main__":
    sample_dense = [
        {"id": "doc1", "content": "Text 1", "score": 0.9, "metadata": {"source": "a", "title": "A", "doc_type": "legal", "url": None, "chunk_index": 0}, "retrieval_method": "dense"},
        {"id": "doc2", "content": "Text 2", "score": 0.8, "metadata": {"source": "b", "title": "B", "doc_type": "legal", "url": None, "chunk_index": 1}, "retrieval_method": "dense"},
    ]
    sample_bm25 = [
        {"id": "doc2", "content": "Text 2", "score": 5.0, "metadata": {"source": "b", "title": "B", "doc_type": "legal", "url": None, "chunk_index": 1}, "retrieval_method": "bm25"},
        {"id": "doc3", "content": "Text 3", "score": 3.0, "metadata": {"source": "c", "title": "C", "doc_type": "news", "url": None, "chunk_index": 2}, "retrieval_method": "bm25"},
    ]
    fused = rerank_rrf([sample_dense, sample_bm25], top_k=2, k=60)
    print("Fused RRF results:")
    for r in fused:
        print(f"  {r['id']}: score={r['score']:.6f} method={r['retrieval_method']}")
