"""
Task 8 — Gemini vectorless fallback, token-optimized.

Architecture:

    Query
      ↓
    BM25 candidate retrieval
      ↓
    top N candidate chunks
      ↓
    Gemini relevance/evidence selection
      ↓
    SearchResult-compatible results

Notes:
- Không sử dụng PAGEINDEX_API_KEY.
- Sử dụng GEMINI_API_KEY.
- Không gửi toàn bộ corpus cho Gemini.
- BM25 được dùng để giới hạn candidate trước khi gọi Gemini.
- Không tạo embedding/vector mới trong Task 8.
- Giữ tên pageindex_search() để Task 9 không phải đổi interface.
"""

import json
import os

from dotenv import load_dotenv
from google import genai

from .task6_lexical_search import lexical_search


load_dotenv()


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

GEMINI_MODEL = os.getenv(
    "GEMINI_FALLBACK_MODEL",
    "gemini-3.8-flash",
).strip()

# Số candidate lấy từ BM25 trước khi gửi cho Gemini.
DEFAULT_CANDIDATE_K = int(
    os.getenv("GEMINI_FALLBACK_CANDIDATE_K", "12")
)

# Giới hạn số ký tự của mỗi chunk gửi vào Gemini.
# Mục đích là tránh prompt quá lớn nếu chunk bất thường.
MAX_CHARS_PER_CANDIDATE = int(
    os.getenv("GEMINI_FALLBACK_MAX_CHARS", "1800")
)


# ---------------------------------------------------------------------
# Gemini client
# ---------------------------------------------------------------------

def _get_client() -> genai.Client:
    """Create Gemini client from GEMINI_API_KEY."""

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not set or is empty in .env"
        )

    return genai.Client(
        api_key=GEMINI_API_KEY
    )


# ---------------------------------------------------------------------
# Candidate preparation
# ---------------------------------------------------------------------

def _get_candidates(
    query: str,
    candidate_k: int = DEFAULT_CANDIDATE_K,
) -> list[dict]:
    """
    Get lexical candidates using BM25.

    This keeps Task 8 vectorless:
    no embedding/vector search is performed here.
    """

    if candidate_k <= 0:
        return []

    candidates = lexical_search(
        query,
        top_k=candidate_k,
    )

    if not candidates:
        return []

    prepared = []

    for index, item in enumerate(candidates):
        content = item.get("content", "") or ""

        # Limit text sent to Gemini.
        content = content[:MAX_CHARS_PER_CANDIDATE]

        prepared.append(
            {
                "index": index,
                "id": item.get("id"),
                "content": content,
                "metadata": item.get("metadata", {}),
                "bm25_score": float(
                    item.get("score", 0.0)
                ),
            }
        )

    return prepared


# ---------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------

def _build_prompt(
    query: str,
    candidates: list[dict],
    top_k: int,
) -> str:
    """
    Build a compact Gemini prompt.

    Only BM25 candidate chunks are included.
    """

    source_blocks = []

    for candidate in candidates:
        source_blocks.append(
            {
                "index": candidate["index"],
                "id": candidate["id"],
                "content": candidate["content"],
            }
        )

    sources_json = json.dumps(
        source_blocks,
        ensure_ascii=False,
    )

    return f"""
Bạn là bộ phận retrieval fallback của hệ thống RAG
về chủ đề tuyển sinh đại học.

Câu hỏi:
{query}

Các candidate passages dưới đây đã được BM25 lọc trước.
Hãy chọn tối đa {top_k} passage phù hợp nhất.

Yêu cầu bắt buộc:
1. Chỉ chọn passage có trong danh sách.
2. Không được tạo source ID.
3. Không được bịa thông tin.
4. Nếu không có passage nào thực sự liên quan, trả về [].
5. Score phải nằm trong khoảng 0 đến 1.
6. Evidence phải lấy trực tiếp từ passage tương ứng.
7. Chỉ trả về JSON hợp lệ.
8. Không trả về Markdown.
9. Không giải thích ngoài JSON.

Candidates:
{sources_json}

JSON format:
[
  {{
    "index": 0,
    "score": 0.95,
    "evidence": "đoạn bằng chứng liên quan trực tiếp"
  }}
]
"""


# ---------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------

def _clean_json_text(text: str) -> str:
    """Remove accidental Markdown code fences."""

    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    return text


