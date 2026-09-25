"""
Task 5 — Semantic search.

Embed query bằng chính hàm của Task 4, query ChromaDB và đổi cosine distance
thành similarity. Output phải theo SearchResult, sort giảm dần và không quá top_k.
"""

from .task4_chunking_indexing import embed_texts, get_collection


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về dense SearchResult theo score giảm dần."""
    if top_k <= 0 or not query.strip():
        return []

    query_vector = embed_texts([query])[0]
    response = get_collection().query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    by_id = {}
    for item_id, content, metadata, distance in zip(
        response.get("ids", [[]])[0],
        response.get("documents", [[]])[0],
        response.get("metadatas", [[]])[0],
        response.get("distances", [[]])[0],
    ):
        result = {
            "id": item_id,
            "content": content,
            "score": 1.0 - float(distance),
            "metadata": metadata,
            "retrieval_method": "dense",
        }
        previous = by_id.get(item_id)
        if previous is None or result["score"] > previous["score"]:
            by_id[item_id] = result
    return sorted(by_id.values(), key=lambda item: item["score"], reverse=True)[:top_k]


if __name__ == "__main__":
    for result in semantic_search("thuế hộ kinh doanh phải kê khai thế nào", top_k=3):
        print(result)
