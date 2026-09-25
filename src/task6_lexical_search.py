"""
Task 6 — Lexical search bằng BM25.

Dùng đúng corpus chunk của Task 4 (đọc lại từ ChromaDB) nên dense và BM25 xếp
hạng trên cùng tập ID — điều kiện để Task 7 fuse theo ID.

BM25 bù đúng điểm yếu của dense: khớp tên riêng và mã dịch vụ như "AWS DMS",
"MGN", "DataSync", "Aurora PostgreSQL".

Output theo SearchResult: retrieval_method="bm25", sort giảm dần, không vượt top_k.

Chạy:
    python -m src.task6_lexical_search
"""

import re

from .task4_chunking_indexing import load_chunks_from_store


# Được nạp lười từ ChromaDB ở lần search đầu tiên; test có thể monkeypatch trực tiếp.
CORPUS: list[dict] = []

# Tách token theo chữ và số, bỏ dấu câu Markdown ("(MGN)," -> "mgn").
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")

_bm25_cache: tuple[tuple[int, int], object, list[set[str]]] | None = None


def tokenize(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def _get_corpus() -> list[dict]:
    """Trả về corpus chunk, nạp từ vector store nếu chưa có."""
    global CORPUS
    if not CORPUS:
        CORPUS = load_chunks_from_store()
    return CORPUS


def build_bm25_index(corpus: list[dict]):
    """Tạo BM25 index từ cùng corpus chunks của Task 4."""
    from rank_bm25 import BM25Okapi

    tokenized = [tokenize(item["content"]) for item in corpus]
    return BM25Okapi(tokenized)


def _get_bm25(corpus: list[dict]) -> tuple[object, list[set[str]]]:
    """Cache index và token set theo corpus đang dùng; corpus đổi thì build lại.

    Token set được cache cùng index để không phải tokenize lại toàn corpus ở
    mỗi query.
    """
    global _bm25_cache
    key = (id(corpus), len(corpus))
    if _bm25_cache is not None and _bm25_cache[0] == key:
        return _bm25_cache[1], _bm25_cache[2]

    bm25 = build_bm25_index(corpus)
    token_sets = [set(tokenize(item["content"])) for item in corpus]
    _bm25_cache = (key, bm25, token_sets)
    return bm25, token_sets


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    if not query or not query.strip() or top_k <= 0:
        return []

    corpus = _get_corpus()
    tokens = tokenize(query)
    if not corpus or not tokens:
        return []

    bm25, token_sets = _get_bm25(corpus)
    scores = bm25.get_scores(tokens)

    # Lọc theo token overlap, không lọc theo `score > 0`: BM25Okapi cho
    # idf = log(N - n + 0.5) - log(n + 0.5), nên trên corpus rất nhỏ một từ xuất
    # hiện ở đúng nửa số document sẽ có idf = 0 và mọi score = 0 dù có khớp thật.
    # Overlap là điều kiện đúng về ngữ nghĩa: chunk phải chứa ít nhất một token
    # của query mới được xếp hạng.
    query_tokens = set(tokens)
    ranked = sorted(
        (index for index, tokens_in_chunk in enumerate(token_sets) if query_tokens & tokens_in_chunk),
        key=lambda index: scores[index],
        reverse=True,
    )[:top_k]

    results: list[dict] = []
    for index in ranked:
        item = corpus[index]
        results.append(
            {
                "id": item["id"],
                "content": item["content"],
                "score": float(scores[index]),
                "metadata": item["metadata"],
                "retrieval_method": "bm25",
            }
        )
    return results


if __name__ == "__main__":
    DEMO_QUERY = "AWS DMS Aurora PostgreSQL migration"
    for result in lexical_search(DEMO_QUERY, top_k=3):
        print(f"[{result['score']:.4f}] {result['metadata']['title']}")
        print(f"         section: {result['metadata'].get('section', '')}")
        print(f"         {result['content'][:160]}...")
        print()