def _parse_response(
    response_text: str,
    candidates: list[dict],
    top_k: int,
) -> list[dict]:
    """Convert Gemini JSON response to SearchResult-compatible results."""

    if not response_text:
        return []

    text = _clean_json_text(response_text)

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        print("Gemini fallback returned invalid JSON.")
        return []

    if not isinstance(data, list):
        return []

    results = []
    seen_indices = set()

    for item in data:
        if not isinstance(item, dict):
            continue

        try:
            index = int(item["index"])
            score = float(item["score"])
        except (
            KeyError,
            TypeError,
            ValueError,
        ):
            continue

        # Gemini must reference an existing candidate.
        if index < 0 or index >= len(candidates):
            continue

        # Do not return the same candidate twice.
        if index in seen_indices:
            continue

        # Clamp score to [0, 1].
        score = max(
            0.0,
            min(1.0, score),
        )

        candidate = candidates[index]

        evidence = item.get(
            "evidence",
            "",
        )

        if not isinstance(evidence, str):
            evidence = ""

        results.append(
            {
                "id": candidate["id"],
                "content": candidate["content"],
                "metadata": candidate["metadata"],
                "score": score,
                "retrieval_method": "gemini_fallback",
                "evidence": evidence,
            }
        )

        seen_indices.add(index)

        if len(results) >= top_k:
            break

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results


# ---------------------------------------------------------------------
# Public fallback API
# ---------------------------------------------------------------------

def pageindex_search(
    query: str,
    top_k: int = 5,
    candidate_k: int = DEFAULT_CANDIDATE_K,
) -> list[dict]:
    """
    Gemini-based vectorless fallback.

    The function name is kept for compatibility with Task 9.

    Flow:
        query
          ↓
        BM25 top candidate_k
          ↓
        Gemini
          ↓
        top_k results
    """

    if not isinstance(query, str):
        return []

    query = query.strip()

    if not query:
        return []

    if top_k <= 0:
        return []

    if candidate_k <= 0:
        return []

    # -------------------------------------------------------------
    # Step 1: BM25 candidate retrieval
    # -------------------------------------------------------------

    candidates = _get_candidates(
        query=query,
        candidate_k=candidate_k,
    )

    # If BM25 finds no lexical evidence, do NOT waste Gemini quota.
    if not candidates:
        return []

    # -------------------------------------------------------------
    # Step 2: Gemini
    # -------------------------------------------------------------

    try:
        client = _get_client()

        prompt = _build_prompt(
            query=query,
            candidates=candidates,
            top_k=top_k,
        )

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )

    except Exception as exc:
        # Important:
        # Do not crash Task 9 if Gemini is temporarily unavailable,
        # rate-limited, or quota-exhausted.
        print(
            "Gemini fallback unavailable: "
            f"{type(exc).__name__}: {exc}"
        )
        return []

    response_text = getattr(
        response,
        "text",
        "",
    ) or ""

    # -------------------------------------------------------------
    # Step 3: Parse and normalize results
    # -------------------------------------------------------------

    return _parse_response(
        response_text=response_text,
        candidates=candidates,
        top_k=top_k,
    )


# ---------------------------------------------------------------------
# Manual test
# ---------------------------------------------------------------------

if __name__ == "__main__":
    print(
        "=== Task 8: Gemini vectorless fallback "
        "(token-optimized) ==="
    )

    print(
        f"Model: {GEMINI_MODEL}"
    )

    print(
        f"Candidate K: {DEFAULT_CANDIDATE_K}"
    )

    print(
        f"Max chars/candidate: "
        f"{MAX_CHARS_PER_CANDIDATE}"
    )

    if not GEMINI_API_KEY:
        print(
            "ERROR: GEMINI_API_KEY is missing or empty in .env"
        )
        raise SystemExit(1)

    query = (
        "HUST năm 2024 có bao nhiêu "
        "chỉ tiêu tuyển sinh?"
    )

    print(f"\nQuery: {query}")

    results = pageindex_search(
        query,
        top_k=3,
    )

    print(
        f"Found {len(results)} fallback results:"
    )

    for result in results:
        print(
            f"[{result['score']:.4f}] "
            f"{result['metadata'].get('title', 'Unknown')}"
        )

        print(
            f"Method: "
            f"{result['retrieval_method']}"
        )

        print(
            f"Evidence: "
            f"{result.get('evidence', '')}"
        )

        print()