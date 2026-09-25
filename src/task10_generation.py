"""
Task 10 — Generation có citation.

Hướng dẫn:
    1. Retrieve top-k chunks.
    2. Reorder để giảm lost-in-the-middle.
    3. Format context kèm title và source.
    4. Gọi provider được chọn trong .env (OpenAI, Gemini, Anthropic).
    5. Trả answer, sources và retrieval_source theo GenerationResult contract.

Nếu context không đủ hoặc provider lỗi, trả safe refusal; không bịa thông tin.
"""

import logging
import os

from dotenv import load_dotenv

from .task9_retrieval_pipeline import retrieve


load_dotenv()

logger = logging.getLogger(__name__)

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower().strip()
LLM_MODEL = os.getenv("LLM_MODEL", "").strip()

SYSTEM_PROMPT = """Bạn là trợ lý tư vấn tuyển sinh chính thức của Trường Đại học Kinh tế Quốc dân (NEU) năm 2026.
Nhiệm vụ của bạn là giải đáp thắc mắc của thí sinh và phụ huynh một cách chuẩn xác, có căn cứ và trung thực dựa HOÀN TOÀN vào context (các đoạn tài liệu được cung cấp bên dưới).

CÁC QUY TẮC BẮT BUỘC:
1. Tính căn cứ và trung thực (Faithfulness & Groundedness):
   - CHỈ trả lời dựa trên thông tin có trong context. Tuyệt đối không tự suy diễn, bịa đặt điều kiện, chỉ tiêu, mã ngành, điểm chuẩn hoặc thời hạn không có trong văn bản.
2. Trích dẫn nguồn (Citations):
   - Mọi thông tin then chốt (chỉ tiêu, điều kiện xét tuyển, chứng chỉ ngoại ngữ, mốc thời gian, số hotline...) PHẢI trích dẫn rõ nguồn theo cú pháp [Tài liệu X] (ví dụ: [Tài liệu 1], [Tài liệu 2]) tương ứng với tài liệu được cung cấp.
3. Xử lý thiếu thông tin & ngoài chủ đề (Safe Refusal):
   - Nếu câu hỏi nằm ngoài phạm vi tuyển sinh NEU hoặc context không có thông tin xác thực để trả lời: Hãy từ chối một cách lịch sự, nêu rõ tài liệu tuyển sinh NEU hiện tại không có thông tin này, không đưa ra suy đoán.
   - Đối với câu hỏi về kết quả xét tuyển/trúng tuyển cá nhân: Không tự kết luận; hướng dẫn người dùng tra cứu tại cổng thông tin chính thức của NEU.
4. Phân biệt thời điểm và đối tượng:
   - Các văn bản có thời điểm ban hành khác nhau (tháng 3, tháng 5, tháng 6/7) hoặc đối tượng khác nhau (đại học chính quy vs liên thông từ cao đẳng/đại học). Nêu rõ thời điểm hoặc đối tượng nếu tài liệu quy định.
   - Nếu câu hỏi chưa nêu rõ năm tuyển sinh hoặc đối tượng, hãy nêu rõ phạm vi thông tin 2026 đang được áp dụng hoặc đề nghị làm rõ.
5. Phong cách trả lời:
   - Ngắn gọn, súc tích, rõ ràng, ngôn ngữ chuẩn mực sư phạm."""


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa chunks quan trọng về đầu và cuối context để giảm lost-in-the-middle.

    Không làm thay đổi list gốc hay mutate các phần tử.
    """
    if len(chunks) <= 2:
        return list(chunks)
    front = chunks[::2]
    back = chunks[1::2]
    return front + back[::-1]


def format_context(chunks: list[dict]) -> str:
    """Tạo context có title, source và metadata để LLM trích dẫn kiểm chứng được."""
    parts = []
    for index, chunk in enumerate(chunks, 1):
        meta = chunk.get("metadata", {})
        title = meta.get("title", "Không có tiêu đề")
        source = meta.get("source", "Không rõ nguồn")
        year = meta.get("admission_year")
        audience = meta.get("audience")

        extra_tags = []
        if year:
            extra_tags.append(f"Năm áp dụng: {year}")
        if audience:
            extra_tags.append(f"Đối tượng: {audience}")
        extra_str = f" | {', '.join(extra_tags)}" if extra_tags else ""

        chunk_id = chunk.get("id", f"chunk-{index}")
        part = (
            f"[Tài liệu {index} | ID: {chunk_id} | Tiêu đề: {title} | Nguồn: {source}{extra_str}]\n"
            f"{chunk['content']}"
        )
        parts.append(part)

    return "\n\n---\n\n".join(parts)


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi OpenAI, Gemini hoặc Anthropic theo cấu hình trong .env."""
    provider = os.getenv("LLM_PROVIDER", LLM_PROVIDER).lower().strip()
    model = os.getenv("LLM_MODEL", LLM_MODEL).strip()

    if provider == "openai":
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY chưa được cấu hình trong .env")
        client = OpenAI(api_key=api_key)
        target_model = model or "gpt-4o-mini"
        response = client.chat.completions.create(
            model=target_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=TEMPERATURE,
            top_p=TOP_P,
        )
        return response.choices[0].message.content or ""

    elif provider == "gemini":
        from google import genai
        from google.genai import types

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY chưa được cấu hình trong .env")
        client = genai.Client(api_key=api_key)
        target_model = model or "gemini-2.5-flash"
        response = client.models.generate_content(
            model=target_model,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=TEMPERATURE,
                top_p=TOP_P,
            ),
        )
        return response.text or ""

    elif provider == "anthropic":
        import anthropic

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY chưa được cấu hình trong .env")
        client = anthropic.Anthropic(api_key=api_key)
        target_model = model or "claude-3-5-sonnet-20241022"
        response = client.messages.create(
            model=target_model,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            max_tokens=1024,
            temperature=TEMPERATURE,
            top_p=TOP_P,
        )
        return response.content[0].text or ""

    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}. Chọn 'openai', 'gemini' hoặc 'anthropic'.")


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả về GenerationResult theo docs/MODULE_CONTRACTS.md."""
    if top_k <= 0 or not query.strip():
        return {
            "answer": "Vui lòng nhập câu hỏi để tìm kiếm thông tin tuyển sinh.",
            "sources": [],
            "retrieval_source": "none",
        }

    # 1. Thu thập chunks liên quan qua retrieval pipeline
    chunks = retrieve(query, top_k=top_k)
    if not chunks:
        return {
            "answer": "Tôi không thể xác minh thông tin này từ nguồn hiện có.",
            "sources": [],
            "retrieval_source": "none",
        }

    # Xác định retrieval_source theo contract: "hybrid" | "pageindex" | "none"
    first_method = chunks[0].get("retrieval_method", "hybrid")
    retrieval_source = "pageindex" if first_method == "pageindex" else "hybrid"

    # 2. Reorder để giảm lost-in-the-middle
    reordered_chunks = reorder_for_llm(chunks)

    # 3. Format context kèm nguồn và metadata
    context_text = format_context(reordered_chunks)

    user_message = (
        f"Dưới đây là các đoạn thông tin trích xuất từ tài liệu tuyển sinh chính thức của NEU:\n\n"
        f"{context_text}\n\n"
        f"====================\n"
        f"CÂU HỎI: {query}\n\n"
        f"Hãy trả lời chính xác, trung thực dựa trên context trên và trích dẫn rõ [Tài liệu X]."
    )

    # 4. Gọi LLM sinh câu trả lời có citation
    try:
        answer = call_llm(SYSTEM_PROMPT, user_message)
    except Exception as exc:
        logger.warning("Không thể gọi LLM provider (%s): %s", type(exc).__name__, exc)
        answer = (
            f"Đã tìm thấy {len(chunks)} tài liệu liên quan từ hệ thống tuyển sinh NEU, "
            f"nhưng hiện tại chưa thể kết nối tới mô hình ngôn ngữ ({type(exc).__name__}: {exc}). "
            f"Vui lòng kiểm tra lại API key hoặc cấu hình LLM_PROVIDER trong file .env."
        )

    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": retrieval_source,
    }


if __name__ == "__main__":
    sample_query = "Thông tin liên hệ tư vấn tuyển sinh NEU năm 2026?"
    print(f"Executing generation for: '{sample_query}'")
    result = generate_with_citation(sample_query, top_k=3)
    print("\n--- ANSWER ---")
    print(result["answer"])
    print("\n--- RETRIEVAL SOURCE ---")
    print(result["retrieval_source"])
    print(f"\n--- SOURCES ({len(result['sources'])}) ---")
    for s in result["sources"]:
        print(f"- [{s['retrieval_method']} | {s['score']:.4f}] {s['id']}: {s['metadata']['title']}")
