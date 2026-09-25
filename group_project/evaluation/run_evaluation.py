"""
Chạy A/B evaluation cho pipeline RAG trên golden_dataset.json.

Config A = dense-only   (retrieve(..., use_reranking=False))
Config B = hybrid + RRF (retrieve(..., use_reranking=True))

Cả hai dùng chung: golden dataset, generator LLM (LLM_PROVIDER/.env), prompt
(SYSTEM_PROMPT của task10), top_k và score_threshold. Chỉ retrieval strategy
khác nhau — đúng yêu cầu "cùng cấu hình còn lại, chỉ đổi retrieval strategy".

KHÔNG sửa public signature của generate_with_citation()/retrieve(): script này
build một hàm generation riêng cho việc eval, tái sử dụng retrieve(), reorder_for_llm(),
format_context(), call_llm() đã có sẵn trong src/task9, src/task10.

Cách chạy (từ thư mục gốc repo, sau khi đã index xong ChromaDB ở Task 4):
    python group_project/evaluation/run_evaluation.py

Yêu cầu:
    - .env đã điền đúng LLM_PROVIDER/LLM_MODEL (và API key tương ứng) dùng làm
      generator VÀ mặc định cũng dùng làm judge cho RAGAS (có thể override bằng
      RAGAS_LLM_PROVIDER/RAGAS_LLM_MODEL nếu muốn judge khác provider).
    - ChromaDB đã được index (đã chạy `python -m src.task4_chunking_indexing`).
    - pip install ragas langchain-community (đã có trong pyproject); nếu dùng
      judge là anthropic/gemini cần thêm `pip install langchain-anthropic` hoặc
      `pip install langchain-google-genai` (script sẽ báo rõ nếu thiếu).

Script KHÔNG tự bịa số liệu: nếu một bước lỗi (thiếu API key, chưa index...),
script dừng và báo lỗi rõ ràng thay vì ghi số giả vào RESULT.md.
"""

from __future__ import annotations

import json
import os
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(REPO_ROOT / ".env")

from src.task9_retrieval_pipeline import retrieve, SCORE_THRESHOLD  # noqa: E402
from src.task10_generation import (  # noqa: E402
    SAFE_REFUSAL,
    SYSTEM_PROMPT,
    call_llm,
    format_context,
    reorder_for_llm,
)

EVAL_DIR = Path(__file__).resolve().parent
GOLDEN_DATASET_PATH = EVAL_DIR / "golden_dataset.json"
RESULT_MD_PATH = EVAL_DIR / "RESULT.md"
RAW_RESULTS_PATH = EVAL_DIR / "eval_raw_results.json"

TOP_K = int(os.getenv("EVAL_TOP_K", "5"))

CONFIGS = {
    "A": {"label": "Config A — dense-only", "use_reranking": False},
    "B": {"label": "Config B — hybrid + RRF", "use_reranking": True},
}


# --------------------------------------------------------------------------
# Generation cho từng config (không đổi signature generate_with_citation gốc)
# --------------------------------------------------------------------------

def generate_for_config(query: str, top_k: int, use_reranking: bool) -> dict:
    chunks = retrieve(
        query, top_k=top_k, score_threshold=SCORE_THRESHOLD, use_reranking=use_reranking
    )
    if not chunks:
        return {"answer": SAFE_REFUSAL, "sources": [], "retrieval_source": "none"}

    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)
    user_message = f"Context:\n{context}\n\nQuestion: {query}"
    try:
        answer = call_llm(SYSTEM_PROMPT, user_message).strip()
    except Exception as error:  # provider lỗi -> safe refusal, không crash
        print(f"    [warn] call_llm failed: {error!r} -> safe refusal")
        answer = ""
    if not answer:
        answer = SAFE_REFUSAL
    return {"answer": answer, "sources": chunks}


def is_refusal(answer: str) -> bool:
    return SAFE_REFUSAL.strip() in answer.strip() or "không thể xác minh" in answer.lower()


