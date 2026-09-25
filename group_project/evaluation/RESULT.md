# Kết quả chuẩn bị đánh giá RAG

Ngày kiểm tra: 2026-09-25. Chủ đề: chính sách trả hàng và hoàn tiền Shopee. Tài liệu nguồn trong corpus được ghi nhận thu thập ngày 2026-09-20; chính sách có thể thay đổi theo thời gian.

## Overall scores

Bộ dữ liệu chuẩn được lập từ 3 tài liệu legal và 7 bài hướng dẫn trong `data/standardized/`. `golden_dataset.json` có 15 câu hỏi và phủ cả 10 file nguồn. Kiểm tra đối chiếu chuỗi cho thấy **15/15** đoạn `expected_context` xuất hiện nguyên văn trong file `source` tương ứng. Đây là mức độ hoàn thành và kiểm tra căn cứ của bộ dữ liệu, **không phải** điểm chất lượng câu trả lời của chatbot.

Bốn chỉ số chất lượng cần đo trên câu trả lời thực tế chưa có kết quả:

- **Faithfulness:** chưa đo; chưa có câu trả lời sinh bởi pipeline để kiểm tra độ bám sát ngữ cảnh.
- **Answer relevance:** chưa đo; chưa có câu trả lời sinh bởi pipeline để so với câu hỏi.
- **Context recall:** chưa đo; các hàm lập chỉ mục và truy xuất ở Task 4–9 chưa chạy được từ đầu đến cuối.
- **Context precision:** chưa đo; chưa có danh sách chunk truy xuất thực tế để đánh giá thứ hạng.

Các hàm của Task 4–10 hiện còn `NotImplementedError`. Vì vậy không có điểm RAGAS hay điểm tổng hợp hợp lệ để báo cáo tại thời điểm này. Việc các kiểm tra acceptance về file dữ liệu đạt yêu cầu chỉ xác nhận cấu trúc đầu vào, không thay thế phép đo chất lượng RAG.

## A/B comparison

Thiết kế so sánh là **A: dense-only** và **B: dense + BM25 + RRF**, dùng cùng 15 câu hỏi, cùng corpus, cùng `top_k` và cùng mô hình sinh câu trả lời. Chưa thể chạy hai nhánh vì embedding, vector store, truy xuất và generation chưa được triển khai. Do đó chưa có chênh lệch điểm hoặc kết luận nhánh nào tốt hơn. Khi chạy được pipeline, cần lưu câu trả lời, chunk truy xuất, nguồn trích dẫn và bốn chỉ số ở trên cho từng câu của cả hai nhánh.

## Worst performers

Chưa xác định được câu có điểm thấp nhất vì chưa có lượt chạy mô hình. Các trường hợp nên theo dõi sát khi đánh giá gồm:

- **G02 và G03:** mốc 24 giờ cho thực phẩm tươi/đông lạnh dễ bị nhầm với 15 ngày cho đơn hàng khác.
- **G04–G06:** trả hàng do đổi ý phụ thuộc đồng thời vào hạng người mua, nhóm sản phẩm và tình trạng niêm phong.
- **G10 và G11:** thời gian Shopee xem xét 3–5 ngày làm việc khác với thời hạn 6 ngày để người mua gửi trả hàng sau khi được chấp nhận.
- **G15:** thời gian hoàn tiền về thẻ tín dụng/ghi nợ là 7–14 ngày làm việc, khác các phương thức hoàn tiền nhanh hơn.

Đây là các trường hợp có nguy cơ nhầm lẫn theo nội dung tài liệu, không phải kết quả lỗi đã quan sát từ hệ thống.

## Recommendations

1. Hoàn thiện Task 4–10 và chạy một lượt end-to-end, lưu kết quả truy xuất cùng câu trả lời và nguồn cho từng câu trong bộ dữ liệu chuẩn.
2. Chạy A/B với cùng cấu hình ngoài phương pháp truy xuất; đo faithfulness, answer relevance, context recall và context precision trên cả hai nhánh.
3. Phân tích các câu có điểm thấp thực tế, kiểm tra nhầm lẫn giữa thời hạn, ngoại lệ sản phẩm và điều kiện đổi ý, rồi ghi lại thay đổi cùng kết quả chạy lại.
