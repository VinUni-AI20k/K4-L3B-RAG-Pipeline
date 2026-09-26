# RAG evaluation results

## Run information

| Field | Value |
| --- | --- |
| Evaluation date | 2026-09-26 |
| Framework | Paired evaluation; structured Gemini LLM-as-judge with RAGAS-compatible definitions |
| Evaluator model | `gemini-3.5-flash-lite` |
| Generator model | `gemini-3.5-flash-lite` |
| Embedding model | `BAAI/bge-m3` |
| Corpus version/commit | `6ab42db`; 8 documents / 498 chunks |
| Golden dataset size | 15 |
| `top_k` | 5 |
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
| Faithfulness | 1.000 | 0.933 | -0.067 |
| Answer relevance | 0.887 | 0.793 | -0.093 |
| Context recall | 0.886 | 0.809 | -0.077 |
| Context precision | 0.909 | 0.821 | -0.089 |
| **Average** | 0.920 | 0.839 | -0.081 |

## A/B comparison

- Better configuration: **Config A — dense-only**.
- Mean latency: Config A `4.46s`; Config B `7.45s` per question.
- Average delta B−A: `-0.081`.
- Interpretation: on this corpus, dense-only is both more accurate and faster. BM25/RRF
  sometimes promotes exact lexical matches that are incomplete or less useful than the
  dense results, so hybrid should not become the production default without further tuning.

## Worst performers

| # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
| --: | --- | :---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 | Một điểm du lịch phải có những dịch vụ và hạ tầng cụ thể nào theo Nghị định 168? | B | 0.000 | 0.000 | 0.667 | 0.806 | generation | Hệ thống từ chối trả lời dù ngữ cảnh chứa thông tin một phần. |
| 2 | Khách du lịch có những quyền cơ bản nào theo Luật Du lịch 2017? | B | 1.000 | 0.300 | 0.200 | 0.250 | generation | The generated answer is incomplete and only provides the first right mentioned in the law. |
| 3 | Điều gì làm sợi cao lầu Hội An trở nên đặc biệt theo bài viết? | B | 1.000 | 0.600 | 0.333 | 0.333 | generation | The generated answer is partially correct based on the context, but misses details mentioned in the reference answer such as the wood ash and udon-like texture. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| ---: | --- | --- | --- | --- |
| 1 | Manually correct high-impact OCR errors in legal headings and article numbers | The legal PDFs are fully OCR-derived and marked not fully proofread | Better exact retrieval and safer legal answers | Rerun the three worst cases and compare recall/precision |
| 2 | Tune chunk size/overlap and `top_k` on this golden set | Some questions require conditions split across adjacent chunks | Improve context recall without excessive noise | Grid-search settings while keeping generator/evaluator fixed |
| 3 | Calibrate `SCORE_THRESHOLD` with separate out-of-domain queries | Fallback is excluded from A/B and 0.30 remains an initial value | Better refusal/fallback decisions | Measure false acceptance and false refusal across thresholds |

## Bonus experiments

No bonus experiment is claimed. PageIndex remains an operational fallback, not a
bonus result, because it was intentionally held constant outside this A/B comparison.
