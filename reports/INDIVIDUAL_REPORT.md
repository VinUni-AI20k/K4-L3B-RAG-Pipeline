# Individual contribution report

## Thông tin

- Họ và tên: Nguyễn Hữu Thành
- Mã học viên: 2A202602813
- Nhóm: K4-L3B-RAG-Pipeline
- Repository/branch: `harrynguyen127/K4-L3B-RAG-Pipeline`, branch `thanh`

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 1 - Thu thập tài liệu legal | Chuẩn bị cấu trúc thư mục `data/landing/legal/` và rà soát yêu cầu tối thiểu 3 tài liệu PDF/DOCX. Phần tải tài liệu và hoàn thiện corpus chưa thực hiện xong. | `src/task1_collect_legal_docs.py`, `data/landing/legal/` | Blocked |
| Task 2 - Crawl news | Xây dựng danh sách 5 URL IELTS công khai, crawler HTTP có timeout/User-Agent, trích title và nội dung chính, lưu JSON với `url`, `title`, `date_crawled`, `content_markdown`. | `src/task2_crawl_news.py`, `data/landing/news/` | Done |
| Task 3 - Chuẩn hóa Markdown | Xây dựng chuyển đổi JSON news sang Markdown có metadata nguồn; hỗ trợ chuyển PDF/DOC/DOCX bằng MarkItDown, loại bỏ title lặp và giữ đường dẫn đầu ra ổn định. | `src/task3_convert_markdown.py`, `data/standardized/news/`, `data/standardized/legal/` | Partial |
| Task 4 - Chunking/indexing | Xây dựng đọc Markdown, nhận diện metadata, chia chunk theo section/paragraph, giữ heading context và chunk ID; embedding theo batch và upsert vào ChromaDB, đồng thời xóa ID cũ không còn dùng. | `src/task4_chunking_indexing.py`, `chroma_db/` | Done |

Chỉ kê khai công việc có thể đối chiếu bằng file, commit, pull request, test hoặc kết quả evaluation.

## Quyết định kỹ thuật quan trọng

Mô tả tối đa hai quyết định mà bạn trực tiếp tham gia:

1. **Quyết định:** Chuẩn hóa dữ liệu news thành Markdown có metadata nguồn ở đầu tài liệu trước khi chunk.
   **Lý do/evidence:** Task 3 kiểm tra các trường bắt buộc của JSON, giữ URL và thời điểm crawl; Task 4 có thể khôi phục `source`, `title`, `doc_type` và URL từ Markdown.
   **Trade-off:** Dữ liệu có thêm phần metadata nhưng truy xuất nguồn và hiển thị citation rõ ràng hơn; nội dung legal vẫn phụ thuộc MarkItDown và file đầu vào hợp lệ.

2. **Quyết định:** Chia chunk theo đường dẫn heading, giới hạn khoảng 1.200 ký tự, không overlap và giữ ID dạng `<source>::chunk-<index>`.
   **Lý do/evidence:** Cách này giữ ngữ cảnh section, bảo đảm ID duy nhất và metadata `chunk_index`; test contract xác nhận chunk không mất identity và độ dài nằm trong giới hạn.
   **Trade-off:** Không overlap giúp giảm số chunk và chi phí embedding, nhưng một ý nằm ở ranh giới chunk có thể thiếu ngữ cảnh lân cận.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: `pytest tests/test_contracts.py -q`; kiểm tra chạy module Task 2–4 theo hướng dẫn trong `docs/STEP_BY_STEP.md`.
- Kết quả trước/sau nếu có: `tests/test_contracts.py` đạt `15 passed`. Acceptance test đạt `1 passed, 4 failed`; các lỗi còn lại liên quan thiếu 3 file legal, thiếu standardized legal, dataset không đúng schema acceptance hiện tại và thiếu `group_project/evaluation/RESULT.md`.
- Lỗi đã phát hiện và cách xử lý: phát hiện Task 1 vẫn còn `NotImplementedError` và thư mục legal chỉ có `.gitkeep`; ghi nhận đây là blocker của Task 1 và nguyên nhân khiến phần legal của Task 3 chưa thể chạy đầy đủ. Crawler Task 2 có xử lý lỗi theo từng URL và báo tổng số URL thất bại.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: corpus legal chưa có tài liệu thực tế nên pipeline mới được kiểm chứng đầy đủ với dữ liệu news; việc index còn phụ thuộc embedding model và môi trường đã cài đủ dependency.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: bổ sung tối thiểu 3 tài liệu legal công khai, chạy Task 3 và Task 4 end-to-end, sau đó cập nhật lại acceptance/evaluation report bằng kết quả thực tế.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Nguyễn Hữu Thành
