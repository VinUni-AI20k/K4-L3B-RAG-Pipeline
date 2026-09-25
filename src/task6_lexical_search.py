"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""

# pyrefly: ignore [missing-import]
from src.task4_chunking_indexing import get_collection

def load_corpus():
    collection = get_collection()
    data=collection.get(include=["documents","metadatas"])
    return [
        {"id": chunk_id,
        "content": doc, 
        "metadata": meta
        }
        for chunk_id, doc, meta in zip(data["ids"], data["documents"], data["metadatas"])
    ]

    
def build_bm25_index(corpus: list[dict]):
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    # TODO: Tokenize và tạo BM25 index.
    #
    from rank_bm25 import BM25Okapi
    tokenized = [item["content"].lower().split() for item in corpus]
    return BM25Okapi(tokenized)

CORPUS: list[dict] = load_corpus() or []
BM25_INDEX = build_bm25_index(CORPUS) if CORPUS else None




def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    # TODO: Tính BM25 scores và map lại corpus.
    #
    if top_k <= 0 or not CORPUS:
        return []
    import numpy as np
    bm25 = build_bm25_index(CORPUS)
    scores = bm25.get_scores(query.lower().split())
    if len(scores) != len(CORPUS):
        raise RuntimeError(
        f"BM25 scores ({len(scores)}) không khớp corpus ({len(CORPUS)})"
    )
    # indices = np.argsort(scores)[::-1][:top_k]
    indices = sorted(
    range(len(CORPUS)),
    key=lambda index: (-float(scores[index]), index),
    )[:top_k]
    
    results = []
    for index in indices:
        item = CORPUS[index]
        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": float(scores[index]),
            "metadata": item["metadata"],
            "retrieval_method": "bm25",
        })
    return results


if __name__ == "__main__":
    for result in lexical_search("test query", top_k=3):
        print(result)
