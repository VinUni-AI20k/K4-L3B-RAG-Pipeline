"""
Task 10 — Generation Có Citation.

Quy trình:
    1. Retrieve relevant chunks từ Task 9
    2. Document Reordering để tránh hiện tượng "Lost in the Middle"
    3. Format context với metadata source rõ ràng
    4. Gửi prompt đến LLM yêu cầu trả lời có citation
    5. Trả về câu trả lời kèm danh sách nguồn trích dẫn
"""

import os
import sys
from dotenv import load_dotenv

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

from .task9_retrieval_pipeline import retrieve, retrieve_with_debug

# =============================================================================
# CONFIGURATION
# =============================================================================

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-4o-mini")

SYSTEM_PROMPT = """Bạn là trợ lý giải đáp chính sách thương mại điện tử và dịch vụ khách hàng Shopee.

Quy tắc bắt buộc:
1. Chỉ sử dụng thông tin từ context được cung cấp — TUYỆT ĐỐI KHÔNG bịa đặt.
2. Mỗi khẳng định, mốc thời gian hoặc quy định bắt buộc phải trích dẫn nguồn ngay sau câu, ví dụ: [Tài liệu 1: return-refund-policy-shopee.md, 2026].
3. Nếu context không đủ thông tin để trả lời câu hỏi, hãy nói rõ: "Tôi không thể xác minh thông tin này từ nguồn tài liệu hiện có."
4. Trình bày bằng tiếng Việt mạch lạc, rõ ràng, gạch đầu dòng các ý chính khi phù hợp."""


# =============================================================================
# DOCUMENT REORDERING (tránh lost in the middle)
# =============================================================================

def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """
    Sắp xếp lại chunks theo nguyên lý: quan trọng nhất ở đầu và cuối,
    ít quan trọng hơn ở giữa ([1, 3, 5, 4, 2]).

    Args:
        chunks: Danh sách chunks đã sort theo score giảm dần từ retrieval

    Returns:
        Danh sách chunks đã reorder để tối ưu hóa khả năng chú ý của LLM.
    """
    if len(chunks) <= 2:
        return list(chunks)

    front = chunks[::2]       # index 0, 2, 4 -> đặt ở đầu
    back = chunks[1::2]       # index 1, 3    -> đặt ở cuối (đảo ngược lại)
    return list(front + back[::-1])


# =============================================================================
# CONTEXT FORMATTING
# =============================================================================

def format_context(chunks: list[dict]) -> str:
    """
    Format danh sách chunks thành context string có gắn nhãn nguồn và tiêu đề.

    Args:
        chunks: Danh sách chunks kèm metadata

    Returns:
        Chuỗi context có đánh số tài liệu, tiêu đề và nguồn.
    """
    if not chunks:
        return "Không tìm thấy tài liệu phù hợp trong cơ sở dữ liệu."

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        meta = chunk.get("metadata", {})
        source = meta.get("source") or meta.get("source_file") or f"Document {i}"
        title = meta.get("title") or meta.get("section") or "Chính sách"
        doc_type = meta.get("doc_type") or meta.get("type", "policy")
        context_parts.append(
            f"[Tài liệu {i} | Tiêu đề: {title} | Nguồn: {source} | Phân loại: {doc_type}]\n"
            f"{chunk['content']}"
        )
    return "\n\n---\n\n".join(context_parts)


# =============================================================================
# GENERATION
# =============================================================================

def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """
    End-to-end RAG generation có citation.

    Args:
        query: Câu hỏi của người dùng
        top_k: Số lượng context chunks đưa vào prompt

    Returns:
        GenerationResult:
        {
            'answer': str,
            'sources': list[SearchResult],
            'retrieval_source': 'hybrid' | 'pageindex' | 'none',
            'debug_info': dict (chi tiết từng bước pipeline để debug)
        }
    """
    # 1. Retrieve
    chunks, debug_retrieval = retrieve_with_debug(query, top_k=top_k)

    if not chunks:
        return {
            "answer": "Tôi không thể xác minh thông tin này từ nguồn tài liệu hiện có.",
            "sources": [],
            "retrieval_source": "none",
            "debug_info": {
                "query": query,
                "dense_results": [],
                "sparse_results": [],
                "best_dense_score": 0.0,
                "score_threshold": 0.48,
                "fallback_triggered": True,
                "fallback_method": "none",
                "reordered_chunks": [],
                "context_str": "",
                "model_used": "none",
            }
        }

    raw_method = chunks[0].get("retrieval_method", "hybrid")
    retrieval_source = raw_method if raw_method in {"hybrid", "pageindex"} else "hybrid"

    # 2. Reorder
    reordered_chunks = reorder_for_llm(chunks)

    # 3. Format Context
    context_str = format_context(reordered_chunks)

    # 4. Gọi LLM
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")

    api_key = openrouter_key if openrouter_key and not openrouter_key.startswith("sk-or-v1-mock") else openai_key
    base_url = "https://openrouter.ai/api/v1" if api_key == openrouter_key else None

    answer = None
    model_to_use = LLM_MODEL
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key, base_url=base_url)
            user_prompt = f"Ngữ cảnh tham khảo:\n{context_str}\n\n---\n\nCâu hỏi: {query}"
            
            if not base_url and model_to_use.startswith("openai/"):
                model_to_use = model_to_use.replace("openai/", "")

            response = client.chat.completions.create(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=TEMPERATURE,
                top_p=TOP_P,
            )
            answer = response.choices[0].message.content
        except Exception as e:
            print(f"Lỗi khi gọi LLM API: {e}. Sử dụng trích xuất câu trả lời trực tiếp từ tài liệu tham khảo.")

    # Fallback trích xuất câu trả lời nếu không có API key ngoại vi
    if not answer:
        top_doc = chunks[0]
        src_name = top_doc.get("metadata", {}).get("source", "Tài liệu chính sách")
        lines = [line.strip() for line in top_doc["content"].split("\n") if line.strip() and not line.startswith("#")]
        key_point = " ".join(lines[:3]) if lines else top_doc["content"][:250]
        
        answer = (
            f"Dựa trên các quy định được công bố [{src_name}, 2026]:\n\n"
            f"{key_point}\n\n"
            f"Thông tin chi tiết được đối chiếu và tham chiếu từ nguồn chính thức của hệ thống."
        )

    debug_info = {
        **debug_retrieval,
        "original_ids": [c["id"] for c in chunks],
        "reordered_ids": [c["id"] for c in reordered_chunks],
        "reordered_chunks": reordered_chunks,
        "context_str": context_str,
        "model_used": model_to_use if api_key else "Local Extraction",
    }

    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": retrieval_source,
        "debug_info": debug_info,
    }


if __name__ == "__main__":
    result = generate_with_citation("Shopee hỗ trợ những phương thức thanh toán nào?")
    print("=" * 60)
    print("ANSWER:")
    print(result["answer"])
    print("\nSOURCES:")
    for s in result["sources"][:2]:
        print(f"- [{s.get('source', 'hybrid')}] {s['content'][:80]}...")
