# Individual contribution report

## Thông tin

- Họ và tên: Trần Quốc Toản
- Mã học viên: 2A202602984
- Nhóm: Lạc Trôi
- Repository/branch: tqt_data (https://github.com/2003congthinh/K4-L3B-RAG-Pipeline/tree/tqt_data)

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 1 — Thu thập tài liệu pháp lý | Viết `download_documents()`: tải 3 PDF nguồn công khai (FDVN, Thư viện pháp luật, Economica) về `data/landing/legal/`, ghi `_manifest.json` map filename → URL gốc để Task 3 nhúng vào metadata | `src/task1_collect_legal_docs.py`, `data/landing/legal/_manifest.json` | Done |
| Task 2 — Crawl bài viết | Điền 5 URL vào `ARTICLE_URLS`, viết `crawl_article()` dùng Crawl4AI, chuẩn hoá `result.markdown` (str hoặc `MarkdownGenerationResult`) về text, lưu mỗi bài thành JSON đủ `url/title/date_crawled/content_markdown` | `src/task2_crawl_news.py`, `data/landing/news/article_01.json` … `article_05.json` | Done |
| Task 3 — Chuẩn hoá Markdown | Viết `convert_legal_docs()` (MarkItDown + front-matter từ manifest) và `convert_news_articles()` (JSON → Markdown + front-matter) | `src/task3_convert_markdown.py`, `data/standardized/legal/*.md`, `data/standardized/news/*.md` | Partial — phát hiện lỗi front-matter khi review, đã vá lại (xem mục Kiểm thử) |
| Golden dataset cho evaluation | Soát nội dung cả 3 văn bản legal và 5 bài news, viết 20 case Q&A grounded (18 in-domain trải đều mọi nguồn, 2 out-of-domain để test safe refusal) | `group_project/evaluation/golden_dataset.json` | Done |

Chỉ kê khai công việc có thể đối chiếu bằng file, commit, pull request, test hoặc kết quả evaluation.

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Ghi `_manifest.json` (filename → URL gốc) ngay ở Task 1 thay vì để Task 3 tự suy ra nguồn.
   **Lý do/evidence:** Sau khi PDF được MarkItDown convert sang `.md`, không còn cách nào đối chiếu ngược một tài liệu đã chuẩn hoá với nguồn công khai của nó nếu không lưu mapping này trước — ảnh hưởng trực tiếp đến citation hiển thị ở Task 10/UI.
   **Trade-off:** Thêm một bước đọc/ghi JSON phụ ở Task 1, và phải cập nhật manifest thủ công nếu sau này đổi/thêm nguồn PDF.

2. **Quyết định:** Xây golden dataset 20 case (nhiều hơn mức tối thiểu 15), cố ý chọn 2 case mà nội dung có sự khác biệt giữa hai nguồn theo thời gian (ngưỡng doanh thu chịu thuế 100 triệu đồng/năm ở tài liệu luận án cũ so với 500 triệu đồng/năm ở sổ tay thuế mới hơn; cơ quan đăng ký cấp huyện theo NĐ 01/2021 so với cấp xã theo NĐ 168/2025), cộng 2 case out-of-domain.
   **Lý do/evidence:** Đảm bảo mọi tài liệu trong corpus đều được ít nhất một câu hỏi kiểm tra trực tiếp, đồng thời tạo được case đo khả năng hệ thống ưu tiên nguồn cập nhật thay vì trích nguồn cũ, và đo safe refusal khi câu hỏi nghe hợp lý nhưng không có trong corpus.
   **Trade-off:** Tốn nhiều thời gian đọc thủ công từng văn bản để đảm bảo `expected_answer`/`expected_context` grounded chính xác, thay vì tạo câu hỏi chung chung nhanh hơn nhưng khó kiểm chứng.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng:
  - `pytest tests/test_acceptance.py::test_corpus_has_required_news_with_metadata -q`
  - `pytest tests/test_acceptance.py::test_standardized_output_covers_both_source_types -q`
  - `pytest tests/test_acceptance.py::test_golden_dataset_has_15_grounded_cases -q`
- Kết quả trước/sau nếu có:
  - Trước: 3 file legal `.md` không có front-matter, 5 file news `.md` có header dạng `# Title / **Source:** url / **Crawled:** date` chứ không phải YAML front-matter — không khớp với `_parse_front_matter()` mà Task 4 dùng, khiến `url`/`title` bị mất khi index. `golden_dataset.json` rỗng, test tương ứng fail.
  - Sau: viết lại front-matter chuẩn (`title`, `source`/`url`, `doc_type`) cho cả 8 file dựa đúng trên `_manifest.json` (Task 1) và header crawl (Task 2); dựng lại `data/landing/news/*.json` đúng schema; `golden_dataset.json` đủ 20 case. Cả 3 test trên pass.
- Lỗi đã phát hiện và cách xử lý: crawler ở Task 2 không lấy được `<title>` của một bài (`article_02` trả về `"Unknown"`) — sửa thủ công thành tiêu đề thật của bài viết sau khi đối chiếu nội dung.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: `data/landing/legal` mới có đúng 3 PDF ở mức tối thiểu yêu cầu, chưa có nguồn dự phòng nếu một trong ba URL gốc (FDVN, thuvienphapluat.vn, economica.vn) thay đổi đường dẫn hoặc ngừng truy cập được.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: thêm bước kiểm tra checksum/kích thước file sau khi tải ở `task1_collect_legal_docs.py` để phát hiện sớm khi PDF tải về bị lỗi/rỗng, và mở rộng golden dataset thêm vài câu hỏi multi-hop cần kết hợp cả tài liệu legal lẫn bài news mới trả lời được.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Trần Quốc Toản