# Báo cáo đóng góp cá nhân

## Thông tin

- Họ và tên: Ngô Thế Khanh
- Mã học viên: 2A20262503
- Nhóm: K4-L3B RAG Pipeline
- Repository/branch: K4-L3B-RAG-Pipeline-NgoTheKhanh
- Vai trò: Member — Retrieval

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Dense retrieval | Dùng chung embedding function với Task 4, query ChromaDB và chuyển cosine distance thành similarity score. | `src/task4_chunking_indexing.py`, `src/task5_semantic_search.py` | Done |
| BM25 retrieval | Nạp cùng corpus chunk với dense retrieval, xử lý token overlap khi corpus nhỏ khiến BM25 score bằng 0. | `src/task6_lexical_search.py` | Done |
| Hybrid RRF | Gộp dense và BM25 theo công thức Reciprocal Rank Fusion, loại kết quả trùng và giữ thứ tự score. | `src/task7_reranking.py`, `src/task9_retrieval_pipeline.py` | Done |
| Fallback | Dùng dense cosine score để quyết định PageIndex fallback; chuẩn hóa metadata retrieved node theo contract. | `src/task8_pageindex_vectorless.py`, `src/task9_retrieval_pipeline.py` | Done |
| API embedding | Chuyển từ model local sang OpenAI `text-embedding-3-small`, đọc `OPENAI_API_KEY` từ `.env`. | `src/task4_chunking_indexing.py`, `.env` | Done |
| Kiểm thử | Sửa lỗi BM25 và chạy acceptance/contract tests. | `tests/`, lệnh `pytest -q` | Done |

## Quyết định kỹ thuật quan trọng

1. **Dùng dense retrieval kết hợp BM25 và RRF.**

   **Lý do/evidence:** dense search phù hợp với câu hỏi diễn đạt tự nhiên; BM25 phù hợp với tên văn bản, điều luật và từ khóa chính xác. RRF giúp gộp thứ hạng mà không cộng trực tiếp hai thang điểm khác nhau.

   **Trade-off:** pipeline phức tạp hơn và phải xây dựng hai danh sách kết quả, nhưng khả năng xử lý câu hỏi pháp lý tốt hơn dense-only.

2. **Dùng OpenAI Embeddings API thay cho `sentence-transformers`.**

   **Lý do/evidence:** môi trường chạy qua API key, không cần tải model local; cấu hình hiện tại dùng `text-embedding-3-small`.

   **Trade-off:** phụ thuộc mạng/API và phát sinh chi phí; khi đổi model phải tạo lại ChromaDB vì số chiều vector có thể thay đổi.

## Kiểm thử và kết quả

- Lệnh: `python -m pytest -q -p no:cacheprovider`.
- Kết quả: `20 passed`.
- Acceptance tests: `5 passed`.
- Contract tests: `15 passed`.
- Lỗi đã xử lý: BM25 trả danh sách rỗng trên corpus nhỏ dù có token khớp; giải pháp là kiểm tra token overlap trước khi xếp hạng.
- Kiểm tra bổ sung: `python -m py_compile app.py src/*.py`.

## Điều còn hạn chế

- Một số bài viết web còn nội dung điều hướng/boilerplate, có thể làm giảm độ chính xác retrieval.
- BM25 hiện token hóa đơn giản bằng khoảng trắng, chưa dùng tokenizer chuyên biệt cho tiếng Việt.
- Embedding và generation phụ thuộc API key, kết nối mạng và hạn mức dịch vụ.

Nếu có thêm thời gian, tôi sẽ lọc boilerplate, tối ưu tokenizer tiếng Việt và hiệu chỉnh `score_threshold` trên tập câu hỏi trong miền và ngoài miền.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Ngô Thế Khanh
