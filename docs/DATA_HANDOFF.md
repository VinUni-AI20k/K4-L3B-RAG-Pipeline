# Bàn giao Người 1 — Dữ liệu tuyển sinh NEU 2026

## Kết quả

- 3 PDF người dùng cung cấp, tổng 22 trang: chính quy 11 trang, liên thông từ cao đẳng 7 trang, liên thông từ đại học 4 trang.
- 5 bài viết có nội dung thực tế từ `fit.neu.edu.vn`, thu thập ngày 25/09/2026; lưu HTML gốc và SHA-256.
- 8 Markdown và 8 JSON theo schema Document để Người 2 sử dụng.
- 20 golden Q&A có đáp án, đoạn bằng chứng khớp nội dung corpus, URL, năm, đối tượng và vị trí nguồn.
- 6 tình huống calibration/fallback riêng; không dùng bộ evaluation để chọn threshold.
- 14 kiểm tra phần dữ liệu đạt. Đây không phải kết quả đánh giá chất lượng chatbot hay xác nhận Task 4–10 đã hoàn thành.

## Chạy lại trên Windows

Mở terminal tại `K4-L3B-RAG-Pipeline`:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m src.task1_collect_legal_docs
.\.venv\Scripts\python.exe -X utf8 -m src.task2_crawl_news
.\.venv\Scripts\python.exe -X utf8 -m src.task3_convert_markdown
.\.venv\Scripts\python.exe -X utf8 -m src.build_golden_dataset
.\.venv\Scripts\python.exe -X utf8 -m pytest tests/test_data_pipeline.py tests/test_acceptance.py -q -k "not evaluation_report" -p no:cacheprovider
```

Task 1 kiểm kê PDF đã có; thêm `--download-missing` nếu cần tải lại từ URL trong manifest. Task 2 mặc định dùng bản crawl đã xác minh; thêm `--refresh` để tải mới. Nếu nguồn lỗi, chương trình báo lỗi và giữ bản cũ, không sinh nội dung giả thay thế.

Với máy mới: tạo venv và cài `python -m pip install -e ".[dev]"` theo README. Task 1–3 không cần API key. Cache OCR đã đi kèm nên với các PDF hiện tại, Task 3 chạy lại không cần công cụ OCR hoặc mạng.

Nếu thêm/thay PDF scan, cài Tesseract với ngôn ngữ `vie` và `eng`, sau đó đặt `TESSERACT_CMD` trỏ tới executable nếu chưa có trên PATH. Trên máy hiện tại có bản cài tại `data/_tmp_pdf/tesseract/tesseract.exe`; thư mục này bị Git bỏ qua. Khi hash PDF thay đổi, cache OCR tự hết hiệu lực. Các bản sửa tay cũng kiểm tra hash và yêu cầu rà soát lại nếu PDF đổi.

## Vị trí bàn giao

| Đường dẫn | Nội dung | Người nhận |
| --- | --- | --- |
| `data/sources.json` | Danh mục 8 nguồn: URL, file gốc, năm, đối tượng | Người 2, 3 |
| `data/legal_inventory.json` | PDF gốc và SHA-256 | Cả nhóm |
| `data/landing/legal/` | Ba PDF gốc, giữ nguyên tên và nội dung | Cả nhóm |
| `data/landing/news/` | Năm JSON bài viết thật | Người 2 |
| `data/landing/raw_html/` | HTML gốc để truy vết nội dung | Người 1, 4 |
| `data/standardized/legal/`, `data/standardized/news/` | Markdown có metadata và JSON Document | Người 2 |
| `data/ocr/` | OCR theo trang, hash PDF, độ tin cậy trung bình | Người 1 |
| `data/reviewed/` | Trang đã đối chiếu ảnh PDF và sửa Markdown | Người 1 |
| `data/archive/news/` | Năm JSON cũ; không đưa vào index | Chỉ để đối chiếu |
| `group_project/evaluation/golden_dataset.json` | 20 câu đánh giá có evidence | Người 4 |
| `group_project/evaluation/fallback_dataset.json` | 6 câu hiệu chỉnh và kiểm tra hành vi | Người 3 |

## Hướng dẫn Người 2

Có thể đọc `data/standardized/*/*.json` để nhận trực tiếp `{id, content, metadata}`. Nếu đọc Markdown, phải parse front matter để giữ URL, năm và đối tượng; không dùng loader mẫu lấy `url=None`.

Chỉ đọc một định dạng để tránh index trùng Markdown và JSON. Không index `data/archive`, `data/ocr`, HTML gốc hoặc báo cáo.

Giữ `source`, `title`, `doc_type`, `url`, `admission_year`, `audience`, và số trang khi chunk. Lọc `audience=dai_hoc_chinh_quy` cho câu hỏi học sinh THPT; hai PDF liên thông không mặc nhiên áp dụng cho đối tượng này. Metadata phụ dạng list/null cần chuyển thành kiểu được vector database hỗ trợ trước khi upsert.

Các bảng cần chunk cùng tiêu đề, tên cột và chú thích. Bảng chứng chỉ và bảng ngành/chỉ tiêu chính quy trang 4–7 đã đối chiếu ảnh, chuyển thành Markdown; tổng chỉ tiêu các dòng được kiểm tra bằng 8.780. Không dùng các bảng của hệ liên thông chưa rà soát làm nguồn duy nhất cho câu trả lời về mã ngành/chỉ tiêu.

## Hướng dẫn Người 3

- Nguồn là snapshot đã lưu, không phải cam kết chatbot luôn có thông báo mới nhất.
- PDF tháng 3, bài tháng 5 và bài tháng 6/7 có thời điểm công bố khác nhau. Câu hỏi nêu ngày/văn bản phải được trả lời đúng phiên bản đó.
- Bài ngày 28/5 ghi hạn hồ sơ 20/6, bài ngày 26/6 ghi đã tiếp nhận đến 25/6. Nêu thời điểm và nguồn; không tự suy ra nguyên nhân thay đổi.
- Các trang Khoa CNTT là bài hướng dẫn/tổng hợp chính thức nhưng không thay thế toàn văn văn bản đính kèm. Khi mâu thuẫn, cần đối chiếu văn bản ban hành phù hợp.
- Bản OCR được gắn `review_status`. Confidence của Tesseract không phải xác suất thông tin tuyển sinh đúng.

## Hướng dẫn Người 4

Golden dataset giữ các trường repo yêu cầu: `question`, `expected_answer`, `expected_context`; bổ sung `id`, `evidence`, `admission_year`, `audience`, `category`, `split`.

`evidence` ghi nguồn và trích đoạn thực tế. Bộ hiện tại có câu đọc bảng, câu tổng hợp hai nguồn và câu phân biệt thông tin theo thời điểm; các câu PDF dùng trang 1/4 đã rà soát ảnh. Chưa bao phủ hết hai hệ liên thông. `expected_context` là bằng chứng tham chiếu, không phải context thực tế chatbot truy xuất. Cần lưu kết quả retrieval thật khi tính metric.

Chạy 4 metric và A/B thuộc Người 4; chưa có số liệu và không điền thay kết quả vào `RESULT.md`.

## Lỗi và giới hạn cần xử lý tiếp

1. Cả ba PDF là scan. Đã trích xuất đủ 22 trang, nhưng chưa kiểm tra trực quan toàn bộ 22 trang. Trang 1, 4, 5, 6, 7 của PDF chính quy đã đối chiếu ảnh, khôi phục thứ tự đọc, bảng chứng chỉ và bảng ngành/chỉ tiêu. Các trang còn lại giữ OCR và cờ cần rà soát.
2. OCR có lỗi dấu/chữ và có thể nhầm ô bảng, nhất là các bảng ở hai PDF liên thông chưa đối chiếu từng ô. Cần rà soát trước khi nghiệm thu dữ liệu sạch hoàn toàn. Golden dataset hiện tránh dựa vào các bảng chưa rà soát này.
3. Mã QR ở trang 1 chưa giải mã; ghi rõ vị trí trong PDF thay vì tự đặt URL.
4. URL gốc của ba PDF được xác định từ trang công bố NEU; chưa tải đối chiếu hash từ xa do kết nối tới `neu.edu.vn` bị timeout. Không biết ngày người dùng tải PDF nên để `date_crawled=null`, không tạo ngày tải giả.
5. Năm JSON cũ gồm bản tóm tắt và placeholder không đủ provenance đã được lưu vào archive, thay bằng bản crawl thật. HTML có ảnh được chuyển phần chữ và chú thích; chưa OCR hình ảnh trong các bài web, chưa tải mọi tệp đính kèm.

Phần code và dữ liệu đã sẵn sàng để tích hợp; nghiệm thu độ chính xác toàn bộ bảng PDF còn cần bước rà soát nêu trên.
