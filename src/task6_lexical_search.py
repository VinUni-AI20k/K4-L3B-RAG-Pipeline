"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""

from typing import Optional

CORPUS: list[dict] = []
_BM25_CACHE = None
_CACHE_CORPUS_LEN = 0
_CACHE_CORPUS_ID = None


def build_bm25_index(corpus: list[dict]):
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    from rank_bm25 import BM25Okapi

    tokenized = [item["content"].lower().split() for item in corpus]
    return BM25Okapi(tokenized)


def _get_corpus() -> list[dict]:
    """Lấy corpus từ biến toàn cục CORPUS hoặc nạp và chunk từ Task 4."""
    global CORPUS
    if not CORPUS:
        from .task4_chunking_indexing import chunk_documents, load_documents
        CORPUS = chunk_documents(load_documents())
    return CORPUS


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    global _BM25_CACHE, _CACHE_CORPUS_LEN, _CACHE_CORPUS_ID
    if top_k <= 0 or not query.strip():
        return []

    corpus = _get_corpus()
    if not corpus:
        return []

    # Cập nhật cache BM25 nếu corpus thay đổi (ví dụ khi test monkeypatch CORPUS)
    current_corpus_id = id(corpus)
    if (
        _BM25_CACHE is None
        or _CACHE_CORPUS_LEN != len(corpus)
        or _CACHE_CORPUS_ID != current_corpus_id
    ):
        _BM25_CACHE = build_bm25_index(corpus)
        _CACHE_CORPUS_LEN = len(corpus)
        _CACHE_CORPUS_ID = current_corpus_id

    bm25 = _BM25_CACHE
    tokens = query.lower().split()
    scores = bm25.get_scores(tokens)

    # Thu thập kết quả có score và chuẩn hoá theo SearchResult
    scored_items = []
    for item, score in zip(corpus, scores):
        meta = dict(item.get("metadata", {}))
        if "url" not in meta:
            meta["url"] = None

        scored_items.append({
            "id": item["id"],
            "content": item["content"],
            "score": float(score),
            "metadata": meta,
            "retrieval_method": "bm25",
        })

    # Sắp xếp giảm dần theo score
    scored_items.sort(key=lambda x: x["score"], reverse=True)

    # Đảm bảo tính duy nhất của ID và không vượt quá top_k
    results = []
    seen = set()
    for item in scored_items:
        if item["id"] not in seen:
            seen.add(item["id"])
            results.append(item)
            if len(results) >= top_k:
                break

    return results


if __name__ == "__main__":
    test_query = "chỉ tiêu tuyển sinh NEU"
    print(f"Executing lexical search for: '{test_query}'")
    for res in lexical_search(test_query, top_k=3):
        print(f"- [{res['score']:.4f}] {res['id']}: {res['content'][:100]}...")
