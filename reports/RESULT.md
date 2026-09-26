# RAG Evaluation Results

## Run Information

| Field | Value |
| --- | --- |
| Evaluation date | 2026-09-25 |
| Framework and version | ChromaDB 0.4+, rank-bm25 0.2.2, sentence-transformers 3.0+ |
| Evaluator model | GPT-4o-mini |
| Generator model | GPT-4o-mini |
| Embedding model | all-MiniLM-L6-v2 |
| Corpus version/commit | 3 legal docs (Luật Du lịch 2017, Quyết định 718, Kế hoạch 75 du lịch biển) + 10 bài viết du lịch Ninh Bình |
| Golden dataset size | 18 câu hỏi (16 in-domain + 2 out-of-domain) |
| `top_k` | 5 |
| Fallback threshold and calibration | 0.35 (hiệu chỉnh trên cosine score gốc: in-domain đạt 0.42 - 0.78, out-of-domain đạt < 0.28) |

## Configurations

- **Config A — Dense-only:** Truy vấn ngữ nghĩa dùng sentence-transformers `all-MiniLM-L6-v2` trên ChromaDB, lấy top_k=5 chunks có cosine similarity cao nhất.
- **Config B — Hybrid + RRF:** Kết hợp Semantic search (top 10) và Lexical search (BM25Okapi, top 10), áp dụng Reciprocal Rank Fusion (RRF với constant $k=60$) để gộp và tái xếp hạng, lấy top_k=5 chunks kết quả.

Hai cấu hình chạy trên cùng bộ câu hỏi chuẩn (18 câu), cùng mô hình generator (GPT-4o-mini), cùng prompt có trích dẫn ([Document N]) và cùng tham số `top_k=5`.

## Overall Scores

| Metric | Config A (Dense-only) | Config B (Hybrid + RRF) | Delta B − A |
| --- | ---: | ---: | ---: |
| Faithfulness | 0.81 | 0.91 | +0.10 |
| Answer relevance | 0.79 | 0.88 | +0.09 |
| Context recall | 0.74 | 0.86 | +0.12 |
| Context precision | 0.76 | 0.87 | +0.11 |
| **Average** | **0.775** | **0.880** | **+0.105** |

## A/B Comparison

- **Cấu hình tốt hơn:** **Config B (Hybrid + RRF)** vượt trội toàn diện trên cả 4 thước đo đánh giá.
- **Evidence:** 
  - Trong tài liệu pháp lý và du lịch, các từ khóa tên riêng (như *Trần Thái Vi, Hang Cả, Ngô Đồng, Vân Long, Yên Mạc*) và số hiệu điều khoản (*Điều 11, Điều 58, 718/QĐ-BVHTTDL*) khi tìm kiếm bằng Dense đơn thuần dễ bị phân tán do biểu diễn embedding không khớp tuyệt đối với từ hiếm. 
  - BM25 bắt chính xác các keyword này, sau đó thuật toán RRF dung hòa xếp hạng giúp tăng **Context Recall (+0.12)** và **Context Precision (+0.11)**.
- **Trade-off về latency/cost:**
  - **Latency:** BM25 trên tập 1.356 chunks mất thêm ~10-15ms, thuật toán RRF mất ~2ms. Tổng thời gian retrieval tăng không đáng kể so với trải nghiệm người dùng (< 20ms).
  - **Cost:** Chi phí token gọi LLM là tương đương nhau giữa 2 config vì đều giới hạn `top_k=5` chunks đưa vào ngữ cảnh.

## Worst Performers

| # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| 1 | Tuyến du lịch biển trọng điểm nào được định hướng phát triển tại Ninh Bình 2026-2030? | Config A | 0.70 | 0.72 | 0.60 | 0.65 | Retrieval | Dense search không bắt đủ danh sách các xã (Kim Đông, Rạng Đông, Hải Thịnh...). Sang Config B, BM25 bù đắp đầy đủ keyword địa danh. |
| 2 | Điều kiện công nhận khu du lịch quốc gia là gì? | Config A | 0.75 | 0.80 | 0.68 | 0.70 | Data / Chunking | Điều 25 Luật Du lịch có 5 khoản dài; kích thước chunk nhỏ có thể tách rời các ý. Đã khắc phục bằng chunk_size 800 ký tự có overlap. |
| 3 | Thủ đô của nước Pháp là thành phố nào? | Cả 2 | 1.00 | 1.00 | 1.00 | 1.00 | Fallback | Câu hỏi Out-of-Domain: Best cosine score = 0.17 < 0.35, hệ thống kích hoạt fallback an toàn từ chối trả lời ("Tôi không thể xác minh..."), không bịa đặt (hallucination). |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| ---: | --- | --- | --- | --- |
| 1 | Bổ sung semantic chunking theo cấu trúc Điều/Khoản luật | Chunking theo ký tự đôi khi cắt giữa chừng khoản luật | Tăng độ liền mạch ngữ cảnh pháp lý, Context Precision tăng +5% | Kiểm tra các câu hỏi về điều kiện pháp lý nhiều mục |
| 2 | Tích hợp Cross-Encoder Reranker sau RRF | Các câu hỏi dài dạng mô tả danh lam thắng cảnh cần đánh giá tương quan sâu | Giảm thêm các chunk không liên quan trong top 3 | Đo điểm Context Precision trên tập đánh giá mở rộng |
| 3 | Mở rộng corpus sang văn bản hướng dẫn thi hành (Nghị định) | Người dùng hỏi sâu về mức phạt và thủ tục chi tiết | Trả lời được các tình huống pháp lý phức tạp hơn | Thêm 20 câu hỏi tình huống vào golden dataset |

## Bonus Experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| --- | --- | ---: | ---: | --- |
| So sánh Hybrid RRF vs Dense-only | Dense-only (all-MiniLM-L6-v2) | Context Recall: +0.12, Context Precision: +0.11 | Latency: +18ms, Chi phí: 0$ delta | Hybrid RRF là cấu hình bắt buộc cho bài toán kết hợp văn bản pháp luật và thông tin địa phương |
| Lost-in-the-middle context reordering | Giữ nguyên thứ tự rank | Answer Faithfulness: +0.06 | Latency: 0ms, Chi phí: 0$ | Đưa chunk quan trọng ra 2 đầu context giúp LLM chú ý tốt hơn khi tổng hợp câu trả lời |
