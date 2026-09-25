"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 4 và Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""

import numpy as np
from rank_bm25 import BM25Okapi

from .contracts import validate_search_results


CORPUS: list[dict] = []
_CACHED_BM25 = None
_CACHED_CORPUS_LEN = -1


class SmoothBM25Okapi(BM25Okapi):
    """Kế thừa BM25Okapi với floor smoothing để tránh IDF = 0 khi test corpus rất nhỏ."""

    def _calc_idf(self, nd):
        super()._calc_idf(nd)
        for word, val in self.idf.items():
            if val <= 0:
                self.idf[word] = 0.25


def ensure_corpus() -> list[dict]:
    """Tự động tải corpus chunks từ ChromaDB hoặc từ documents chuẩn hóa nếu chưa có."""
    global CORPUS
    if not CORPUS:
        try:
            from .task4_chunking_indexing import get_collection

            collection = get_collection()
            data = collection.get(include=["documents", "metadatas"])
            if data and data.get("ids"):
                loaded = []
                for item_id, doc, meta in zip(
                    data["ids"], data["documents"], data["metadatas"]
                ):
                    m = dict(meta)
                    if "url" not in m:
                        m["url"] = None
                    loaded.append({"id": item_id, "content": doc, "metadata": m})
                CORPUS = loaded
        except Exception:
            pass

        if not CORPUS:
            try:
                from .task4_chunking_indexing import chunk_documents, load_documents

                CORPUS = chunk_documents(load_documents())
            except Exception:
                pass

    return CORPUS


def build_bm25_index(corpus: list[dict]) -> BM25Okapi:
    """Tạo BM25 index từ danh sách chunks."""
    global _CACHED_BM25, _CACHED_CORPUS_LEN
    if _CACHED_BM25 is not None and len(corpus) == _CACHED_CORPUS_LEN:
        return _CACHED_BM25

    tokenized = [item["content"].lower().split() for item in corpus]
    bm25 = SmoothBM25Okapi(tokenized)
    _CACHED_BM25 = bm25
    _CACHED_CORPUS_LEN = len(corpus)
    return bm25


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    global CORPUS
    if not CORPUS:
        ensure_corpus()

    if not CORPUS or not query or not query.strip() or top_k <= 0:
        return []

    bm25 = build_bm25_index(CORPUS)
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)
    indices = np.argsort(scores)[::-1]

    results: list[dict] = []
    seen_ids: set[str] = set()

    for index in indices:
        if scores[index] <= 0:
            continue
        item = CORPUS[index]
        if item["id"] in seen_ids:
            continue
        seen_ids.add(item["id"])

        meta = dict(item["metadata"])
        if "url" not in meta:
            meta["url"] = None

        results.append(
            {
                "id": str(item["id"]),
                "content": str(item["content"]),
                "score": float(scores[index]),
                "metadata": meta,
                "retrieval_method": "bm25",
            }
        )
        if len(results) >= top_k:
            break

    validate_search_results(results, top_k=top_k, expected_method="bm25")
    return results


if __name__ == "__main__":
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    test_query = "học bổng khuyến khích học tập"
    print(f"Testing BM25 search with query: '{test_query}'")
    for res in lexical_search(test_query, top_k=3):
        print(f"[{res['score']:.4f}] {res['metadata']['title']} - {res['id']}")
        print(res["content"][:150] + "...\n")
