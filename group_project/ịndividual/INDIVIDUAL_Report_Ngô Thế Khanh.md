# BÁO CÁO CÁ NHÂN

## 1. Thông tin thành viên

| Nội dung | Thông tin |
|---|---|
| Họ và tên | Ngô Thế Khanh |
| Mã học viên | 2A20262503 |
| Vai trò | Member |
| Phần việc chính | Retrieval |
| Đề tài | Chatbot hỏi đáp về du lịch Việt Nam |

## 2. Mục tiêu cá nhân

Tôi phụ trách xây dựng và kiểm thử phần retrieval cho chatbot hỏi đáp về du lịch Việt Nam. Mục tiêu là kết hợp dense retrieval, BM25 và reciprocal-rank fusion để tìm được các đoạn văn bản phù hợp, đồng thời bảo đảm pipeline có fallback an toàn khi dịch vụ PageIndex không khả dụng. Embedding được gọi qua OpenAI API, không phụ thuộc vào model chạy local.

## 3. Công việc đã thực hiện

### 3.1. Xác định phạm vi dữ liệu

Nhóm thống nhất phạm vi gồm ba nhóm nội dung:

- Quyền và nghĩa vụ của khách du lịch theo Luật Du lịch 2017.
- Điều kiện kinh doanh dịch vụ lữ hành theo Nghị định 168/2017/NĐ-CP.
- Quy định quản lý, bảo vệ tài nguyên và môi trường tại khu du lịch quốc gia.
- Thông tin tham khảo về các điểm đến nổi bật của Việt Nam như Hạ Long, Hội An, Phú Quốc, Sa Pa và Hà Nội.

### 3.2. Sử dụng corpus dữ liệu

Corpus hiện có:

- 5 tài liệu pháp lý trong `data/landing/legal/` và `data/standardized/legal/`:
  - Luật Du lịch 2017.
  - Nghị định 168/2017/NĐ-CP.
  - Quy chế quản lý khu du lịch quốc gia.
- Kế hoạch du lịch biển Ninh Bình giai đoạn 2026–2030.
- Quy tắc ứng xử văn minh du lịch.
- 10 bài viết về điểm đến trong `data/landing/news/`, mỗi bài có metadata gồm `url`, `title`, `date_crawled` và `content_markdown`.

Các tệp được lưu theo hai nhóm `legal/` và `news/`, giúp retrieval giữ được thông tin nguồn khi hiển thị citation.

### 3.3. Tích hợp retrieval

Tôi phối hợp hoàn thiện và kiểm tra các module retrieval:

- Sử dụng chung embedding model và ChromaDB cho semantic search.
- Xây dựng BM25 trên cùng corpus chunk với dense search.
- Kết hợp các danh sách kết quả bằng Reciprocal Rank Fusion.
- So sánh ngưỡng fallback bằng cosine score gốc của dense retrieval.
- Bổ sung PageIndex vectorless fallback và chuẩn hóa metadata của retrieved nodes.
- Chuyển embedding sang OpenAI `text-embedding-3-small` thông qua `OPENAI_API_KEY` trong `.env`.
- Kết nối `app.py` với `generate_with_citation()` để giao diện Streamlit hiển thị câu trả lời và nguồn tham khảo.

### 3.4. Phối hợp tích hợp

Tôi thống nhất với nhóm schema chung cho document và search result, đặc biệt là các trường `id`, `content`, `score`, `metadata` và `retrieval_method`. Việc giữ metadata giúp hệ thống có thể trích dẫn đúng tài liệu nguồn ở bước generation.

## 4. Kết quả đạt được

- Hoàn thiện luồng dense search, BM25, RRF và PageIndex fallback.
- BM25 tự nạp cùng corpus chunk với dense retrieval, tránh danh sách lexical rỗng.
- Xử lý trường hợp corpus nhỏ khi BM25 trả điểm bằng 0 cho từ khóa khớp.
- Acceptance tests đạt `5 passed`.
- Contract tests đạt `15 passed`; toàn bộ test suite đạt `20 passed`.
- Các câu hỏi đánh giá bao phủ cả quy định pháp lý và thông tin điểm đến trong `group_project/evaluation/golden_dataset.json`.

## 5. Khó khăn và cách xử lý

### 5.1. Điểm BM25 trên corpus nhỏ

Với corpus nhỏ, BM25 có thể trả điểm bằng 0 dù tài liệu vẫn chứa từ khóa do IDF bằng 0. Tôi xử lý bằng token overlap trước khi xếp hạng để không loại nhầm kết quả hợp lệ.

### 5.2. Fallback từ PageIndex

Retrieved node từ PageIndex không luôn có đầy đủ metadata theo contract. Tôi bổ sung các trường `title`, `doc_type`, `url` và `chunk_index` để tương thích với generation và validation.

### 5.3. Khác biệt thang điểm

RRF score chỉ phản ánh thứ hạng, không thể so sánh trực tiếp với cosine score. Pipeline được giữ đúng nguyên tắc dùng dense score để quyết định fallback.

### 5.4. Embedding qua API

Môi trường chạy không sử dụng `sentence-transformers` local. Tôi chuyển cấu hình embedding sang OpenAI API với model `text-embedding-3-small`, kiểm tra API key từ `.env` và hướng dẫn tạo lại ChromaDB khi đổi model để tránh xung đột số chiều vector.

## 6. Đánh giá đóng góp cá nhân

Tôi hoàn thành phần retrieval, gồm dense search, lexical search, RRF và fallback PageIndex. Đóng góp này giúp hệ thống xử lý được cả câu hỏi ngữ nghĩa, câu hỏi chứa từ khóa pháp lý và trường hợp dense retrieval không đủ tự tin.

## 7. Bài học kinh nghiệm

- Dense và lexical retrieval bổ trợ cho nhau: dense phù hợp với truy vấn diễn đạt tự nhiên, BM25 phù hợp với thuật ngữ và tên riêng.
- Metadata nguồn cần được giữ xuyên suốt pipeline để generation tạo citation chính xác.
- Cần kiểm tra dữ liệu bằng cả acceptance test và contract test.
- Với dữ liệu tiếng Việt, cần chú ý encoding, tokenization và nội dung thừa từ website.
- Việc thống nhất schema giữa các thành viên giúp giảm lỗi tích hợp đáng kể.
- Embedding qua API giúp giảm yêu cầu cài đặt model local, nhưng cần kiểm soát API key, chi phí và lỗi mạng.

## 8. Đề xuất cải thiện

- Lọc phần menu và điều hướng khỏi các bài viết Wikipedia trước khi chunk.
- Tối ưu tokenizer BM25 cho tiếng Việt.
- Điều chỉnh `score_threshold` bằng tập câu hỏi trong miền và ngoài miền.
- Đánh giá riêng dense, BM25, hybrid và PageIndex fallback.
- Theo dõi version của corpus để kết quả đánh giá có thể tái lập.

## 9. Kết luận

Trong vai trò Member phụ trách Retrieval, tôi đã hoàn thiện các thành phần dense search, BM25, RRF và PageIndex fallback, đồng thời bảo đảm kết quả tuân thủ schema chung và được sắp xếp đúng theo score. Phần việc đã được kiểm tra bằng acceptance và contract tests của dự án.
# cập nhật bài làm cá nhân
