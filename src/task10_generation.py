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


load_dotenv(override=True)

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3
SAFE_REFUSAL = "Tôi không thể xác minh thông tin này từ nguồn hiện có."

SYSTEM_PROMPT = """Trả lời chỉ từ context được cung cấp.
Mỗi khẳng định phải có citation dạng [1], [2] khớp với số của tài liệu.
Không dùng kiến thức bên ngoài context. Nếu thiếu evidence, hãy từ chối xác minh."""


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa chunks quan trọng về đầu và cuối context."""
    if len(chunks) <= 2:
        return list(chunks)
    front = list(chunks[::2])
    back = list(chunks[1::2])
    return front + back[::-1]


def format_context(chunks: list[dict]) -> str:
    """Tạo context có title và source label."""
    return "\n\n---\n\n".join(
        f"[{index}] Title: {chunk['metadata']['title']} | "
        f"Source: {chunk['metadata']['source']}\n{chunk['content']}"
        for index, chunk in enumerate(chunks, 1)
    )


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi OpenAI, Gemini hoặc Anthropic theo cấu hình."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    model = os.getenv("LLM_MODEL", "") or {"openai": "gpt-4o-mini", "gemini": "gemini-2.0-flash", "anthropic": "claude-3-5-haiku-latest"}.get(provider, "")
    if provider == "openai" and os.getenv("OPENAI_API_KEY"):
        from openai import OpenAI
        response = OpenAI().chat.completions.create(model=model, temperature=TEMPERATURE,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}])
        return response.choices[0].message.content or ""
    if provider == "gemini" and os.getenv("GEMINI_API_KEY"):
        from google import genai
        response = genai.Client(api_key=os.getenv("GEMINI_API_KEY")).models.generate_content(model=model, contents=f"{system_prompt}\n\n{user_message}")
        return response.text or ""
    if provider == "anthropic" and os.getenv("ANTHROPIC_API_KEY"):
        from anthropic import Anthropic
        response = Anthropic().messages.create(model=model, max_tokens=1000, temperature=TEMPERATURE, system=system_prompt, messages=[{"role": "user", "content": user_message}])
        return "".join(getattr(block, "text", "") for block in response.content)
    return "Tôi chưa thể tạo câu trả lời vì chưa cấu hình nhà cung cấp LLM."


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả về GenerationResult."""
    threshold = float(os.getenv("SCORE_THRESHOLD") or "0.45")
    chunks = retrieve(query, top_k=top_k, score_threshold=threshold)
    if not chunks:
        return {"answer": SAFE_REFUSAL, "sources": [], "retrieval_source": "none"}
    ordered_chunks = reorder_for_llm(chunks)
    context = format_context(ordered_chunks)
    try:
        answer = call_llm(SYSTEM_PROMPT, f"Context:\n{context}\n\nQuestion: {query}")
    except Exception:
        answer = ""
    return {
        "answer": answer or SAFE_REFUSAL,
        "sources": ordered_chunks,
        "retrieval_source": chunks[0]["retrieval_method"],
    }


if __name__ == "__main__":
    print(generate_with_citation("test query"))
