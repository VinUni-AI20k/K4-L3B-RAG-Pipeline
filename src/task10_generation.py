"""Task 10 — Tạo câu trả lời có citation từ kết quả retrieval."""

import os
import re

from dotenv import load_dotenv

from .task9_retrieval_pipeline import retrieve

load_dotenv()

TOP_K = 5
REFUSAL = "Tôi không thể xác minh thông tin này từ nguồn hiện có."

SYSTEM_PROMPT = f"""Bạn là trợ lý hỏi đáp du lịch Ninh Bình.
Chỉ dùng thông tin trong CONTEXT để trả lời.
Gắn số nguồn dạng [1], [2] ngay sau mỗi thông tin thực tế.
Chỉ dùng số nguồn có trong CONTEXT. Không tự suy đoán giá vé, lịch trình hay quy định.
Chỉ gắn số của đoạn trực tiếp chứa thông tin dùng để trả lời.
Không gắn thêm nguồn chỉ vì đoạn đó cùng chủ đề.
Nếu CONTEXT không đủ bằng chứng, chỉ trả lời: {REFUSAL}"""


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa các đoạn được xếp hạng cao về đầu và cuối context."""
    items = list(chunks)
    if len(items) <= 2:
        return items
    return items[::2] + items[1::2][::-1]


def format_context(chunks: list[dict]) -> str:
    """Hiển thị nội dung cùng tên tài liệu và nguồn."""
    parts = []
    for number, chunk in enumerate(chunks, start=1):
        metadata = chunk["metadata"]
        parts.append(
            f"[{number}] Tiêu đề: {metadata['title']}\n"
            f"Nguồn: {metadata['source']}\n"
            f"URL: {metadata.get('url') or 'Không có URL'}\n"
            f"Nội dung: {chunk['content']}"
        )
    return "\n\n---\n\n".join(parts)


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi OpenAI bằng cấu hình trong .env."""
    if os.getenv("LLM_PROVIDER", "openai").lower() != "openai":
        raise ValueError("Task 10 hiện được cấu hình cho OpenAI.")

    model = os.getenv("LLM_MODEL", "").strip()
    if not model or not os.getenv("OPENAI_API_KEY"):
        raise ValueError("Cần điền LLM_MODEL và OPENAI_API_KEY trong .env.")

    from openai import OpenAI

    response = OpenAI().chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content or ""


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả lời câu hỏi và giữ các nguồn để đối chiếu citation."""
    refusal = {
        "answer": REFUSAL,
        "sources": [],
        "retrieval_source": "none",
    }

    if not query.strip() or top_k <= 0:
        return refusal

    try:
        sources = retrieve(query, top_k=top_k)
        if not sources:
            return refusal

        # Số [1], [2] luôn theo thứ tự sources gốc, kể cả khi
        # đổi vị trí trình bày các đoạn trong context.
        source_numbers = {item["id"]: i for i, item in enumerate(sources, 1)}
        reordered = reorder_for_llm(sources)
        context_parts = []

        for item in reordered:
            number = source_numbers[item["id"]]
            metadata = item["metadata"]
            context_parts.append(
                f"[{number}] Tiêu đề: {metadata['title']}\n"
                f"Nguồn: {metadata['source']}\n"
                f"URL: {metadata.get('url') or 'Không có URL'}\n"
                f"Nội dung: {item['content']}"
            )

        answer = call_llm(
            SYSTEM_PROMPT,
            "CONTEXT:\n"
            + "\n\n---\n\n".join(context_parts)
            + f"\n\nCÂU HỎI: {query}"
        ).strip()

        cited_numbers = {
            int(number) for number in re.findall(r"\[(\d+)\]", answer)
        }
        if (
            not answer
            or answer == REFUSAL
            or not cited_numbers
            or any(number < 1 or number > len(sources) for number in cited_numbers)
        ):
            return refusal

        return {
            "answer": answer,
            "sources": sources,
            "retrieval_source": (
                "pageindex"
                if sources[0]["retrieval_method"] == "pageindex"
                else "hybrid"
            ),
        }
    except Exception as error:
        print(f"Generation failed: {error}")
        return refusal