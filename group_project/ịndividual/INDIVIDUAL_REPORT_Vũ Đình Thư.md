# Individual contribution report

## Thông tin

* **Họ và tên:** Vũ Đình Thư
* **Mã học viên:** 2A202602652
* **Nhóm:** ThienAn
* **Repository/branch:** `sanh1ie77e/K4-L3B-RAG-Pipeline-LeVanSang` / `ninh-binh-rag`

## Phần việc đã thực hiện

| Module/deliverable     | Việc tôi trực tiếp làm                                                                                                  | File/commit/PR                                                                                              | Trạng thái |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ---------- |
| Corpus Ninh Bình       | Thu thập 5 bài viết, chuyển sang Markdown và kiểm tra tiêu đề, nội dung, URL nguồn.                                     | `src/task2_crawl_news.py`, `src/task3_convert_markdown.py`, `data/landing/news/`, `data/standardized/news/` | Done       |
| Index và tìm kiếm      | Chia 8 tài liệu thành 97 chunks, tạo index; chạy thử dense search, BM25 và hybrid RRF với câu hỏi về Tam Cốc, Hang Múa. | `src/task4_chunking_indexing.py` đến `src/task9_retrieval_pipeline.py`                                      | Partial    |
| Generation và đánh giá | Thử trả lời bằng OpenAI; chuẩn bị 15 câu hỏi và chạy so sánh dense-only với hybrid RRF.                                 | `src/task10_generation.py`, `group_project/evaluation/golden_dataset.json`, `ab_results.json`, `RESULT.md`  | Partial    |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Lọc menu, ảnh và nội dung chân trang khi chuẩn hóa bài viết.
   **Lý do/evidence:** Bản crawl ban đầu chứa nhiều nội dung điều hướng; bản Markdown sau xử lý hiển thị tiêu đề và nội dung bài.
   **Trade-off:** Cần kiểm tra lại nếu website thay đổi cấu trúc.

2. **Quyết định:** So sánh dense-only và hybrid trên cùng 15 câu hỏi, dùng Hit@5 và MRR@5 để đo retrieval.
   **Lý do/evidence:** Kết quả từng câu được lưu trong `ab_results.json`, có thể chạy lại.
   **Trade-off:** Bộ câu hỏi hiện lấy từ 5 bài viết; điểm đo theo file nguồn chưa đánh giá đầy đủ chất lượng câu trả lời.

## Kiểm thử và kết quả

* `pytest tests/test_contracts.py -q`: **15 passed**.
* `pytest tests/test_acceptance.py -q`: **5 passed**.
* Task 4: **8 tài liệu, 97 chunks được index**.
* A/B trên 15 câu: cả hai cấu hình đạt **Hit@5 = 1,0**; MRR@5 của dense-only là **0,9333**, hybrid RRF là **0,9222**. Chưa kết luận hybrid tốt hơn.
* Lỗi đã phát hiện: Task 5 gọi `count()` khiến test dùng `FakeCollection` thất bại; đã sửa và chạy lại test. Một câu trả lời về Tam Cốc gắn citation `[1]` vào chunk chưa chứa bằng chứng, dù citation `[2]` đúng.

## Điều còn hạn chế

* Citation chưa được kiểm chứng tự động theo từng chunk; PageIndex fallback chưa cấu hình vì nhóm không có PageIndex API key. Thời gian A/B hiện chưa phù hợp để kết luận cấu hình nào nhanh hơn.
* Nếu có thêm thời gian, tôi sẽ sửa bước kiểm chứng citation, thử lại trên nhiều câu hỏi và bổ sung câu hỏi đánh giá từ tài liệu quy định đã xác minh nguồn gốc.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

* **Ngày:** 25/09/2026
* **Tên thành viên:** Vũ Đình Thư
