# Individual contribution report

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
| Generation và citation | Tích hợp Gemini/OpenAI/Anthropic, reorder context, chuẩn hóa citation, kiểm tra nguồn và safe refusal | `src/task10_generation.py` | Done |
| Chatbot UI | Kết nối pipeline vào Streamlit; hiển thị nguồn, trang, score, retrieval source và xóa lịch sử | `app.py` | Done |
| Evaluation | Xây dựng 15 golden cases, runner A/B có cache, structured LLM judge, raw result và báo cáo | `src/evaluate.py`, `group_project/evaluation/` | Done |
| Kiểm thử và tài liệu | Bổ sung regression tests, README và tài liệu Task 5–10 | `tests/test_contracts.py`, `README.md`, `docs/TASK5_TO_10.md` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Dùng cosine score gốc của dense retrieval để quyết định fallback; RRF chỉ hợp nhất thứ hạng đúng một lần.  
   **Lý do/evidence:** Cosine, BM25 và RRF có thang điểm khác nhau; contract tests xác nhận đúng invariant này.  
   **Trade-off:** `SCORE_THRESHOLD=0.30` vẫn cần hiệu chỉnh bằng query đúng/sai domain.

2. **Quyết định:** Chỉ nhận câu trả lời có citation `[S#]` hợp lệ; lỗi provider hoặc citation sai dẫn tới safe refusal.  
   **Lý do/evidence:** Nội dung pháp luật cần đối chiếu được nguồn; regression tests bao phủ citation sai/gộp và provider lỗi.  
   **Trade-off:** Có thể từ chối một câu đúng nếu model không tuân thủ định dạng.

## Kiểm thử và kết quả

- Test/query: toàn bộ `pytest`; câu hỏi pháp luật, điểm đến, ẩm thực và câu Bitcoin ngoài domain.
- Kết quả: 42 test đạt. Trên 15 golden cases, dense-only đạt 0.920; hybrid + RRF đạt 0.839. Latency trung bình tương ứng 4.46 và 7.45 giây/câu.
- Lỗi đã xử lý: BM25 score 0 trên corpus nhỏ; Gemini client bị đóng sớm; model quá tải; citation gộp; lỗi provider bị ẩn; evaluation bị gián đoạn.

## Điều còn hạn chế

- Evaluator và generator cùng dùng Gemini nên có thể có thiên lệch; dữ liệu pháp luật OCR chưa được soát thủ công toàn bộ.
- Nếu có thêm thời gian, tôi sẽ tối ưu chunking/RRF trên development set riêng rồi xác nhận bằng hold-out set.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 26/09/2026
- Tên thành viên: Trần Thị Thu Hiền
