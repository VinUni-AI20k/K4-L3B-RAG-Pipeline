# Individual contribution report

---

## Thông tin

- Họ và tên: Phùng Quốc Việt
- Mã học viên: 2A202602456
- Nhóm: Soul
- Repository/branch: `vietpq`
- Vai trò: Backend / Pipeline & Generation Engineer

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 8 — PageIndex vectorless | Xây dựng hàm `upload_documents` có cache ID (`pageindex_cache.json`) và hàm `pageindex_search` có xử lý timeout/bắt lỗi an toàn | `src/task8_pageindex_vectorless.py` (commit `b3008c2`) | Done |
| Task 9 — Retrieval pipeline | Hoàn thiện hàm `retrieve()` kết hợp Dense + BM25 qua RRF một lần duy nhất, kích hoạt fallback khi dense score < threshold, chống crash khi service lỗi | `src/task9_retrieval_pipeline.py` (commit `b3008c2`) | Done |
| Task 10 — Generation & Citation | Cài đặt `reorder_for_llm` chống Lost-in-the-middle, `format_context` kèm nhãn Title/Source, `call_llm` đa provider (Gemini/OpenAI/Claude) và sinh câu trả lời kèm Safe Refusal | `src/task10_generation.py` (commit `b3008c2`) | Done |
| Unit Test & Contract Verification | Kiểm tra và pass toàn bộ 15/15 contract tests của toàn pipeline, đặc biệt là các test liên quan đến fallback, non-mutating reorder và safe refusal | `tests/test_contracts.py` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Sử dụng điểm tương đồng cosine dense gốc (`best_dense_score`) thay vì điểm sau RRF để so sánh với `score_threshold` khi kích hoạt Fallback.  
   **Lý do/evidence:** Điểm xếp hạng RRF ($1/(k + rank)$) chỉ mang tính xếp hạng tương đối trong danh sách kết quả cục bộ chứ không phản ánh độ tương đồng ngữ nghĩa thực sự giữa câu hỏi và tài liệu. Với các câu hỏi ngoài phạm vi (out-of-domain), chunk đứng đầu vẫn có thể có điểm RRF cao (xấp xỉ $1/61$), làm hệ thống không nhận diện được trường hợp thiếu thông tin. Ngược lại, điểm cosine dense score gốc ($1 - dist$) phản ánh chính xác độ tự tin của mô hình embedding để đưa ra quyết định chuyển hướng sang PageIndex hoặc Safe Refusal.  
   **Trade-off:** Cần lưu giữ giá trị score từ dense search ban đầu trước khi đưa vào hàm RRF fusion.

2. **Quyết định:** Áp dụng kỹ thuật xếp đặt lại ngữ cảnh (`reorder_for_llm`) theo dạng đối xứng (phần tử chẵn lên đầu, phần tử lẻ đảo ngược đưa về cuối) và cơ chế Safe Refusal chuẩn.  
   **Lý do/evidence:** Hiện tượng "Lost-in-the-Middle" khiến các mô hình LLM thường ghi nhớ và trích dẫn tốt nhất ở đầu và cuối prompt, dễ bỏ qua thông tin nằm ở giữa context. Việc reorder giúp các chunk quan trọng nhất xuất hiện ở hai vị trí đắc địa này mà không làm biến đổi mảng gốc (`non-mutating`). Đồng thời, khi tập `sources` rỗng hoặc câu hỏi ngoài miền, hệ thống trả về đúng mẫu câu Safe Refusal theo hợp đồng ("Tôi không thể xác minh thông tin này từ nguồn hiện có.") để triệt tiêu hiện tượng ảo giác (hallucination).  
   **Trade-off:** Phải đảm bảo logic reorder không làm mất mát ID và metadata của các chunk gốc.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng:
  - Chạy toàn bộ bộ kiểm thử hợp đồng:
    ```bash
    .venv\Scripts\pytest tests/test_contracts.py -v
    ```
  - Kiểm thử trực tiếp các case Fallback, Fusion và Generation:
    ```bash
    .venv\Scripts\pytest tests/test_contracts.py -k "reorder or retrieve or generation" -v
    ```
- Kết quả trước/sau:
  - **Trước:** Task 8, 9, 10 đều ném lỗi `NotImplementedError`, có 4/15 tests bị FAILED trong `test_contracts.py`.
  - **Sau:** **15/15 bài test PASSED 100%**:
    + `test_reorder_is_non_mutating_and_context_contains_source`: PASSED
    + `test_retrieve_uses_dense_score_for_fallback`: PASSED (chuyển sang PageIndex khi dense score thấp hơn ngưỡng).
    + `test_retrieve_fuses_once_when_dense_is_confident`: PASSED (chỉ gọi RRF 1 lần, không gọi fallback thừa).
    + `test_retrieve_survives_fallback_provider_error`: PASSED (bắt ngoại lệ an toàn, trả về hybrid thay vì sập app).
    + `test_generation_result_validator_accepts_safe_refusal`: PASSED.
- Lỗi đã phát hiện và cách xử lý:
  - Khi mock PageIndex bị lỗi ngoại lệ mạng hoặc API provider die, nếu không bọc `try...except` chặt chẽ trong `retrieve()` thì toàn bộ pipeline sẽ bị gián đoạn. Tôi đã xử lý bằng cách bọc khối fallback trong `try...except` và luôn trả về `hybrid[:top_k]` dự phòng.
  - Hàm `generate_with_citation()` cần đảm bảo trường `retrieval_source` luôn thuộc tập hợp hợp lệ `{"hybrid", "pageindex", "none"}` theo yêu cầu của `validate_generation_result()`.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: Hiện tại hàm `call_llm` mới chỉ trả về toàn bộ text một lần (blocking request), chưa hỗ trợ cơ chế phản hồi theo luồng (streaming tokens) trên giao diện chatbot Streamlit.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: Bổ sung generator streaming cho `generate_with_citation` để tích hợp mượt mà vào giao diện Streamlit, đồng thời viết thêm script tự động tính điểm đo lường độ tin cậy trích dẫn (Faithfulness score) trên tập câu hỏi Golden Dataset.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Phùng Quốc Việt
