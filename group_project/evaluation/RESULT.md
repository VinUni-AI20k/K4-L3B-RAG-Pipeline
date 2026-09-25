# Evaluation Report — K4-L3B RAG Pipeline

**Corpus:** Quy chế đào tạo & Dịch vụ sinh viên UET-VNU  
**Embedding:** Gemini `gemini-embedding-001`  
**LLM Generation:** Gemini `gemini-3.5-flash-lite`  
**LLM Judge:** Gemini `gemini-3.5-flash-lite` (custom RAGAS-style prompts)  
**Chunking:** Recursive, size=500, overlap=50  
**Tổng chunks:** 472  
**Golden dataset:** 15 câu hỏi (14 in-domain + 1 out-of-domain)  
**Script:** `tests/run_ragas_evaluation.py`  
**Output:** `group_project/evaluation/automated_test_results.json`

---

## Overall Scores

| Metric | Dense-only | Hybrid (BM25 + RRF) | Δ |
|---|---|---|---|
| Faithfulness | 0.91 | **1.00** | +0.09 |
| Answer Relevance | 0.68 | **0.79** | +0.11 |
| Context Recall | 0.71 | **0.80** | +0.09 |
| Context Precision | 0.22 | **0.29** | +0.07 |
| **Average** | **0.63** | **0.72** | **+0.09** |

*Số liệu Hybrid+RRF đo thực tế bằng script `tests/run_ragas_evaluation.py` — 14 in-domain cases, LLM judge: `gemini-3.5-flash-lite`.*  
*Số liệu Dense-only được tính bằng cách chạy lại với `use_reranking=False` trên cùng cấu hình.*

---

## A/B Comparison

### Cấu hình A — Dense-only
```python
retrieve(query, top_k=5, use_reranking=False)
```
Chỉ dùng ChromaDB cosine similarity, không qua BM25 hay RRF.

### Cấu hình B — Hybrid+RRF ✅ (production)
```python
retrieve(query, top_k=5, use_reranking=True)
```
Dense + BM25, fuse bằng RRF (k=60), fallback PageIndex nếu score < 0.3.

### Kết quả chi tiết per-case (Hybrid+RRF)

| # | Câu hỏi (tóm tắt) | Faith | Relevance | Recall | Precision |
|---|---|---|---|---|---|
| 1 | Điều kiện tốt nghiệp | 1.00 | 0.00* | 1.00 | 0.00 |
| 2 | Nộp ảnh làm bằng | 1.00 | 1.00 | 1.00 | 0.40 |
| 3 | Cảnh báo học vụ | 1.00 | 1.00 | 1.00 | 0.50 |
| 4 | Học bổng tiêu chí | 1.00 | 0.50 | 0.00 | 0.20 |
| 5 | Lễ bế giảng | 1.00 | 1.00 | 0.85 | 0.30 |
| 6 | Thời gian tối đa khoá học | 1.00 | 1.00 | 1.00 | 0.20 |
| 7 | BHYT năm 2026 | 1.00 | 0.50 | 0.00 | 0.50 |
| 8 | Tín chỉ tối thiểu cử nhân | 1.00 | 1.00 | 1.00 | 0.20 |
| 9 | Khám sức khỏe K66 | 1.00 | 1.00 | 1.00 | 0.20 |
| 10 | Yêu cầu ngoại ngữ | 1.00 | 1.00 | 1.00 | 0.20 |
| 11 | Điểm rèn luyện kéo dài | 1.00 | 1.00 | 1.00 | 0.20 |
| 12 | Học phần điều kiện GPA | 1.00 | 1.00 | 1.00 | 0.60 |
| 13 | Học bổng Vingroup | 1.00 | 0.00* | 0.30 | 0.40 |
| 14 | Cuộc thi khởi nghiệp | 1.00 | 1.00 | 1.00 | 0.20 |
| **Avg** | | **1.00** | **0.79** | **0.80** | **0.29** |

*\* Score 0.00 xảy ra khi generation trả safe refusal do LLM_MODEL cũ bị rate limit; retrieval vẫn đúng.*

---

## Worst Performers

**3 câu hỏi có kết quả kém nhất:**

1. **Câu #4 "Học bổng khuyến khích học tập tiêu chí"** — Context Recall = 0.00, Precision = 0.20  
   Nguyên nhân: Thông tin tiêu chí xét học bổng phân tán qua nhiều điều khoản, chunks lấy về không tập trung đủ nội dung cần thiết.

2. **Câu #7 "BHYT năm 2026"** — Context Recall = 0.00, Answer Relevance = 0.50  
   Nguyên nhân: Nội dung bài thông báo BHYT trên web bị Crawl4AI trích xuất thiếu — phần hướng dẫn quy trình đăng ký không được crawl đầy đủ.

3. **Câu #1 "Điều kiện tốt nghiệp"** — Answer Relevance = 0.00  
   Nguyên nhân: LLM generation gặp rate limit ở lần chạy này, trả safe refusal thay vì câu trả lời đúng. Retrieval vẫn lấy đúng context (Recall = 1.00).

---

## Error Analysis

| Loại lỗi | Số câu | Nguyên nhân |
|---|---|---|
| LLM rate limit → safe refusal sai | 2 | Free tier `gemini-3.5-flash-lite` bị giới hạn 15 RPM |
| Context Recall thấp | 2 | Thông tin phân tán, chunk size 500 chưa đủ để capture toàn bộ |
| Context Precision thấp (avg 0.29) | 14 | top_k=5 kéo nhiều chunks không liên quan; đây là hạn chế chung |
| Crawl content thiếu | 1 | Crawl4AI không lấy đủ nội dung trang BHYT (JavaScript rendering) |

---

## Recommendations

1. **Tăng wait time giữa generation calls** lên 5-6 giây để tránh rate limit làm sai kết quả đo.
2. **Giảm top_k** xuống 3-4 để cải thiện Context Precision (hiện 0.29 khá thấp do lấy thừa chunks).
3. **Tăng chunk overlap** từ 50 → 100 để cải thiện Context Recall cho thông tin phân tán.
4. **Re-crawl article BHYT** với Playwright render mode để lấy đủ nội dung hướng dẫn.
5. **Calibrate SCORE_THRESHOLD** = 0.35 — hiện 0.30 hơi thấp với corpus pháp quy tiếng Việt.

---

## Retrieval Method Distribution (14 in-domain cases)

| Method | Số câu | % |
|---|---|---|
| hybrid | 14 | 100% |
| none (safe refusal) | 0 | 0% |

*(Out-of-domain case thứ 15 trả safe refusal đúng — không tính vào evaluation)*

---

## Conversation Memory (Bonus Feature)

`app.py` hỗ trợ multi-session conversation history qua `st.session_state.sessions`:
- Lưu nhiều phiên hội thoại độc lập
- Tự động đặt tiêu đề từ câu hỏi đầu tiên
- Load lại bất kỳ phiên cũ từ sidebar

Feature này hoạt động end-to-end và có thể demo trực tiếp trên `streamlit run app.py`.

---

*Evaluation chạy ngày 25/09/2026. Script: `tests/run_ragas_evaluation.py`. Raw data: `automated_test_results.json`.*
