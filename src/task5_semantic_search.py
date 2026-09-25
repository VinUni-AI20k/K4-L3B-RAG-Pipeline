"""Task 5 — Tìm kiếm ngữ nghĩa trong ChromaDB."""

from .task4_chunking_indexing import embed_texts, get_collection


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về các đoạn liên quan, xếp theo điểm giảm dần."""
    if not query.strip() or top_k <= 0:
        return []

    query_vector = embed_texts([query])[0]
    response = get_collection().query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    results = []
    for item_id, content, metadata, distance in zip(
        response["ids"][0],
        response["documents"][0],
        response["metadatas"][0],
        response["distances"][0],
    ):
        item_metadata = dict(metadata or {})
        item_metadata.setdefault("url", None)

        results.append({
            "id": item_id,
            "content": content,
            "score": max(0.0, 1.0 - float(distance)),
            "metadata": item_metadata,
            "retrieval_method": "dense",
        })

    return sorted(
        results,
        key=lambda item: item["score"],
        reverse=True,
    )[:top_k]