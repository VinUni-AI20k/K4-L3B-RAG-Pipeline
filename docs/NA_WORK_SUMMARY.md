# Tổng kết công việc Người 4 — Na

## Phạm vi

Phụ trách giao diện Streamlit, runner đánh giá, lưu bằng chứng retrieval, so sánh Dense-only với Dense + BM25 + RRF, và báo cáo bàn giao.

## Đã thực hiện

- `app.py` hiển thị hội thoại, trạng thái xử lý, câu trả lời, nguồn, URL, retrieval method, score và đoạn chunk được trích dẫn.
- Sidebar nêu rõ chatbot phục vụ tư vấn tuyển sinh NEU 2026 và cho chỉnh `top_k`.
- `src/task11_evaluation.py` đọc `group_project/evaluation/golden_dataset.json`, chạy hai nhánh A/B với cùng câu hỏi, corpus và `top_k=5`, sau đó lưu toàn bộ chunks truy xuất cùng cấu hình.
- Bốn metric được lưu cho từng câu: faithfulness, answer relevance, context recall và context precision.
- Kết quả chạy được lưu trong `group_project/evaluation/runs/` dưới dạng JSON để báo cáo có thể kiểm chứng.

## Cách chạy

```powershell
python -m src.task11_evaluation --mode both
streamlit run app.py
```

Runner mặc định dùng metric overlap xác định, không cần API key. Đây là proxy kiểm thử retrieval; nếu cần điểm RAGAS chính thức, dùng cùng các record đã lưu và cấu hình evaluator/LLM cố định.

## Kịch bản demo

1. Câu có đáp án trực tiếp: hỏi cổng đăng ký hồ sơ NEU 2026.
2. Câu cần tổng hợp: hỏi điều kiện và thời hạn của nhiều nhóm xét tuyển.
3. Câu thiếu bằng chứng: hỏi điểm chuẩn NEU năm 2030; chatbot phải nói không đủ căn cứ.

## Hạn chế còn lại

Hai điều kiện cần có khi chạy đánh giá đầy đủ là index ChromaDB đã được tạo và provider LLM đã cấu hình trong `.env`. Nếu thiếu một trong hai, runner vẫn có thể báo lỗi môi trường; không được xem đó là điểm metric hợp lệ.
