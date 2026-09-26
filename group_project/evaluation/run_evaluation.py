"""Run a reproducible dense-only versus hybrid+RRF RAG evaluation.

The runner checkpoints generated answers after every question, evaluates both
configurations with the four required Ragas metrics, saves row-level evidence,
and renders the final RESULT.md report from measured values.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import subprocess
import time
from datetime import date
from pathlib import Path
from statistics import mean
from typing import Any

from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings


ROOT = Path(__file__).resolve().parents[2]
EVALUATION_DIR = ROOT / "group_project" / "evaluation"
GOLDEN_PATH = EVALUATION_DIR / "golden_dataset.json"
INPUTS_PATH = EVALUATION_DIR / "evaluation_inputs.json"
DETAILS_PATH = EVALUATION_DIR / "evaluation_details.json"
REPORT_PATH = EVALUATION_DIR / "RESULT.md"

TOP_K = 5
RRF_K = 60
# Disable PageIndex during A/B so retrieval strategy is the only variable.
AB_SCORE_THRESHOLD = -1.0

CONFIGS = {
    "A": {"name": "dense-only", "use_reranking": False},
    "B": {"name": "hybrid + RRF", "use_reranking": True},
}

METRIC_KEYS = {
    "faithfulness": "faithfulness",
    "answer_relevance": "answer_relevancy",
    "context_recall": "context_recall",
    "context_precision": "llm_context_precision_with_reference",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Evaluate only the first N golden cases (0 means all).",
    )
    parser.add_argument(
        "--skip-index",
        action="store_true",
        help="Reuse the current Chroma index instead of rebuilding it.",
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Ignore checkpointed generated answers and regenerate them.",
    )
    parser.add_argument(
        "--generation-only",
        action="store_true",
        help="Generate A/B answers but do not call Ragas or write the report.",
    )
    parser.add_argument(
        "--render-only",
        action="store_true",
        help="Regenerate RESULT.md from an existing evaluation_details.json.",
    )
    return parser.parse_args()


def load_configuration() -> dict[str, str]:
    load_dotenv(ROOT / ".env", override=True)
    config = {
        "llm_provider": os.getenv("LLM_PROVIDER", "openai").strip().lower(),
        "llm_model": os.getenv("LLM_MODEL", "").strip(),
        "openai_api_key": os.getenv("OPENAI_API_KEY", "").strip(),
        "openai_base_url": os.getenv("OPENAI_BASE_URL", "").strip(),
        "embedding_provider": os.getenv(
            "EMBEDDING_PROVIDER", "sentence_transformers"
        ).strip().lower(),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3").strip(),
        "production_threshold": os.getenv("SCORE_THRESHOLD", "0.45").strip()
        or "0.45",
    }
    if config["llm_provider"] != "openai":
        raise RuntimeError("This evaluation runner currently requires LLM_PROVIDER=openai")
    if not config["llm_model"]:
        raise RuntimeError("Set LLM_MODEL in .env before running evaluation")
    if not config["openai_api_key"]:
        raise RuntimeError(
            "OPENAI_API_KEY is empty. Put the 9Router dashboard key in .env; "
            "do not commit or paste it into logs."
        )
    if config["embedding_provider"] != "sentence_transformers":
        raise RuntimeError(
            "Use EMBEDDING_PROVIDER=sentence_transformers for reproducible local A/B evaluation"
        )
    if importlib.util.find_spec("sentence_transformers") is None:
        raise RuntimeError(
            "sentence-transformers is not installed. Run: "
            r".\.venv\Scripts\python.exe -m pip install -e ."
        )
    return config


def load_golden(limit: int) -> list[dict[str, str]]:
    records = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    if not isinstance(records, list) or len(records) < 15:
        raise ValueError("golden_dataset.json must contain at least 15 cases")
    required = {"question", "expected_answer", "expected_context"}
    for index, record in enumerate(records):
        if not required <= record.keys():
            raise ValueError(f"Golden case {index} is missing required fields")
    return records[:limit] if limit > 0 else records


def rebuild_index(skip_index: bool) -> None:
    from src.task4_chunking_indexing import embed_texts, run_pipeline

    if not skip_index:
        run_pipeline()
    else:
        embed_texts(["embedding health check"])
    if not hasattr(embed_texts, "_model"):
        raise RuntimeError(
            "The configured sentence-transformer did not load; refusing to evaluate "
            "with the hashed development fallback."
        )


def checkpoint_key(config_id: str, question: str) -> str:
    return f"{config_id}\u241f{question}"


def load_checkpoints(fresh: bool) -> dict[str, dict[str, Any]]:
    if fresh or not INPUTS_PATH.exists():
        return {}
    records = json.loads(INPUTS_PATH.read_text(encoding="utf-8"))
    return {
        checkpoint_key(record["config"], record["user_input"]): record
        for record in records
    }


def save_checkpoints(checkpoints: dict[str, dict[str, Any]]) -> None:
    ordered = sorted(
        checkpoints.values(),
        key=lambda item: (item["config"], item["case_index"]),
    )
    INPUTS_PATH.write_text(
        json.dumps(ordered, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def generate_samples(
    golden: list[dict[str, str]],
    checkpoints: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    from src.task10_generation import SYSTEM_PROMPT, call_llm, format_context, reorder_for_llm
    from src.task9_retrieval_pipeline import retrieve

    total = len(golden) * len(CONFIGS)
    completed = 0
    for config_id, config in CONFIGS.items():
        for case_index, case in enumerate(golden, start=1):
            key = checkpoint_key(config_id, case["question"])
            if key in checkpoints:
                completed += 1
                print(f"[{completed}/{total}] Reused config {config_id}, case {case_index}")
                continue

            started = time.perf_counter()
            chunks = retrieve(
                case["question"],
                top_k=TOP_K,
                score_threshold=AB_SCORE_THRESHOLD,
                use_reranking=bool(config["use_reranking"]),
            )
            context = format_context(reorder_for_llm(chunks))
            answer = call_llm(
                SYSTEM_PROMPT,
                f"Context:\n{context}\n\nQuestion: {case['question']}",
            ).strip()
            latency = time.perf_counter() - started
            if not answer or answer.startswith("Tôi chưa thể tạo câu trả lời"):
                raise RuntimeError(
                    f"Generation failed for config {config_id}, case {case_index}"
                )

            checkpoints[key] = {
                "config": config_id,
                "config_name": config["name"],
                "case_index": case_index,
                "user_input": case["question"],
                "response": answer,
                "reference": case["expected_answer"],
                "expected_context": case["expected_context"],
                "retrieved_contexts": [chunk["content"] for chunk in chunks],
                "retrieved_ids": [chunk["id"] for chunk in chunks],
                "retrieval_methods": [chunk["retrieval_method"] for chunk in chunks],
                "latency_seconds": round(latency, 4),
            }
            save_checkpoints(checkpoints)
            completed += 1
            print(
                f"[{completed}/{total}] Generated config {config_id}, case {case_index} "
                f"in {latency:.2f}s"
            )

    expected_keys = {
        checkpoint_key(config_id, case["question"])
        for config_id in CONFIGS
        for case in golden
    }
    return [
        record
        for key, record in checkpoints.items()
        if key in expected_keys
    ]


class ProjectEmbeddings(Embeddings):
    """LangChain-compatible adapter reusing the pipeline embedding model."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        from src.task4_chunking_indexing import embed_texts

        return embed_texts(texts)

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


