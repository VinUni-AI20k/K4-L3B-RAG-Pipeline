# Individual contribution report

Mỗi thành viên copy template này thành:

```text
reports/<student-id>-<short-name>.md
```

Giới hạn khuyến nghị: 1 trang, không chép lại README hoặc mô tả lý thuyết chung. Báo cáo không phải một bài pipeline cá nhân; mục đích là ghi nhận ownership và bằng chứng đóng góp trong sản phẩm nhóm.

---

## Thông tin

- Họ và tên: Trần Thị Thu Hiền
- Mã học viên: 2A202602737
- Nhóm: Gradflow
- Repository/branch: `K4-L3B-RAG-Pipeline` / `hien-feature`

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Hybrid retrieval | Hoàn thiện BM25 edge case, RRF khử trùng lặp và retrieval pipeline dùng cosine score gốc để fallback | `src/task6_lexical_search.py`, `src/task7_reranking.py`, `src/task9_retrieval_pipeline.py` | Done |
| PageIndex fallback | Upload PDF theo SHA-256, cache document ID, xử lý timeout/lỗi provider an toàn | `src/task8_pageindex_vectorless.py` | Done |
| Generation và citation | Tích hợp Gemini/OpenAI/Anthropic, reorder context, chuẩn hóa `[S1, S2]`, kiểm tra citation và safe refusal | `src/task10_generation.py` | Done |
| Chatbot UI | Kết nối pipeline vào Streamlit; hiển thị nguồn, trang, score, retrieval source và nút xóa lịch sử | `app.py` | Done |
| Evaluation | Xây dựng 15 golden cases, runner A/B có cache, structured LLM judge, raw result và báo cáo tổng hợp | `src/evaluate.py`, `group_project/evaluation/` | Done |
| Kiểm thử và tài liệu | Bổ sung regression tests, cập nhật README và tài liệu Task 5–10 | `tests/test_contracts.py`, `README.md`, `docs/TASK5_TO_10.md` | Done |

Chỉ kê khai công việc có thể đối chiếu bằng file, commit, pull request, test hoặc kết quả evaluation.

## Quyết định kỹ thuật quan trọng

Mô tả tối đa hai quyết định mà bạn trực tiếp tham gia:

1. **Quyết định:** Dùng cosine score gốc của dense retrieval để quyết định fallback; RRF chỉ dùng để hợp nhất thứ hạng đúng một lần.

   **Lý do/evidence:** Cosine similarity, BM25 và RRF có thang điểm khác nhau; so threshold với RRF score sẽ không có ý nghĩa. Contract tests xác nhận fallback dùng dense score và RRF chỉ được gọi một lần.

   **Trade-off:** Cần hiệu chỉnh `SCORE_THRESHOLD` riêng trên query đúng/sai domain; giá trị 0.30 hiện chỉ là cấu hình ban đầu.

2. **Quyết định:** Chỉ chấp nhận câu trả lời có citation `[S#]` ánh xạ được về danh sách nguồn; provider lỗi hoặc citation sai sẽ trả safe refusal.

   **Lý do/evidence:** Đây là chatbot pháp luật/du lịch nên khả năng đối chiếu nguồn quan trọng hơn việc luôn tạo ra câu trả lời. Regression tests bao phủ citation sai, citation gộp và provider không khả dụng.

   **Trade-off:** Cơ chế thận trọng có thể từ chối một câu đúng nếu model không tuân thủ định dạng citation.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: `python -m pytest -q`; các câu hỏi về quyền khách du lịch, điều kiện công nhận điểm du lịch, thời hạn thẻ hướng dẫn viên và cao lầu Hội An; một câu Bitcoin ngoài domain.
- Kết quả trước/sau nếu có: 42 test đạt. Paired A/B trên 15 câu cho dense-only trung bình 0.920 và hybrid + RRF 0.839; dense-only nhanh hơn (4.46 giây so với 7.45 giây/câu).
- Lỗi đã phát hiện và cách xử lý: sửa BM25 loại nhầm kết quả score 0 trên corpus nhỏ; giữ Gemini client sống hết request để tránh `client has been closed`; chuyển khỏi model quá tải; chuẩn hóa citation gộp; thêm log provider và cache evaluation.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: evaluator và generator cùng dùng Gemini nên có thể có thiên lệch; ba PDF pháp luật là OCR và chưa được soát thủ công hoàn toàn.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: grid-search chunk size, overlap, BM25 weight/RRF và `top_k` trên tập development riêng, sau đó đánh giá lại trên một hold-out set để tránh tối ưu trực tiếp lên 15 golden cases.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 26/09/2026
- Tên thành viên: Trần Thị Thu Hiền
