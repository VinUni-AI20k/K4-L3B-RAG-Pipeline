"""
Task 9 — Retrieval pipeline hoàn chỉnh.

Luồng xử lý:
    1. Chạy semantic_search và lexical_search.
    2. Fuse hai danh sách bằng RRF đúng một lần.
    3. Lấy best cosine score gốc từ dense results.
    4. Nếu score dưới threshold, thử PageIndex fallback.
    5. Nếu fallback lỗi hoặc rỗng, trả hybrid results thay vì crash.

Không so sánh threshold với RRF score vì hai thang đo khác nhau: RRF tối đa
chỉ khoảng 2/(k+1) ≈ 0.033, còn cosine của dense nằm trong [0, 1].

Chạy:
    python -m src.task9_retrieval_pipeline
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

# Hiệu chỉnh trên corpus AWS migration với gemini-embedding-001 (10 query in-domain
# EN/VI: best cosine 0.714–0.880; 10 query out-of-domain: 0.505–0.574). 0.65 nằm
# giữa khoảng trống đó. Gemini cho cả query lạc đề ~0.5, nên 0.3 không bao giờ
# kích hoạt fallback. Đổi corpus hoặc embedding model thì phải hiệu chỉnh lại.
# .env có SCORE_THRESHOLD thì ưu tiên .env.
DEFAULT_SCORE_THRESHOLD = 0.65
SCORE_THRESHOLD = float(os.getenv("SCORE_THRESHOLD") or DEFAULT_SCORE_THRESHOLD)
DEFAULT_TOP_K = 5

# Lấy nhiều ứng viên hơn top_k từ mỗi nhánh để RRF có chỗ đẩy chunk xuất hiện
# ở cả hai danh sách lên trên.
CANDIDATE_MULTIPLIER = 2


def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    use_reranking: bool = True,
) -> list[dict]:
    """Trả về hybrid hoặc pageindex SearchResult."""
    if not query or not query.strip() or top_k <= 0:
        return []

    candidate_k = top_k * CANDIDATE_MULTIPLIER

    # Dense gọi embedding API; lỗi provider không được làm dừng pipeline.
    try:
        dense = semantic_search(query, top_k=candidate_k)
    except Exception as error:
        logger.warning("Dense search lỗi, coi như không có kết quả dense: %s", error)
        dense = []

    if use_reranking:
        sparse = lexical_search(query, top_k=candidate_k)
        # RRF đúng một lần trong toàn pipeline.
        hybrid = rerank_rrf([dense, sparse], top_k=top_k)
    else:
        # Config A (dense-only) cho A/B evaluation.
        hybrid = dense[:top_k]

    # Quyết định fallback bằng cosine gốc của dense, không bao giờ bằng RRF score.
    best_dense_score = max((item["score"] for item in dense), default=0.0)
    if best_dense_score >= score_threshold:
        return hybrid

    logger.info(
        "Best dense score %.4f < threshold %.4f, thử PageIndex fallback",
        best_dense_score,
        score_threshold,
    )
    try:
        fallback = pageindex_search(query, top_k=top_k)
    except Exception as error:
        logger.warning("PageIndex fallback lỗi, giữ hybrid results: %s", error)
        return hybrid

    return fallback[:top_k] if fallback else hybrid


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    for demo_query in (
        "What are the phases of the cutover stage?",
        "Công thức nấu phở bò?",
    ):
        print(f"\n=== {demo_query}")
        for result in retrieve(demo_query, top_k=3):
            print(
                f"[{result['retrieval_method']} {result['score']:.4f}] "
                f"{result['metadata'].get('title', '')}"
            )
