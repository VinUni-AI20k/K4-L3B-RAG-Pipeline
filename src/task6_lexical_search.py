"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""

import json
from pathlib import Path


CORPUS_PATH = Path(__file__).parent.parent / "data" / "bm25_corpus.json"


def _load_corpus() -> list[dict]:
    if not CORPUS_PATH.exists():
        return []
    data = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("BM25 corpus cache must contain a JSON list")
    return data


CORPUS: list[dict] = _load_corpus()


def build_bm25_index(corpus: list[dict]):
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    from rank_bm25 import BM25Okapi

    if not corpus:
        return None
    tokenized = [item["content"].lower().split() for item in corpus]
    return BM25Okapi(tokenized)


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    if top_k <= 0 or not query.strip() or not CORPUS:
        return []

    query_tokens = query.lower().split()
    bm25 = build_bm25_index(CORPUS)
    scores = bm25.get_scores(query_tokens)
    query_token_set = set(query_tokens)
    overlap = [
        len(query_token_set.intersection(item["content"].lower().split()))
        for item in CORPUS
    ]
    order = sorted(
        range(len(CORPUS)),
        key=lambda index: (-float(scores[index]), -overlap[index], index),
    )

    results = []
    seen_ids = set()
    for index in order:
        if len(results) >= top_k:
            break
        if float(scores[index]) <= 0 and overlap[index] == 0:
            continue
        item = CORPUS[index]
        if item["id"] in seen_ids:
            continue
        seen_ids.add(item["id"])
        results.append(
            {
                "id": item["id"],
                "content": item["content"],
                "score": float(scores[index]),
                "metadata": item["metadata"],
                "retrieval_method": "bm25",
            }
        )
    return results


if __name__ == "__main__":
    for result in lexical_search("thuế hộ kinh doanh", top_k=3):
        print(result)
