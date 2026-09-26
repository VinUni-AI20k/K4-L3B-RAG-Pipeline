# Individual Contribution Report

## Thông tin

- Họ và tên: Phạm Văn Hoàng Anh Tú
- Mã học viên: 2A202602507
- Nhóm: K4-L3B-RAG-Pipeline
- Vai trò: Member & Generation Engineer

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Task 8: Vectorless Fallback | Thiết kế interface tích hợp PageIndex fallback khi dense score thấp hơn ngưỡng | `src/task8_pageindex_vectorless.py` | Done |
| Task 9: Retrieval Pipeline | Tích hợp hoàn chỉnh pipeline truy xuất: Dense + BM25 -> RRF -> Score Threshold check -> Fallback | `src/task9_retrieval_pipeline.py` | Done |
| Task 10: Generation & Citation | Xây dựng prompt sinh câu trả lời kèm citation `[Document N]`, cài đặt context reordering và safe refusal | `src/task10_generation.py` | Done |
| Đa nền tảng LLM | Hỗ trợ cấu hình chuyển đổi linh hoạt giữa OpenAI, Gemini và Anthropic qua biến môi trường | `src/task10_generation.py` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Áp dụng kỹ thuật Lost-in-the-Middle context reordering trong `reorder_for_llm`.  
   **Lý do/evidence:** Nghiên cứu của Liu et al. chỉ ra các mô hình LLM thường chú ý tốt nhất ở phần đầu và phần cuối ngữ cảnh. Việc đảo xen kẽ giúp chunk quan trọng nhất nằm ở vị trí thu hút sự chú ý của model.  
   **Trade-off:** Cần đảo mảng trước khi đưa vào prompt nhưng không làm thay đổi ID của nguồn.

2. **Quyết định:** Thiết lập safe refusal bắt buộc khi không có văn bản phù hợp hoặc khi fallback không tìm thấy thông tin.  
   **Lý do/evidence:** Trong lĩnh vực du lịch và quy định pháp luật, việc mô hình bịa đặt thông tin (hallucination) có thể gây hiểu sai luật hoặc sai lệch lịch trình.  
   **Trade-off:** Mô hình chấp nhận trả lời "Tôi không thể xác minh thông tin..." đối với các câu hỏi ngoài phạm vi thay vì cố đoán.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: Kiểm tra với câu hỏi trong miền ("Quyền của khách du lịch") và ngoài miền ("Thủ đô của nước Pháp").
- Kết quả trước/sau: Với câu hỏi ngoài miền, hệ thống trả về điểm cosine ~0.17 < 0.35 và sinh ra câu từ chối an toàn kèm `sources: []`.
- Lỗi đã phát hiện và cách xử lý: Lỗi format citation không khớp với danh sách source trả về; đã đồng bộ hóa việc đánh số Document 1, 2, ... với danh sách `sources`.

## Điều còn hạn chế

- Một hạn chế cụ thể: Hiện tại citation mới dừng ở mức cấp độ chunk/document, chưa trích dẫn chính xác đến từng chỉ số ký tự (span-level citation).
- Hướng cải tiến: Bổ sung logic trích xuất trích đoạn trực tiếp (quote snippet) để tô sáng trên giao diện người dùng.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 2026-09-25
- Tên thành viên: Phạm Văn Hoàng Anh Tú
