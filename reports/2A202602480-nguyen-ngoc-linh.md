# Individual contribution report

## Thông tin

- Họ và tên: Nguyễn Ngọc Linh
- Mã học viên: 2A202602480
- Nhóm: Trung thu
- Repository/branch: https://github.com/pddczpl/K4-L3B-RAG-Pipeline

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Fusion & fallback | Phụ trách hoàn thiện pipeline retrieval: chạy dense search và BM25, gộp kết quả bằng RRF một lần, dùng dense cosine score gốc để quyết định PageIndex fallback, và giữ pipeline không bị crash khi fallback lỗi. | `src/task9_retrieval_pipeline.py` | Partial |
| Generation có citation | Phụ trách reorder chunks, format context có title/source, gọi provider LLM theo cấu hình, trả về answer cùng `sources` và `retrieval_source`, đồng thời dùng safe refusal khi không đủ evidence. | `src/task10_generation.py` | Partial |
| Chatbot UI | Phụ trách tích hợp `generate_with_citation` vào Streamlit và hiển thị answer, sources, retrieval method và score trong giao diện. | `app.py` | Partial |

## Quyết định kỹ thuật quan trọng

1. **Dùng RRF để fusion dense search và BM25:**
   **Lý do/evidence:** Dense search phù hợp với truy vấn theo ngữ nghĩa, còn BM25 bổ trợ các từ khóa và mã định danh chính xác. Contract yêu cầu công thức RRF `sum(1 / (k + rank))`, rank bắt đầu từ 1 và chỉ fuse một lần.
   **Trade-off:** Phải chạy hai phương thức retrieval nên có thể tăng thời gian xử lý; bù lại không cần chuẩn hóa hai thang điểm khác nhau.

2. **Dùng dense cosine score gốc cho fallback:**
   **Lý do/evidence:** Contract yêu cầu so sánh `score_threshold` với điểm dense ban đầu, không so sánh với RRF score. Khi điểm dense thấp hơn threshold thì thử PageIndex; nếu fallback lỗi thì trả kết quả hybrid thay vì làm UI crash.
   **Trade-off:** Threshold cần được hiệu chỉnh bằng cả query đúng domain và query ngoài domain để cân bằng giữa khả năng fallback và độ ổn định của kết quả.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng:
- Kết quả trước/sau nếu có:
- Lỗi đã phát hiện và cách xử lý: Hiện các hàm `retrieve`, `reorder_for_llm`, `format_context`, `call_llm`, `generate_with_citation` và phần gọi generation trong `app.py` vẫn còn `TODO`/`NotImplementedError`, nên chưa có kết quả chạy end-to-end để ghi nhận.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: Các module thuộc phạm vi phụ trách chưa được implement hoàn chỉnh; chưa có bằng chứng test hoặc evaluation để xác nhận pipeline fusion, fallback, generation và UI hoạt động end-to-end.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện:

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc được phân công và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/9/2026
- Tên thành viên: Nguyễn Ngọc Linh
