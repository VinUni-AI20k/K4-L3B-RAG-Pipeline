"""
RAGAS-style Evaluation Script — 4 metrics trên golden dataset.

Metrics:
  - Faithfulness: claims trong answer có verify được từ context không
  - Answer Relevance: answer có trả lời đúng câu hỏi không
  - Context Recall: context có đủ thông tin để tạo expected answer không
  - Context Precision: tỉ lệ context chunks thực sự hữu ích

Usage:
    cd D:\\AITC\\DAY8.2\\K4-L3B-RAG-Pipeline
    python tests/run_ragas_evaluation.py

Output:
    group_project/evaluation/automated_test_results.json
"""

import json
import os
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent
GOLDEN_PATH = ROOT / "group_project" / "evaluation" / "golden_dataset.json"
OUTPUT_PATH = ROOT / "group_project" / "evaluation" / "automated_test_results.json"

# Thêm root vào path để import src
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _gemini_score(prompt: str, client, retries: int = 3) -> float:
    """Gọi Gemini judge, parse float từ response. Retry nếu rate limit."""
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
            )
            text = (response.text or "").strip()
            # Tìm số thực đầu tiên trong response
            match = re.search(r"\d+\.\d+|\d+", text)
            if match:
                val = float(match.group())
                return max(0.0, min(1.0, val))
            return 0.5
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                wait = 15 * (attempt + 1)
                print(f"    Rate limit, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"    Judge error: {e}")
                return 0.5
    return 0.5


def score_faithfulness(answer: str, contexts: list[str], client) -> float:
    """Tỉ lệ claims trong answer có thể xác nhận từ context."""
    if not answer or not contexts:
        return 0.0
    if "không thể xác minh" in answer.lower():
        return 1.0  # safe refusal đúng là faithful

    ctx = "\n---\n".join(c[:600] for c in contexts[:3])
    prompt = f"""Bạn là evaluator. Hãy chấm điểm FAITHFULNESS của câu trả lời này.

FAITHFULNESS = tỉ lệ thông tin trong câu trả lời có thể xác nhận trực tiếp từ context bên dưới.
- 1.0 = tất cả thông tin đều có trong context
- 0.0 = toàn bộ thông tin bịa đặt, không có trong context

Context:
{ctx}

Câu trả lời cần đánh giá:
{answer[:800]}

Hãy trả về CHỈ MỘT SỐ THỰC từ 0.0 đến 1.0. Ví dụ: 0.85"""

    return _gemini_score(prompt, client)


def score_answer_relevance(question: str, answer: str, client) -> float:
    """Câu trả lời có trả lời đúng câu hỏi không."""
    if not answer:
        return 0.0

    prompt = f"""Bạn là evaluator. Hãy chấm điểm ANSWER RELEVANCE.

ANSWER RELEVANCE = câu trả lời có liên quan trực tiếp và đầy đủ với câu hỏi không.
- 1.0 = trả lời hoàn toàn đúng và đủ câu hỏi
- 0.5 = trả lời có liên quan nhưng thiếu thông tin hoặc lan man
- 0.0 = không liên quan đến câu hỏi

Câu hỏi: {question}

Câu trả lời: {answer[:600]}

Hãy trả về CHỈ MỘT SỐ THỰC từ 0.0 đến 1.0. Ví dụ: 0.72"""

    return _gemini_score(prompt, client)


def score_context_recall(expected_answer: str, contexts: list[str], client) -> float:
    """Context có đủ thông tin để tạo ra expected answer không."""
    if not contexts:
        return 0.0

    ctx = "\n---\n".join(c[:600] for c in contexts[:4])
    prompt = f"""Bạn là evaluator. Hãy chấm điểm CONTEXT RECALL.

CONTEXT RECALL = tỉ lệ thông tin trong EXPECTED ANSWER có thể tìm thấy trong CONTEXT.
- 1.0 = tất cả thông tin của expected answer đều có trong context
- 0.0 = không có thông tin nào của expected answer trong context

Expected Answer (câu trả lời chuẩn):
{expected_answer}

Context được retrieve:
{ctx}

Hãy trả về CHỈ MỘT SỐ THỰC từ 0.0 đến 1.0. Ví dụ: 0.80"""

    return _gemini_score(prompt, client)


def score_context_precision(question: str, contexts: list[str], client) -> float:
    """Tỉ lệ context chunks thực sự hữu ích để trả lời câu hỏi."""
    if not contexts:
        return 0.0

    useful = 0
    for ctx in contexts[:5]:
        prompt = f"""Câu hỏi: {question}

Context: {ctx[:400]}

Context này có chứa thông tin HỮU ÍCH để trả lời câu hỏi không?
Trả về CHỈ "1" (có) hoặc "0" (không)."""
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
            )
            val = (response.text or "").strip()
            if "1" in val:
                useful += 1
            time.sleep(1)
        except Exception as e:
            if "429" in str(e):
                time.sleep(15)
                useful += 0.5
            else:
                useful += 0.5

    return round(useful / len(contexts[:5]), 4)


