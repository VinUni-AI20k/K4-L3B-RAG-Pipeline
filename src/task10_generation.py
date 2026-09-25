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

from .task9_retrieval_pipeline import retrieve


load_dotenv()

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "")

SYSTEM_PROMPT = """You are a Shopee return and refund policy assistant. Your job:
1. Answer ONLY based on the context documents provided below.
2. Always respond in Vietnamese.
3. For every factual claim, add a citation like [Document 1], [Document 2], etc.
4. If the context does not contain enough information to answer, respond with exactly:
   "Tôi không tìm thấy thông tin cụ thể về câu hỏi này trong tài liệu hiện có."
5. Never make up information not present in the context."""

SAFE_REFUSAL = "Tôi không thể xác minh thông tin này từ nguồn tài liệu hiện có. Vui lòng tham khảo trực tiếp chính sách Shopee."


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa chunks quan trọng về đầu và cuối context (giảm lost-in-the-middle)."""
    if len(chunks) <= 2:
        return list(chunks)
    front = chunks[::2]
    back = chunks[1::2]
    return front + back[::-1]


def format_context(chunks: list[dict]) -> str:
    """Tạo context có title và source label để LLM tạo citation kiểm chứng được."""
    parts = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata", {})
        title = metadata.get("title", "Không rõ tiêu đề")
        source = metadata.get("source", "Không rõ nguồn")
        parts.append(
            f"[Document {index} | Title: {title} | Source: {source}]\n{chunk['content']}"
        )
    return "\n\n---\n\n".join(parts)


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi OpenAI, Gemini hoặc Anthropic theo cấu hình LLM_PROVIDER."""
    provider = LLM_PROVIDER.lower()
    # Nhúng system prompt vào đầu user message để tương thích với mọi proxy
    full_message = f"{system_prompt}\n\n{user_message}"

    if provider == "anthropic":
        # mwapi.dev proxy dùng OpenAI-compatible format (chat/completions)
        from openai import OpenAI

        base_url = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1")
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        model = LLM_MODEL or "claude-haiku-4-5-20251001"

        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=model,
            temperature=TEMPERATURE,
            max_tokens=1024,
            messages=[{"role": "user", "content": full_message}],
        )
        return response.choices[0].message.content or SAFE_REFUSAL

    elif provider == "openai":
        from openai import OpenAI

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
        model = LLM_MODEL or "gpt-4o-mini"
        response = client.chat.completions.create(
            model=model,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content or SAFE_REFUSAL

    elif provider == "gemini":
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", ""))
        model = LLM_MODEL or "gemini-2.0-flash"
        response = client.models.generate_content(
            model=model,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=TEMPERATURE,
                top_p=TOP_P,
            ),
        )
        return response.text or SAFE_REFUSAL

    else:
        raise ValueError(f"LLM_PROVIDER không hợp lệ: {provider!r}. Dùng 'anthropic', 'openai' hoặc 'gemini'.")


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả về GenerationResult."""
    chunks = retrieve(query, top_k=top_k)

    if not chunks:
        return {
            "answer": SAFE_REFUSAL,
            "sources": [],
            "retrieval_source": "none",
        }

    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)
    user_message = f"Context:\n{context}\n\nCâu hỏi: {query}"

    try:
        answer = call_llm(SYSTEM_PROMPT, user_message)
    except Exception as exc:
        print(f"LLM lỗi: {exc}")
        answer = SAFE_REFUSAL

    retrieval_source = chunks[0].get("retrieval_method", "hybrid")
    if retrieval_source not in ("hybrid", "pageindex"):
        retrieval_source = "hybrid"

    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": retrieval_source,
    }


if __name__ == "__main__":
    result = generate_with_citation("Tôi có thể trả hàng trong bao nhiêu ngày?")
    print("Answer:", result["answer"])
    print("Retrieval source:", result["retrieval_source"])
    print("Sources:", len(result["sources"]))
