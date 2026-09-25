"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""


CORPUS: list[dict] = []


def build_bm25_index(corpus: list[dict]):
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    from rank_bm25 import BM25Okapi

    tokenized = [item["content"].lower().split() for item in corpus]
    bm25 = BM25Okapi(tokenized)
    # Với corpus nhỏ (ví dụ 2 documents trong unit test), idf(t) có thể bằng 0.
    # Ta đặt ngưỡng sàn dương nhỏ để từ khóa xuất hiện vẫn được tính điểm.
    for word in bm25.idf:
        if bm25.idf[word] <= 0:
            bm25.idf[word] = 0.25
    return bm25


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    global CORPUS
    if not CORPUS:
        try:
            from .task4_chunking_indexing import chunk_documents, load_documents
            CORPUS = chunk_documents(load_documents())
        except Exception:
            pass

    if not CORPUS:
        return []

    tokens = query.lower().split()
    if not tokens:
        return []

    bm25 = build_bm25_index(CORPUS)
    scores = bm25.get_scores(tokens)

    sorted_indices = sorted(
        range(len(scores)),
        key=lambda idx: scores[idx],
        reverse=True,
    )

    results: list[dict] = []
    for idx in sorted_indices:
        if scores[idx] <= 0:
            continue
        item = CORPUS[idx]
        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": float(scores[idx]),
            "metadata": item["metadata"],
            "retrieval_method": "bm25",
        })
        if len(results) >= top_k:
            break

    return results


if __name__ == "__main__":
    for result in lexical_search("test query", top_k=3):
        print(result)
