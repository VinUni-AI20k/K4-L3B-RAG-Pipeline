"""
Task 5 — Semantic search.

Embed query bằng chính embed_texts() của Task 4 (cùng model, cùng dimension),
query ChromaDB rồi đổi cosine distance thành similarity.

Output theo SearchResult: retrieval_method="dense", sort giảm dần, không trùng
ID và không vượt top_k.

Chạy:
    python -m src.task5_semantic_search
"""

from .task4_chunking_indexing import _from_chroma_metadata, embed_texts, get_collection


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về dense SearchResult theo score giảm dần."""
    if not query or not query.strip() or top_k <= 0:
        return []

    query_vector = embed_texts([query])[0]
    response = get_collection().query(
        query_embeddings=[query_vector],
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
        if item_id in seen or not content:
            continue
        seen.add(item_id)
        results.append(
            {
                "id": item_id,
                "content": content,
                # Cosine distance -> similarity. Đây là score gốc mà Task 9 dùng
                # để so với threshold fallback, nên không được chuẩn hoá lại.
                "score": max(0.0, 1.0 - float(distance)),
                "metadata": _from_chroma_metadata(metadata),
                "retrieval_method": "dense",
            }
        )

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    DEMO_QUERY = "Trước khi cutover cần kiểm tra những gì?"
    for result in semantic_search(DEMO_QUERY, top_k=3):
        print(f"[{result['score']:.4f}] {result['metadata']['title']}")
        print(f"         section: {result['metadata'].get('section', '')}")
        print(f"         {result['content'][:160]}...")
        print()
