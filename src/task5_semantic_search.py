"""
Task 5 — Semantic search.

Embed query bằng chính hàm của Task 4, query ChromaDB và đổi cosine distance
thành similarity. Output theo SearchResult, sort giảm dần và không quá top_k.
"""

from .task4_chunking_indexing import embed_texts, get_collection


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về dense SearchResult theo score giảm dần."""
    if not isinstance(query, str) or not query.strip():
        return []

    if top_k <= 0:
        return []

    collection = get_collection()

    # ChromaDB không thể query collection rỗng.
    if collection.count() == 0:
        return []

    # Task 5 phải dùng chính embedding provider của Task 4.
    query_vector = embed_texts([query.strip()])[0]

    # Không yêu cầu nhiều hơn số document hiện có.
    n_results = min(top_k, collection.count())

    response = collection.query(
        query_embeddings=[query_vector],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    ids = response.get("ids", [[]])[0]
    documents = response.get("documents", [[]])[0]
    metadatas = response.get("metadatas", [[]])[0]
    distances = response.get("distances", [[]])[0]

    results: list[dict] = []

    for item_id, content, metadata, distance in zip(
        ids,
        documents,
        metadatas,
        distances,
    ):
        # ChromaDB cosine distance thường nằm trong [0, 2].
        # Contract của pipeline dùng similarity không âm.
        similarity = max(0.0, 1.0 - float(distance))

        results.append(
            {
                "id": item_id,
                "content": content,
                "score": similarity,
                "metadata": metadata or {},
                "retrieval_method": "dense",
            }
        )

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    results = semantic_search("tuyển sinh đại học", top_k=3)

    print(f"Found {len(results)} dense results:")

    for result in results:
        print(
            f"[{result['score']:.4f}] "
            f"{result['metadata'].get('title', 'Unknown')}"
        )