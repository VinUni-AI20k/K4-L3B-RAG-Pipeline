# Individual contribution report

## Thông tin
- Họ và tên: Lục Tiến Đạt
- Mã học viên: 2A202602969
- Nhóm: Gene
- Repository/branch: main

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| RRF Reranking (Task 7) | Cài đặt thuật toán Reciprocal Rank Fusion (k=60), gộp thứ hạng từ Dense và BM25, deduplicate ID | `src/task7_reranking.py` | Done |
| Lexical Search (Task 6) | Cài đặt tìm kiếm từ khóa chính xác BM25Okapi, đặt ngưỡng sàn IDF tránh điểm 0 | `src/task6_lexical_search.py` | Done |
| Semantic Search (Task 5) | Truy vấn vector từ ChromaDB, chuyển đổi Cosine Distance sang Similarity Score chuẩn hợp đồng | `src/task5_semantic_search.py` | Done |
| PageIndex Fallback (Task 8) | Xây dựng cơ chế upload tài liệu, cache document ID và truy vấn vectorless fallback an toàn | `src/task8_pageindex_vectorless.py` | Done |
| Retrieval Pipeline (Task 9) | Tích hợp toàn bộ luồng Hybrid Retrieval, kiểm tra độ tin cậy của Dense score để kích hoạt Fallback | `src/task9_retrieval_pipeline.py` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Sử dụng Reciprocal Rank Fusion (RRF với k=60) thay vì cộng điểm trực tiếp giữa Dense và BM25.  
   **Lý do/evidence:** Dense Cosine Similarity (0-1) và BM25 score (không chặn trên) có phân phối và thang đo khác biệt hoàn toàn. RRF hợp nhất theo thứ hạng giúp tận dụng ưu điểm của cả hai mà không cần chuẩn hóa phân phối điểm số.  
   **Trade-off:** RRF score chỉ phản ánh thứ tự ưu tiên tương đối, không phản ánh trực tiếp xác suất/độ tin cậy ngữ nghĩa tuyệt đối.

2. **Quyết định:** Dùng Cosine Similarity gốc từ Dense search để kiểm tra ngưỡng Fallback (threshold=0.3) thay vì dùng RRF score.  
   **Lý do/evidence:** Điểm Cosine thể hiện trực tiếp mức độ liên quan ngữ nghĩa giữa query và corpus. Nếu điểm này < 0.3, chứng tỏ câu hỏi nằm ngoài phạm vi tài liệu và cần kích hoạt PageIndex fallback.  
   **Trade-off:** Phải giữ lại điểm gốc của Dense search đi kèm trong pipeline trước khi thực hiện fusion.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: `pytest tests/test_contracts.py` (chạy các bài test về semantic, lexical, rrf, retrieve và signatures).
- Kết quả: Vượt qua 100% các bài test hợp đồng liên quan đến Role B (7/7 tests PASSED).
- Lỗi đã phát hiện và cách xử lý: Khi corpus test có số lượng document quá nhỏ (N=2), IDF của BM25Okapi bị về 0 khiến kết quả rỗng. Đã khắc phục bằng cách đặt sàn `idf >= 0.25` cho các từ khóa xuất hiện.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: BM25 hiện tại đang tokenize từ vựng bằng tách khoảng trắng cơ bản (`.split()`), chưa tích hợp thư viện tách từ tiếng Việt chuyên sâu như PyVi hay Underthesea.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: Tích hợp bộ tách từ tiếng Việt cho BM25 và thử nghiệm thêm Cross-Encoder Reranker để so sánh chất lượng với RRF.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Lục Tiến Đạt
