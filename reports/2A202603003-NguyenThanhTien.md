# Individual contribution report

## Thông tin

- Họ và tên: NGUYỄN THÀNH TIẾN
- Mã học viên: 2A202603003
- Nhóm: Gene (hoặc tên nhóm của bạn)
- Vai trò theo TEAMMATES.md: Người C (Generation & UI)

## Đóng góp chính

- Viết các hàm `reorder_for_llm` và `format_context` trong file `src/task10_generation.py` để xử lý list các chunks trước khi đẩy vào LLM, giúp tối ưu context window và giảm thiểu hiện tượng lost-in-the-middle.
- Thiết kế và lập trình giao diện Streamlit toàn diện trong `app.py` cho chủ đề **Tuyển sinh Đại học**. Giao diện bao gồm: sidebar thống kê (tài liệu, chunks), gợi ý câu hỏi (suggested questions), giao diện chat trực quan với topic cards, và đặc biệt là hệ thống expander hiển thị minh bạch các citation/nguồn tham chiếu cho từng câu trả lời.
- Xử lý việc tích hợp với hàm `generate_with_citation` để nhận về câu trả lời và list `SearchResult`.

## Quyết định kỹ thuật

1. **Quyết định:** Tích hợp CSS custom vào thẳng Streamlit thông qua `st.markdown(..., unsafe_allow_html=True)` thay vì dùng các thư viện component ngoài.
   **Lý do/evidence:** Muốn giao diện có tính thẩm mỹ cao (như shadow, hover effect, badge) giống mockup nhất có thể mà không bị phụ thuộc vào package bên thứ ba có thể gây lỗi môi trường.
   **Trade-off:** Code trong `app.py` hơi dài hơn vì chứa cả block CSS, nhưng đổi lại dễ dàng chỉnh sửa giao diện tức thời.

2. **Quyết định:** Hiển thị chi tiết `Score` và `Chunk Index` trong phần Nguồn tham khảo.
   **Lý do/evidence:** RAG chatbot cần sự minh bạch. Việc cho người dùng thấy điểm cosine score và vị trí chunk giúp tăng độ tin cậy của câu trả lời.
   **Trade-off:** Giao diện chi tiết hơn có thể làm phần expander hơi chật, nhưng được giải quyết bằng layout dạng `source-card` rõ ràng.

## Kiểm thử và kết quả

- Test hoặc query tôi đã dùng: "Có những phương thức xét tuyển đại học nào năm nay?"
- Kết quả trước/sau nếu có: Xử lý thành công việc LLM nhận context từ các documents và cite lại đúng cú pháp `[Document i]`, sau đó UI parse và render kèm link.
- Lỗi đã phát hiện và cách xử lý: Quá trình setup môi trường bị lỗi chứng chỉ TLS (SSL) khi cài thư viện `streamlit` bằng uv. Xử lý bằng cách force install và tạo lại virtual environment.

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: UI Streamlit khi reload lại sẽ mất trạng thái nếu không quản lý session state cẩn thận, hiện tại mới quản lý mảng `messages` cơ bản.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: Bổ sung tính năng feedback (thumbs up/down) cho từng câu trả lời để đánh giá chất lượng retrieval.

## Xác nhận đóng góp

Tôi xác nhận toàn bộ nội dung trên do tôi tự thực hiện hoặc đóng góp chính.
