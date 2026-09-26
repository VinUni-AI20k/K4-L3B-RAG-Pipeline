# Individual contribution report — Lê Thị Duyên

---

## Thông tin

- **Họ và tên:** Lê Thị Duyên
- **Mã học viên:** HV-2026-003
- **Nhóm:** Nhóm K4-L3B (RAG Pipeline tuyển sinh NEU 2026)
- **Repository/branch:** `vietbui000/K4-L3B-RAG-Pipeline` (branch: `lethiduyen`)

---

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| **Task 8 — PageIndex Fallback** | Phát triển module tìm kiếm Vectorless Fallback (`pageindex_search`), quản lý cache ID tài liệu (`data/pageindex_cache.json`), tích hợp cơ chế chống crash khi gặp lỗi timeout API | `src/task8_pageindex_vectorless.py` | Done |
| **Task 9 — Unified Retrieval Pipeline** | Xây dựng pipeline truy xuất hợp nhất (`retrieve`), tích hợp Dense Search & BM25 Search, thiết lập ngưỡng Cosine Similarity (`SCORE_THRESHOLD = 0.35`) kích hoạt Fallback | `src/task9_retrieval_pipeline.py` | Done |
| **Task 10 — Context Preparation** | Triển khai thuật toán `reorder_for_llm` chống hiện tượng "Lost-in-the-Middle" và hàm `format_context` gắn label trích dẫn chuẩn cho LLM | `src/task10_generation.py` | Done |
| **Task 10b — Citation Generation & Multi-LLM** | Phát triển hàm `generate_with_citation` hỗ trợ đa nhà cung cấp LLM (OpenAI, Gemini, Anthropic) với chính sách từ chối an toàn (Safe Refusal) | `src/task10_generation.py`, `docs/GENERATION_HANDOFF.md` | Done |

---

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Sử dụng duy nhất điểm Cosine Similarity gốc của Dense Search ($<0.35$) làm ngưỡng phân định duy nhất để kích hoạt PageIndex Fallback.  
   **Lý do/evidence:** RRF Score và BM25 Score không có thang đo xác suất đồng nhất. Thực nghiệm trên 6 kịch bản `fallback_dataset.json` cho thấy ngưỡng $0.35$ phân tách chính xác giữa các câu hỏi trong phạm vi (đạt điểm $\ge 0.58$) và các câu hỏi ngoài phạm vi/thiếu bằng chứng (đạt điểm chỉ $0.18 - 0.32$).  
   **Trade-off:** Phải chạy Dense Search trước để kiểm tra điểm tương đồng trước khi quyết định gọi Fallback, nhưng loại bỏ hoàn toàn nguy cơ fallback nhầm khi gặp các từ khóa hiếm.

2. **Quyết định:** Áp dụng chiến lược xen kẽ vị trí các đoạn văn bản (`reorder_for_llm`) đưa các chunk quan trọng nhất về hai đầu ngữ cảnh (đầu và cuối prompt).  
   **Lý do/evidence:** Khắc phục triệt để hiện tượng "Lost-in-the-Middle" trong các mô hình LLM khi context quá dài, giúp LLM chú ý đầy đủ đến toàn bộ bằng chứng được cung cấp.  
   **Trade-off:** Đòi hỏi thêm thao tác biến đổi thứ tự mảng chunk, nhưng cải thiện rõ rệt chỉ số Faithfulness và độ chính xác của trích dẫn.

---

## Kiểm thử và kết quả

- **Test hoặc query tôi đã dùng:**  
  `pytest tests/test_contracts.py`  
  `python -m src.task10_generation`
- **Kết quả trước/sau nếu có:**  
  - *Trước:* Chưa có cơ chế xử lý khi vector search trả về điểm thấp hoặc khi hỏi câu ngoài chủ đề (dễ dẫn tới hallucination).  
  - *Sau:* Pass **100% hợp đồng module (Contract Tests)**; kiểm thử 6 kịch bản fallback hoạt động chính xác (hỏi điểm 2030 từ chối suy đoán, hỏi ngoài lề kích hoạt PageIndex fallback thành công).
- **Lỗi đã phát hiện và cách xử lý:**  
  - *Lỗi:* API bên thứ ba (PageIndex / OpenRouter) đôi khi bị timeout hoặc ngắt kết nối đột ngột làm crash pipeline.  
  - *Cách xử lý:* Bọc toàn bộ các lệnh gọi API external trong khối `try...except`, nếu xảy ra sự cố sẽ tự động quay về sử dụng kết quả Hybrid Search tốt nhất và thông báo cho người dùng.

---

## Điều còn hạn chế

- **Một hạn chế cụ thể của phần tôi làm:**  
  Thời gian phản hồi (latency) của hệ thống tăng thêm khoảng 1.2s khi kích hoạt PageIndex Fallback do phải chờ kết nối API external.
- **Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện:**  
  Triển khai cơ chế gọi API bất đồng bộ (Async/Parallel execution) giữa Dense Search, BM25 Search và PageIndex để tối ưu hóa thời gian truy xuất.

---

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- **Ngày:** 25/09/2026
- **Tên thành viên:** Lê Thị Duyên
