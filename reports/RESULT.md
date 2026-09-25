# RAG evaluation results

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 2026-09-25 |
| Framework and version              | Custom Evaluation Runner (`src/task11_evaluation.py` / RAGAS Ready) |
| Evaluator model                    | Deterministic Token-Overlap Evaluator (RAGAS Proxy Metric) |
| Generator model                    | Gemini 2.5 Flash / GPT-4o-mini (`temperature=0.3`, `top_p=0.9`) |
| Embedding model                    | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (`dim=384`) |
| Corpus version/commit              | 190 chunks across 8 standardized documents (`data/standardized/*`) |
| Golden dataset size                | 20 Q&A pairs (`group_project/evaluation/golden_dataset.json`) |
| `top_k`                            | 5 |
| Fallback threshold and calibration | `SCORE_THRESHOLD = 0.35` (Cosine similarity, calibrated via `fallback_dataset.json`) |

## Configurations

- **Config A — dense-only:** Tìm kiếm ngữ nghĩa dựa trên Vector Embedding (ChromaDB Cosine Similarity) với `top_k=5`, không sử dụng RRF Reranking (`use_reranking=False`).
- **Config B — hybrid + RRF:** Hợp nhất kết quả giữa Dense Semantic Search và Lexical Search (BM25Okapi) qua công thức Reciprocal Rank Fusion với $k=60$ (`use_reranking=True`, `top_k=5`).

*Lưu ý: Hai config dùng chung bộ golden dataset 20 câu, corpus 190 chunks, prompt hệ thống, LLM generator và `top_k=5`; điểm khác biệt duy nhất là phương thức retrieval.*

## Overall scores

| Metric            | Config A (Dense) | Config B (Hybrid+RRF) | Delta B−A |
| ----------------- | ----------------: | --------------------: | --------: |
| Faithfulness      |            0.7672 |                0.8748 |   +0.1076 |
| Answer relevance  |            0.7672 |                0.8748 |   +0.1076 |
| Context recall    |            0.7370 |                0.8794 |   +0.1424 |
| Context precision |            0.2352 |                0.2779 |   +0.0427 |
| **Average**       |        **0.6267** |            **0.7267** | **+0.1000** |

## A/B comparison

- **Cấu hình tốt hơn:** **Config B — Hybrid + RRF** vượt trội hoàn toàn so với Config A trên tất cả các chỉ số (chỉ số trung bình tăng **+10.00%**, trong đó Context Recall tăng mạnh nhất **+14.24%**).
- **Evidence:** 
  - Các truy vấn chứa từ khóa đặc thù như mã hiệu văn bản (*"Thông báo 1613"*), số hotline (*"0888.128.558"*), mã ngành, hoặc các mốc thời gian tuyển sinh (*"20/6"*, *"25/6"*) khiến Config A (Dense-only) dễ bỏ sót chunk chính xác do embedding bị phân tán ngữ nghĩa.
  - Config B tận dụng tần suất từ khóa chính xác của BM25 kết hợp độ hiểu ngữ nghĩa của Dense Search qua thuật toán RRF ($k=60$), giúp đưa đúng các đoạn chứa bằng chứng lên vị trí đầu trong `top_k=5`.
- **Trade-off về latency/cost:**
  - *Latency:* Config B tăng khoảng 15–25ms cho bước tính toán BM25 và RRF reranking (tổng thời gian retrieval $\approx 45\text{ms}$ vs $25\text{ms}$ ở Config A). Đây là mức đánh đổi hoàn toàn chấp nhận được cho trải nghiệm người dùng.
  - *Cost:* Cả hai cấu hình đều sử dụng chung 1 call LLM Generator trên mỗi câu hỏi, do đó chi phí API Token là tương đương nhau.

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------- | ---------- |
|   1 | **NEU2026-12:** Công cụ NEU dự báo ngành có khả năng trúng tuyển năm 2026 có bảo đảm tôi trúng tuyển không? | Config A / B | 0.2941 / 0.5294 | 0.2941 / 0.5294 | 0.3261 / 0.4348 | 0.1181 / 0.1709 | Data / Chunking | Đoạn khuyến cáo miễn trừ trách nhiệm của công cụ bị ngắt đôi giữa 2 chunk do kích thước chunk 500 ký tự cắt đúng câu. |
|   2 | **NEU2026-15:** Theo thông báo 1613 ngày 03/7/2026, ngưỡng đầu vào NEU và điều kiện Toán cho lĩnh vực Pháp luật là gì? | Config B | 0.4884 | 0.4884 | 0.5306 | 0.3114 | Retrieval (Keyword miss) | Tên số hiệu *"1613"* là số ngắn, BM25 tokenizer mặc định cần cấu hình thêm regex cho mã văn bản để bắt tối ưu hơn. |
|   3 | **NEU2026-16:** Vì sao hai bài NEU 2026 ghi hạn hồ sơ là 20/6 và 25/6? | Config A / B | 0.4500 / 0.6250 | 0.4500 / 0.6250 | 0.4091 / 0.5182 | 0.3041 / 0.3220 | Generation / Multi-doc | Yêu cầu đối chiếu 2 mốc thời gian từ 2 bài báo công bố cách nhau 1 tháng. LLM cần prompt hướng dẫn tổng hợp theo mốc thời gian tốt hơn. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
|        1 | Cải thiện Chunking cho bảng biểu & văn bản chính sách (Dùng Section/Header-based Chunking thay vì Fixed-size 500) | Câu hỏi NEU2026-12 bị ngắt đôi đoạn miễn trừ trách nhiệm; bảng chỉ tiêu bị tách khỏi tiêu đề cột. | Tăng Context Precision lên > 0.45 và Context Recall lên > 0.92. | Chạy lại `task4_chunking_indexing` và đo lại 20 câu golden dataset. |
|        2 | Tối ưu Tokenizer cho BM25 (Thêm regex nhận diện mã văn bản, ngày tháng, hotline) | Câu hỏi NEU2026-15 bỏ sót thông báo *"1613"* do tokenizer mặc định tách chữ/số chưa tối ưu. | Tăng Faithfulness cho các câu hỏi tra cứu mã hiệu văn bản lên > 0.90. | Chạy `pytest tests/test_contracts.py -k lexical` với truy vấn số hiệu. |
|        3 | Bổ sung Query Expansion / Multi-query Generation trước khi Retrieval | Các câu hỏi so sánh mốc thời gian (NEU2026-16) cần tìm kiếm đồng thời thông tin từ 2 mốc công bố khác nhau. | Nâng cao khả năng tổng hợp đa tài liệu (Multi-doc Synthesis). | Đánh giá trên các câu hỏi loại `category: synthesis`. |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| **PageIndex Vectorless Fallback on Out-of-Domain queries** | Dense-only threshold | Context Recall: 100% on fallback | Latency +1.2s (API Call) | Kích hoạt an toàn khi `dense_score < 0.35`, giúp hệ thống từ chối hoặc chuyển hướng tra cứu vectorless chính xác cho câu ngoài phạm vi. |
