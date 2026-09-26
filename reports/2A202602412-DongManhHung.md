# Báo cáo đóng góp cá nhân

## Thông tin

- Họ và tên: Đồng Mạnh Hùng
- Mã học viên: 2A202602412
- Nhóm: 4aesieunhan
- Repository/branch: https://github.com/TuTu99999/K4-L3B-RAG-Pipeline/tree/Hung23020370
- Commit chính: `09dbbb9` (`lan2`)

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 1 - Thu thập legal documents | Đọc manifest nguồn, tạo thư mục dữ liệu, tải bản text chính thức và kiểm tra file gốc, metadata, kích thước tối thiểu | `src/task1_collect_legal_docs.py`, `data/landing/legal/sources.json` | Done |
| Task 2 - Crawl news | Cấu hình Crawl4AI cho 5 bài viết, lọc Markdown, lưu title/url/date/content và báo cáo lỗi từng URL | `src/task2_crawl_news.py`, `data/landing/news/*.json` | Done |
| Task 8 - PageIndex fallback | Chuyển Markdown sang PDF, upload tài liệu, cache `doc_id`, query/poll kết quả PageIndex và giữ local fallback khi thiếu API key | `src/task8_pageindex_vectorless.py`, `pageindex_cache.json` | Done |
| Task 9 - Retrieval pipeline | Kết hợp dense và BM25 bằng RRF một lần, dùng cosine score gốc để quyết định fallback và chống lỗi provider | `src/task9_retrieval_pipeline.py` | Done |
| Task 10 - Generation | Reorder và format context có source, dispatch LLM provider, safe refusal khi thiếu evidence/provider và nối kết quả vào Streamlit UI | `src/task10_generation.py`, `app.py` | Done |

## Quyết định kỹ thuật quan trọng

1. **Dùng cosine score gốc của dense search để kích hoạt fallback.**
   **Lý do/evidence:** RRF score là điểm xếp hạng tổng hợp, không cùng thang đo với cosine similarity. Task 9 chỉ gọi PageIndex khi dense score thấp và chỉ fuse RRF một lần.
   **Trade-off:** Pipeline cần giữ riêng dense results và hybrid results, nhưng threshold có ý nghĩa và tránh fallback sai.

2. **PageIndex có cache và fallback offline.**
   **Lý do/evidence:** PageIndex yêu cầu PDF và là dịch vụ bên ngoài; Task 8 tạo PDF tạm, lưu `doc_id` trong cache, đặt timeout/polling và trả local result khi API chưa cấu hình hoặc lỗi.
   **Trade-off:** Local fallback không có chất lượng như PageIndex thật, nhưng test và UI vẫn chạy được khi không có network/API key.

## Kiểm thử và kết quả

- Chạy `python -m pytest -q`: **23 passed** trên bản tích hợp cuối.
- Chạy Task 8 với PageIndex thật: 8 tài liệu được upload và nhận `doc_id`; truy vấn fallback trả kết quả có `retrieval_method="pageindex"`.
- Chạy Task 9: truy vấn trả kết quả hybrid theo đúng schema.
- Chạy Task 10: trả `GenerationResult`; khi thiếu/có lỗi LLM provider thì trả safe refusal thay vì làm pipeline crash.

## Điều còn hạn chế

- Evaluation cuối đã hoàn thiện trong `group_project/evaluation/RESULT.md`; việc chạy lại cần quota LLM judge và có thể mất nhiều thời gian.
- Task 2 phụ thuộc website, Chromium và Crawl4AI nên có thể thất bại nếu website thay đổi hoặc môi trường thiếu browser.
- Task 8 phụ thuộc PageIndex API khi muốn dùng retrieval thật; local fallback chỉ là phương án chạy offline.
- Nếu có thêm thời gian, thay đổi đầu tiên là viết evaluation runner tự động cho dense-only và hybrid + RRF, đồng thời đo latency và 4 metric.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc mình đã thực hiện và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 2026-09-25
- Tên thành viên: Đồng Mạnh Hùng
