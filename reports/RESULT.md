# RAG evaluation results

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 2026-09-25 |
| Framework and version              | Deterministic retrieval audit, Python 3.11 |
| Evaluator model                    | N/A - chưa chạy evaluator LLM |
| Generator model                    | gpt-4o-mini (cấu hình trong `.env`) |
| Embedding model                    | sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |
| Corpus version/commit              | branch `tainangtre`, corpus commit `99c00fa` |
| Golden dataset size                | 15 |
| `top_k`                            | 3 |
| Fallback threshold and calibration | 0.6; in-domain dense score khoảng 0.72-0.86, out-of-domain khoảng 0.28-0.45 |

## Configurations

- **Config A — dense-only:** Task 5 semantic search, không RRF.
- **Config B — hybrid + RRF:** Task 5 + Task 6 BM25, hợp nhất bằng Task 7 RRF.

Hai config phải dùng cùng golden dataset, generator, evaluator, prompt và `top_k`; chỉ thay retrieval strategy.

## Overall scores

| Metric            | Config A | Config B | Delta B−A |
| ----------------- | -------: | -------: | --------: |
| Faithfulness      | N/A      | N/A      | N/A       |
| Answer relevance  | N/A      | N/A      | N/A       |
| Context recall    | 0.600    | 0.733    | +0.133    |
| Context precision | 0.289    | 0.356    | +0.067    |
| **Average**       | N/A      | N/A      | N/A       |

## A/B comparison

- Cấu hình tốt hơn: Config B - hybrid + RRF.
- Evidence: context recall tăng từ 0.600 lên 0.733 và context precision tăng từ 0.289 lên 0.356 trên 15 câu hỏi.
- Trade-off về latency/cost: hybrid phải chạy thêm BM25 và RRF; đổi lại cải thiện khả năng tìm đúng nguồn. LLM generation dùng cùng cấu hình nên chưa đo chênh lệch chi phí.

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage             | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------------------- | ---------- |
|   1 | Mã phương thức xét điểm ĐGNL ĐHQG TP.HCM của HUTECH năm 2026 là gì? | Config B | N/A | N/A | 0 | 0 | retrieval | Top-k chưa đưa đúng tài liệu thông tin tuyển sinh vào kết quả |
|   2 | Hạn cung cấp minh chứng xét học bạ HUTECH 2026 theo bài viết tuyển sinh là khi nào? | Config B | N/A | N/A | 0 | 0 | retrieval | Chunk chứa hạn minh chứng chưa được xếp vào top-k |
|   3 | Chính sách học bổng tuyển sinh HUTECH 2026 trong corpus có các mức chính nào? | Config B | N/A | N/A | 0 | 0 | retrieval | Chunk chính sách học bổng không nằm trong top-k dù câu hỏi chứa đúng chủ đề |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
|        1 | Tăng recall cho tài liệu dài bằng chunking theo section/table và metadata field | 4/15 hybrid cases chưa hit đúng expected source | Cải thiện context recall | Chạy lại audit 15 golden cases |
|        2 | Bổ sung query expansion cho mã phương thức, deadline và thông tin liên hệ | Các câu hỏi factual ngắn dễ bị chunk liên quan cạnh tranh | Cải thiện top-k precision | So sánh trên cùng golden set |
|        3 | Chạy evaluator LLM cho faithfulness và answer relevance | Hai metric này hiện chưa có số đo độc lập | Hoàn thiện đủ 4 metric | Chạy evaluator trên cả Config A và Config B |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| MiniLM dense vs TF-IDF fallback trong UI | MiniLM dense | N/A | TF-IDF không cần tải model thứ hai | Dùng làm baseline; BGE-M3 chưa tải hoàn chỉnh |
