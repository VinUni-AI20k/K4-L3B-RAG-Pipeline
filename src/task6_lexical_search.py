"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5.
BM25 phù hợp với từ khóa chính xác, mã tài liệu và tên riêng.

Output theo SearchResult và sort score giảm dần.
"""

import re
from functools import lru_cache

from .task4_chunking_indexing import get_collection


CORPUS: list[dict] = []


def _tokenize(text: str) -> list[str]:
    """
    Tokenizer đơn giản nhưng phù hợp với tiếng Việt.

    Giữ Unicode và tách theo khoảng trắng/dấu câu.
    """
    if not isinstance(text, str):
        return []

    text = text.lower()

    # Giữ chữ cái/số Unicode, thay ký tự khác bằng khoảng trắng.
    text = re.sub(r"[^\wÀ-ỹ]", " ", text, flags=re.UNICODE)

    return [token for token in text.split() if token]


def _load_corpus_from_chroma() -> list[dict]:
    """Đọc toàn bộ chunks đã được Task 4 index vào ChromaDB."""
    collection = get_collection()

    count = collection.count()

    if count == 0:
        return []

    response = collection.get(
        include=["documents", "metadatas"],
    )

    ids = response.get("ids", [])
    documents = response.get("documents", [])
    metadatas = response.get("metadatas", [])

    corpus: list[dict] = []

    for item_id, content, metadata in zip(
        ids,
        documents,
        metadatas,
    ):
        corpus.append(
            {
                "id": item_id,
                "content": content or "",
                "metadata": metadata or {},
            }
        )

    return corpus


def build_bm25_index(corpus: list[dict]):
    """Tạo BM25 index từ corpus chunks."""
    from rank_bm25 import BM25Okapi

    if not corpus:
        return None

    tokenized_corpus = [
        _tokenize(item.get("content", ""))
        for item in corpus
    ]

    return BM25Okapi(tokenized_corpus)


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    if not isinstance(query, str) or not query.strip():
        return []

    if top_k <= 0:
        return []

    global CORPUS

    # Dùng cùng corpus với Task 5.
    CORPUS = _load_corpus_from_chroma()

    if not CORPUS:
        return []

    bm25 = build_bm25_index(CORPUS)

    if bm25 is None:
        return []

    query_tokens = _tokenize(query)

    if not query_tokens:
        return []

    scores = bm25.get_scores(query_tokens)

    # Sort bằng Python để không cần phụ thuộc numpy.
    ranked_indices = sorted(
        range(len(scores)),
        key=lambda index: float(scores[index]),
        reverse=True,
    )

    results: list[dict] = []

    for index in ranked_indices:
        score = float(scores[index])

        # Không trả những document hoàn toàn không match.
        if score <= 0:
            continue

        item = CORPUS[index]

        results.append(
            {
                "id": item["id"],
                "content": item["content"],
                "score": score,
                "metadata": item["metadata"],
                "retrieval_method": "bm25",
            }
        )

        if len(results) >= top_k:
            break

    return results


if __name__ == "__main__":
    results = lexical_search("tuyển sinh đại học", top_k=3)

    print(f"Found {len(results)} BM25 results:")

    for result in results:
        print(
            f"[{result['score']:.4f}] "
            f"{result['metadata'].get('title', 'Unknown')}"
        )