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
import re
import logging

from dotenv import load_dotenv

from .contracts import validate_document, validate_generation_result
from .task9_retrieval_pipeline import retrieve


load_dotenv()

logger = logging.getLogger(__name__)

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL = os.getenv("LLM_MODEL", "")

SYSTEM_PROMPT = """Trả lời chỉ từ context được cung cấp.
Mỗi khẳng định phải có citation dạng [S1], [S2], ... tương ứng đúng nhãn nguồn.
Không được dùng kiến thức bên ngoài context. Nếu thiếu evidence, hãy trả lời đúng câu:
Tôi không thể xác minh thông tin này từ nguồn hiện có."""

SAFE_REFUSAL = "Tôi không thể xác minh thông tin này từ nguồn hiện có."


def _normalize_citations(answer: str) -> str:
    """Convert Gemini-style ``[S1, S2]`` groups to canonical labels."""
    pattern = re.compile(r"\[(S\d+(?:\s*,\s*S\d+)+)\]")

    def replace(match: re.Match) -> str:
        return "".join(f"[{label}]" for label in re.findall(r"S\d+", match.group(1)))

    return pattern.sub(replace, answer)


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa chunks quan trọng về đầu và cuối context."""
    if not isinstance(chunks, list):
        raise ValueError("chunks must be a list")
    if len(chunks) <= 2:
        return list(chunks)
    # Input is relevance-sorted. This long-context ordering keeps the most
    # relevant item first and the second-most relevant item last.
    return list(chunks[::2]) + list(reversed(chunks[1::2]))


def format_context(chunks: list[dict]) -> str:
    """Tạo context có title và source label."""
    if not isinstance(chunks, list):
        raise ValueError("chunks must be a list")
    # Reordered context is intentionally not score-sorted, so validate each
    # item's schema without applying the ranked-list ordering invariant.
    for chunk in chunks:
        validate_document(chunk, require_chunk=True)
        if not isinstance(chunk.get("score"), (int, float)) or isinstance(chunk.get("score"), bool):
            raise ValueError("chunk.score must be numeric")
    parts = []
    for index, chunk in enumerate(chunks, start=1):
        metadata = chunk["metadata"]
        citation_index = metadata.get("citation_index", index)
        details = [
            f"Title: {metadata['title']}",
            f"Source: {metadata['source']}",
        ]
        if metadata.get("page") is not None:
            details.append(f"Page: {metadata['page']}")
        if metadata.get("url"):
            details.append(f"URL: {metadata['url']}")
        parts.append(f"[S{citation_index} | {' | '.join(details)}]\n{chunk['content']}")
    return "\n\n---\n\n".join(parts)


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi OpenAI, Gemini hoặc Anthropic theo cấu hình."""
    provider = LLM_PROVIDER.strip().casefold()
    if provider not in {"openai", "gemini", "anthropic"}:
        raise ValueError("LLM_PROVIDER must be openai, gemini, or anthropic")
    if not LLM_MODEL.strip():
        raise RuntimeError("LLM_MODEL is not configured")

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        from openai import OpenAI

        response = OpenAI(api_key=api_key).responses.create(
            model=LLM_MODEL,
            instructions=system_prompt,
            input=user_message,
            temperature=TEMPERATURE,
            top_p=TOP_P,
        )
        text = response.output_text
    elif provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        from google import genai
        from google.genai import types

        # Keep the client alive for the full request. With google-genai 2.x,
        # chaining ``genai.Client(...).models.generate_content(...)`` can let
        # the temporary client be finalized while its retry transport is still
        # running, producing "Cannot send a request, as the client has been closed".
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=TEMPERATURE,
                top_p=TOP_P,
            ),
        )
        text = response.text
    else:
        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not configured")
        from anthropic import Anthropic

        response = Anthropic(api_key=api_key).messages.create(
            model=LLM_MODEL,
            max_tokens=1200,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            temperature=TEMPERATURE,
            top_p=TOP_P,
        )
        text = "".join(block.text for block in response.content if getattr(block, "type", "") == "text")

    text = str(text or "").strip()
    if not text:
        raise RuntimeError("LLM returned an empty response")
    return text


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả về GenerationResult."""
    if not isinstance(query, str):
        raise ValueError("query must be a string")
    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 0:
        raise ValueError("top_k must be a non-negative integer")

    empty = {"answer": SAFE_REFUSAL, "sources": [], "retrieval_source": "none"}
    if top_k == 0 or not query.strip():
        validate_generation_result(empty)
        return empty
    try:
        chunks = retrieve(query.strip(), top_k=top_k)
    except Exception:
        logger.exception("Retrieval failed; returning a safe refusal")
        validate_generation_result(empty)
        return empty
    if not chunks:
        validate_generation_result(empty)
        return empty

    labelled = []
    for index, chunk in enumerate(chunks, start=1):
        labelled.append({**chunk, "metadata": {**chunk["metadata"], "citation_index": index}})
    reordered = reorder_for_llm(labelled)
    context = format_context(reordered)
    user_message = (
        f"Context:\n{context}\n\n"
        f"Question: {query.strip()}\n\n"
        "Hãy trả lời ngắn gọn bằng ngôn ngữ của câu hỏi và gắn citation [S#] "
        "ngay sau từng thông tin được sử dụng."
    )
    retrieval_source = "pageindex" if chunks[0]["retrieval_method"] == "pageindex" else "hybrid"
    try:
        answer = call_llm(SYSTEM_PROMPT, user_message)
    except Exception:
        logger.exception("LLM generation failed; returning a safe refusal")
        answer = SAFE_REFUSAL

    answer = _normalize_citations(answer)

    # Do not expose hallucinated citation labels. An evidence-bearing answer
    # must cite at least one source; a refusal is allowed without citations.
    labels = [int(value) for value in re.findall(r"\[S(\d+)\]", answer)]
    if answer != SAFE_REFUSAL and (not labels or any(value < 1 or value > len(reordered) for value in labels)):
        answer = SAFE_REFUSAL
    result = {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": retrieval_source,
    }
    validate_generation_result(result)
    return result


if __name__ == "__main__":
    print(generate_with_citation("test query"))
