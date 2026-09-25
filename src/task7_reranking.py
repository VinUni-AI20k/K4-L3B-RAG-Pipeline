"""
Task 7 — Reciprocal Rank Fusion.

RRF gộp nhiều bảng xếp hạng mà không cộng trực tiếp cosine score với BM25
score. Công thức: RRF(d) = sum(1 / (k + rank)), rank bắt đầu từ 1.

Lưu ý: RRF score chỉ phản ánh thứ hạng, không dùng để quyết định fallback.
Task 9 so threshold với cosine score gốc của dense, nên RRF phải trả item
mới (copy) và giữ nguyên các ranked list đầu vào.

Chạy:
    python -m src.task7_reranking
"""


def rerank_rrf(
    ranked_lists: list[list[dict]],
    top_k: int = 5,
    k: int = 60,
) -> list[dict]:
    """Fuse nhiều ranked lists và trả hybrid SearchResult."""
    if k <= 0:
        raise ValueError(f"k phải dương, nhận {k}")
    if top_k <= 0:
        return []

    scores: dict[str, float] = {}
    items: dict[str, dict] = {}

    for list_index, ranked_list in enumerate(ranked_lists):
        seen_in_list: set[str] = set()
        for rank, item in enumerate(ranked_list, 1):
            item_id = item["id"]
            # Trùng ID trong cùng một list là lỗi của module tạo list; báo lỗi
            # thay vì cộng điểm hai lần và che đi lỗi upstream.
            if item_id in seen_in_list:
                raise ValueError(
                    f"ID {item_id!r} xuất hiện nhiều lần trong ranked list #{list_index}"
                )
            seen_in_list.add(item_id)

            scores[item_id] = scores.get(item_id, 0.0) + 1 / (k + rank)
            # Giữ dữ liệu của lần xuất hiện đầu tiên (list đầu, thường là dense).
            items.setdefault(item_id, item)

    # sorted() ổn định: điểm bằng nhau thì giữ thứ tự xuất hiện đầu tiên.
    ranked_ids = sorted(scores, key=lambda item_id: scores[item_id], reverse=True)

    results: list[dict] = []
    for item_id in ranked_ids[:top_k]:
        result = dict(items[item_id])
        result["metadata"] = dict(result.get("metadata") or {})
        result["score"] = scores[item_id]
        result["retrieval_method"] = "hybrid"
        results.append(result)
    return results


if __name__ == "__main__":
    def _demo(item_id: str, score: float, method: str) -> dict:
        return {
            "id": item_id,
            "content": f"content of {item_id}",
            "score": score,
            "metadata": {"source": "demo.md", "title": "Demo"},
            "retrieval_method": method,
        }

    dense = [_demo("chunk-a", 0.82, "dense"), _demo("chunk-b", 0.79, "dense")]
    bm25 = [_demo("chunk-b", 11.4, "bm25"), _demo("chunk-c", 9.1, "bm25")]

    fused = rerank_rrf([dense, bm25], top_k=3)
    for item in fused:
        print(f"{item['id']}: RRF = {item['score']:.5f} ({item['retrieval_method']})")

    # chunk-b: rank 2 ở dense + rank 1 ở BM25 -> 1/62 + 1/61.
    assert fused[0]["id"] == "chunk-b"
    assert abs(fused[0]["score"] - (1 / 62 + 1 / 61)) < 1e-12
    # Input không bị sửa: dense vẫn giữ cosine score gốc.
    assert dense[1]["score"] == 0.79 and dense[1]["retrieval_method"] == "dense"
    print("OK: chunk có mặt ở cả hai list đứng đầu, input giữ nguyên.")
