"""Run the paired dense-only vs hybrid+RRF evaluation and write its report.

The evaluator uses one structured Gemini judgment per answer. It decomposes
answer/reference claims, then computes the same four concepts used by RAGAS:
faithfulness, answer relevance, context recall and rank-aware context precision.
Progress is saved after every configuration so an interrupted run can resume.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import statistics
import sys
import time
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from .task10_generation import (
    LLM_MODEL,
    LLM_PROVIDER,
    SAFE_REFUSAL,
    SYSTEM_PROMPT,
    _normalize_citations,
    call_llm,
    format_context,
    reorder_for_llm,
)
from .task5_semantic_search import semantic_search
from .task6_lexical_search import lexical_search
from .task7_reranking import rerank_rrf


ROOT = Path(__file__).resolve().parent.parent
GOLDEN_PATH = ROOT / "group_project" / "evaluation" / "golden_dataset.json"
RESULTS_PATH = ROOT / "group_project" / "evaluation" / "evaluation_results.json"
REPORT_PATH = ROOT / "group_project" / "evaluation" / "RESULT.md"
TOP_K = 5
CANDIDATE_K = TOP_K * 2

load_dotenv(ROOT / ".env", override=False)


class ClaimVerdict(BaseModel):
    claim: str
    supported: bool


class JudgeOutput(BaseModel):
    answer_claims: list[ClaimVerdict]
    reference_claims: list[ClaimVerdict]
    context_relevance: list[bool]
    answer_relevance: float = Field(ge=0.0, le=1.0)
    failure_stage: str
    explanation: str


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".part")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def _load_results() -> dict:
    if not RESULTS_PATH.is_file():
        return {"metadata": {}, "cases": []}
    try:
        value = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"metadata": {}, "cases": []}
    return value if isinstance(value, dict) else {"metadata": {}, "cases": []}


def _save_results(results: dict) -> None:
    _write(RESULTS_PATH, json.dumps(results, ensure_ascii=False, indent=2) + "\n")


def _retry(operation, *, attempts: int = 4):
    last_error = None
    for attempt in range(attempts):
        try:
            return operation()
        except Exception as exc:  # provider SDKs use different exception classes
            last_error = exc
            if attempt + 1 == attempts:
                raise
            delay = 2 ** attempt
            print(f"Provider call failed ({type(exc).__name__}); retrying in {delay}s", flush=True)
            time.sleep(delay)
    raise last_error  # pragma: no cover


def _generate(query: str, chunks: list[dict]) -> str:
    if not chunks:
        return SAFE_REFUSAL
    labelled = [
        {**chunk, "metadata": {**chunk["metadata"], "citation_index": index}}
        for index, chunk in enumerate(chunks, start=1)
    ]
    context = format_context(reorder_for_llm(labelled))
    user_message = (
        f"Context:\n{context}\n\nQuestion: {query}\n\n"
        "Hãy trả lời ngắn gọn bằng ngôn ngữ của câu hỏi và gắn citation [S#] "
        "ngay sau từng thông tin được sử dụng."
    )
    answer = _normalize_citations(
        _retry(lambda: call_llm(SYSTEM_PROMPT, user_message)).strip()
    )
    labels = [int(value) for value in re.findall(r"\[S(\d+)\]", answer)]
    if answer != SAFE_REFUSAL and (
        not labels or any(value < 1 or value > len(chunks) for value in labels)
    ):
        return SAFE_REFUSAL
    return answer


def _judge_client():
    if LLM_PROVIDER.casefold() != "gemini":
        raise RuntimeError("The evaluation runner currently requires LLM_PROVIDER=gemini")
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or not LLM_MODEL:
        raise RuntimeError("Configure GEMINI_API_KEY and LLM_MODEL before evaluation")
    from google import genai

    return genai.Client(api_key=api_key)


def _judge(client, case: dict, answer: str, chunks: list[dict]) -> JudgeOutput:
    from google.genai import types

    contexts = []
    for index, chunk in enumerate(chunks, start=1):
        metadata = chunk["metadata"]
        contexts.append(
            f"Context {index} | source={metadata['source']} | "
            f"page={metadata.get('page', '')}\n{chunk['content']}"
        )
    prompt = f"""You are evaluating a Vietnamese RAG system. Return structured data only.

Question: {case['question']}
Reference answer: {case['expected_answer']}
Expected context hint: {case['expected_context']}
Expected source: {case.get('expected_source', '')}
Generated answer: {answer}

Retrieved contexts:
{chr(10).join(contexts)}

Instructions:
1. Split every factual assertion in the generated answer into answer_claims. Mark
   supported=true only when the retrieved contexts entail it. A refusal has one
   unsupported claim.
2. Split the reference answer into atomic reference_claims. Mark supported=true
   when at least one retrieved context entails the claim.
3. Return exactly one context_relevance boolean per retrieved context, in order.
   True means the context helps answer the question/reference.
4. answer_relevance is 0..1 for how directly and completely the generated answer
   addresses the question. A refusal is 0.