# --------------------------------------------------------------------------
# Judge LLM / embeddings cho RAGAS — mặc định dùng lại LLM_PROVIDER trong .env
# --------------------------------------------------------------------------

def build_judge_llm():
    from ragas.llms import LangchainLLMWrapper

    provider = os.getenv("RAGAS_LLM_PROVIDER", os.getenv("LLM_PROVIDER", "openai")).lower()
    model = os.getenv("RAGAS_LLM_MODEL", os.getenv("LLM_MODEL", ""))
    if not model:
        raise RuntimeError("RAGAS_LLM_MODEL hoặc LLM_MODEL chưa được cấu hình trong .env")

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        chat = ChatOpenAI(model=model, temperature=0)
    elif provider == "anthropic":
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError as error:
            raise RuntimeError(
                "Cần cài `pip install langchain-anthropic` để dùng Anthropic làm judge."
            ) from error
        chat = ChatAnthropic(model=model, temperature=0)
    elif provider == "gemini":
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError as error:
            raise RuntimeError(
                "Cần cài `pip install langchain-google-genai` để dùng Gemini làm judge."
            ) from error
        chat = ChatGoogleGenerativeAI(model=model, temperature=0)
    else:
        raise ValueError(f"Unsupported judge provider: {provider}")

    return LangchainLLMWrapper(chat)


def build_judge_embeddings():
    from ragas.embeddings import LangchainEmbeddingsWrapper

    embedding_provider = os.getenv("EMBEDDING_PROVIDER", "sentence_transformers").lower()
    embedding_model = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")

    if embedding_provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        embeddings = OpenAIEmbeddings(model=embedding_model or "text-embedding-3-small")
    else:
        # Mặc định: dùng LẠI đúng model sentence-transformers đã dùng để index
        # (embed_texts() ở task4), để AnswerRelevancy nhất quán với retrieval.
        from langchain_community.embeddings import HuggingFaceEmbeddings

        embeddings = HuggingFaceEmbeddings(model_name=embedding_model)

    return LangchainEmbeddingsWrapper(embeddings)


# --------------------------------------------------------------------------
# Chạy 1 case cho 1 config
# --------------------------------------------------------------------------

def run_case(case: dict, config_key: str, top_k: int) -> dict:
    use_reranking = CONFIGS[config_key]["use_reranking"]
    started = time.perf_counter()
    generation = generate_for_config(case["question"], top_k, use_reranking)
    latency = time.perf_counter() - started

    contexts = [chunk["content"] for chunk in generation["sources"]]
    sources = [
        {
            "id": chunk["id"],
            "score": chunk["score"],
            "retrieval_method": chunk["retrieval_method"],
            "source": chunk["metadata"].get("source"),
            "title": chunk["metadata"].get("title"),
        }
        for chunk in generation["sources"]
    ]
    return {
        "id": case["id"],
        "question": case["question"],
        "answerable": case.get("answerable", True),
        "answer": generation["answer"],
        "retrieved_contexts": contexts,
        "sources": sources,
        "latency_s": round(latency, 3),
        "refused": is_refusal(generation["answer"]),
    }


# --------------------------------------------------------------------------
# RAGAS scoring
# --------------------------------------------------------------------------

