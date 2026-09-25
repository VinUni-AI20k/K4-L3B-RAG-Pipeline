"""
Task 7 — Reranking Module.

Hỗ trợ các phương pháp:
    - RRF (Reciprocal Rank Fusion): Gộp kết quả từ nhiều ranker (Semantic + Lexical)
    - Cross-Encoder / Dense Re-scoring: Đo lại tương đồng ngữ nghĩa chi tiết giữa Query và Candidates
    - MMR (Maximal Marginal Relevance): Tối ưu hoá giữa độ liên quan và đa dạng nội dung
"""

import sys
import numpy as np
from typing import Optional
from .task4_chunking_indexing import embed_texts

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """Tính cosine similarity giữa 2 vectors."""
    a = np.array(v1)
    b = np.array(v2)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def rerank_rrf(
    ranked_lists: list[list[dict]], top_k: int = 5, k: int = 60
) -> list[dict]:
    """
    Reciprocal Rank Fusion — gộp thứ hạng từ nhiều danh sách retrieval.

    Công thức:
        RRF(d) = Σ 1 / (k + rank_r(d))

    Args:
        ranked_lists: Danh sách các danh sách kết quả đã xếp hạng (ví dụ [dense_results, sparse_results])
        top_k: Số lượng kết quả cuối cùng cần lấy
        k: Hằng số làm mượt (mặc định k=60 theo chuẩn Cormack et al. 2009)

    Returns:
        List of top_k candidates được gộp và sắp xếp theo điểm RRF giảm dần,
        tuân thủ contract SearchResult với retrieval_method='hybrid'.
    """
    if not ranked_lists:
        return []

    rrf_scores = {}
    item_map = {}
    # Lưu điểm cosine gốc tốt nhất (nếu có) để phục vụ threshold checking ở Task 9
    best_dense_scores = {}

    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, 1):
            key = item.get("id") or item["content"]
            rrf_scores[key] = rrf_scores.get(key, 0.0) + (1.0 / (k + rank))
            
            if key not in item_map:
                item_map[key] = item.copy()
            
            # Nếu item có điểm cosine similarity gốc từ dense retrieval
            if item.get("retrieval_method") == "dense" or item.get("source") != "bm25":
                if "score" in item:
                    best_dense_scores[key] = max(best_dense_scores.get(key, 0.0), item["score"])

    # Sắp xếp theo điểm RRF giảm dần
    sorted_items = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

    results = []
    for key, rrf_score in sorted_items[:top_k]:
        item = item_map[key].copy()
        item["score"] = float(rrf_score)
        item["retrieval_method"] = "hybrid"
        item["source"] = "hybrid"
        if key in best_dense_scores:
            item["dense_score"] = best_dense_scores[key]
        results.append(item)

    return results


def rerank_dense_similarity(
    query: str, candidates: list[dict], top_k: int = 5
) -> list[dict]:
    """
    Rerank các candidates bằng cách tính lại cosine similarity chi tiết với câu truy vấn.
    """
    if not candidates:
        return []

    query_vec = embed_texts([query])[0]
    candidate_texts = [c["content"] for c in candidates]
    cand_vecs = embed_texts(candidate_texts)

    scored_candidates = []
    for cand, vec in zip(candidates, cand_vecs):
        sim = cosine_similarity(query_vec, vec)
        item = cand.copy()
        item["score"] = round(float(sim), 4)
        scored_candidates.append(item)

    scored_candidates.sort(key=lambda x: x["score"], reverse=True)
    return scored_candidates[:top_k]


def rerank(
    query: str,
    candidates: list[dict],
    top_k: int = 5,
    method: str = "rrf",
) -> list[dict]:
    """
    Unified reranking interface.

    Args:
        query: Câu truy vấn
        candidates: Danh sách candidates từ retrieval (hoặc list of lists nếu gộp nhiều rankers)
        top_k: Số lượng kết quả sau rerank
        method: 'rrf' hoặc 'cross_encoder' / 'dense'

    Returns:
        List of top_k reranked candidates.
    """
    if not candidates:
        return []

    # Trường hợp candidates là danh sách các danh sách (list of ranked lists)
    if isinstance(candidates[0], list):
        return rerank_rrf(candidates, top_k=top_k)

    # Trường hợp candidates là danh sách phẳng (list of dicts)
    # Tái chấm điểm và sắp xếp theo độ tương đồng với câu truy vấn
    return rerank_dense_similarity(query, candidates, top_k=top_k)


if __name__ == "__main__":
    dummy_candidates = [
        {"content": "Chính sách trả hàng và hoàn tiền Shopee trong 15 ngày", "score": 0.8, "metadata": {}},
        {"content": "Các phương thức thanh toán hỗ trợ trên Shopee Vietnam", "score": 0.6, "metadata": {}},
        {"content": "Quy định đăng bán sản phẩm dành cho người bán", "score": 0.5, "metadata": {}},
    ]
    results = rerank("chính sách trả hàng shopee", dummy_candidates, top_k=2)
    print(f"Reranked {len(results)} items:")
    for r in results:
        print(f"[{r['score']:.4f}] {r['content']}")
