"""
Task 5 — Semantic search.

Embed query bằng chính hàm của Task 4, query ChromaDB và đổi cosine distance
thành similarity. Output phải theo SearchResult, sort giảm dần và không quá top_k.
"""

from .contracts import validate_search_results
from .task4_chunking_indexing import embed_texts, get_collection


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về dense SearchResult theo score giảm dần."""
    if not query or not query.strip() or top_k <= 0:
        return []

    collection = get_collection()
    query_vector = embed_texts([query])[0]

    # Kiểm tra số lượng phần tử có sẵn trong collection (nếu hỗ trợ)
    try:
        count = collection.count()
        if count == 0:
            return []
        n_results = min(top_k, count)
    except Exception:
        n_results = top_k

    response = collection.query(
        query_embeddings=[query_vector],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    ids = response.get("ids", [[]])[0] if response and "ids" in response else []
    docs = response.get("documents", [[]])[0] if response and "documents" in response else []
    metas = response.get("metadatas", [[]])[0] if response and "metadatas" in response else []
    distances = response.get("distances", [[]])[0] if response and "distances" in response else []

    results: list[dict] = []
    seen_ids: set[str] = set()

    for item_id, doc, meta, dist in zip(ids, docs, metas, distances):
        if item_id in seen_ids:
            continue
        seen_ids.add(item_id)
        similarity = max(0.0, 1.0 - float(dist))
        meta_dict = dict(meta)
        if "url" not in meta_dict:
            meta_dict["url"] = None

        results.append(
            {
                "id": str(item_id),
                "content": str(doc),
                "score": float(similarity),
                "metadata": meta_dict,
                "retrieval_method": "dense",
            }
        )

    results.sort(key=lambda item: item["score"], reverse=True)
    results = results[:top_k]

    validate_search_results(results, top_k=top_k, expected_method="dense")
    return results


if __name__ == "__main__":
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    test_query = "Quy định điều kiện xét học bổng khuyến khích học tập ĐHQGHN"
    print(f"Testing semantic search with query: '{test_query}'")
    for res in semantic_search(test_query, top_k=3):
        print(f"[{res['score']:.4f}] {res['metadata']['title']} - {res['id']}")
        print(res["content"][:150] + "...\n")
