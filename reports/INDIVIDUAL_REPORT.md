# Individual contribution report

## Thông tin

- **Họ và tên**: Nguyễn Hữu Chương
- **Mã học viên**: 2A202602601
- **Nhóm**: Nova
- **Repository/branch**: https://github.com/Dzzuy/K4-L3B-RAG-Pipeline/

---

## Phần việc đã thực hiện

| Module / Deliverable | Việc tôi trực tiếp làm | File / Commit / Artifact | Trạng thái |
|---|---|---|---|
| **Chunking & Indexing** | Thiết kế chiến lược chunking Markdown với `RecursiveCharacterTextSplitter` (chunk_size=750, overlap=100); xây dựng pipeline nhúng vector vào ChromaDB và tạo chỉ mục Lexical BM25. | `src/task4_chunking_indexing.py`<br>`src/task6_lexical_search.py`<br> | **Done** |
| **Hybrid Retrieval & RRF Reranking** | Cài đặt thuật toán Reciprocal Rank Fusion (k=60) kết hợp song song Dense Semantic (MiniLM) và Lexical (BM25); xử lý cơ chế fallback threshold và chuẩn hóa điểm số tự tin. | `src/task7_reranking.py`<br>`src/task9_retrieval_pipeline.py`<br> | **Done** |
| **Generation & System Prompt** | Cấu hình Generator (`openai/gpt-4o-mini`) với System Prompt tuân thủ nghiêm ngặt ngữ cảnh trích xuất, chống hallucination và từ chối trả lời ngoài tài liệu chính sách Shopee. | `src/task10_generation.py`<br>Commit: `cb456ff` | **Done** |


---

## Quyết định kỹ thuật quan trọng

1. **Quyết định: Sử dụng Hybrid Search (Dense + BM25) kết hợp RRF (k=60) thay vì Dense-only.**
   - **Lý do / Evidence**: Tập dữ liệu là các văn bản chính sách TMĐT chứa nhiều số liệu cụ thể (3 ngày, 7 ngày), mốc thời gian, và danh xưng riêng (*Shopee Mall*, *ShopeePay*). Dense vector embedding thường bị mờ ngữ nghĩa với các từ khóa số và thuật ngữ đặc thù. Đánh giá A/B thực nghiệm trên 16 test cases chứng minh Hybrid RRF giúp tăng **Context Recall từ 0.8752 lên 0.9528 (+7.8%)**, **Faithfulness từ 0.8863 lên 0.9812 (+9.5%)**, và **Answer Relevance từ 0.8445 lên 0.9762 (+13.2%)**.
   - **Trade-off**: Phải lưu trữ và duy trì đồng thời 2 index (ChromaDB + BM25 corpus); tăng nhẹ thời gian tính toán reranking (~5–10ms CPU), nhưng đổi lại chất lượng retrieval và tính chính xác của câu trả lời vượt trội.

2. **Quyết định: Áp dụng `RecursiveCharacterTextSplitter` với `chunk_size = 750`, `chunk_overlap = 100`.**
   - **Lý do / Evidence**: Trước đó, chunk size nhỏ gây trường hợp tiêu đề ở chunk này, nội dung ở chunk kia, dẫn đến BM25 kết quả thấp.
   - **Trade-off**: Context vào LLM dài hơn, tăng chi phí

---

## Kiểm thử và kết quả

- **Test hoặc query đã dùng**:
  - Chạy toàn bộ test suite dự án qua `pytest`: **20/20 tests Passed** (bao gồm unit tests cho vectorstore, BM25 retrieval, RRF ranking, threshold fallback).
  - Kiểm thử định lượng qua bộ 16 test cases thực tế thuộc 3 nhóm: *Keyword* (mã điều khoản, định danh sàn), *Semantic* (diễn đạt tự nhiên về quyền lợi), và *Cross-source* (xung đột trách nhiệm Người Mua vs Người Bán).
- **Kết quả trước / sau**:
  - *Trước (Config A - Dense-Only)*: Context Recall = 0.8752 \| Context Precision = 0.9358 \| Faithfulness = 0.8863 \| Answer Relevance = 0.8445.
  - *Sau (Config B - Hybrid + RRF)*: Context Recall = **0.9528 (+7.8%)** \| Context Precision = 0.9306 \| Faithfulness = **0.9812 (+9.5%)** \| Answer Relevance = **0.9762 (+13.2%)**.
- **Lỗi đã phát hiện và cách xử lý**:
  - *Lỗi 1 (Latency skew do Cold Start)*: Lượt nhúng đầu tiên của `sentence-transformers` tốn ~61s do nạp mô hình vào PyTorch. Đã xử lý bằng cách tích hợp warmup query trước khi thực thi đo đạc, đưa latency đo lường về giá trị thực tế ổn định (~103 ms/query).
  - *Lỗi 2 (Vỡ cấu trúc điều khoản khi chunking)*: Các danh sách đánh số `1. 2. 3.` trong chính sách Shopee Mall bị phân tán rải rác. Đã điều chỉnh separator hierarchy `["\n\n", "\n", "### ", "## "]` để gom cụm logic trước khi ngắt đoạn.

---

## Điều còn hạn chế

- **Một hạn chế cụ thể**: RRF đang gán trọng số đồng đều ($1 / (k + rank)$) cho cả Dense và Lexical; chưa có tầng Cross-Encoder Deep Re-ranker (như `bge-reranker-base`) do cân nhắc giới hạn tài nguyên tính toán local (chạy CPU).
- **Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện**: Bổ sung một lightweight Re-ranker model hoặc tích hợp Cohere Rerank API ở tầng sau RRF để chấm điểm tương đồng trực tiếp giữa câu hỏi và Top 10 chunks ứng viên, giúp tối ưu hóa hơn nữa Context Precision.

---

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- **Ngày**: 26/09/2026
- **Tên thành viên**: Nguyễn Hữu Chương
