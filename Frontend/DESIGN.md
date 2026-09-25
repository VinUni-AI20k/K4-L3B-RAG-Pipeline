# Thiết kế Track D: Sinh câu trả lời và giao diện

**Ngày:** 2026-09-25

## Mục tiêu

Hoàn thiện phần Track D cho chatbot RAG về thuế và nghĩa vụ kê khai của hộ kinh doanh: sinh câu trả lời có căn cứ, giao diện Streamlit ổn định và phong cách trực quan lấy cảm hứng từ Ant Design cùng ảnh tham chiếu portal dịch vụ công.

## Phạm vi

Thiết kế này bao gồm D0 đến D3:

- `src/task10_generation.py`: sắp xếp context, định dạng context, gọi nhà cung cấp và sinh câu trả lời có citation.
- `tests/test_edge_cases.py`: kiểm thử generation với retrieval và nhà cung cấp được mô phỏng.
- `app.py`: giao diện Streamlit và phần hiển thị nguồn.

Golden dataset, đánh giá Ragas và báo cáo đánh giá thuộc các bước D4–D5. Track C vẫn sở hữu retrieval.

## Hợp đồng tích hợp

`generate_with_citation(query, top_k)` gọi hàm public `retrieve` của Track C nhưng không đọc chi tiết dense, BM25, RRF hoặc PageIndex.

Mỗi kết quả truy xuất phải theo `SearchResult`: có ID, nội dung, điểm số, metadata nguồn và phương thức `hybrid` hoặc `pageindex`. Generator trả `GenerationResult` gồm câu trả lời, các chunk gốc trong `sources` và nguồn truy xuất.

Nếu retrieval không có chunk, retrieval bị lỗi, nhà cung cấp bị lỗi hoặc trả text rỗng, generation phải trả đúng:

```text
Tôi không thể xác minh thông tin này từ nguồn hiện có.
```

với `sources=[]` và `retrieval_source="none"`.

## Thiết kế generation

`reorder_for_llm` trả về list mới, giữ nguyên toàn bộ ID và đưa các chunk xen kẽ về đầu, phần còn lại theo thứ tự đảo ngược để giảm nguy cơ bỏ sót thông tin ở giữa context.

`format_context` gắn nhãn ổn định, có thể nhìn thấy cho từng chunk:

```text
[Document N | Title: ... | Source: ...]
```

Các khóa tiếng Anh trong nhãn được giữ nguyên vì thuộc contract của pipeline. Prompt yêu cầu nhà cung cấp chỉ dùng context này và trích dẫn bằng nhãn tài liệu. Provider được chọn qua `.env`: OpenAI, Gemini hoặc Anthropic; timeout 30 giây, nhiệt độ 0.3.

## Thiết kế giao diện

Ứng dụng vẫn là Streamlit; Ant Design chỉ là ngôn ngữ thị giác, không thêm frontend React. CSS cung cấp các token:

- thanh ứng dụng màu than (`#202124`) với dấu hiệu sản phẩm và tên chatbot;
- màu cam đất (`#D55A43`) cho CTA, trạng thái đang chọn và điểm nhấn trợ lý;
- nền cam đào nhạt (`#FFF0E8`) cho hero và nền ngà (`#FCFBF8`) cho trang;
- card trắng bo góc 12px, viền nhẹ và đổ bóng mềm;
- xanh teal (`#146B62`) cho điểm nhấn nguồn đáng tin cậy.

Trang gồm hero giới thiệu, ba câu hỏi gợi ý có thể bấm, lịch sử hội thoại Streamlit và danh sách nguồn có thể mở rộng. Mỗi nguồn hiển thị `title | source | retrieval_method | score` cùng trích đoạn nguồn. Toàn bộ lịch sử được lưu trong `st.session_state.messages`.

Ảnh mock chỉ là tài liệu tham chiếu thiết kế, không cần nhúng vào runtime để ứng dụng nhẹ và có thể chạy lại.

## Xử lý lỗi và khả năng tiếp cận

Ứng dụng hiển thị safe refusal do generation trả về mà không lộ stack trace của provider. Câu hỏi và câu từ chối được lưu trong lịch sử. Source expander dùng nhãn văn bản rõ ràng; phương thức retrieval và điểm số không chỉ được phân biệt bằng màu.

## Kiểm chứng

- Unit test và contract test kiểm tra thứ tự chunk, nhãn context, safe refusal và public signature.
- Sau khi Track C sẵn sàng, chạy Streamlit với một câu hỏi đúng phạm vi và một câu hỏi ngoài phạm vi.
- Kiểm tra browser trên desktop, metadata nguồn, responsive layout, lỗi console và cây accessibility.