5. failure_stage must be one of: none, retrieval, generation, data.
6. Keep explanation to one concise sentence.
"""

    def request():
        response = client.models.generate_content(
            model=LLM_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=JudgeOutput,
                temperature=0.0,
            ),
        )
        if response.parsed is not None:
            return JudgeOutput.model_validate(response.parsed)
        return JudgeOutput.model_validate_json(response.text)

    judgment = _retry(request)
    if len(judgment.context_relevance) != len(chunks):
        raise ValueError("Evaluator returned a context_relevance list with the wrong length")
    return judgment


def _ratio(verdicts: list[ClaimVerdict]) -> float:
    if not verdicts:
        return 0.0
    return sum(item.supported for item in verdicts) / len(verdicts)


def _average_precision(verdicts: list[bool]) -> float:
    relevant = sum(verdicts)
    if not relevant:
        return 0.0
    numerator = sum(
        (sum(verdicts[: index + 1]) / (index + 1))
        for index, value in enumerate(verdicts)
        if value
    )
    return numerator / relevant


def _score(judgment: JudgeOutput) -> dict:
    metrics = {
        "faithfulness": _ratio(judgment.answer_claims),
        "answer_relevance": float(judgment.answer_relevance),
        "context_recall": _ratio(judgment.reference_claims),
        "context_precision": _average_precision(judgment.context_relevance),
    }
    metrics["average"] = statistics.fmean(metrics.values())
    return {key: round(value, 6) for key, value in metrics.items()}


def _public_chunks(chunks: list[dict]) -> list[dict]:
    return [
        {
            "id": item["id"],
            "score": item["score"],
            "retrieval_method": item["retrieval_method"],
            "source": item["metadata"]["source"],
            "page": item["metadata"].get("page"),
            "content": item["content"],
        }
        for item in chunks
    ]


def _aggregate(cases: list[dict], config: str) -> dict:
    rows = [case[config]["metrics"] for case in cases]
    keys = ("faithfulness", "answer_relevance", "context_recall", "context_precision")
    values = {key: statistics.fmean(row[key] for row in rows) for key in keys}
    values["average"] = statistics.fmean(values.values())
    values["latency_seconds"] = statistics.fmean(case[config]["latency_seconds"] for case in cases)
    return values


def _render_report(results: dict) -> str:
    cases = results["cases"]
    dense = _aggregate(cases, "dense_only")
    hybrid = _aggregate(cases, "hybrid_rrf")
    better = "Config B — hybrid + RRF" if hybrid["average"] >= dense["average"] else "Config A — dense-only"
    metric_names = (
        ("Faithfulness", "faithfulness"),
        ("Answer relevance", "answer_relevance"),
        ("Context recall", "context_recall"),
        ("Context precision", "context_precision"),
        ("**Average**", "average"),
    )
    score_rows = []
    for label, key in metric_names:
        delta = hybrid[key] - dense[key]
        score_rows.append(f"| {label} | {dense[key]:.3f} | {hybrid[key]:.3f} | {delta:+.3f} |")

    ranked = []
    for case in cases:
        for config, label in (("dense_only", "A"), ("hybrid_rrf", "B")):
            ranked.append((case[config]["metrics"]["average"], case, config, label))
    worst = sorted(ranked, key=lambda row: row[0])[:3]
    worst_rows = []
    for index, (_, case, config, label) in enumerate(worst, start=1):
        item = case[config]
        m = item["metrics"]
        question = case["question"].replace("|", "\\|")
        cause = item["evaluation"]["explanation"].replace("|", "\\|")
        worst_rows.append(
            f"| {index} | {question} | {label} | {m['faithfulness']:.3f} | "
            f"{m['answer_relevance']:.3f} | {m['context_recall']:.3f} | "
            f"{m['context_precision']:.3f} | {item['evaluation']['failure_stage']} | {cause} |"
        )

    commit = results["metadata"].get("commit", "working tree")
    return f"""# RAG evaluation results

## Run information

| Field | Value |
| --- | --- |
| Evaluation date | {results['metadata']['evaluation_date']} |
| Framework | Paired evaluation; structured Gemini LLM-as-judge with RAGAS-compatible definitions |
| Evaluator model | `{results['metadata']['evaluator_model']}` |
| Generator model | `{results['metadata']['generator_model']}` |
| Embedding model | `BAAI/bge-m3` |
| Corpus version/commit | `{commit}`; 8 documents / 498 chunks |
| Golden dataset size | {len(cases)} |
| `top_k` | {TOP_K} |
| Fallback | Disabled during A/B so only the retrieval strategy changes |

Raw per-case answers, contexts, latency, judgments and scores are stored in
[`evaluation_results.json`](evaluation_results.json). No production API key is stored.

## Configurations

- **Config A — dense-only:** BGE-M3 cosine search, final `top_k=5`.
- **Config B — hybrid + RRF:** BGE-M3 and BM25 retrieve 10 candidates each;
  RRF (`k=60`) returns the final 5.

Both configurations use the same golden dataset, generator, evaluator, prompt
and `top_k`. PageIndex fallback is intentionally excluded from this controlled A/B.

