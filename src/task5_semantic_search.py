"""Task 5 — Semantic search over the persistent Chroma index."""

from __future__ import annotations

from .contracts import validate_search_results
from .task4_chunking_indexing import embed_texts, get_collection


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """Return dense SearchResults ordered by cosine similarity."""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string")
    if top_k <= 0:
        return []

    collection = get_collection()
    query_vectors = embed_texts([query.strip()])
    if len(query_vectors) != 1 or not query_vectors[0]:
        raise RuntimeError("Embedding provider did not return one query vector")

    response = collection.query(
        query_embeddings=[query_vectors[0]],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    ids = (response.get("ids") or [[]])[0]
    documents = (response.get("documents") or [[]])[0]
    metadatas = (response.get("metadatas") or [[]])[0]
    distances = (response.get("distances") or [[]])[0]

    results: list[dict] = []
    seen: set[str] = set()
    for item_id, content, metadata, distance in zip(ids, documents, metadatas, distances):
        if not item_id or item_id in seen or not content or distance is None:
            continue
        seen.add(item_id)
        safe_metadata = dict(metadata or {})
        safe_metadata.setdefault("source", "unknown")
        safe_metadata.setdefault("title", safe_metadata["source"])
        safe_metadata.setdefault("doc_type", "news")
        safe_metadata.setdefault("url", None)
        # Chroma's cosine distance is 1 - cosine similarity; keep the original
        # similarity scale so Task 9 can compare it with the calibrated threshold.
        results.append({
            "id": item_id,
            "content": content,
            "score": float(1.0 - distance),
            "metadata": safe_metadata,
            "retrieval_method": "dense",
        })

    results.sort(key=lambda item: (-item["score"], item["id"]))
    results = results[:top_k]
    validate_search_results(results, top_k=top_k, expected_method="dense")
    return results


if __name__ == "__main__":
    for result in semantic_search("IELTS Writing band descriptors", top_k=3):
        print(result)
