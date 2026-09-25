"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""

import re


CORPUS: list[dict] = []


def build_bm25_index(corpus: list[dict]):
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    from rank_bm25 import BM25Okapi

    if not corpus:
        return None
    tokenized = [_tokenize(item["content"]) for item in corpus]
    return BM25Okapi(tokenized)


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    if top_k <= 0 or not query.strip():
        return []

    corpus = CORPUS or _load_corpus()
    bm25 = build_bm25_index(corpus)
    if bm25 is None:
        return []

    query_tokens = _tokenize(query)
    scores = bm25.get_scores(query_tokens)
    ranked_indices = sorted(range(len(corpus)), key=lambda index: (-scores[index], index))
    results = []
    for index in ranked_indices[:top_k]:
        has_matching_token = bool(
            set(query_tokens) & set(_tokenize(corpus[index]["content"]))
        )
        if scores[index] <= 0 and not has_matching_token:
            continue
        item = corpus[index]
        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": float(scores[index]),
            "metadata": item["metadata"],
            "retrieval_method": "bm25",
        })
    return results


def _tokenize(text: str) -> list[str]:
    """Tokenize unicode text while retaining document IDs and punctuation-free terms."""
    return re.findall(r"\w+", text.lower(), flags=re.UNICODE)


def _load_corpus() -> list[dict]:
    """Load the same standardized chunks used by Task 4 when no corpus is injected."""
    from .task4_chunking_indexing import chunk_documents, load_documents

    return chunk_documents(load_documents())


if __name__ == "__main__":
    for result in lexical_search("test query", top_k=3):
        print(result)
