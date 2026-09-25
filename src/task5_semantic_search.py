"""
Task 5 — Semantic Search Module.

Viết module tìm kiếm ngữ nghĩa (dense retrieval) trên vector store ChromaDB.

Yêu cầu:
    - Input: query string + top_k
    - Output: danh sách chunks có score, sorted descending
    - Phải tương thích với embedding model và vector store ở Task 4
"""

import sys
from .task4_chunking_indexing import get_collection, embed_texts

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm ngữ nghĩa sử dụng vector similarity (Dense Retrieval).

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of SearchResult dictionaries theo schema hợp đồng:
        {
            'id': str,
            'content': str,
            'score': float,
            'metadata': dict,
            'retrieval_method': 'dense'
        }
        Sorted by score descending.
    """
    if not query or not query.strip():
        return []

    collection = get_collection()

    # Kiểm tra xem collection có documents không (an toàn với mock collection)
    n_results = top_k
    if hasattr(collection, "count"):
        try:
            cnt = collection.count()
            if cnt == 0:
                return []
            n_results = min(top_k, cnt)
        except Exception:
            pass

    # 1. Embed query vector
    query_vector = embed_texts([query])[0]

    # 2. Truy vấn ChromaDB
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    output = []
    if results and results.get("documents") and results["documents"][0]:
        docs = results["documents"][0]
        ids = results.get("ids", [[]])[0] if results.get("ids") else []
        metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
        distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

        for i, (doc, meta, dist) in enumerate(zip(docs, metas, distances)):
            # ChromaDB cosine distance: 0 (identical) -> 2 (opposite)
            # cosine similarity: 1 - distance
            score = max(0.0, 1.0 - dist)
            chunk_id = ids[i] if i < len(ids) else f"dense-{i}"
            output.append({
                "id": chunk_id,
                "content": doc,
                "score": round(float(score), 4),
                "metadata": meta if meta is not None else {},
                "retrieval_method": "dense",
            })

    # 3. Sắp xếp theo score giảm dần và lấy đúng top_k
    output.sort(key=lambda x: x["score"], reverse=True)
    return output[:top_k]


if __name__ == "__main__":
    results = semantic_search("quy định đổi trả hàng và hoàn tiền shopee", top_k=3)
    print(f"Found {len(results)} results:")
    for r in results:
        print(f"[{r['score']:.4f}] {r['content'][:100]}...")
