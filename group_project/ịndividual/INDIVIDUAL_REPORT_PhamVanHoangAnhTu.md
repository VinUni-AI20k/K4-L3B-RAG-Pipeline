# Individual contribution report

## Thông tin

- Họ và tên: Phạm Văn Hoàng Anh Tú
- Mã học viên: 2A202602507
- Nhóm: Chatbot RAG — Du lịch Ninh Bình (Ngô Thế Khanh, Phạm Văn Hoàng Anh Tú, Vũ Đình Thư, Lê Văn Sang)
- Repository/branch: <link repo nhóm> — nhánh `PhamVanHoangAnhTu`

## Phần việc đã thực hiện

Vai trò trong nhóm: **C — Retrieval** (Task 6–9 và hiệu chỉnh threshold).

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 6 — Lexical search | BM25Plus trên cùng corpus chunk với dense (đọc từ ChromaDB); tokenizer tiếng Việt: chuẩn hóa NFC, tách âm tiết, thêm bigram âm tiết; chỉ trả chunk có ít nhất 1 token khớp | `src/task6_lexical_search.py` | Done |
| Task 7 — RRF | Fuse dense + BM25 theo `sum(1/(k+rank))`, k=60, rank từ 1; gộp theo ID, không sửa kết quả gốc, hòa điểm thì giữ thứ tự xuất hiện | `src/task7_reranking.py` | Done |
| Task 8 — PageIndex fallback | Upload PDF legal, cache doc_id, parse node → SearchResult `pageindex`; bọc timeout 20s vì SDK không có timeout; mọi lỗi trả `[]` | `src/task8_pageindex_vectorless.py` | Partial — chưa chạy với API thật (nhóm không có PAGEINDEX_API_KEY) |
| Task 9 — Retrieval pipeline | Dense + BM25 (top_k×2 mỗi nhánh), RRF đúng 1 lần; fallback theo cosine gốc của dense; `use_reranking=False` = dense-only cho A/B | `src/task9_retrieval_pipeline.py` | Done |
| Hiệu chỉnh threshold | Script chạy 10 câu in-domain + 10 out-of-domain, chọn ngưỡng theo balanced accuracy | `src/calibrate_threshold.py`, `group_project/evaluation/threshold_calibration.md` | Done |
| Tích hợp & đánh giá | Chạy toàn pipeline trên máy, duyệt golden dataset (bỏ 2, sửa 7 câu), chạy A/B, phân tích worst performers | `group_project/evaluation/` | Done |

Ghi chú: mã nguồn được viết với sự hỗ trợ của Claude (Anthropic). Tôi là người chạy, kiểm thử, phát hiện và sửa lỗi, đọc kết quả đánh giá, và có thể giải thích từng quyết định bên dưới.

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Dùng BM25Plus thay BM25Okapi, kèm tokenizer tiếng Việt (NFC + âm tiết + bigram âm tiết).
   **Lý do/evidence:** Corpus nhỏ, âm tiết phổ biến như "du", "lịch" xuất hiện ở hơn nửa số chunk khiến IDF của Okapi bằng 0 hoặc âm; contract test `test_lexical_search_returns_bm25_contract` fail nếu dùng Okapi như code gợi ý. PDF tiếng Việt thường lưu dạng Unicode tổ hợp (NFD) — đã thử: văn bản NFD vẫn khớp đúng query NFC sau chuẩn hóa. Bigram giúp "Tam Cốc", "Cúc Phương" khớp như một từ.
   **Trade-off:** BM25Plus cộng điểm nền cho mọi document nên phải lọc thêm chunk không khớp token nào; bigram làm index lớn hơn; chưa dùng thư viện tách từ chuyên dụng (pyvi, underthesea).

2. **Quyết định:** Quyết định fallback bằng cosine gốc của dense, không dùng RRF score; ngưỡng lấy từ hiệu chỉnh thay vì đoán.
   **Lý do/evidence:** RRF score chỉ phản ánh thứ hạng (khoảng 0.016–0.033), khác thang đo với cosine. Hiệu chỉnh với `text-embedding-3-small`: in-domain min 0.5014 / max 0.8395, out-of-domain min 0.2352 / max 0.4487 → ngưỡng 0.475 tách đúng 100% (balanced accuracy).
   **Trade-off:** Chỉ 20 câu hiệu chỉnh nên khoảng cách an toàn giữa hai nhóm (0.449–0.501) còn hẹp; ngưỡng phụ thuộc embedding model, đổi model phải hiệu chỉnh lại.

## Kiểm thử và kết quả

- **Test hoặc query tôi đã dùng:**
  - `pytest tests/test_contracts.py -q` → 15/15 pass; `pytest -q` toàn bộ → 20 passed.
  - `python -m src.task9_retrieval_pipeline "Tam Cốc cách trung tâm bao xa"`, `python -m src.task10_generation "Vườn quốc gia Cúc Phương được thành lập năm nào?"` (trả lời "năm 1962 [1][2]"), câu ngoài chủ đề "Cách nấu phở bò?" → từ chối đúng.
  - Đánh giá ragas 0.4.3 trên golden dataset 18 câu, top_k=5.
- **Kết quả trước/sau (A = dense-only, B = hybrid + RRF — phần retrieval tôi phụ trách):**

  | Metric | A | B | Delta |
  |---|---:|---:|---:|
  | Faithfulness | 0.875 | 0.972 | +0.097 |
  | Answer relevance | 0.654 | 0.715 | +0.060 |
  | Context recall | 0.889 | 1.000 | +0.111 |
  | Context precision | 0.755 | 0.823 | +0.069 |
  | Hit@5 | 0.889 | 1.000 | +0.111 |
  | Số câu bị từ chối | 2 | 0 | −2 |

  Hai câu về Tuần Du lịch Ninh Bình bị A từ chối (điểm 0) nhưng B trả lời đúng nhờ BM25 khớp từ khóa "Tuần du lịch", kéo chunk đúng vào top 5.
- **Lỗi đã phát hiện và cách xử lý:**
  - Câu "Tam Cốc cách thành phố Ninh Bình bao xa?" bị từ chối dù đã truy xuất đúng bài: điều kiện phát hiện từ chối quá rộng — câu trả lời có citation nhưng kèm ý "không thể xác minh" bị coi là từ chối. Sửa thành chỉ từ chối khi không có citation (`src/task10_generation.py`); sau sửa trả lời "khoảng 7 km [1]".
  - Top 5 dense bị bài quy hoạch `article_05` (khoảng 1.200 chunk) chiếm 4–5 vị trí → nguyên nhân chính của worst performers #1–#3; đã ghi vào Recommendations của `RESULT.md`.

## Điều còn hạn chế

- **Một hạn chế cụ thể của phần tôi làm:** retrieval chưa có cơ chế đa dạng nguồn, nên một tài liệu rất dài lấn át top_k (context precision của B ở câu worst #3 chỉ 0.25); PageIndex fallback chưa được kiểm chứng với API thật; lần chạy đánh giá vẫn dùng ngưỡng mặc định 0.3 thay vì 0.475 đã hiệu chỉnh.
- **Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện:** giới hạn tối đa 2 chunk mỗi tài liệu trong top_k của `retrieve()`, cập nhật `SCORE_THRESHOLD=0.475`, rồi chạy lại A/B để đo thay đổi của context precision và số câu bị từ chối.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Phạm Văn Hoàng Anh Tú