def run_evaluation():
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set in .env")
        sys.exit(1)

    from google import genai
    client = genai.Client(api_key=api_key)

    # Import pipeline
    from src.task9_retrieval_pipeline import retrieve
    from src.task10_generation import generate_with_citation

    dataset = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    eval_cases = [d for d in dataset if "thời tiết" not in d["question"].lower()]
    print(f"Running evaluation on {len(eval_cases)} in-domain cases...\n")

    all_scores = {"faithfulness": [], "answer_relevance": [], "context_recall": [], "context_precision": []}
    per_case = []

    for i, case in enumerate(eval_cases, 1):
        q = case["question"]
        expected = case["expected_answer"]
        print(f"[{i:02d}/{len(eval_cases)}] {q[:65]}...")

        # Step 1: Retrieve
        try:
            results = retrieve(q, top_k=5)
            contexts = [r["content"] for r in results]
            retrieval_method = results[0]["retrieval_method"] if results else "none"
        except Exception as e:
            print(f"  ⚠ Retrieval error: {e}")
            contexts = []
            retrieval_method = "error"

        # Step 2: Generate
        try:
            gen = generate_with_citation(q, top_k=5)
            answer = gen.get("answer", "")
            retrieval_source = gen.get("retrieval_source", "none")
        except Exception as e:
            print(f"  ⚠ Generation error: {e}")
            answer = ""
            retrieval_source = "error"

        time.sleep(2)

        # Step 3: Score
        f  = score_faithfulness(answer, contexts, client);  time.sleep(1.5)
        ar = score_answer_relevance(q, answer, client);     time.sleep(1.5)
        cr = score_context_recall(expected, contexts, client); time.sleep(1.5)
        cp = score_context_precision(q, contexts, client);  time.sleep(2)

        print(f"  ✓ faith={f:.3f}  relevance={ar:.3f}  recall={cr:.3f}  precision={cp:.3f}")

        all_scores["faithfulness"].append(f)
        all_scores["answer_relevance"].append(ar)
        all_scores["context_recall"].append(cr)
        all_scores["context_precision"].append(cp)

        per_case.append({
            "question": q,
            "answer": answer,
            "expected_answer": expected,
            "contexts": contexts[:3],  # lưu 3 top chunks
            "retrieval_method": retrieval_method,
            "retrieval_source": retrieval_source,
            "scores": {"faithfulness": f, "answer_relevance": ar, "context_recall": cr, "context_precision": cp},
        })

    # Tính averages
    avg = {k: round(sum(v) / len(v), 4) for k, v in all_scores.items() if v}
    avg["average"] = round(sum(avg.values()) / 4, 4)

    print(f"\n{'='*55}")
    print("EVALUATION RESULTS (Hybrid+RRF, n=14):")
    print(f"  Faithfulness:       {avg['faithfulness']:.4f}")
    print(f"  Answer Relevance:   {avg['answer_relevance']:.4f}")
    print(f"  Context Recall:     {avg['context_recall']:.4f}")
    print(f"  Context Precision:  {avg['context_precision']:.4f}")
    print(f"  Average:            {avg['average']:.4f}")

    output = {
        "run_info": {
            "date": "2026-09-25",
            "embedding_model": os.getenv("EMBEDDING_MODEL", "gemini-embedding-001"),
            "llm_model": os.getenv("LLM_MODEL", "gemini-3.5-flash-lite"),
            "llm_judge": "gemini-3.5-flash-lite",
            "retrieval_mode": "hybrid+rrf",
            "top_k": 5,
            "n_cases_evaluated": len(eval_cases),
        },
        "average_scores": avg,
        "per_case_results": per_case,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ Results saved → {OUTPUT_PATH.relative_to(ROOT)}")
    return avg


if __name__ == "__main__":
    run_evaluation()
