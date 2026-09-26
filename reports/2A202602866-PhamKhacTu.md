# Báo cáo đóng góp cá nhân

## Thông tin

- Họ và tên: Phạm Khắc Tú
- Mã học viên: 2A202602866
- Nhóm: 4aesieunhan
- Repository/branch: https://github.com/TuTu99999/K4-L3B-RAG-Pipeline/tree/phamkhactu
- Commit phần data: `f8b3a1c` (`feat(data): build Vietnamese tourism corpus`)

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File đối chiếu | Trạng thái |
|---|---|---|---|
| Task 1 - Legal data | Thu thập và kiểm tra 3 văn bản pháp luật về du lịch; giữ bản PDF ký số, bổ sung bản Công báo có lớp text và metadata nguồn chính thức | `data/landing/legal/`, `data/landing/legal/sources.json`, `src/task1_collect_legal_docs.py` | Done |
| Task 2 - News data | Cấu hình Crawl4AI dùng Chrome có sẵn; crawl 5 bài về Hà Nội, Ninh Bình, Huế và ẩm thực Việt Nam; lưu đủ URL, tiêu đề, thời điểm crawl và Markdown | `data/landing/news/`, `src/task2_crawl_news.py` | Done |
| Task 3 - Chuẩn hóa | Chuyển 3 tài liệu legal và 5 bài news thành Markdown UTF-8; giữ metadata nguồn ở đầu file và chặn nội dung rỗng/quá ngắn | `data/standardized/legal/`, `data/standardized/news/`, `src/task3_convert_markdown.py` | Done |
| Kiểm thử dữ liệu | Chạy lại toàn bộ ba task và acceptance test dành cho corpus/standardized output | `tests/test_acceptance.py` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Giữ ba PDF scan ký số làm bản gốc, đồng thời dùng bản PDF Công báo chính thức có lớp text để chuẩn hóa.
   **Lý do/evidence:** Ba bản scan ban đầu có 70/73 trang không trích xuất được chữ; MarkItDown chỉ thu được thông tin chữ ký. Ba bản Công báo trích xuất được khoảng 81.031, 38.922 và 22.077 ký tự.
   **Trade-off:** Tốn thêm dung lượng do lưu hai phiên bản, nhưng bảo toàn được tài liệu ký số và tạo corpus có nội dung thực cho RAG. Quan hệ giữa hai phiên bản được ghi rõ trong `sources.json`.

2. **Quyết định:** Loại nguồn Vinpearl sau lần crawl thử và thay bằng cẩm nang Huế của VnExpress.
   **Lý do/evidence:** URL Vinpearl chỉ trả về 472 ký tự, chủ yếu là thông báo đăng nhập và lịch; bài Huế trả về 29.365 ký tự nội dung du lịch thực tế.
   **Trade-off:** Bộ news không còn bài Vinpearl tổng hợp 40 địa điểm, nhưng chất lượng văn bản và khả năng truy hồi cao hơn.

## Kiểm thử và kết quả

- Lệnh chạy lại: `python -m src.task1_collect_legal_docs`, `python -m src.task2_crawl_news`, `python -m src.task3_convert_markdown`.
- Acceptance test phần data: `python -m pytest tests/test_acceptance.py -q -k "corpus or standardized"`.
- Kết quả: **3 passed**, gồm đủ legal landing, news landing và standardized output.
- Dữ liệu đầu ra: 3 legal Markdown và 5 news Markdown; mọi file đều dài hơn ngưỡng 200 ký tự.
- Legal Markdown: khoảng 22.077-81.031 ký tự nội dung mỗi file.
- News Markdown: khoảng 11.741-29.365 ký tự nội dung mỗi file.
- Lỗi đã xử lý: PDF scan không có text layer; cache Crawl4AI ghi ngoài workspace; máy chưa tải Chromium của Playwright; một URL trả nội dung rác. Cách xử lý lần lượt là dùng bản Công báo có text, đặt cache trong project, dùng Chrome hệ thống và thay URL kém chất lượng.

## Điều còn hạn chế

- Nghị định 348/2025/NĐ-CP là văn bản sửa đổi nên một số câu trả lời về xử phạt vẫn cần đối chiếu Nghị định 45/2019/NĐ-CP và 129/2021/NĐ-CP hoặc văn bản hợp nhất.
- Markdown bài báo vẫn có một phần menu/liên kết điều hướng do cấu trúc trang nguồn.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện là bổ sung văn bản hợp nhất về xử phạt du lịch và thêm bước loại boilerplate trước khi chunking; sau đó đo lại chất lượng retrieval trên các câu hỏi pháp lý.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Phạm Khắc Tú
