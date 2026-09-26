# Track C — Tổng quan và checklist

## 1. Tổng quan bài toán

Nhóm xây dựng chatbot tiếng Việt giúp chủ hộ kinh doanh tra cứu:

- Các loại thuế phải nộp.
- Cách tính và ngưỡng miễn thuế.
- Hồ sơ, biểu mẫu và thời hạn kê khai.
- Hóa đơn điện tử.
- Mức phạt khi khai hoặc nộp thuế sai hạn.

Chatbot chỉ trả lời dựa trên tài liệu đã thu thập và hiển thị nguồn để người dùng kiểm chứng.

## 2. Vai trò của Track C

Track C phụ trách chọn và kết hợp thông tin tìm được trước khi chuyển cho chatbot viết câu trả lời.

Các file phụ trách:

- `src/task7_reranking.py`
- `src/task8_pageindex_vectorless.py`
- `src/task9_retrieval_pipeline.py`

Ngoài ra, Track C cần điều chỉnh `SCORE_THRESHOLD` — ngưỡng xác định kết quả tìm kiếm có đủ đáng tin hay không.

## 3. Luồng xử lý

```text
TRACK A — Chuẩn bị dữ liệu
- Thu thập văn bản pháp luật và bài báo
- Chuyển nội dung thành các file Markdown chuẩn
        ↓
TRACK B — Tạo kho tìm kiếm
- Chia tài liệu thành các đoạn nhỏ
- Lưu các đoạn vào kho dữ liệu
- Chuẩn bị hai cách tìm kiếm:
  1. Tìm theo ý nghĩa của câu hỏi
  2. Tìm theo từ ngữ xuất hiện trong câu hỏi
        ↓
Người dùng đặt câu hỏi
        ↓
TRACK B — Trả về hai danh sách tài liệu
- Danh sách tìm theo ý nghĩa
- Danh sách tìm theo từ ngữ
        ↓
TRACK C — Gộp và sắp xếp kết quả
- Gộp hai danh sách
- Loại tài liệu bị trùng
- Đưa tài liệu phù hợp hơn lên đầu
        ↓
TRACK C — Kiểm tra độ tin cậy
- Xem điểm gốc của kết quả tìm theo ý nghĩa tốt nhất
        ↓
Nếu đủ tốt ───────────────→ Trả danh sách đã gộp
Nếu quá thấp
        ↓
TRACK C — Thử tìm dự phòng bằng PageIndex
        ↓
Có kết quả → trả kết quả PageIndex
Không có hoặc bị lỗi → trả danh sách đã gộp
        ↓
TRACK D — Tạo câu trả lời
- Dùng các tài liệu Track C trả về
- Viết câu trả lời và hiển thị nguồn tham khảo
```

Tóm lại: Track A chuẩn bị tài liệu; Track B biến tài liệu thành kho có thể tìm kiếm; Track C chọn và kiểm tra kết quả; Track D viết câu trả lời cho người dùng.

Quyết định có gọi PageIndex hay không phải dựa trên điểm gốc của kết quả tìm theo ý nghĩa do Track B trả về, không dùng điểm sau khi Track C gộp kết quả.

## 4. Công việc cần thực hiện

### Task 7 — Gộp và xếp hạng

- Nhận hai danh sách kết quả từ Track B.
- Tính điểm theo công thức `sum(1 / (k + rank))`.
- Vị trí xếp hạng bắt đầu từ `1`.
- Loại tài liệu trùng ID.
- Sắp xếp điểm từ cao xuống thấp.
- Gắn `retrieval_method="hybrid"`.

### Task 8 — Tìm kiếm dự phòng

- Chỉ tải tài liệu lên PageIndex khi cần.
- Lưu quan hệ `source → doc_id` trong `data/pageindex_cache.json`.
- Có giới hạn thời gian chờ và bắt lỗi.
- Không có `PAGEINDEX_API_KEY` thì trả `[]`, không làm chương trình dừng.

### Task 9 — Nối luồng tìm kiếm

- Gọi hai cách tìm kiếm với số lượng `top_k * 2`.
- Gộp kết quả đúng một lần.
- So sánh `dense[0]["score"]` với `SCORE_THRESHOLD`.
- Điểm thấp thì thử PageIndex.
- PageIndex lỗi hoặc không có kết quả thì trả danh sách đã gộp.
- Hỗ trợ trường hợp `use_reranking=False` theo contract.

### Chọn ngưỡng điểm

- Chạy 3 câu đúng chủ đề thuế và kê khai.
- Chạy 3 câu ngoài chủ đề.
- Chọn ngưỡng phân biệt hai nhóm tốt nhất.
- Ghi ngưỡng vào `.env` và giải thích ngắn trong `reports/RESULT.md`.

## 5. Checklist Track C

- [ ] Hoàn thành `rerank_rrf`, loại trùng và xếp đúng điểm.
- [ ] Hoàn thành `pageindex_search`, có cache, timeout và bắt lỗi.
- [ ] Không có API key thì PageIndex trả `[]`.
- [ ] Hoàn thành `retrieve` theo đúng luồng fallback.
- [ ] Fallback dùng điểm `dense[0]["score"]`.
- [ ] Chạy 3 câu đúng chủ đề và 3 câu ngoài chủ đề.
- [ ] Ghi ngưỡng vào `.env`, lý do vào `reports/RESULT.md`.
- [ ] Chạy test Track C và bảo đảm pass.
- [ ] Thử một câu về thuế và một câu “cách nướng cá basa”.
- [ ] Không commit `.env`, API key hoặc `chroma_db/`.
