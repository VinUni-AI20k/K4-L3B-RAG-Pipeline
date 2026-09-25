"""
Task 6 — Lexical Search Module (BM25).

Sử dụng thuật toán BM25 (BM25Okapi) từ rank-bm25.
"""

import re
import sys
from pathlib import Path
from rank_bm25 import BM25Okapi
from .task4_chunking_indexing import load_documents, chunk_documents

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Global corpus & index cache
CORPUS: list[dict] = []
_INDEXED_CACHE_KEY = None
_BM25_INDEX = None


def tokenize(text: str) -> list[str]:
    """Tách từ đơn giản bằng regex hỗ trợ tiếng Việt và tiếng Anh."""
    if not text:
        return []
    return re.findall(r"\w+", text.lower())


def get_corpus() -> list[dict]:
    """Lấy danh sách các chunk làm corpus cho BM25."""
    global CORPUS
    if CORPUS:
        return CORPUS
    docs = load_documents()
    CORPUS = chunk_documents(docs)
    return CORPUS


def get_bm25_index():
    """Singleton getter cho BM25Okapi index."""
    global _BM25_INDEX, _INDEXED_CACHE_KEY
    corpus = get_corpus()
    current_key = (id(corpus), len(corpus))
    if _BM25_INDEX is None or _INDEXED_CACHE_KEY != current_key:
        tokenized_corpus = [tokenize(doc["content"]) for doc in corpus]
        _BM25_INDEX = BM25Okapi(tokenized_corpus)
        _INDEXED_CACHE_KEY = current_key
    return _BM25_INDEX


def build_bm25_index(corpus: list[dict]):
    """Xây dựng BM25 index từ corpus đầu vào."""
    global CORPUS, _BM25_INDEX, _INDEXED_CACHE_KEY
    CORPUS = corpus
    tokenized_corpus = [tokenize(doc["content"]) for doc in corpus]
    _BM25_INDEX = BM25Okapi(tokenized_corpus)
    _INDEXED_CACHE_KEY = (id(corpus), len(corpus))
    return _BM25_INDEX


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm từ khoá sử dụng thuật toán BM25.

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
            'retrieval_method': 'bm25'
        }
        Sorted by score descending.
    """
    if not query or not query.strip():
        return []

    corpus = get_corpus()
    if not corpus:
        return []

    bm25 = get_bm25_index()
    tokenized_query = tokenize(query)
    scores = bm25.get_scores(tokenized_query)

    # Lấy chỉ số sắp xếp theo score giảm dần
    sorted_indices = sorted(range(len(scores)), key=lambda idx: scores[idx], reverse=True)

    results = []
    for idx in sorted_indices[:top_k]:
        item = corpus[idx]
        results.append({
            "id": item.get("id") or f"bm25-{idx}",
            "content": item["content"],
            "score": round(float(scores[idx]), 4),
            "metadata": item.get("metadata", {}),
            "retrieval_method": "bm25",
        })

    return results


if __name__ == "__main__":
    results = lexical_search("phương thức thanh toán shopee", top_k=3)
    print(f"BM25 Search Results ({len(results)} items):")
    for r in results:
        print(f"[{r['score']:.4f}] {r['content'][:100]}...")
