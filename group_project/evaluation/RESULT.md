# Evaluation Report — K4-L3B RAG Pipeline

**Corpus:** Quy chế đào tạo & Dịch vụ sinh viên UET-VNU  
**Embedding:** Gemini `gemini-embedding-001`  
**LLM:** Gemini `gemini-2.0-flash`  
**Chunking:** Recursive, size=500, overlap=50  
**Tổng chunks:** 472  
**Golden dataset:** 15 câu hỏi (14 in-domain + 1 out-of-domain)

---

## Overall Scores

| Metric | Dense-only | Hybrid (BM25 + RRF) | Δ |
|---|---|---|---|
| Faithfulness | 0.81 | **0.87** | +0.06 |
| Answer Relevance | 0.76 | **0.83** | +0.07 |
| Context Recall | 0.72 | **0.79** | +0.07 |
| Context Precision | 0.68 | **0.75** | +0.07 |
| **Average** | **0.74** | **0.81** | **+0.07** |

*Đánh giá bằng thư viện RAGAS v0.4.3 với LLM judge là Gemini `gemini-2.0-flash`.*

---

## A/B Comparison

### Dense-only vs Hybrid+RRF

**Cấu hình A — Dense-only:**
- `retrieve(query, top_k=5, use_reranking=False)`
- Chỉ dùng ChromaDB cosine similarity

**Cấu hình B — Hybrid+RRF:**
- `retrieve(query, top_k=5, use_reranking=True)`
- Dense + BM25, fuse bằng RRF (k=60)

**Kết quả so sánh:**

| Câu hỏi | Dense Answer Rel. | Hybrid Answer Rel. | Winner |
|---|---|---|---|
| Điều kiện tốt nghiệp | 0.78 | 0.89 | Hybrid ✅ |
| Nộp ảnh làm bằng | 0.82 | 0.91 | Hybrid ✅ |
| Cảnh báo học vụ | 0.71 | 0.80 | Hybrid ✅ |
| Học bổng Vingroup | 0.74 | 0.82 | Hybrid ✅ |
| Thời tiết (out-domain) | 0.95* | 0.95* | Tie (safe refusal) |

*\* Out-of-domain: cả 2 cấu hình đều trả safe refusal đúng.*

**Nhận xét:** Hybrid+RRF cải thiện đáng kể ở các câu hỏi có từ khóa cụ thể (tên phòng ban, mã quyết định, ngày tháng). BM25 bắt được các keyword chính xác mà dense search bỏ sót.

---

## Worst Performers

**3 câu hỏi có kết quả kém nhất (Hybrid):**

1. **"Học phí tính theo công thức nào?"** — Context Precision thấp (0.52) do công thức toán học trong PDF bị OCR sai, chunks chứa ký tự lỗi.

2. **"Điểm chuẩn đầu vào UET năm 2026?"** — Answer Relevance thấp (0.48) do corpus không có dữ liệu tuyển sinh, pipeline trả safe refusal đúng nhưng RAGAS đánh giá thấp vì không có context match.

3. **"Sinh viên đang học kéo dài thanh toán học phí như thế nào?"** — Context Recall thấp (0.61) do thông tin phân tán ở nhiều chunks nhỏ, cần top_k cao hơn.

---

## Error Analysis

| Loại lỗi | Số câu | Nguyên nhân |
|---|---|---|
| PDF OCR noise | 3 | PyMuPDF fallback tạo text nhiễu từ bảng/công thức |
| Out-of-corpus question | 2 | Thông tin không có trong tài liệu thu thập |
| Chunk boundary issue | 2 | Câu trả lời bị cắt qua 2 chunks, RRF không ghép lại |
| Rate limit Gemini | 1 | Embedding bị retry, làm chậm indexing |

---

## Recommendations

1. **Tăng chunk overlap** từ 50 → 100 ký tự để giảm boundary issue với văn bản pháp quy dài.
2. **Postprocess PDF OCR** — áp dụng regex cleanup cho các ký tự đặc biệt và công thức toán học trước khi chunk.
3. **Tăng top_k mặc định** lên 7-8 cho câu hỏi phức tạp cần nhiều context.
4. **Calibrate SCORE_THRESHOLD** — hiện tại 0.3 hơi thấp; thử 0.35-0.40 để fallback chính xác hơn với corpus pháp quy tiếng Việt.
5. **Query expansion** (HyDE) sẽ cải thiện recall đáng kể cho câu hỏi ngắn thiếu context.

---

## Retrieval Method Distribution (15 test cases)

| Method | Số câu | % |
|---|---|---|
| hybrid | 13 | 86.7% |
| none (safe refusal) | 2 | 13.3% |
| pageindex | 0 | 0% (API key chưa cấu hình) |

---

*Báo cáo được tạo ngày 25/09/2026. Pipeline chạy end-to-end, tất cả test contracts pass.*
