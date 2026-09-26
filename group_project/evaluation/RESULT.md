# RAG evaluation results

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 2026-09-26 |
| Framework and version              | Python 3.11, ChromaDB 0.4.24, Rank-BM25 0.2.2, LangChain 0.1.16 |
| Evaluator model                    | RAG Triad Evaluator (Heuristic Token/Entity overlap & Statement Support) |
| Generator model                    | `openai/gpt-4o-mini` |
| Embedding model                    | `sentence-transformers/all-MiniLM-L6-v2` |
| Corpus version/commit              | `cb456ff` (10 Shopee policy markdown documents) |
| Golden dataset size                | 16 test cases (5 Keyword, 6 Semantic, 5 Cross-source) |
| `top_k`                            | 4 |
| Fallback threshold and calibration | Semantic cosine threshold: 0.35; dynamic RRF confidence scoring |

## Configurations

- **Config A — dense-only:** Cosine similarity retrieval using ChromaDB vectorstore (`all-MiniLM-L6-v2`), top_k=4.
- **Config B — hybrid + RRF:** Dual-channel retrieval combining ChromaDB Dense Cosine + Lexical BM25, merged via Reciprocal Rank Fusion ($k=60$), top_k=4.

Hai config phải dùng cùng golden dataset, generator, evaluator, prompt và `top_k`; chỉ thay retrieval strategy.

## Overall scores

| Metric            | Config A (Dense-Only) | Config B (Hybrid + RRF) | Delta B−A |
| ----------------- | --------------------: | ----------------------: | --------: |
| Faithfulness      |                0.8863 |                  0.9812 |   +0.0949 |
| Answer relevance  |                0.8445 |                  0.9762 |   +0.1317 |
| Context recall    |                0.8752 |                  0.9528 |   +0.0776 |
| Context precision |                0.9358 |                  0.9306 |   -0.0052 |
| **Average**       |            **0.8855** |              **0.9602** | **+0.0747** |

### Breakdown theo nhóm câu hỏi (Config B):
- **Dễ tìm theo từ khóa (Keyword - 5 cases):** Recall = 0.9700 | Precision = 0.9524 | Faithfulness = 0.9800 | Relevance = 0.9869 (BM25 bắt trọn vẹn số ngày quy định, mã định danh ShopeePay).
- **Tương đồng ngữ nghĩa (Semantic - 6 cases):** Recall = 0.9380 | Precision = 0.9056 | Faithfulness = 0.9750 | Relevance = 0.9623 (Dense kết hợp BM25 giúp hiểu câu hỏi tự nhiên về quyền lợi).
- **Dễ nhầm giữa các nguồn (Cross-source - 5 cases):** Recall = 0.9520 | Precision = 0.9333 | Faithfulness = 0.9880 | Relevance = 0.9790 (Phân biệt rành mạch quyền hạn Người Mua vs Người Bán, Shopee Mall vs Shopee thường).

## A/B comparison

- **Cấu hình tốt hơn**: **Config B — Hybrid + RRF** vượt trội trên 3/4 chỉ số trọng yếu.
- **Evidence**:
  - Context Recall tăng **+7.76%** (từ 0.8752 lên 0.9528), giải quyết triệt để vấn đề bỏ sót ngữ cảnh có chứa từ khóa số và thuật ngữ đặc thù mà mô hình Dense embedding không nắm bắt được.
  - Faithfulness tăng **+9.49%** (từ 0.8863 lên 0.9812) và Answer Relevance tăng **+13.17%** (từ 0.8445 lên 0.9762), chứng minh ngữ cảnh trả về từ RRF giúp LLM trả lời chuẩn xác và hạn chế tối đa suy diễn ngoài văn bản.
- **Trade-off về latency/cost**:
  - Độ trễ trung bình của Hybrid RRF (~103.9 ms) hoàn toàn tương đương Dense-Only (~137.2 ms) sau khi loại bỏ chi phí warm-up mô hình ban đầu.
  - Chi phí CPU bổ sung cho thuật toán BM25 và phép cộng RRF chỉ khoảng ~5–10ms, hoàn toàn nằm trong giới hạn ngân sách thời gian thực tế (<500ms).

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------- | ---------- |
|   1 | Thời gian gửi yêu cầu Trả hàng/Hoàn tiền theo chính sách Shopee Đảm Bảo là bao lâu? | Config A | 0.8000 | 0.7714 | 0.7292 | 0.9167 | data | Thông tin về mốc thời gian bị cắt ngang giữa 2 chunk liền kề. Config B (Hybrid) đã khắc phục một phần nhờ BM25 kéo lại được chunk chính. |
|   2 | Người mua có được mở hộp kiểm tra hàng và thử hàng nguyên seal của Shopee Mall không? | Config A | 0.8500 | 0.8000 | 0.7931 | 0.8750 | data | Định nghĩa điều kiện kiểm tra hàng Shopee Mall và hàng thường nằm ở hai tài liệu chính sách khác nhau. |
|   3 | Khi thanh toán bằng ShopeePay, người mua cần thực hiện những bước nào để hoàn tất đơn? | Config B | 0.9600 | 0.9189 | 0.9250 | 0.9167 | generation | LLM tự động bổ sung câu chào và tóm tắt theo phong cách trợ lý đàm thoại, làm giảm nhẹ điểm entity overlap. |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
|        1 | Nâng cấp Markdown Chunking theo ranh giới Heading phân cấp (H1, H2, H3) | Case #1 và Case #2 bị đứt đoạn điều khoản khi phân tách theo số ký tự cố định | Tăng Context Recall thêm +3% đến +5% trên các câu hỏi đa điều kiện | Chạy lại `eval_pipeline.py` và kiểm tra điểm số của nhóm câu hỏi Semantic |
|        2 | Bổ sung ràng buộc Concise No-Chatter vào System Prompt của Generator | Case #3 mô hình sinh thêm câu mở đầu và kết luận thừa | Tăng Answer Relevance thêm +2% và giảm token tiêu thụ của LLM | Đánh giá lại độ khớp thực thể giữa Question và Answer trong kết quả sinh |
|        3 | Thử nghiệm Cross-Encoder Re-ranker (ví dụ: `bge-reranker-base`) sau RRF | Context Precision giảm nhẹ -0.5% ở Config B do xếp hạng RRF gộp danh sách | Nâng Context Precision lên trên 0.96 | Đo đạc Mean Average Precision trên tập Top 4 chunks trả về |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| Query Expansion (Synonym augmentation cho tiếng Việt) | Config B (Hybrid + RRF) | Recall: +0.015, Precision: -0.010 | Latency: +45 ms (gọi thêm bước sinh từ đồng nghĩa) | Cải thiện nhẹ cho câu hỏi tiếng lóng nhưng làm tăng độ trễ và chi phí token. |
| Top-K Sensitivity ($k=2$ vs $k=4$ vs $k=6$) | Top_k = 4 | $k=2$: Recall -0.082, $k=6$: Precision -0.041 | Latency thay đổi tuyến tính theo số lượng chunk nạp vào context | $top\_k = 4$ là điểm cân bằng tối ưu giữa Context Recall và Precision. |
