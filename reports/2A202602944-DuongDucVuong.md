# Báo cáo đóng góp cá nhân

## Thông tin

- **Họ và tên:** Dương Đức Vương
- **Mã học viên:** 2A202602944
- **Nhóm:** Gene — Hệ thống RAG hỏi đáp tuyển sinh đại học VinUni
- **Repository/branch:** `K4-L3B-RAG-Pipeline`; đang làm trên `main` (working tree chưa commit). Nhánh được phân công trong `TEAMMATES.md`: `feat/data-ingestion`.

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | Bằng chứng | Trạng thái |
|---|---|---|---|
| Thu thập tài liệu — Task 1 | Kiểm tra tài liệu chính sách trong landing và bổ sung quy định tuyển sinh công khai của VinUni. Landing có 6 PDF; 3 file có thể trích xuất văn bản để chuẩn hóa. | `src/task1_collect_legal_docs.py`, `data/landing/legal/` | Done; còn 3 PDF scan không trích được text |
| Crawl bài viết — Task 2 | Điền 8 URL tuyển sinh VinUni; dùng Crawl4AI lưu nội dung cùng `url`, `title`, `date_crawled`, `content_markdown`. | `src/task2_crawl_news.py`, 8 JSON trong `data/landing/news/` | Done |
| Chuẩn hóa — Task 3 | Chuyển PDF/DOC/DOCX và JSON sang Markdown, giữ hai nhánh `legal/`, `news/`; bỏ qua PDF không có text thay vì tạo Markdown rỗng. | `src/task3_convert_markdown.py`, `data/standardized/` | Done; 3 legal MD và 8 news MD |
| Chunking, embedding, indexing — Task 4 | Đọc Markdown theo contract, chunk 500 ký tự với overlap 50, embed bằng cấu hình Gemini dùng chung và upsert các ID ổn định vào ChromaDB. | `src/task4_chunking_indexing.py`, `chroma_db/` | Done; index có 400 chunks |

## Quyết định kỹ thuật

1. **Giữ `CHUNK_SIZE=500`, `CHUNK_OVERLAP=50` và tách ưu tiên theo đoạn/dòng/câu.** Giữ cấu hình starter để overlap bảo toàn ngữ cảnh biên mà không làm tăng kích thước index quá nhiều; ID dạng `đường_dẫn::chunk-n` ổn định theo nguồn. Đổi lại, một số bảng và cấu trúc Markdown có thể bị chia qua nhiều chunk.
2. **Ánh xạ model Gemini cũ `text-embedding-004` sang `gemini-embedding-001` với 768 chiều.** Model cũ trả 404 khi gọi API; model mới được Google tài liệu hóa cho embedding văn bản. Dùng retry có chờ khi nhận 429 để tôn trọng quota. Đổi lại, indexing phụ thuộc quota/API và tốn thời gian khi corpus vượt giới hạn theo phút.

## Kiểm thử và kết quả

- Chạy Task 1–3 và thu thập thành công 8 bài viết; chuẩn hóa 3 tài liệu pháp lý có text cùng 8 bài viết.
- Chạy Task 4: Chroma báo **400 chunks**; `--inspect` xác nhận mẫu metadata có `source`, `title`, `doc_type`, `url`, `chunk_index`.
- `pytest tests/test_contracts.py -q`: **8 passed, 7 failed**. Kiểm tra chunk Task 4 pass; các lỗi còn lại thuộc semantic search, BM25, RRF, retrieval pipeline và generation/reordering ở Tasks 5–10.
- Lỗi đã xử lý: PDF scan không có text được đánh dấu và bỏ qua; model embedding cũ được thay thế trong cấu hình runtime; cache Crawl4AI và ChromaDB được đưa vào `.gitignore`.

## Điều còn hạn chế

- Một số tài liệu PDF là bản scan nên chưa có OCR; chúng có mặt ở landing nhưng chưa có Markdown tương ứng.
- Index dùng Gemini API; để chạy lại cần có key hợp lệ và quota. Các tác vụ retrieval sau Task 4 chưa được hoàn thiện trong phạm vi phần việc này.
- Nếu có thêm thời gian, tôi sẽ bổ sung OCR có kiểm tra thủ công và chạy lại index; sau đó phối hợp kiểm thử end-to-end cùng Role B.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh phần việc và kết quả có thể đối chiếu trong repository.

- **Ngày:** 25/09/2026
- **Tên thành viên:** Dương Đức Vương
