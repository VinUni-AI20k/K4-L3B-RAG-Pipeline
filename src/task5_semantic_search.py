"""
Task 5 — Semantic search.

Reuse Task 4 embeddings and cosine Chroma collection, preserving source metadata.
"""

import math

from .contracts import validate_document, validate_search_results
from .task4_chunking_indexing import embed_texts, get_collection


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """Return unique dense results ordered by descending similarity."""
    if not isinstance(top_k, int) or isinstance(top_k, bool):
        raise TypeError("top_k must be an integer")
    if not isinstance(query, str):
        raise TypeError("query must be a string")
    if top_k <= 0 or not query.strip():
        return []

    query_vector = embed_texts([query])[0]
    response = get_collection().query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    # Chroma returns one nested result list for each query embedding.
    by_id = {}
    for item_id, content, metadata, distance in zip(
        response["ids"][0],
        response["documents"][0],
        response["metadatas"][0],
        response["distances"][0],
        strict=True,
    ):
        if distance is None or not math.isfinite(float(distance)):
            raise ValueError("Chroma returned an invalid cosine distance")
        item = {
            "id": item_id,
            "content": content,
            "score": max(0.0, 1.0 - float(distance)),
            "metadata": dict(metadata) if metadata is not None else None,
            "retrieval_method": "dense",
        }
        validate_document(item, require_chunk=True)
        # Keep the strongest match if the backend returns an ID more than once.
        previous = by_id.get(item_id)
        if previous is None or item["score"] > previous["score"]:
            by_id[item_id] = item

    results = sorted(
        by_id.values(), key=lambda item: item["score"], reverse=True
    )[:top_k]
    validate_search_results(results, top_k=top_k, expected_method="dense")
    return results


if __name__ == "__main__":
    for result in semantic_search("test query", top_k=3):
        print(result)
