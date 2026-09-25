"""Compare dense-only and hybrid RRF on the same grounded questions.

Run from project root: python -m group_project.evaluation.evaluate_ab
Metrics are source-level retrieval metrics, not Ragas scores.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from time import perf_counter

from src.task9_retrieval_pipeline import retrieve


HERE = Path(__file__).resolve().parent
TOP_K = 5
EXPECTED_SOURCE = re.compile(r"^(news|legal)/[^:\s]+\.md:")


def load_cases() -> list[dict]:
    path = HERE / "golden_dataset.json"
    cases = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(cases, list) or len(cases) < 15:
        raise ValueError("Cần ít nhất 15 câu hỏi trong golden_dataset.json")
    for index, case in enumerate(cases, 1):
        if not all(str(case.get(field, "")).strip() for field in (
            "question", "expected_answer", "expected_context"
        )):
            raise ValueError(f"Câu {index} thiếu question/expected_answer/expected_context")
        match = EXPECTED_SOURCE.match(case["expected_context"])
        if match is None:
            raise ValueError(f"Câu {index}: expected_context cần bắt đầu bằng news/file.md: hoặc legal/file.md:")
        case["expected_source"] = match.group(0)[:-1]
    return cases


def source_for(result: dict) -> str:
    """Normalize source names from both local chunks and Chroma metadata."""
    source = str(result.get("metadata", {}).get("source", ""))
    if source.startswith(("news/", "legal/")):
        return source.replace("\\", "/")
    doc_type = result.get("metadata", {}).get("doc_type")
    return f"{doc_type}/{source}" if doc_type in ("news", "legal") else source


def evaluate_case(case: dict, use_reranking: bool) -> dict:
    start = perf_counter()
    results = retrieve(case["question"], top_k=TOP_K,
                       use_reranking=use_reranking)
    elapsed = perf_counter() - start
    if not isinstance(results, list):
        raise TypeError("retrieve() phải trả về list")
    sources = [source_for(item) for item in results]
    if len(sources) > TOP_K:
        raise ValueError("retrieve() trả vượt top_k")
    expected = case["expected_source"]
    first_rank = next((i for i, value in enumerate(sources, 1)
                       if value == expected), None)
    return {
        "question": case["question"],
        "expected_answer": case["expected_answer"],
        "expected_source": expected,
        "source_ids": [item["id"] for item in results],
        "retrieved_sources": sources,
        "hit_at_5": int(first_rank is not None),
        "reciprocal_rank": 1 / first_rank if first_rank else 0.0,
        "first_rank": first_rank,
        "latency_seconds": round(elapsed, 3),
    }


def summarize(rows: list[dict]) -> dict:
    return {
        "hit_at_5": round(mean(row["hit_at_5"] for row in rows), 4),
        "mrr_at_5": round(mean(row["reciprocal_rank"] for row in rows), 4),
        "avg_latency_seconds": round(mean(row["latency_seconds"] for row in rows), 3),
    }


def write_report(data: dict) -> None:
    dense = data["summary"]["dense_only"]
    hybrid = data["summary"]["hybrid_rrf"]
    worst = sorted(
        zip(data["cases"]["dense_only"], data["cases"]["hybrid_rrf"]),
        key=lambda pair: (pair[1]["hit_at_5"], pair[1]["reciprocal_rank"]),
    )[:3]
    lines = [
        "# RAG evaluation results — Du lịch Ninh Bình", "",
        "## Run information", "",
        f"- Time (UTC): {data['run_at_utc']}",
        f"- Questions: {data['question_count']}; top_k: {data['top_k']}",
        "- Corpus: 3 tài liệu legal + 5 bài news; 15 câu kiểm tra lấy từ 5 bài news.",
        "- Phép đo: retrieval theo đúng file nguồn được ghi trong expected_context.",
        "- Dense-only và hybrid dùng cùng câu hỏi, top_k, corpus, embedding; "
        "hybrid thêm BM25 và RRF.", "",
        "## Overall scores", "",
        "| Metric | Dense-only | Hybrid + RRF | Delta (hybrid - dense) |",
        "|---|---:|---:|---:|",
    ]
    for key, label in (("hit_at_5", "Hit@5"), ("mrr_at_5", "MRR@5"),
                       ("avg_latency_seconds", "Avg latency (s)")):
        lines.append(f"| {label} | {dense[key]:.4f} | {hybrid[key]:.4f} | "
                     f"{hybrid[key] - dense[key]:+.4f} |")
    lines += [
        "", "## A/B comparison", "",
        "Hit@5 = tỷ lệ câu có ít nhất một chunk từ đúng file nguồn trong top 5. "
        "MRR@5 = trung bình nghịch đảo vị trí đầu tiên của đúng file nguồn.",
        "Điểm cao hơn của Hit@5 và MRR@5 là tốt hơn; thời gian thấp hơn là tốt hơn.",
        "Kết quả từng câu và danh sách ID được lưu ở ab_results.json.",
        "Đây là số đo retrieval theo file nguồn, không phải điểm Ragas hoặc "
        "đánh giá faithfulness của câu trả lời.", "",
        "## Worst performers", "",
    ]
    for d, h in worst:
        lines.append(f"- {h['question']} — nguồn chuẩn {h['expected_source']}; "
                     f"dense rank {d['first_rank'] or 'missing'}, "
                     f"hybrid rank {h['first_rank'] or 'missing'}.")
    lines += [
        "", "## Recommendations", "",
        "1. Xem từng câu bị miss trong ab_results.json, sửa nội dung corpus "
        "hoặc chunking dựa trên bằng chứng trước khi tăng top_k.",
        "2. Kiểm tra citation đến đúng chunk; test contract và kết quả theo file "
        "nguồn không đủ chứng minh mỗi lời đáp đều có dẫn chứng đúng.",
        "3. Kiểm chứng nguồn gốc ba PDF; bổ sung câu hỏi pháp lý có reference "
        "được đối chiếu trước khi đánh giá toàn corpus.",
        "4. Nếu bài lab yêu cầu Ragas, chạy thêm phép đo Ragas thật; "
        "không gắn nhãn Ragas cho các số đo trong báo cáo này.", "",
    ]
    (HERE / "RESULT.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    cases = load_cases()
    results = {"dense_only": [], "hybrid_rrf": []}
    for index, case in enumerate(cases, 1):
        # Alternate on the same question, making result comparison easy to audit.
        results["dense_only"].append(evaluate_case(case, False))
        results["hybrid_rrf"].append(evaluate_case(case, True))
        print(f"Done {index}/{len(cases)}: {case['question']}", flush=True)
    output = {
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "question_count": len(cases), "top_k": TOP_K,
        "summary": {label: summarize(rows) for label, rows in results.items()},
        "cases": results,
    }
    (HERE / "ab_results.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_report(output)
    print(json.dumps(output["summary"], ensure_ascii=False, indent=2))
    print("Saved: group_project/evaluation/ab_results.json and RESULT.md")


if __name__ == "__main__":
    main()

