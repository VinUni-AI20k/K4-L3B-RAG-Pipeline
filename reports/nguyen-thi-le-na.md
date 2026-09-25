# Individual contribution report — Nguyễn Thị Lê Na

---

## Thông tin

- **Họ và tên:** Nguyễn Thị Lê Na
- **Mã học viên:** HV-2026-002
- **Nhóm:** Nhóm K4-L3B (RAG Pipeline tuyển sinh NEU 2026)
- **Repository/branch:** `vietbui000/K4-L3B-RAG-Pipeline` (branch: `nguyenthilena`)

---

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| **Task 11 — Streamlit Chatbot UI** | Thiết kế & lập trình giao diện người dùng tương tác Streamlit (`app.py`), hiển thị câu trả lời, citation, badge phương thức retrieval, score, và expander trích đoạn chunk | `app.py`, `docs/NA_WORK_SUMMARY.md` | Done |
| **Task 11b — Automated Evaluation Runner** | Xây dựng chương trình runner đánh giá RAG A/B Testing (`src/task11_evaluation.py`) đọc 20 câu hỏi `golden_dataset.json` và tự động thực thi 2 nhánh Dense-only và Hybrid+RRF | `src/task11_evaluation.py` | Done |
| **Task 12 — RAG Metric Computation & Log Traces** | Đo lường 4 chỉ số (Faithfulness, Answer Relevance, Context Recall, Context Precision), xuất các bản ghi trace định dạng JSON có thể kiểm chứng | `group_project/evaluation/runs/dense_run.json`, `group_project/evaluation/runs/hybrid_run.json` | Done |
| **Task 12b — RAG Evaluation Report** | Tổng hợp kết quả thực nghiệm A/B, xây dựng bảng điểm, phân tích câu lỗi (Worst performers) và đề xuất khuyến nghị nâng cấp hệ thống | `reports/RESULT.md` | Done |

---

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Xây dựng Runner Đánh giá A/B độc lập tự động ghi log vết truy xuất dưới định dạng JSON (`dense_run.json` & `hybrid_run.json`).  
   **Lý do/evidence:** Cần có bằng chứng thực nghiệm minh bạch, độc lập và có thể chạy lại (reproducible) để so sánh khách quan giữa nhánh Config A (Dense-only) và Config B (Hybrid+RRF).  
   **Trade-off:** Gia tăng dung lượng lưu trữ file log run (khoảng 200KB/file JSON), nhưng đảm bảo kết quả báo cáo trung thực, có vết dữ liệu truy soát thực tế.

2. **Quyết định:** Thiết kế giao diện Chatbot minh bạch nguồn trích dẫn với các khối hiển thị rõ nguồn văn bản, đường dẫn URL gốc, score tương đồng và nút expander xem nội dung chunk gốc.  
   **Lý do/evidence:** Người dùng tư vấn tuyển sinh đòi hỏi tính chính xác tuyệt đối và cần được kiểm chứng trực tiếp đoạn văn bản gốc mà chatbot căn cứ trả lời.  
   **Trade-off:** Giao diện cần xử lý thêm các component hiển thị trạng thái và badge phương thức retrieval, nhưng đem lại trải nghiệm minh bạch và gia tăng độ tin cậy.

---

## Kiểm thử và kết quả

- **Test hoặc query tôi đã dùng:**  
  `python -m src.task11_evaluation --mode both`  
  `streamlit run app.py`
- **Kết quả trước/sau nếu có:**  
  - *Chạy runner A/B evaluation:* Hoàn thành đánh giá 20 câu hỏi golden dataset cho cả 2 cấu hình.  
  - *Kết quả:* Config B (Hybrid+RRF) vượt trội Config A (Dense-only) với điểm trung bình **72.67% vs 62.66% (+10.00%)**, trong đó chỉ số **Context Recall tăng từ 73.70% lên 87.94% (+14.24%)**.
- **Lỗi đã phát hiện và cách xử lý:**  
  - *Lỗi:* Giao diện Streamlit bị giật và cuộn lại từ đầu trang mỗi khi nút fallback hoặc expander chunk được mở.  
  - *Cách xử lý:* Sử dụng `st.container()` và `st.empty()` để cập nhật dữ liệu động cục bộ mà không làm re-render lại toàn bộ trang web.

---

## Điều còn hạn chế

- **Một hạn chế cụ thể của phần tôi làm:**  
  Giao diện Chatbot Streamlit hiện tại chưa hỗ trợ phản hồi dạng dòng chảy (streaming tokens) cho LLM response.
- **Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện:**  
  Tích hợp RAGAS Framework chính thức chạy qua API LLM Evaluator (GPT-4o) để thay thế cho bộ proxy metric token-overlap hiện tại.

---

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- **Ngày:** 25/09/2026
- **Tên thành viên:** Nguyễn Thị Lê Na
