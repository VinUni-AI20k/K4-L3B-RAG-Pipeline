# Individual contribution report

- Họ và tên: Thân Thị Kim Chi
- Mã học viên: 2A202602797
- Nhóm: 4aesieunhan
- Repository/branch: https://github.com/TuTu99999/K4-L3B-RAG-Pipeline/tree/chi
- Commit code chính: `ff85510` (`feat(ui): complete React RAG UI and FastAPI backend bridge`)

---

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| **Frontend UI** | Thiết kế và lập trình toàn bộ giao diện Web RAG Pipeline hiện đại gồm 5 tabs: Trò chuyện RAG, Kho cẩm nang & Luật, Debug Chunks, So sánh A/B và Đánh giá 4 Metrics. | Thư mục `frontend/` (Commit `ff85510`) | Done |
| **Interactive Citation & Modal** | Xây dựng tính năng trích dẫn tương tác: click vào badge `[1]`, `[2]` để mở popup xem chi tiết đoạn trích gốc, số trang và nguồn tài liệu. | `frontend/src/tabs/TabChat.jsx`, `frontend/src/components/SourceCards.jsx` | Done |
| **Safe Refusal & Metrics Dashboard** | Hiện thực trực quan hóa cơ chế từ chối an toàn khi câu hỏi ngoài phạm vi (Out-of-domain) và bảng đo lường 4 chỉ số (Faithfulness, Answer Relevance, Context Precision, Context Recall). | `frontend/src/tabs/TabEvaluation.jsx`, `frontend/src/api/client.js` | Done |
| **Mock & Fallback Engine** | Xây dựng kho tri thức mẫu du lịch (KB Mock) giúp giao diện chạy độc lập, tự động fallback an toàn khi backend offline, đảm bảo không bị crash khi demo. | `frontend/src/data/mockData.js`, `frontend/src/api/client.js` | Done |
| **Backend API Bridge** | Xây dựng API trung gian bằng FastAPI nối giao diện React với các hàm cốt lõi `src/task10_generation.py` và `src/task9_retrieval_pipeline.py`. | `backend/api.py` | Done |

---

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Thiết kế kiến trúc phân tách độc lập (Decoupled Frontend/Backend) tích hợp cơ chế **Mock / Demo Fallback Mode** thay vì dùng giao diện Streamlit nguyên khối.  
   **Lý do/evidence:** Giúp tiến độ phát triển giao diện không bị nghẽn (blocked) bởi tiến độ làm dữ liệu vectorstore của các thành viên khác trong nhóm. Khi demo sản phẩm cho giảng viên, hệ thống luôn sẵn sàng 100%, không bị phụ thuộc vào việc nạp database hay kết nối mạng ngoài.  
   **Trade-off:** Cần xây dựng thêm lớp API trung gian (`backend/api.py`) và bộ dữ liệu du lịch mẫu, tốn nhiều công sức thiết kế và viết code hơn so với việc viết script Streamlit cơ bản.

2. **Quyết định:** Hiện thực tương tác trích dẫn dạng Badge động (`[1]`, `[2]`) kèm popup tra cứu ngữ cảnh gốc và bộ đo độ tương đồng trực quan (Confidence Meter).  
   **Lý do/evidence:** Đáp ứng đúng yêu cầu của hợp đồng Module Contracts (Task 10 - Generation có Citation & Fallback), giúp người dùng và người chấm thi kiểm chứng tức thì tính trung thực (Faithfulness) và nguồn gốc của từng luận điểm trong câu trả lời.  
   **Trade-off:** Phải viết thêm bộ parser regex nhận diện số trích dẫn từ văn bản trả về của LLM và quản lý state mở modal chi tiết trên client.

---

## Kiểm thử và kết quả

- **Kiểm thử trên bản tích hợp cuối:** `npm run build` hoàn thành thành công và toàn bộ Python test đạt **23 passed**.
- **Query live đã kiểm tra:** câu hỏi về địa điểm du lịch Hà Nội trả kết quả hybrid có URL nguồn; câu hỏi viết mã Python trả safe refusal với `retrieval_source="none"`.
- **Kết quả trước/sau nếu có:**
  - *Trước:* Giao diện ban đầu của repo là Streamlit tối giản, chỉ có 1 ô chat đơn thuần, không có trích dẫn chi tiết, không có tab xem chunks và không có dashboard đánh giá metrics.
  - *Sau:* Giao diện web hoàn chỉnh; câu trả lời hiển thị trích dẫn nguồn rõ ràng; ngưỡng production được hiệu chỉnh ở `0.45` và câu hỏi ngoài domain kích hoạt safe refusal.
- **Lỗi đã phát hiện và cách xử lý:**
  - Lỗi chặn cổng mạng (CORS) khi React gọi sang FastAPI: Đã xử lý bằng cách cấu hình `CORSMiddleware` trong `backend/api.py`.
  - Lỗi giao diện bị sập khi Backend chưa chạy: Đã xử lý bằng `AbortSignal.timeout` và cơ chế tự động chuyển sang chế độ Demo dữ liệu mẫu trong `api/client.js`.

---

## Điều còn hạn chế

- **Một hạn chế cụ thể của phần tôi làm:** Người dùng cần chạy đồng thời 2 tiến trình terminal nếu muốn chạy full pipeline thật (port 5173 cho React và port 8000 cho FastAPI).
- **Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện:** Viết một file script tự động (`run.ps1` hoặc `Makefile`/Docker Compose) để khởi động cả Frontend và Backend bằng một cú click duy nhất.

---

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Thân Thị Kim Chi