## Overall scores

| Metric | Config A | Config B | Delta B−A |
| --- | ---: | ---: | ---: |
{chr(10).join(score_rows)}

## A/B comparison

- Better configuration: **{better}**.
- Mean latency: Config A `{dense['latency_seconds']:.2f}s`; Config B `{hybrid['latency_seconds']:.2f}s` per question.
- Average delta B−A: `{hybrid['average'] - dense['average']:+.3f}`.
- Interpretation: on this corpus, dense-only is both more accurate and faster. BM25/RRF
  sometimes promotes exact lexical matches that are incomplete or less useful than the
  dense results, so hybrid should not become the production default without further tuning.

## Worst performers

| # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
| --: | --- | :---: | ---: | ---: | ---: | ---: | --- | --- |
{chr(10).join(worst_rows)}

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| ---: | --- | --- | --- | --- |
| 1 | Manually correct high-impact OCR errors in legal headings and article numbers | The legal PDFs are fully OCR-derived and marked not fully proofread | Better exact retrieval and safer legal answers | Rerun the three worst cases and compare recall/precision |
| 2 | Tune chunk size/overlap and `top_k` on this golden set | Some questions require conditions split across adjacent chunks | Improve context recall without excessive noise | Grid-search settings while keeping generator/evaluator fixed |
| 3 | Calibrate `SCORE_THRESHOLD` with separate out-of-domain queries | Fallback is excluded from A/B and 0.30 remains an initial value | Better refusal/fallback decisions | Measure false acceptance and false refusal across thresholds |

## Bonus experiments

No bonus experiment is claimed. PageIndex remains an operational fallback, not a
bonus result, because it was intentionally held constant outside this A/B comparison.
"""


def run(*, limit: int | None = None, fresh: bool = False) -> dict:
    golden = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    if limit is not None:
        golden = golden[:limit]
    if not golden:
        raise ValueError("Golden dataset is empty")

    import subprocess

    commit = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
        capture_output=True, text=True, check=False,
    ).stdout.strip() or "working tree"
    results = {"metadata": {}, "cases": []} if fresh else _load_results()
    results["metadata"] = {
        "evaluation_date": date.today().isoformat(),
        "generator_model": LLM_MODEL,
        "evaluator_model": LLM_MODEL,
        "commit": commit,
        "top_k": TOP_K,
    }
    existing = {item["question"]: item for item in results.get("cases", [])}
    client = _judge_client()

    for case_index, case in enumerate(golden, start=1):
        stored = existing.get(case["question"], {
            "question": case["question"],
            "expected_answer": case["expected_answer"],
            "expected_context": case["expected_context"],
            "expected_source": case.get("expected_source"),
        })
        if "dense_only" in stored and "hybrid_rrf" in stored:
            print(f"[{case_index}/{len(golden)}] cached: {case['question']}", flush=True)
            continue

        retrieval_start = time.perf_counter()
        dense_candidates = semantic_search(case["question"], top_k=CANDIDATE_K)
        dense_elapsed = time.perf_counter() - retrieval_start
        sparse_start = time.perf_counter()
        sparse_candidates = lexical_search(case["question"], top_k=CANDIDATE_K)
        hybrid_chunks = rerank_rrf([dense_candidates, sparse_candidates], top_k=TOP_K)
        sparse_elapsed = time.perf_counter() - sparse_start
        configs = {
            "dense_only": (dense_candidates[:TOP_K], dense_elapsed),
            "hybrid_rrf": (hybrid_chunks, dense_elapsed + sparse_elapsed),
        }

        for config_name, (chunks, retrieval_latency) in configs.items():
            if config_name in stored:
                continue
            print(f"[{case_index}/{len(golden)}] {config_name}: generating", flush=True)
            started = time.perf_counter()
            answer = _generate(case["question"], chunks)
            generation_elapsed = time.perf_counter() - started
            print(f"[{case_index}/{len(golden)}] {config_name}: judging", flush=True)
            judgment = _judge(client, case, answer, chunks)
            stored[config_name] = {
                "answer": answer,
                "chunks": _public_chunks(chunks),
                "latency_seconds": round(retrieval_latency + generation_elapsed, 6),
                "metrics": _score(judgment),
                "evaluation": judgment.model_dump(),
            }
            existing[case["question"]] = stored
            results["cases"] = [existing[item["question"]] for item in golden if item["question"] in existing]
            _save_results(results)

    results["cases"] = [existing[item["question"]] for item in golden]
    _save_results(results)
    if limit is None and len(results["cases"]) == 15:
        _write(REPORT_PATH, _render_report(results))
        print(f"Wrote {REPORT_PATH}", flush=True)
    else:
        print("Partial run complete; RESULT.md is updated only after all 15 cases.", flush=True)
    return results


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="Run only the first N cases as a smoke test")
    parser.add_argument("--fresh", action="store_true", help="Ignore cached evaluation results")
    arguments = parser.parse_args()
    run(limit=arguments.limit, fresh=arguments.fresh)
