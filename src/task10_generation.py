"""
Task 10 — Generation có citation.

Hướng dẫn:
    1. Retrieve top-k chunks.
    2. Reorder để giảm lost-in-the-middle.
    3. Format context kèm title và source.
    4. Gọi provider được chọn trong .env.
    5. Trả answer, sources và retrieval_source.

Nếu context không đủ hoặc provider lỗi, trả safe refusal; không bịa thông tin.
"""

import os
from dotenv import load_dotenv

from .contracts import validate_generation_result
from .task9_retrieval_pipeline import retrieve


load_dotenv()

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()
LLM_MODEL = os.getenv("LLM_MODEL", "")

SYSTEM_PROMPT = """Bạn là trợ lý thông tin dịch vụ sinh viên trường Đại học Công nghệ (UET) - ĐHQGHN.
Chỉ trả lời dựa trên context được cung cấp.
Mỗi khẳng định hoặc thông tin quan trọng cần chỉ rõ nguồn/tài liệu trích dẫn tương ứng (ví dụ: [Source: ...]).
Nếu context không chứa đủ thông tin để trả lời, hãy từ chối lịch sự bằng câu: "Tôi không thể xác minh thông tin này từ nguồn hiện có." và tuyệt đối không bịa đặt thông tin."""

SAFE_REFUSAL_ANSWER = "Tôi không thể xác minh thông tin này từ nguồn hiện có."


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa chunks quan trọng về đầu và cuối context để giảm Lost-in-the-Middle."""
    if len(chunks) <= 2:
        return list(chunks)
    # Lấy các chunk ở vị trí chẵn xếp lên đầu, các chunk ở vị trí lẻ đảo ngược đưa về cuối
    front = chunks[::2]
    back = chunks[1::2]
    return front + back[::-1]


def format_context(chunks: list[dict]) -> str:
    """Tạo context có title và source label rõ ràng cho citation."""
    parts = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata", {})
        title = metadata.get("title", "Tài liệu")
        source = metadata.get("source", "Nguồn không xác định")
        content = chunk.get("content", "").strip()
        parts.append(
            f"[Document {index} | Title: {title} | Source: {source}]\n{content}"
        )
    return "\n\n---\n\n".join(parts)


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi OpenAI, Gemini hoặc Anthropic theo cấu hình .env."""
    provider = os.getenv("LLM_PROVIDER", LLM_PROVIDER).lower()
    model = os.getenv("LLM_MODEL", LLM_MODEL)

    if provider == "gemini":
        from google import genai
        from google.genai import types

        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required for Gemini provider")

        client = genai.Client(api_key=api_key)
        target_model = model or "gemini-2.0-flash"
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=TEMPERATURE,
            top_p=TOP_P,
        )
        response = client.models.generate_content(
            model=target_model,
            contents=user_message,
            config=config,
        )
        return response.text or ""

    elif provider == "openai":
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI provider")

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

    elif provider == "anthropic":
        import anthropic

        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for Anthropic provider")

        client = anthropic.Anthropic(api_key=api_key)
        target_model = model or "claude-3-5-sonnet-20241022"
        response = client.messages.create(
            model=target_model,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            temperature=TEMPERATURE,
            max_tokens=1024,
        )
        return response.content[0].text or ""

    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả về GenerationResult theo chuẩn hợp đồng."""
    if not query or not query.strip():
        result = {
            "answer": SAFE_REFUSAL_ANSWER,
            "sources": [],
            "retrieval_source": "none",
        }
        validate_generation_result(result)
        return result

    try:
        chunks = retrieve(query, top_k=top_k)
    except Exception as ret_err:
        print(f"Retrieval error: {ret_err}")
        chunks = []

    if not chunks:
        result = {
            "answer": SAFE_REFUSAL_ANSWER,
            "sources": [],
            "retrieval_source": "none",
        }
        validate_generation_result(result)
        return result

    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)
    user_message = (
        f"Context:\n{context}\n\n"
        f"Question: {query}\n\n"
        f"Hãy trả lời câu hỏi và đính kèm trích dẫn nguồn."
    )

    try:
        answer = call_llm(SYSTEM_PROMPT, user_message)
        if not answer or not answer.strip():
            answer = SAFE_REFUSAL_ANSWER
    except Exception as llm_err:
        print(f"LLM call error: {llm_err}")
        answer = SAFE_REFUSAL_ANSWER

    raw_method = chunks[0].get("retrieval_method", "hybrid")
    retrieval_source = raw_method if raw_method in {"hybrid", "pageindex"} else "hybrid"

    result = {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": retrieval_source,
    }
    validate_generation_result(result)
    return result


if __name__ == "__main__":
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    test_q = "Quy định điều kiện xét học bổng khuyến khích học tập ĐHQGHN"
    print(f"Query: {test_q}")
    res = generate_with_citation(test_q, top_k=3)
    print(f"Answer: {res['answer']}")
    print(f"Retrieval Source: {res['retrieval_source']}")
    print(f"Number of sources: {len(res['sources'])}")