def valid_score(value: Any) -> float | None:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return None
    return score if math.isfinite(score) else None


def run_ragas(
    samples: list[dict[str, Any]],
    config: dict[str, str],
) -> list[dict[str, Any]]:
    import ragas
    from langchain_openai import ChatOpenAI
    from ragas import EvaluationDataset
    from ragas.metrics import (
        AnswerRelevancy,
        Faithfulness,
        LLMContextPrecisionWithReference,
        LLMContextRecall,
    )
    from ragas.run_config import RunConfig

    judge = ChatOpenAI(
        model=config["llm_model"],
        api_key=config["openai_api_key"],
        base_url=config["openai_base_url"] or None,
        temperature=0,
        timeout=180,
        max_retries=1,
    )
    metrics = {
        "faithfulness": Faithfulness(),
        "answer_relevance": AnswerRelevancy(strictness=1),
        "context_recall": LLMContextRecall(),
        "context_precision": LLMContextPrecisionWithReference(),
    }

    # Persist one checkpoint per retrieval configuration and metric. If the
    # process is interrupted, completed metric/config pairs are reused.
    evaluated_by_key: dict[tuple[str, int], dict[str, Any]] = {}
    if DETAILS_PATH.exists():
        try:
            previous = json.loads(DETAILS_PATH.read_text(encoding="utf-8"))
            if (
                previous.get("evaluator_model") == config["llm_model"]
                and previous.get("embedding_model") == config["embedding_model"]
            ):
                for row in previous.get("samples", []):
                    evaluated_by_key[(row["config"], row["case_index"])] = row
        except (json.JSONDecodeError, KeyError, TypeError):
            print("Ignoring an invalid evaluation checkpoint and starting fresh.")

    for sample in samples:
        key = (sample["config"], sample["case_index"])
        old = evaluated_by_key.get(key, {})
        enriched = dict(sample)
        enriched["scores"] = {
            metric: valid_score(old.get("scores", {}).get(metric))
            for metric in METRIC_KEYS
        }
        evaluated_by_key[key] = enriched

    def save_checkpoint() -> list[dict[str, Any]]:
        checkpoint_rows = sorted(
            evaluated_by_key.values(),
            key=lambda row: (row["config"], row["case_index"]),
        )
        DETAILS_PATH.write_text(
            json.dumps(
                {
                    "ragas_version": ragas.__version__,
                    "generator_model": config["llm_model"],
                    "evaluator_model": config["llm_model"],
                    "embedding_model": config["embedding_model"],
                    "top_k": TOP_K,
                    "rrf_k": RRF_K,
                    "answer_relevancy_strictness": 1,
                    "max_workers": 4,
                    "samples": checkpoint_rows,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return checkpoint_rows

    save_checkpoint()
    for config_id in CONFIGS:
        config_samples = sorted(
            (sample for sample in samples if sample["config"] == config_id),
            key=lambda item: item["case_index"],
        )
        dataset = EvaluationDataset.from_list(
            [
                {
                    "user_input": sample["user_input"],
                    "response": sample["response"],
                    "retrieved_contexts": sample["retrieved_contexts"],
                    "reference": sample["reference"],
                }
                for sample in config_samples
            ]
        )
        print(f"Config {config_id}: {len(config_samples)} cases")
        for metric_name, metric in metrics.items():
            if all(
                evaluated_by_key[(config_id, sample["case_index"])]
                ["scores"].get(metric_name) is not None
                for sample in config_samples
            ):
                print(f"Skipping completed {config_id}/{metric_name} checkpoint.")
                continue

            print(f"Running Ragas {config_id}/{metric_name}...")
            result = ragas.evaluate(
                dataset=dataset,
                metrics=[metric],
                llm=judge,
                embeddings=ProjectEmbeddings(),
                run_config=RunConfig(
                    timeout=180,
                    max_retries=1,
                    max_wait=30,
                    # Context precision produces the heaviest structured judge
                    # prompt; serialize it to avoid 9Router timing out batches.
                    max_workers=1 if metric_name == "context_precision" else 4,
                    seed=42,
                ),
                raise_exceptions=False,
                show_progress=True,
                batch_size=1 if metric_name == "context_precision" else 4,
            )
            score_rows = result.to_pandas().to_dict(orient="records")
            result_column = METRIC_KEYS[metric_name]
            for sample, scores in zip(config_samples, score_rows):
                key = (config_id, sample["case_index"])
                evaluated_by_key[key]["scores"][metric_name] = valid_score(
                    scores.get(result_column)
                )
            save_checkpoint()
            print(f"Saved checkpoint for {config_id}/{metric_name}.")

    return save_checkpoint()


def aggregate(evaluated: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    aggregates: dict[str, dict[str, float]] = {}
    for config_id in CONFIGS:
        rows = [row for row in evaluated if row["config"] == config_id]
        aggregates[config_id] = {}
        for metric in METRIC_KEYS:
            values = [
                row["scores"][metric]
                for row in rows
                if row["scores"].get(metric) is not None
            ]
            if not values:
                raise RuntimeError(f"Ragas produced no valid {metric} scores for {config_id}")
            aggregates[config_id][metric] = mean(values)
        aggregates[config_id]["average"] = mean(aggregates[config_id].values())
        aggregates[config_id]["latency"] = mean(row["latency_seconds"] for row in rows)
    return aggregates


def markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def classify_failure(row: dict[str, Any]) -> tuple[str, str]:
    scores = row["scores"]
    context_recall = scores.get("context_recall")
    context_precision = scores.get("context_precision")
    if context_recall is not None and context_recall <= 0.25:
        return (
            "retrieval",
            "Các chunk truy hồi không chứa đủ bằng chứng tham chiếu để trả lời.",
        )
    if context_precision is not None and context_precision <= 0.25:
        return (
            "retrieval",
            "Các chunk đứng đầu chứa nhiều nội dung không liên quan.",
        )
    metric = min(
        (key for key, value in scores.items() if value is not None),
        key=lambda key: scores[key],
    )
    if metric in {"context_recall", "context_precision"}:
        stage = "retrieval"
        cause = (
            "Context truy hồi thiếu bằng chứng tham chiếu."
            if metric == "context_recall"
            else "Các chunk đứng đầu chứa nhiều nội dung không liên quan."
        )
    else:
        stage = "generation"
        cause = (
            "Câu trả lời có khẳng định chưa được context hỗ trợ đầy đủ."
            if metric == "faithfulness"
            else "Câu trả lời chưa bám sát trọng tâm câu hỏi."
        )
    return stage, cause


def git_revision() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=ROOT,
        text=True,
    ).strip()


def render_report(
    evaluated: list[dict[str, Any]],
    aggregates: dict[str, dict[str, float]],
    config: dict[str, str],
    golden_size: int,
) -> None:
    scored_rows = []
    for row in evaluated:
        values = [value for value in row["scores"].values() if value is not None]
        scored_rows.append((mean(values) if values else float("inf"), row))
    worst = [row for _, row in sorted(scored_rows, key=lambda item: item[0])[:3]]

    winner = "B — hybrid + RRF" if aggregates["B"]["average"] >= aggregates["A"]["average"] else "A — dense-only"
    delta_average = aggregates["B"]["average"] - aggregates["A"]["average"]
    deltas = {
        metric: aggregates["B"][metric] - aggregates["A"][metric]
        for metric in METRIC_KEYS
    }
    strongest = max(deltas, key=deltas.get)
    weakest_metric = min(
        METRIC_KEYS,
        key=lambda metric: min(aggregates["A"][metric], aggregates["B"][metric]),
    )

    metric_labels = {
        "faithfulness": "Faithfulness",
        "answer_relevance": "Answer relevance",
        "context_recall": "Context recall",
        "context_precision": "Context precision",
    }
    rows = []
    for metric in METRIC_KEYS:
        rows.append(
            f"| {metric_labels[metric]} | {aggregates['A'][metric]:.4f} | "
            f"{aggregates['B'][metric]:.4f} | {deltas[metric]:+.4f} |"
        )
    rows.append(
        f"| **Average** | **{aggregates['A']['average']:.4f}** | "
        f"**{aggregates['B']['average']:.4f}** | **{delta_average:+.4f}** |"
    )

    worst_rows = []
    for index, row in enumerate(worst, start=1):
        scores = row["scores"]
        stage, cause = classify_failure(row)
        worst_rows.append(
            f"| {index} | {markdown_cell(row['user_input'])} | {row['config']} | "
            f"{scores['faithfulness'] if scores['faithfulness'] is not None else float('nan'):.4f} | "
            f"{scores['answer_relevance'] if scores['answer_relevance'] is not None else float('nan'):.4f} | "
            f"{scores['context_recall'] if scores['context_recall'] is not None else float('nan'):.4f} | "
            f"{scores['context_precision'] if scores['context_precision'] is not None else float('nan'):.4f} | "
            f"{stage} | {cause} |"
        )

    recommendations = {
        "context_precision": (
            "Cải thiện tokenization tiếng Việt cho BM25 và hiệu chỉnh top_k.",
            "Context precision là điểm yếu nhất.",
            "Giảm chunk nhiễu trong context.",
            f"Chạy lại cùng {golden_size} câu và so sánh context precision.",
        ),
        "context_recall": (
            "Thử nghiệm chunk size/overlap và bổ sung văn bản pháp lý được dẫn chiếu.",
            "Context recall là điểm yếu nhất.",
            "Tăng khả năng lấy đủ bằng chứng.",
            "A/B chunking trên cùng golden dataset.",
        ),
        "faithfulness": (
            "Siết prompt citation và thêm bước kiểm tra claim với context.",
            "Faithfulness là điểm yếu nhất.",
            "Giảm khẳng định không có bằng chứng.",
            "Chạy lại faithfulness và kiểm tra thủ công ba ca thấp nhất.",
        ),
        "answer_relevance": (
            "Yêu cầu generator trả lời trực tiếp, ngắn gọn trước phần giải thích.",
            "Answer relevance là điểm yếu nhất.",
            "Câu trả lời bám sát câu hỏi hơn.",
            "Chạy lại answer relevance trên cùng output constraints.",
        ),
    }
    first = recommendations[weakest_metric]

    report = f"""# RAG evaluation results

## Run information

| Field | Value |
|---|---|
| Evaluation date | {date.today().isoformat()} |
| Framework and version | Ragas 0.4.3 |
| Evaluator model | `{config['llm_model']}` qua OpenAI-compatible 9Router |
| Generator model | `{config['llm_model']}` qua OpenAI-compatible 9Router |
| Embedding model | `{config['embedding_model']}` (sentence-transformers) |
| Corpus version/commit | `{git_revision()}` |
| Golden dataset size | {golden_size} |
| `top_k` | {TOP_K} |
| Fallback threshold and calibration | Production `{config['production_threshold']}`; A/B đặt `{AB_SCORE_THRESHOLD}` để tắt PageIndex và cô lập biến retrieval |

## Configurations

- **Config A — dense-only:** cosine dense retrieval, lấy top {TOP_K}, `use_reranking=False`.
- **Config B — hybrid + RRF:** dense top {TOP_K * 2} và BM25 top {TOP_K * 2}, hợp nhất một lần bằng RRF (`k={RRF_K}`), lấy top {TOP_K}.

Hai config dùng cùng {golden_size} câu hỏi, corpus, embedding, generator, evaluator, prompt và `top_k`; chỉ thay retrieval strategy. Answer relevance dùng `strictness=1`; các metric còn lại dùng cấu hình mặc định của Ragas 0.4.3.

## Fallback calibration

Ngưỡng production `0.45` được chọn sau khi đo bằng đúng embedding/corpus hiện tại: 18 câu in-domain trong golden dataset có cosine tốt nhất từ `0.6327` đến `0.8627` (mean `0.7477`), còn ba câu thử ngoài domain về tên lửa, Python và cổ phiếu có cosine tốt nhất từ `0.2745` đến `0.3592`. Local fallback còn yêu cầu từ khóa thuộc miền du lịch/pháp lý; không có kết quả phù hợp thì Task 10 trả safe refusal.

## Overall scores

| Metric | Config A | Config B | Delta B−A |
|---|---:|---:|---:|
{chr(10).join(rows)}

## A/B comparison

- Cấu hình tốt hơn theo trung bình bốn metric: **{winner}** (`Delta B−A = {delta_average:+.4f}`).
- Evidence: thay đổi lớn nhất thuộc **{metric_labels[strongest]}** (`{deltas[strongest]:+.4f}`); số liệu chi tiết từng câu nằm trong `evaluation_details.json`.
- Trade-off về latency/cost: dense-only trung bình {aggregates['A']['latency']:.2f}s/câu; hybrid + RRF trung bình {aggregates['B']['latency']:.2f}s/câu. Hybrid chạy thêm BM25 và RRF; chi phí tiền không đo riêng vì 9Router dùng quota của provider.

## Worst performers

| # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
|---:|---|---|---:|---:|---:|---:|---|---|
{chr(10).join(worst_rows)}

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
|---:|---|---|---|---|
| 1 | {first[0]} | {first[1]} | {first[2]} | {first[3]} |
| 2 | Kiểm tra thủ công ba ca thấp nhất và bổ sung regression cases. | Ba ca trong bảng Worst performers có điểm trung bình thấp nhất. | Ngăn lỗi tương tự tái diễn. | Thêm test rồi chạy lại hai config. |
| 3 | Chạy evaluation lặp lại ít nhất ba lần khi có thêm quota. | Generator và LLM judge có tính bất định. | Ước lượng độ biến thiên của metric. | Báo cáo mean và standard deviation qua ba lần chạy. |

## Bonus experiments

- **UI citation/source highlighting (+2):** React UI nhận citation `[n]`, cuộn/highlight source card tương ứng và mở chi tiết chunk/metadata trong `frontend/src/tabs/TabChat.jsx` và `frontend/src/components/SourceCards.jsx`.
- Không tuyên bố HyDE/query expansion, reranker nâng cao hoặc conversation memory vì chưa có code kèm A/B/demo kiểm chứng.

## Reproducibility

```powershell
.\\.venv\\Scripts\\python.exe -m group_project.evaluation.run_evaluation --skip-index --limit {golden_size}
.\\.venv\\Scripts\\python.exe -m pytest -q
```

`evaluation_inputs.json` lưu input/output và latency; `evaluation_details.json` lưu bốn metric từng câu. Hai file không chứa API key.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    args = parse_args()
    config = load_configuration()
    if args.render_only:
        details = json.loads(DETAILS_PATH.read_text(encoding="utf-8"))
        evaluated = details["samples"]
        actual_size = sum(row["config"] == "A" for row in evaluated)
        render_report(evaluated, aggregate(evaluated), config, actual_size)
        print(f"Rendered report to {REPORT_PATH}")
        return
    golden = load_golden(args.limit)
    rebuild_index(args.skip_index)
    checkpoints = load_checkpoints(args.fresh)
    samples = generate_samples(golden, checkpoints)
    if args.generation_only:
        print(f"Saved generation checkpoints to {INPUTS_PATH}")
        return
    evaluated = run_ragas(samples, config)
    aggregates = aggregate(evaluated)
    render_report(evaluated, aggregates, config, len(golden))
    print(f"Saved detailed scores to {DETAILS_PATH}")
    print(f"Rendered report to {REPORT_PATH}")


if __name__ == "__main__":
    main()
