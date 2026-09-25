"""Task 6 — Tìm kiếm từ khóa bằng BM25."""

import re

from rank_bm25 import BM25Plus

from .task4_chunking_indexing import chunk_documents, load_documents


# Để trống khi chạy thật. Test có thể gán corpus mẫu vào biến này.
CORPUS: list[dict] = []


def tokenize(text: str) -> list[str]:
    """Tách từ, giữ được chữ tiếng Việt và số."""
    return re.findall(r"\w+", text.lower(), flags=re.UNICODE)


def build_bm25_index(corpus: list[dict]):
    """Tạo BM25 index từ các chunks của Task 4."""
    return BM25Plus([tokenize(item["content"]) for item in corpus])


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Tìm chunks theo từ khóa, sắp xếp điểm giảm dần."""
    query_tokens = tokenize(query)
    if not query_tokens or top_k <= 0:
        return []

    corpus = CORPUS if CORPUS else chunk_documents(load_documents())
    if not corpus:
        return []

    scores = build_bm25_index(corpus).get_scores(query_tokens)
    query_words = set(query_tokens)

    indices = sorted(
        range(len(corpus)),
        key=lambda i: float(scores[i]),
        reverse=True,
    )

    results = []
    for i in indices:
        if len(results) >= top_k:
            break

        item = corpus[i]
        # BM25Plus có thể cho điểm dương dù đoạn không chứa từ khóa.
        if not query_words.intersection(tokenize(item["content"])):
            continue

        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": float(scores[i]),
            "metadata": item["metadata"],
            "retrieval_method": "bm25",
        })

    return results