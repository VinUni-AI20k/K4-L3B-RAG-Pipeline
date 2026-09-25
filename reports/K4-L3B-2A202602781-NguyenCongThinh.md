# Individual contribution report

## Thông tin

- Họ và tên: Nguyễn Công Thịnh
- Mã học viên: 2A202602781
- Nhóm: Lạc Trôi
- Repository/branch: feat/generation

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 4: Chunking & Indexing | Xây dựng pipeline cắt nhỏ văn bản, tạo embedding bằng SentenceTransformer (có xác thực HF_TOKEN) và upsert vào ChromaDB | `src/task4_chunking_indexing.py` | Done |
| Task 5: Semantic Search | Triển khai tìm kiếm vector ngữ nghĩa với cosine similarity trên Chroma | `src/task5_semantic_search.py` | Done |
| Task 6: Lexical Search | Triển khai tìm kiếm từ khóa BM25 cho tài liệu pháp luật và tin tức | `src/task6_lexical_search.py` | Done |
| Task 7: Reranking | Xây dựng bộ lọc và reranker kết quả tìm kiếm | `src/task7_reranking.py` | Done |
| Task 8: PageIndex Vectorless | Tích hợp PageIndex SDK dự phòng không cần vector store | `src/task8_pageindex_vectorless.py` | Done |
| Task 9: Retrieval Pipeline | Kết hợp hybrid retrieval, rerank và định tuyến truy vấn | `src/task9_retrieval_pipeline.py` | Done |
| Task 10: Generation & UI | Xây dựng tính năng sinh câu trả lời kèm trích dẫn nguồn | `src/task10_generation.py` | Done |

Chỉ kê khai công việc có thể đối chiếu bằng file, commit, pull request, test hoặc kết quả evaluation.

## Quyết định kỹ thuật quan trọng

Mô tả tối đa hai quyết định mà bạn trực tiếp tham gia:

1. **Quyết định:** Tích hợp Hybrid Retrieval kết hợp Semantic Search (BGE-M3) và Lexical Search (BM25) qua Task 9.  
   **Lý do/evidence:** Đảm bảo bao phủ cả từ khóa chính xác lẫn ý nghĩa ngữ nghĩa trong các văn bản pháp luật và thuế phức tạp.  
   **Trade-off:** Tăng nhẹ thời gian xử lý truy vấn đầu vào so với chỉ dùng một phương pháp duy nhất.

2. **Quyết định:** Sử dụng SentenceTransformer với xác thực `HF_TOKEN` trong Task 4 nhằm tránh lỗi rate-limit từ Hugging Face Hub.  
   **Lý do/evidence:** Ổn định quá trình tải model embed trong môi trường chạy liên tục.  
   **Trade-off:** Yêu cầu cấu hình biến môi trường chính xác.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: `pytest tests/test_acceptance.py -q` và chạy ứng dụng Streamlit kiểm tra end-to-end.
- Kết quả trước/sau nếu có: Vượt qua toàn bộ bài kiểm tra acceptance tests và các contract tests.
- Lỗi đã phát hiện và cách xử lý: Khắc phục cảnh báo unauthenticated request từ Hugging Face bằng cách load `.env` và truyền trực tiếp `token=os.getenv("HF_TOKEN")` vào model khởi tạo.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: Chưa tối ưu hóa tốc độ inference cho tập dữ liệu lớn với hàng triệu chunks.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: Triển khai caching cho retrieval results và tăng cường đánh giá bằng Ragas framework.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Nguyễn Công Thịnh