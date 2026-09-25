"""
Task 9 — Retrieval pipeline hoàn chỉnh.

Luồng xử lý:
    1. Chạy semantic_search và lexical_search.
    2. Lấy best cosine score gốc từ dense results.
    3. Nếu score dưới threshold, thử PageIndex fallback.
    4. Nếu fallback lỗi hoặc không có kết quả, trả hybrid results (hoặc dense-only nếu không dùng reranking).
    5. Chỉ fuse bằng RRF đúng một lần khi dense search tự tin hoặc khi fallback không khả dụng.

Không so sánh threshold với RRF score vì hai thang đo khác nhau.
"""

import logging
import os

from dotenv import load_dotenv

from .task5_semantic_search import semantic_search
from .task6_lexical_search import lexical_search
from .task7_reranking import rerank_rrf
from .task8_pageindex_vectorless import pageindex_search


load_dotenv()

logger = logging.getLogger(__name__)

# Ngưỡng cosine similarity mặc định được hiệu chỉnh dựa trên fallback_dataset.json:
# - Các truy vấn out-of-domain hoặc không liên quan thường có cosine similarity < 0.35
# - Các truy vấn in-domain tuyển sinh NEU 2026 có cosine similarity >= 0.35 (thường 0.45 - 0.85)
DEFAULT_THRESHOLD = 0.35
SCORE_THRESHOLD = float(os.getenv("SCORE_THRESHOLD") or DEFAULT_THRESHOLD)
DEFAULT_TOP_K = 5


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    use_reranking: bool = True,
) -> list[dict]:
    """Trả về hybrid hoặc pageindex SearchResult."""
    if top_k <= 0 or not query.strip():
        return []

    # 1. Chạy semantic_search và lexical_search
    dense = semantic_search(query, top_k=top_k * 2)
    sparse = lexical_search(query, top_k=top_k * 2)

    # 2. Lấy best cosine score gốc từ dense results (không dùng BM25 hay RRF score)
    best_dense_score = dense[0]["score"] if dense else 0.0

    # 3. Nếu score dưới threshold, thử PageIndex fallback
    if best_dense_score < score_threshold:
        try:
            fallback = pageindex_search(query, top_k=top_k)
            if fallback:
                return fallback[:top_k]
        except Exception as exc:
            logger.warning("PageIndex fallback thất bại (%s), tiếp tục dùng hybrid retrieval.", exc)

    # 4. Hợp nhất bằng RRF đúng một lần hoặc trả dense-only
    if use_reranking:
        hybrid = rerank_rrf([dense, sparse], top_k=top_k)
        return hybrid
    else:
        return dense[:top_k]


if __name__ == "__main__":
    test_query = "Thông tin liên hệ tư vấn tuyển sinh NEU năm 2026?"
    print(f"Retrieving for query: '{test_query}'")
    results = retrieve(test_query, top_k=3)
    for idx, r in enumerate(results, 1):
        print(f"[{idx}] id={r['id']} score={r['score']:.4f} method={r['retrieval_method']}")
        print(f"    content: {r['content'][:120]}...\n")
