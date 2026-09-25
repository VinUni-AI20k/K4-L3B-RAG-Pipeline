"""
Task 6 — BM25 over the exact chunks indexed by Task 4.

The default corpus is read from the shared Chroma collection without embedding
or re-chunking. CORPUS may be supplied explicitly for offline use and tests.
"""

import re
import unicodedata

from .contracts import validate_document, validate_search_results
from .task4_chunking_indexing import CHROMA_DIR, get_collection


# None means read the indexed corpus; [] means an explicitly empty corpus.
CORPUS: list[dict] | None = None


def _tokenize(text: str) -> list[str]:
    """Keep Vietnamese accents, numbers and internal legal-code separators."""
    text = unicodedata.normalize("NFC", text).casefold()
    return re.findall(r"\w+(?:[/-]\w+)*", text, flags=re.UNICODE)


def _load_indexed_chunks() -> list[dict]:
    """Read the same persisted IDs/content/metadata queried by dense search."""
    if not CHROMA_DIR.exists():
        return []
    response = get_collection().get(include=["documents", "metadatas"])
    chunks = []
    for item_id, content, metadata in zip(
        response["ids"],
        response["documents"],
        response["metadatas"],
        strict=True,
    ):
        chunk = {"id": item_id, "content": content, "metadata": metadata}
        validate_document(chunk, require_chunk=True)
        chunks.append(chunk)
    return sorted(chunks, key=lambda chunk: chunk["id"])


def build_bm25_index(corpus: list[dict]):
    """Build BM25Okapi in corpus order; return None for an empty vocabulary."""
    tokenized = []
    for chunk in corpus:
        validate_document(chunk, require_chunk=True)
        tokenized.append(_tokenize(chunk["content"]))
    if not any(tokenized):
        return None

    from rank_bm25 import BM25Okapi

    return BM25Okapi(tokenized)


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Return unique matching chunks, sorted by their unmodified BM25 scores."""
    if not isinstance(top_k, int) or isinstance(top_k, bool):
        raise TypeError("top_k must be an integer")
    if not isinstance(query, str):
        raise TypeError("query must be a string")
    if top_k <= 0:
        return []
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    corpus = _load_indexed_chunks() if CORPUS is None else CORPUS
    # Deduplicate before scoring, so duplicate records cannot skew IDF.
    unique = {}
    for chunk in corpus:
        validate_document(chunk, require_chunk=True)
        previous = unique.get(chunk["id"])
        if previous is not None and (
            previous["content"] != chunk["content"]
            or previous["metadata"] != chunk["metadata"]
        ):
            raise ValueError(f"Conflicting chunks share ID: {chunk['id']}")
        unique.setdefault(chunk["id"], chunk)
    corpus = list(unique.values())
    index = build_bm25_index(corpus)
    if index is None:
        return []

    scores = index.get_scores(query_tokens)
    query_terms = set(query_tokens)
    results = []
    for chunk, score in zip(corpus, scores, strict=True):
        # Okapi IDF can be zero/negative on a small corpus. Test actual token
        # overlap instead of discarding relevant chunks with score <= 0.
        if not query_terms.intersection(_tokenize(chunk["content"])):
            continue
        results.append({
            "id": chunk["id"],
            "content": chunk["content"],
            "score": float(score),
            "metadata": dict(chunk["metadata"]),
            "retrieval_method": "bm25",
        })

    results.sort(key=lambda item: (-item["score"], item["id"]))
    results = results[:top_k]
    validate_search_results(results, top_k=top_k, expected_method="bm25")
    return results


if __name__ == "__main__":
    CORPUS = _load_indexed_chunks()
    if not CORPUS:
        print("No indexed chunks found. Run Task 3 and Task 4 first.")
    else:
        for result in lexical_search("test query", top_k=3):
            print(result)