def score_with_ragas(records: list[dict], golden_by_id: dict) -> dict:
    """Chấm faithfulness / answer_relevancy / context_recall / context_precision
    bằng RAGAS cho các case answerable=True. Trả {case_id: {metric: score}}."""
    from ragas.dataset_schema import EvaluationDataset, SingleTurnSample
    from ragas.metrics import (
        AnswerRelevancy,
        Faithfulness,
        LLMContextPrecisionWithReference,
        LLMContextRecall,
    )

    judge_llm = build_judge_llm()
    judge_embeddings = build_judge_embeddings()

    answerable = [r for r in records if r["answerable"]]
    if not answerable:
        return {}

    samples = []
    for record in answerable:
        golden = golden_by_id[record["id"]]
        samples.append(
            SingleTurnSample(
                user_input=record["question"],
                response=record["answer"],
                retrieved_contexts=record["retrieved_contexts"] or [""],
                reference=golden["expected_answer"],
            )
        )

    dataset = EvaluationDataset(samples=samples)
    metrics = [
        Faithfulness(llm=judge_llm),
        AnswerRelevancy(llm=judge_llm, embeddings=judge_embeddings),
        LLMContextRecall(llm=judge_llm),
        LLMContextPrecisionWithReference(llm=judge_llm),
    ]

    from ragas import evaluate

    result = evaluate(dataset=dataset, metrics=metrics)
    df = result.to_pandas()

    per_case = {}
    for record, (_, row) in zip(answerable, df.iterrows()):
        per_case[record["id"]] = {
            "faithfulness": float(row.get("faithfulness", float("nan"))),
            "answer_relevancy": float(row.get("answer_relevancy", float("nan"))),
            "context_recall": float(row.get("context_recall", float("nan"))),
            "context_precision": float(
                row.get("llm_context_precision_with_reference", float("nan"))
            ),
        }
    return per_case


# --------------------------------------------------------------------------
# Aggregation + RESULT.md rendering
# --------------------------------------------------------------------------

def safe_mean(values: list[float]) -> float:
    values = [v for v in values if v == v]  # loại NaN
    return statistics.fmean(values) if values else float("nan")


def aggregate(per_case_scores: dict) -> dict:
    metrics = ["faithfulness", "answer_relevancy", "context_recall", "context_precision"]
    return {
        metric: safe_mean([scores[metric] for scores in per_case_scores.values()])
        for metric in metrics
    }


def refusal_accuracy(records: list[dict]) -> float:
    unanswerable = [r for r in records if not r["answerable"]]
    if not unanswerable:
        return float("nan")
    correct = sum(1 for r in unanswerable if r["refused"])
    return correct / len(unanswerable)


def worst_cases(per_case_scores: dict, records_by_id: dict, n: int = 3) -> list[dict]:
    def avg(cid):
        scores = per_case_scores[cid]
        return safe_mean(list(scores.values()))

    ranked = sorted(per_case_scores.keys(), key=avg)[:n]
    rows = []
    for cid in ranked:
        scores = per_case_scores[cid]
        record = records_by_id[cid]
        if scores["context_recall"] < 0.5 or scores["context_precision"] < 0.5:
            stage = "retrieval"
        elif scores["faithfulness"] < 0.5:
            stage = "generation"
        else:
            stage = "data"
        rows.append({"id": cid, "record": record, "scores": scores, "stage": stage})
    return rows


def fmt(value: float) -> str:
    return "n/a" if value != value else f"{value:.3f}"


