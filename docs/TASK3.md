# Task 3 — Chuẩn hóa dữ liệu

Đầu vào hiện tại là 3 PDF (75 trang scan) và 5 JSON từ Task 1–2.
RTF đã được loại khỏi dữ liệu theo yêu cầu người dùng.

## Cách xử lý

1. JSON đã có `content_markdown`: giữ nội dung và ngôn ngữ, thêm metadata ở đầu.
2. PDF: thử trích xuất văn bản; trang có quá ít chữ, hoặc ảnh scan lớn kèm
   lớp chữ ngắn chỉ chứa chữ ký điện tử, thì OCR tiếng Việt ở 300 DPI
   bằng PyMuPDF/Tesseract. Không dùng API trả phí hoặc gửi tài liệu lên dịch vụ OCR.
3. Ghép các từ OCR theo từng dòng để tránh mất khoảng trắng giữa hai từ.
   Mỗi PDF tạo một Markdown, giữ mốc `## Trang N`. Dòng nhận diện được là
   chương/điều được chuyển thành heading để hỗ trợ chunking.
4. Metadata dạng YAML front matter gồm tiêu đề, loại tài liệu, tên file gốc,
   URL, SHA-256 nguồn; tin bài có ngày crawl, PDF có số trang và danh sách trang OCR.
5. Kết quả nằm trong `data/standardized/legal/` và `data/standardized/news/`.
   Không sửa các bản gốc trong `data/landing/`.

Script dùng công cụ thay thế theo hướng dẫn cho phép của Task 3 vì PDF scan
cần OCR. DOCX nếu bổ sung sau này dùng MarkItDown (đã khai báo trong dự án).

## Môi trường riêng, không ảnh hưởng `.venv`

Từ thư mục gốc repo:

```powershell
python -m venv .cache\task3-venv
.\.cache\task3-venv\Scripts\python.exe -m pip install pymupdf==1.28.2 --timeout 120 --retries 5
New-Item -ItemType Directory -Force .cache\tessdata-fast
curl.exe -L --fail --retry 5 -o .cache\tessdata-fast\vie.traineddata https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/main/vie.traineddata
.\.cache\task3-venv\Scripts\python.exe -m src.task3_convert_markdown
```

Máy hiện tại đã được chuẩn bị môi trường riêng này. Chạy lại chỉ cần lệnh cuối.
Nếu chỉ chuyển tin bài thì không cần thêm thư viện:

```powershell
python -m src.task3_convert_markdown --only news
```

Có thể dùng `--only legal` để chỉ xử lý tài liệu. Nếu đặt mô hình OCR ở nơi khác,
truyền thư mục đó qua biến môi trường `TESSDATA_PREFIX`.

## Chạy lại và phục hồi

Tên output cố định theo tên nguồn, không tạo file trùng. Nếu nội dung không đổi,
không ghi lại file. File mới ghi vào `.part` trước khi thay thế để tránh Markdown
dở dang. JSON thiếu trường hoặc nội dung rỗng bị từ chối.

Kết quả OCR từng trang nằm trong `.cache/task3-ocr/` (Git bỏ qua). Cache gắn với
SHA-256 PDF, mô hình, phiên bản thư viện và cấu hình OCR. Nếu bị ngắt, chạy lại
dùng các trang đã hoàn thành. Đổi tài liệu hoặc cấu hình sẽ tạo cache khác.

## Kiểm tra và giới hạn

Kết quả đã chạy: **8 Markdown**, gồm 3 tài liệu pháp luật (37 + 16 + 22 = 75
trang OCR) và 5 bài/trang web. Đủ metadata nguồn và mốc trang liên tục. Chạy lại
toàn bộ giữ nguyên SHA-256 và thời gian sửa của cả 8 file. Có 8 kiểm thử offline
đạt, gồm kiểm tra trang scan có chữ ký điện tử và khoảng trắng giữa từ OCR.

```powershell
python -m unittest discover -s tests -p test_task3_conversion.py -v
```

OCR có thể nhầm dấu tiếng Việt, số hiệu hoặc bố cục bảng; trường `review_status`
ghi rõ chưa soát thủ công toàn bộ. Mốc trang dùng để đối chiếu PDF gốc. Không tự
viết lại nội dung pháp luật để sửa những chỗ OCR chưa chắc chắn.

Task 4 cần đọc metadata front matter để giữ URL, tiêu đề và nguồn khi chunk/index.
Đây là dữ liệu văn bản chuẩn hóa, chưa phải vector hoặc chatbot hoàn chỉnh.

Tài liệu công cụ: [PyMuPDF OCR](https://pymupdf.readthedocs.io/en/latest/page.html#Page.get_textpage_ocr),
[mô hình Tesseract tiếng Việt](https://github.com/tesseract-ocr/tessdata_fast).
