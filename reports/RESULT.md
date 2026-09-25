# Báo cáo đánh giá RAG — NEU 2026

## 1. Phạm vi và cấu hình

| Thành phần | Cấu hình |
|---|---|
| Corpus | `data/standardized/legal/` và `data/standardized/news/` |
| Golden set | `group_project/evaluation/golden_dataset.json`, 20 câu |
| Embedding | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| Retrieval A | Dense-only |
| Retrieval B | Dense + BM25 + RRF |
| `top_k` | 5 |
| Fallback threshold | 0.35 cosine similarity |
| Generator | Theo `LLM_PROVIDER` trong `.env` |

Hai nhánh A/B giữ nguyên corpus, câu hỏi, `top_k`, threshold và chính sách fallback; chỉ thay đổi việc có dùng BM25/RRF hay không.

## 2. Cách chạy tái lập

```powershell
python -m src.task4_chunking_indexing
python -m src.task11_evaluation --mode both
```

Kết quả chi tiết được ghi tại:

- `group_project/evaluation/runs/dense_run.json`
- `group_project/evaluation/runs/hybrid_run.json`

Mỗi record gồm câu hỏi, đáp án tham chiếu, chunks thực tế, metadata, score và metric.

## 3. Metric

Runner hiện dùng token-overlap proxy xác định để kiểm tra retrieval offline. Bốn trường được tính là faithfulness, answer relevance, context recall và context precision. Đây là kiểm tra hồi quy có thể chạy không cần API key; không trình bày chúng như điểm RAGAS.

| Metric | A — Dense | B — Hybrid | Delta |
|---|---:|---:|---:|
| Faithfulness | Xem `dense_run.json` | Xem `hybrid_run.json` | Tính từ hai file |
| Answer relevance | Xem `dense_run.json` | Xem `hybrid_run.json` | Tính từ hai file |
| Context recall | Xem `dense_run.json` | Xem `hybrid_run.json` | Tính từ hai file |
| Context precision | Xem `dense_run.json` | Xem `hybrid_run.json` | Tính từ hai file |

Không điền số liệu giả khi index chưa được tạo hoặc môi trường thiếu provider.

## 4. Phân tích A/B dự kiến kiểm tra

- Hybrid thường có lợi với mã ngành, URL, tên riêng và cụm từ chính xác nhờ BM25.
- Dense-only có thể tốt hơn với câu hỏi diễn đạt tự nhiên hoặc đồng nghĩa.
- RRF làm tăng độ phủ nhưng có thể đưa thêm chunk từ khóa vào top-k, làm giảm precision ở một số câu.
- PageIndex fallback chỉ được xem là phương án dự phòng, không dùng để thay đổi corpus A/B.

## 5. Lỗi và giới hạn

1. Không thể đánh giá chính thức nếu ChromaDB chưa được index.
2. Điểm token-overlap không thay thế đánh giá ngữ nghĩa bằng RAGAS.
3. Chất lượng generation phụ thuộc `LLM_PROVIDER`, model và API key trong `.env`.
4. Các câu hỏi khác năm tuyển sinh cần được kiểm tra phạm vi trước khi kết luận.

## 6. Demo

- Có đáp án trực tiếp: “Cổng đăng ký hồ sơ xét tuyển NEU 2026 ở đâu?”
- Cần tổng hợp: “Nhóm 5 có nộp lệ phí trên cổng NEU không và các mốc thời gian là gì?”
- Thiếu bằng chứng: “Điểm chuẩn NEU năm 2030 là bao nhiêu?” — hệ thống phải từ chối an toàn.
