# Task 5–10 — Retrieval, generation và giao diện

## Luồng dữ liệu

1. `task5_semantic_search` mã hóa query bằng đúng encoder BGE-M3 của Task 4,
   truy vấn Chroma cosine và đổi distance thành similarity.
2. `task6_lexical_search` đọc cùng `chunks.jsonl` (hoặc Chroma) và xếp hạng
   bằng BM25, phù hợp với số điều, mã văn bản và tên riêng.
3. `task7_reranking` gộp hai danh sách đúng một lần bằng RRF. Điểm RRF chỉ dùng
   để xếp hạng, không dùng để quyết định fallback.
4. `task9_retrieval_pipeline` so sánh `SCORE_THRESHOLD` với cosine score gốc.
   Khi confidence thấp, nó thử PageIndex; lỗi dịch vụ giữ lại kết quả local.
5. `task10_generation` reorder context, gắn nhãn `[S1]`, dispatch tới provider
   được cấu hình và kiểm tra mọi citation có ánh xạ tới `sources`.
6. `app.py` lưu cả câu trả lời, nguồn, trang, URL, score và retrieval source
   trong session state để lịch sử chat render ổn định.

## PageIndex fallback

PageIndex là tùy chọn vì đây là dịch vụ ngoài. `upload_documents()` gửi ba PDF
gốc trong `data/landing/legal/`, lưu `doc_id` theo SHA-256 vào file cache đã được
Git ignore và không upload lại file không đổi. `pageindex_search()` gọi Chat API
với citation; thiếu key hoặc mapping thì trả danh sách rỗng an toàn.

```powershell
python -m src.task8_pageindex_vectorless
```

Việc upload tài liệu ra dịch vụ ngoài chỉ nên thực hiện sau khi nhóm xác nhận
quyền chia sẻ tài liệu và cấu hình `PAGEINDEX_API_KEY`.

## Generation

Đặt `LLM_PROVIDER` là `openai`, `gemini` hoặc `anthropic`; đặt `LLM_MODEL` và API
key tương ứng. Provider lỗi, retrieval rỗng, citation thiếu hoặc citation vượt
phạm vi đều dẫn tới câu từ chối an toàn thay vì bịa câu trả lời.

## Kiểm thử và giới hạn còn lại

```powershell
pytest -q
```

Các test offline không gọi mạng. Đánh giá A/B thực tế đã chạy đủ 15 golden cases
bằng BGE-M3, Chroma và Gemini; báo cáo cùng raw output nằm trong
`group_project/evaluation/`. Chạy lại bằng `python -m src.evaluate`; tiến độ được
cache sau từng cấu hình để có thể tiếp tục nếu provider tạm thời lỗi.
