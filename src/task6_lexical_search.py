"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""

import re


CORPUS: list[dict] = []


def _get_corpus() -> list[dict]:
    #  Load the same chunk corpus used by the other retrieval stages.
    if CORPUS:
        return CORPUS

    from .task4_chunking_indexing import chunk_documents, load_documents

    CORPUS.extend(chunk_documents(load_documents()))
    return CORPUS


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.casefold(), flags=re.UNICODE)


def build_bm25_index(corpus: list[dict]):
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    from rank_bm25 import BM25Okapi

    if not corpus:
        raise ValueError("Cannot build BM25 index from an empty corpus")

    tokenized = [_tokenize(item["content"]) for item in corpus]
    return BM25Okapi(tokenized)


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    if top_k <= 0 or not query.strip():
        return []

    corpus = _get_corpus()
    if not corpus:
        return []

    bm25 = build_bm25_index(corpus)
    scores = bm25.get_scores(_tokenize(query))
    indices = sorted(
        range(len(corpus)), key=lambda index: (-scores[index], index)
    )[:top_k]
    results = []
    for index in indices:
        if scores[index] <= 0 and not any(
            token in _tokenize(corpus[index]["content"])
            for token in _tokenize(query)
        ):
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


if __name__ == "__main__":
    for result in lexical_search("test query", top_k=3):
        print(result)
