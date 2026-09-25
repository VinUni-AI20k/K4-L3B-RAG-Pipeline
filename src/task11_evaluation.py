"""Evaluation runner for the Na handoff.

The runner keeps the corpus and questions fixed, evaluates dense-only (A) and
hybrid Dense+BM25+RRF (B), and stores raw evidence before aggregating metrics.
The overlap metrics are deterministic and can run without an LLM/API key.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .task9_retrieval_pipeline import retrieve

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "group_project" / "evaluation" / "golden_dataset.json"
OUTPUT_DIR = ROOT / "group_project" / "evaluation" / "runs"
TOKEN_RE = re.compile(r"[\wÀ-ỹ]+", re.UNICODE)


def tokens(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(text or "") if len(token) > 1}


def overlap(left: str, right: str) -> float:
    a, b = tokens(left), tokens(right)
    return len(a & b) / len(a) if a else 0.0


def score_case(case: dict[str, Any], results: list[dict[str, Any]]) -> dict[str, float]:
    expected = case.get("expected_context", "")
    answer = case.get("expected_answer", "")
    context = "\n".join(item.get("content", "") for item in results)
    # Deterministic proxy metrics: every numerator is recorded in the raw run.
    return {
        "faithfulness": overlap(answer, context),
        "answer_relevance": overlap(answer, context),
        "context_recall": overlap(expected, context),
        "context_precision": overlap(context, expected),
    }


def run(mode: str) -> dict[str, Any]:
    cases = json.loads(GOLDEN.read_text(encoding="utf-8"))
    use_reranking = mode == "hybrid"
    records = []
    for case in cases:
        results = retrieve(case["question"], top_k=5, use_reranking=use_reranking)
        records.append({
            "id": case.get("id"),
            "question": case["question"],
            "expected_answer": case.get("expected_answer", ""),
            "retrieved": results,
            "metrics": score_case(case, results),
        })
    metric_names = ("faithfulness", "answer_relevance", "context_recall", "context_precision")
    aggregate = {name: round(sum(r["metrics"][name] for r in records) / len(records), 4) for name in metric_names}
    return {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "configuration": {"mode": mode, "top_k": 5, "corpus": "data/standardized/*", "question_count": len(cases), "score_threshold": 0.35, "metric_note": "deterministic token-overlap proxy; install/configure an LLM evaluator for RAGAS scores"},
        "metrics": aggregate,
        "records": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("dense", "hybrid", "both"), default="both")
    args = parser.parse_args()
    modes = ("dense", "hybrid") if args.mode == "both" else (args.mode,)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for mode in modes:
        output = OUTPUT_DIR / f"{mode}_run.json"
        output.write_text(json.dumps(run(mode), ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Saved {output}")


if __name__ == "__main__":
    main()
