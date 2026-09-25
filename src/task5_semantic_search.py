"""
Task 5 — Semantic search.

Embed query bằng chính hàm embed_texts() của Task 4, query ChromaDB và đổi cosine distance
thành similarity: score = max(0.0, 1.0 - distance).
Output tuân theo SearchResult schema, sort giảm dần theo score và không vượt top_k.
"""

from .task4_chunking_indexing import embed_texts, get_collection


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về dense SearchResult theo score giảm dần."""
    if top_k <= 0 or not query.strip():
        return []

    # Dùng chung embed_texts() từ Task 4 để bảo đảm cùng model và dimension
    query_vectors = embed_texts([query])
    if not query_vectors:
        return []
    query_vector = query_vectors[0]

    collection = get_collection()
    response = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    ids = response.get("ids", [[]])[0]
    documents = response.get("documents", [[]])[0]
    metadatas = response.get("metadatas", [[]])[0]
    distances = response.get("distances", [[]])[0]

    results = []
    seen_ids = set()
    for item_id, content, metadata, distance in zip(ids, documents, metadatas, distances):
        if item_id in seen_ids:
            continue
        seen_ids.add(item_id)

        meta = dict(metadata) if metadata else {}
        # Chuẩn hoá URL None nếu được lưu chuỗi rỗng trong ChromaDB
        if meta.get("url") == "" or "url" not in meta:
            meta["url"] = None
        if "chunk_index" in meta and not isinstance(meta["chunk_index"], int):
            meta["chunk_index"] = int(meta["chunk_index"])

        # Cosine distance sang similarity: max(0.0, 1.0 - distance)
        similarity_score = max(0.0, 1.0 - float(distance))
        results.append({
            "id": item_id,
            "content": content,
            "score": similarity_score,
            "metadata": meta,
            "retrieval_method": "dense",
        })

    # Sắp xếp giảm dần theo score
    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    test_query = "Chỉ tiêu tuyển sinh đại học chính quy năm 2026"
    print(f"Executing semantic search for: '{test_query}'")
    for res in semantic_search(test_query, top_k=3):
        print(f"- [{res['score']:.4f}] {res['id']}: {res['content'][:100]}...")
