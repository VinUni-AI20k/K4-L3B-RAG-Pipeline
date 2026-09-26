"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""

import json
import re
from pathlib import Path

from .contracts import validate_document, validate_search_results
from .task4_chunking_indexing import CHUNKS_PATH, get_collection


CORPUS: list[dict] = []
_BM25_INDEX = None
_INDEX_SIGNATURE: tuple[tuple[str, str], ...] | None = None

_TOKEN_PATTERN = re.compile(r"[^\W_]+(?:[./-][^\W_]+)*", re.UNICODE)


def _tokenize(text: str) -> list[str]:
    """Keep Unicode words and common legal/document identifiers intact."""
    return [token.casefold() for token in _TOKEN_PATTERN.findall(text)]


def load_corpus() -> list[dict]:
    """Load Task 4 chunks from its local export or the persistent Chroma index."""
    path = Path(CHUNKS_PATH)
    if path.is_file():
        chunks = []
        with path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid chunk JSON on line {line_number} of {path}") from exc
                validate_document(chunk, require_chunk=True)
                chunks.append(chunk)
        if chunks:
            return chunks

    collection = get_collection()
    if not hasattr(collection, "count") or collection.count() == 0:
        return []
    response = collection.get(include=["documents", "metadatas"])
    chunks = []
    for item_id, content, metadata in zip(
        response.get("ids", []),
        response.get("documents", []),
        response.get("metadatas", []),
    ):
        if not isinstance(content, str) or not isinstance(metadata, dict):
            continue
        metadata = {**metadata, "url": metadata.get("url") or None}
        chunk = {"id": item_id, "content": content, "metadata": metadata}
        validate_document(chunk, require_chunk=True)
        chunks.append(chunk)
    return chunks


def build_bm25_index(corpus: list[dict]):
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    if not corpus:
        return None
    tokenized = []
    for item in corpus:
        validate_document(item, require_chunk=True)
        tokenized.append(_tokenize(item["content"]))
    from rank_bm25 import BM25Okapi

    return BM25Okapi(tokenized)


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 0:
        raise ValueError("top_k must be a non-negative integer")
    if top_k == 0:
        return []
    if not isinstance(query, str):
        raise ValueError("query must be a string")
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    global CORPUS, _BM25_INDEX, _INDEX_SIGNATURE
    if not CORPUS:
        CORPUS = load_corpus()
    if not CORPUS:
        return []

    signature = tuple((item["id"], item["content"]) for item in CORPUS)
    if _BM25_INDEX is None or signature != _INDEX_SIGNATURE:
        _BM25_INDEX = build_bm25_index(CORPUS)
        _INDEX_SIGNATURE = signature

    scores = _BM25_INDEX.get_scores(query_tokens)
    ranked = sorted(enumerate(scores), key=lambda pair: (-float(pair[1]), pair[0]))
    results = []
    seen = set()
    for index, score in ranked:
        score = float(score)
        item = CORPUS[index]
        if score <= 0 or item["id"] in seen:
            continue
        seen.add(item["id"])
        metadata = dict(item["metadata"])
        metadata["url"] = metadata.get("url") or None
        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": score,
            "metadata": metadata,
            "retrieval_method": "bm25",
        })
        if len(results) >= top_k:
            break
    validate_search_results(results, top_k=top_k, expected_method="bm25")
    return results


if __name__ == "__main__":
    for result in lexical_search("test query", top_k=3):
        print(result)
