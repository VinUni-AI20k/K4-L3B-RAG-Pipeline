"""
Task 5 — Semantic search.

Embed query bằng chính hàm của Task 4, query ChromaDB và đổi cosine distance
thành similarity. Output phải theo SearchResult, sort giảm dần và không quá top_k.
"""

from .task4_chunking_indexing import embed_texts, get_collection
from .contracts import validate_search_results


def _top_k(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("top_k must be a non-negative integer")
    return value


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về dense SearchResult theo score giảm dần."""
    top_k = _top_k(top_k)
    if top_k < 0:
        raise ValueError("top_k must be a non-negative integer")
    if top_k == 0:
        return []
    if not isinstance(query, str):
        raise ValueError("query must be a string")
    if not query.strip():
        return []

    collection = get_collection()
    if hasattr(collection, "count") and collection.count() == 0:
        return []
    query_vector = embed_texts([query])[0]
    response = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    rows = [response.get(key) or [[]] for key in ("ids", "documents", "metadatas", "distances")]
    ids, documents, metadatas, distances = [row[0] if row else [] for row in rows]

    results = []
    seen = set()
    for item_id, content, metadata, distance in zip(ids, documents, metadatas, distances):
        if item_id in seen or not isinstance(content, str) or not isinstance(metadata, dict):
            continue
        seen.add(item_id)
        results.append({
            "id": item_id,
            "content": content,
            "score": float(1.0 - distance),
            "metadata": {**metadata, "url": metadata.get("url") or None},
            "retrieval_method": "dense",
        })
    results.sort(key=lambda item: item["score"], reverse=True)
    results = results[:top_k]
    validate_search_results(results, top_k=top_k, expected_method="dense")
    return results


if __name__ == "__main__":
    for result in semantic_search("test query", top_k=3):
        print(result)
