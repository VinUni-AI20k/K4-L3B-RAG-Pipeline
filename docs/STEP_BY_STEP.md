## 1. Chọn đề tài

- Chọn một chủ đề trong [danh sách gợi ý](SUGGESTED_TOPICS.md) hoặc chủ đề khác.
- Phân công role, chia nhiệm vụ các thành viên
- Mỗi thành viên ghi lại commit mình phụ trách để hoàn thiện individual report

## 2. Cài môi trường

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
python -m playwright install chromium
cp .env.example .env
```

## 3. Thu thập dữ liệu

- Tải tối thiểu 3 PDF/DOCX vào `data/landing/legal/`.
- Crawl tối thiểu 5 bài vào `data/landing/news/`.
- Mỗi JSON có `url`, `title`, `date_crawled`, `content_markdown`.

```bash
python -m src.task1_collect_legal_docs
python -m src.task2_crawl_news
```

Trong repo có setup sẵn Crawl4AI, các bạn tùy ý sử dụng công cụ khác của mình

## 4. Chuẩn hóa Markdown

Hoàn thiện Task 3 rồi chạy:

```bash
python -m src.task3_convert_markdown
```

Trong repo có setup sẵn marktidown, các bạn tùy ý sử dụng công cụ khác

## 5. Chunk, embedding và index

```bash
python -m src.task4_chunking_indexing
```

## 6. Xây dựng hybrid retrieval

- Task 5: semantic search từ ChromaDB.
- Task 6: BM25 trên cùng corpus chunks.
- Task 7: RRF gộp hai bảng xếp hạng theo ID.

```bash
python -m src.task5_semantic_search
python -m src.task6_lexical_search
python -m src.task7_reranking
```

Về rerank là không bắt buộc, các bận có thể sử dụng Jina, hoặc tự self host BGE (hoặc không làm)

## 7. Hoàn thiện fallback và retrieval pipeline

- Task 8 trả `retrieval_method="pageindex"`.
- Task 9 chỉ chạy RRF một lần.
- Calibrate threshold bằng query đúng domain và query ngoài domain.
- Dùng dense cosine score gốc để quyết định fallback.

## 8. Generation có citation

Hoàn thiện Task 10:

- Reorder chunks nhưng không làm mất ID.
- Context có title/source.
- Dispatch theo `LLM_PROVIDER`: OpenAI, Gemini hoặc Anthropic Claude.
- Không đủ evidence thì trả safe refusal.

```bash
python -m src.task10_generation
```

**Hoàn thành khi:** answer đúng `GenerationResult` và citation map được về `sources`.

## 9. Chatbot và evaluation

```bash
streamlit run app.py
```

- UI hiển thị answer, source, retrieval method và score.
- Tạo ít nhất 15 golden Q&A dựa trên corpus.
- Chạy 4 metric: faithfulness, answer relevance, context recall, context precision.
- So sánh dense-only với hybrid + RRF trên cùng cấu hình còn lại.
- Điền `group_project/evaluation/RESULT.md`.

**Hoàn thành khi:** chatbot chạy end-to-end và báo cáo không còn placeholder.

## 10. Kiểm tra và nộp bài

```bash
pytest tests/test_contracts.py -q
pytest tests/test_acceptance.py -q
pytest -q
```

- Mỗi thành viên hoàn thiện individual report.
- Kiểm tra repository không chứa `.env`, API key hoặc file cache.
- Demo một query đúng, một query ngoài domain và kết quả A/B.

### Task 3: dữ liệu chuẩn hóa cho corpus Liên Quân

Triển khai hiện tại đọc 3 HTML chính sách của Task 1 và 8 JSON từ crawler
Task 2 đã cải tiến. Không cần crawl lại hoặc gọi API/LLM để chuẩn hóa:

```bash
python -m pip install -e '.[dev]'
python -m src.task3_convert_markdown
python -m pytest tests/test_task3_convert_markdown.py -q
```

Kết quả nằm trong `data/standardized/legal/` và `data/standardized/news/`,
mỗi nguồn tương ứng một file `.md` cùng tên gốc. Mỗi file gồm:

- YAML front matter: `id`, `source`, `title`, `doc_type`, `url`, `date_crawled`,
  thêm `date_published` nếu HTML cung cấp ngày đăng.
- Một H1 là tiêu đề tài liệu, tiếp theo là nội dung với heading, bảng, danh sách
  và liên kết. Các heading rỗng được loại bỏ, heading cha có nội dung con vẫn giữ.
- `source` tương đối với `data/landing/`; `id` tương đối với `data/standardized/`.
  Metadata được quote bằng JSON scalar hợp lệ trong YAML, giữ an toàn các dấu
  hai chấm, ngoặc kép trong tiêu đề. Ngày nguồn được giữ đúng dạng thu thập.

Làm sạch HTML tập trung vào phần bài viết, bỏ menu/footer/script/style; điều
khoản Garena được khôi phục các heading mục có số. Markdown wiki được chuẩn hóa
Unicode, dòng trống, link bắt đầu bằng `/`; bỏ thông báo stub, bảng điều hướng
chỉ chứa liên kết thể loại Tướng và các mục rỗng. Giữ bảng nội dung, citation,
danh sách lồng nhau, hard break và fenced code. Đặc biệt giữ nguyên các phần
**Phù hiệu**, **Bảng ngọc**, **Phép bổ trợ** được Task 2 khôi phục từ wikitext,
kể cả nhiều bộ ngọc và số lượng từng loại. Không tự bổ sung dữ kiện bị thiếu,
không suy diễn lại build hoặc cập nhật chỉ số gameplay.

Chạy lại không tạo file trùng và không ghi lại file nếu kết quả không đổi. Khi
nguồn được cập nhật, file cùng tên được thay thế qua file tạm. Dữ liệu lỗi/rỗng
làm lệnh dừng với lỗi rõ ràng; file đầu ra cũ không bị thay bằng nội dung rỗng.
Các file hoàn tất trước lỗi vẫn được giữ. Không tự xóa đầu ra khi nguồn bị xóa;
đổi tên/xóa nguồn cần dọn file đầu ra tương ứng. Hai legal input trùng stem bị
từ chối trước khi ghi để tránh ghi đè nhau.

HTML/HTM được xử lý bằng BeautifulSoup và markdownify. PDF/DOCX dùng MarkItDown
khi gặp các định dạng này; PDF scan cần OCR riêng và `.doc` cần đổi sang DOCX.
Corpus hiện tại và kiểm thử nội dung thực tế là HTML/JSON; nhánh PDF/DOCX có
kiểm thử dispatch bằng converter giả, chưa xác minh chuyển đổi file nhị phân thật.

Khi implement Task 4, tách YAML front matter khỏi nội dung trước khi chunk,
đưa `id` vào Document và giữ `source`, `title`, `doc_type`, `url` trong metadata
theo `MODULE_CONTRACTS.md`. Task 4 hiện vẫn là skeleton, chưa tự đọc metadata này.
Test nghiệm thu Task 1 gốc chỉ chấp nhận PDF/DOCX nên chưa khớp corpus HTML;
các test Task 4–10 và evaluation cần hoàn thiện trong các task tương ứng.