def render_result_md(context: dict) -> str:
    a = context["agg"]["A"]
    b = context["agg"]["B"]

    def delta(metric: str) -> str:
        if a[metric] != a[metric] or b[metric] != b[metric]:
            return "n/a"
        return f"{b[metric] - a[metric]:+.3f}"

    worst_rows = []
    for i, item in enumerate(context["worst_B"], start=1):
        golden = context["golden_by_id"][item["id"]]
        s = item["scores"]
        worst_rows.append(
            f"|   {i} | {golden['question'][:60]} | B | {fmt(s['faithfulness'])} | "
            f"{fmt(s['answer_relevancy'])} | {fmt(s['context_recall'])} | "
            f"{fmt(s['context_precision'])} | {item['stage']} | "
            f"[DRAFT — điền root cause cụ thể sau khi đọc retrieved_contexts trong "
            f"eval_raw_results.json cho case {item['id']}] |"
        )
    while len(worst_rows) < 3:
        i = len(worst_rows) + 1
        worst_rows.append(f"|   {i} | (không đủ case tệ để liệt kê) | - | - | - | - | - | - | - |")

    avg_a = safe_mean(list(a.values()))
    avg_b = safe_mean(list(b.values()))

    return f"""# RAG evaluation results

## Run information

| Field                              | Value |
| ----------------------------------- | ----- |
| Evaluation date                    | {context['run_date']} |
| Framework and version              | ragas {context['ragas_version']} |
| Evaluator model                    | {context['judge_provider']} / {context['judge_model']} |
| Generator model                    | {context['llm_provider']} / {context['llm_model']} |
| Embedding model                    | {context['embedding_provider']} / {context['embedding_model']} |
| Corpus version/commit              | {context['git_commit']} |
| Golden dataset size                | {context['dataset_size']} ({context['answerable_count']} answerable, {context['unanswerable_count']} out-of-domain) |
| `top_k`                            | {context['top_k']} |
| Fallback threshold and calibration | SCORE_THRESHOLD = {context['score_threshold']} (xem src/task9_retrieval_pipeline.py; [DRAFT — điền quan sát in-domain/out-of-domain cụ thể của nhóm]) |

## Configurations

- **Config A — dense-only:** `retrieve(query, top_k={context['top_k']}, use_reranking=False)` — chỉ dùng `semantic_search()`, bỏ qua BM25 và RRF.
- **Config B — hybrid + RRF:** `retrieve(query, top_k={context['top_k']}, use_reranking=True)` — dense + BM25 gộp bằng RRF (mặc định của hệ thống).

Hai config dùng cùng golden dataset, cùng generator ({context['llm_provider']}/{context['llm_model']}), cùng `SYSTEM_PROMPT`, cùng `top_k` và cùng `SCORE_THRESHOLD`; chỉ khác retrieval strategy.

## Overall scores

(Trung bình trên {context['answerable_count']} case có `answerable=true`; {context['unanswerable_count']} case out-of-domain được chấm riêng ở mục Safe refusal bên dưới.)

| Metric            | Config A | Config B | Delta B−A |
| ----------------- | -------: | -------: | --------: |
| Faithfulness      | {fmt(a['faithfulness'])} | {fmt(b['faithfulness'])} | {delta('faithfulness')} |
| Answer relevance  | {fmt(a['answer_relevancy'])} | {fmt(b['answer_relevancy'])} | {delta('answer_relevancy')} |
| Context recall    | {fmt(a['context_recall'])} | {fmt(b['context_recall'])} | {delta('context_recall')} |
| Context precision | {fmt(a['context_precision'])} | {fmt(b['context_precision'])} | {delta('context_precision')} |
| **Average**       | {fmt(avg_a)} | {fmt(avg_b)} | {f"{avg_b - avg_a:+.3f}" if avg_a == avg_a and avg_b == avg_b else "n/a"} |

## Safe refusal (out-of-domain cases)

| Config | Refusal accuracy trên {context['unanswerable_count']} case out-of-domain |
| ------ | -------------------------------------------------------------------------: |
| A      | {fmt(context['refusal_A'])} |
| B      | {fmt(context['refusal_B'])} |

## A/B comparison

- Cấu hình tốt hơn: [DRAFT — dựa trên bảng Overall scores ở trên, điền config nào có Average cao hơn và có ý nghĩa hay không]
- Evidence: [DRAFT — trích 1-2 case cụ thể trong eval_raw_results.json cho thấy RRF giúp hoặc không giúp so với dense-only]
- Trade-off về latency/cost: xem cột `latency_s` theo case trong `eval_raw_results.json` (Config B chạy thêm BM25 + RRF nên tốn thêm thời gian CPU so với Config A; [DRAFT — điền con số latency trung bình đo được]).

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage             | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------------------- | ---------- |
{chr(10).join(worst_rows)}

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------- | ---------------- | ------------- |
|        1 | [DRAFT — điền theo worst case #1] | [DRAFT] | [DRAFT] | Chạy lại `python group_project/evaluation/run_evaluation.py` sau khi sửa và so sánh `eval_raw_results.json` |
|        2 | [DRAFT — điền theo worst case #2] | [DRAFT] | [DRAFT] | như trên |
|        3 | [DRAFT — điền theo worst case #3] | [DRAFT] | [DRAFT] | như trên |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | ------------------: | ---------- |
| (chưa chạy) | - | - | - | [DRAFT — điền nếu nhóm làm thêm HyDE/query expansion/reranker nâng cao theo mục Bonus của GRADING_RUBRIC.md] |
"""


