# Evaluation Result — NEU RAG Chatbot

## Cấu hình cố định

- Corpus: `data/standardized/legal` và `data/standardized/news`; index cục bộ ChromaDB.
- Golden set: `group_project/evaluation/golden_dataset.json` (20 câu).
- `top_k=5`, `SCORE_THRESHOLD=0.35`, cùng câu hỏi và prompt cho hai nhánh.
- A: Dense-only (`use_reranking=False`). B: Dense + BM25 + RRF (`use_reranking=True`).

## Cách tạo bằng chứng chạy

```powershell
python -m src.task11_evaluation --mode both
```

Lệnh trên tạo `runs/dense_run.json` và `runs/hybrid_run.json`. Mỗi record có câu hỏi, đáp án tham chiếu, chunks truy xuất, metadata, score và bốn metric. Không ghi số liệu giả khi index hoặc provider chưa sẵn sàng.

## Bốn metric

Runner hiện dùng token-overlap proxy xác định để kiểm tra hồi quy retrieval offline: faithfulness, answer relevance, context recall và context precision. Đây không phải điểm RAGAS; nếu cần điểm RAGAS, dùng các record đã lưu làm đầu vào evaluator với cùng model đánh giá và ghi thêm phiên bản model vào cấu hình.

## Bảng A/B

| Nhánh | Retrieval | Metric output |
|---|---|---|
| A | Dense-only | `runs/dense_run.json` |
| B | Dense + BM25 + RRF | `runs/hybrid_run.json` |

Các con số chỉ được công bố sau khi chạy lệnh trên thành công. Điều này giúp tránh nhầm kết quả mô phỏng với kết quả thực tế.

## Lỗi tiêu biểu và giới hạn

- Câu hỏi ngoài phạm vi hoặc khác năm tuyển sinh có thể kích hoạt PageIndex fallback; nếu fallback không khả dụng, hệ thống trả kết quả hybrid và generation phải từ chối khi thiếu bằng chứng.
- Chunk overlap đo được là proxy cho quality retrieval, không thay thế đánh giá ngữ nghĩa của RAGAS.
- Hai nhánh phải chạy trên cùng corpus, câu hỏi, `top_k`, threshold và prompt; không dùng toàn bộ evaluation set để chỉnh threshold.
