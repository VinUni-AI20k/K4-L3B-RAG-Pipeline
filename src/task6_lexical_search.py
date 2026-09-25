"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""

import numpy as np
from rank_bm25 import BM25Okapi


# CORPUS được load khi task4.run_pipeline() hoàn thành,
# hoặc được inject trực tiếp trong tests qua monkeypatch.
CORPUS: list[dict] = []


def _load_corpus_from_chroma() -> list[dict]:
    """Tải toàn bộ chunks từ ChromaDB để build BM25 index."""
    from .task4_chunking_indexing import get_collection

    collection = get_collection()
    count = collection.count()
    if count == 0:
        return []
    response = collection.get(
        limit=count,
        include=["documents", "metadatas"],
    )
    corpus = []
    for item_id, content, metadata in zip(
        response["ids"],
        response["documents"],
        response["metadatas"],
    ):
        corpus.append({
            "id": item_id,
            "content": content,
            "metadata": metadata,
        })
    return corpus


def build_bm25_index(corpus: list[dict]) -> BM25Okapi:
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    tokenized = [item["content"].lower().split() for item in corpus]
    return BM25Okapi(tokenized)


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    import sys

    # Đọc CORPUS qua sys.modules để monkeypatch trong tests hoạt động đúng
    module_corpus = sys.modules[__name__].CORPUS
    corpus = module_corpus if module_corpus else _load_corpus_from_chroma()
    if not corpus:
        return []

    bm25 = build_bm25_index(corpus)
    scores = bm25.get_scores(query.lower().split())

    # Sort theo score giảm dần; khi score bằng nhau, giữ thứ tự corpus gốc (stable)
    indexed_scores = sorted(
        enumerate(scores), key=lambda x: x[1], reverse=True
    )

    results = []
    for orig_index, score in indexed_scores[:top_k]:
        item = corpus[orig_index]
        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": float(score),
            "metadata": item["metadata"],
            "retrieval_method": "bm25",
        })

    # Lọc kết quả không liên quan (score <= 0) chỉ khi có ít nhất 1 kết quả > 0
    positive = [r for r in results if r["score"] > 0]
    return positive if positive else results



if __name__ == "__main__":
    for result in lexical_search("test query", top_k=3):
        print(result)