def main() -> None:
    with GOLDEN_DATASET_PATH.open(encoding="utf-8") as fh:
        golden_dataset = json.load(fh)
    golden_by_id = {case["id"]: case for case in golden_dataset}

    all_records: dict[str, list[dict]] = {"A": [], "B": []}
    for config_key in ("A", "B"):
        print(f"== Running {CONFIGS[config_key]['label']} ==")
        for case in golden_dataset:
            print(f"  - {case['id']}: {case['question'][:60]}...")
            record = run_case(case, config_key, TOP_K)
            all_records[config_key].append(record)

    print("== Scoring with RAGAS ==")
    scores_A = score_with_ragas(all_records["A"], golden_by_id)
    scores_B = score_with_ragas(all_records["B"], golden_by_id)

    agg_A = aggregate(scores_A)
    agg_B = aggregate(scores_B)

    records_by_id_A = {r["id"]: r for r in all_records["A"]}
    records_by_id_B = {r["id"]: r for r in all_records["B"]}

    raw_output = {
        "run_date": datetime.now(timezone.utc).isoformat(),
        "top_k": TOP_K,
        "score_threshold": SCORE_THRESHOLD,
        "config_A": {"records": all_records["A"], "per_case_scores": scores_A, "aggregate": agg_A},
        "config_B": {"records": all_records["B"], "per_case_scores": scores_B, "aggregate": agg_B},
    }
    RAW_RESULTS_PATH.write_text(
        json.dumps(raw_output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Raw results written to {RAW_RESULTS_PATH}")

    import subprocess

    try:
        git_commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT
        ).decode().strip()
    except Exception:
        git_commit = "unknown (chưa commit hoặc không phải git repo)"

    import ragas

    context = {
        "run_date": raw_output["run_date"],
        "ragas_version": getattr(ragas, "__version__", "unknown"),
        "judge_provider": os.getenv("RAGAS_LLM_PROVIDER", os.getenv("LLM_PROVIDER", "openai")),
        "judge_model": os.getenv("RAGAS_LLM_MODEL", os.getenv("LLM_MODEL", "")),
        "llm_provider": os.getenv("LLM_PROVIDER", "openai"),
        "llm_model": os.getenv("LLM_MODEL", ""),
        "embedding_provider": os.getenv("EMBEDDING_PROVIDER", "sentence_transformers"),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3"),
        "git_commit": git_commit,
        "dataset_size": len(golden_dataset),
        "answerable_count": sum(1 for c in golden_dataset if c.get("answerable", True)),
        "unanswerable_count": sum(1 for c in golden_dataset if not c.get("answerable", True)),
        "top_k": TOP_K,
        "score_threshold": SCORE_THRESHOLD,
        "agg": {"A": agg_A, "B": agg_B},
        "refusal_A": refusal_accuracy(all_records["A"]),
        "refusal_B": refusal_accuracy(all_records["B"]),
        "worst_B": worst_cases(scores_B, records_by_id_B),
        "golden_by_id": golden_by_id,
    }

    RESULT_MD_PATH.write_text(render_result_md(context), encoding="utf-8")
    print(f"RESULT.md written to {RESULT_MD_PATH}")
    print(
        "\nLƯU Ý: các ô đánh dấu [DRAFT — ...] cần bạn đọc eval_raw_results.json và "
        "điền nhận định/khuyến nghị thật — script không tự suy diễn nguyên nhân gốc rễ."
    )


if __name__ == "__main__":
    main()
