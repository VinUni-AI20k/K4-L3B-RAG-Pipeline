"""Task 6 — BM25 lexical search over the same chunks as semantic search."""

from __future__ import annotations

import re
import math

from .contracts import validate_search_results


CORPUS: list[dict] = []
_INDEX_SIGNATURE: tuple[tuple[str, str], ...] | None = None
_BM25_INDEX = None


def _tokens(text: str) -> list[str]:
    return re.findall(r"[\w]+(?:[-'][\w]+)*", text.casefold(), flags=re.UNICODE)


def _load_corpus() -> list[dict]:
    """Use explicitly assigned corpus, or build it from the Task 4 documents."""
    if CORPUS:
        return CORPUS
    from .task4_chunking_indexing import chunk_documents, load_documents

    return chunk_documents(load_documents())


def build_bm25_index(corpus: list[dict]):
    """Build a BM25Okapi index from the supplied Task 4 chunks."""
    from rank_bm25 import BM25Okapi

    if not corpus:
        return None
    return BM25Okapi([_tokens(item["content"]) or [""] for item in corpus])


def _get_index(corpus: list[dict]):
    global _INDEX_SIGNATURE, _BM25_INDEX
    signature = tuple((item["id"], item["content"]) for item in corpus)
    if signature != _INDEX_SIGNATURE:
        _BM25_INDEX = build_bm25_index(corpus)
        _INDEX_SIGNATURE = signature
    return _BM25_INDEX


def _positive_bm25_scores(query_tokens: list[str], corpus: list[dict]) -> list[float]:
    """Positive-IDF BM25 fallback for tiny corpora where Okapi IDF is zero."""
    tokenized = [_tokens(item["content"]) for item in corpus]
    document_count = len(tokenized)
    average_length = sum(map(len, tokenized)) / max(document_count, 1)
    scores = [0.0] * document_count
    k1 = 1.5
    b = 0.75
    for term in set(query_tokens):
        document_frequency = sum(term in set(document) for document in tokenized)
        if not document_frequency:
            continue
        idf = math.log(1.0 + (document_count - document_frequency + 0.5) / (document_frequency + 0.5))
        for index, document in enumerate(tokenized):
            frequency = document.count(term)
            if not frequency:
                continue
            length_norm = 1.0 - b + b * len(document) / max(average_length, 1.0)
            scores[index] += idf * frequency * (k1 + 1.0) / (frequency + k1 * length_norm)
    return scores


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Return BM25 SearchResults, sorted by descending score."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")
    if top_k <= 0:
        return []
    query_tokens = _tokens(query)
    if not query_tokens:
        return []

    corpus = _load_corpus()
    bm25 = _get_index(corpus)
    if bm25 is None:
        return []
    scores = bm25.get_scores(query_tokens)
    if not any(float(score) > 0.0 for score in scores):
        scores = _positive_bm25_scores(query_tokens, corpus)
    ranked = [
        (index, float(score))
        for index, score in enumerate(scores)
        if float(score) > 0.0
    ]
    ranked.sort(key=lambda item: (-item[1], corpus[item[0]]["id"]))

    results: list[dict] = []
    for index, score in ranked[:top_k]:
        item = corpus[index]
        metadata = {**item["metadata"]}
        metadata.setdefault("url", None)
        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": score,
            "metadata": metadata,
            "retrieval_method": "bm25",
        })
    validate_search_results(results, top_k=top_k, expected_method="bm25")
    return results


if __name__ == "__main__":
    for result in lexical_search("IELTS Writing band descriptors", top_k=3):
        print(result)
