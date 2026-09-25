# Bàn giao Người 3 — Retrieval Pipeline, PageIndex Fallback & Generation có Citation (Task 8–10)

**Người thực hiện:** Lê Thị Duyên (Người 3 — Kỹ thuật tích hợp & Generation)  
**Người nhận bàn giao:** Người 4 (Na — Evaluation & UI), Cả nhóm  
**Tài liệu liên quan:** `docs/DATA_HANDOFF.md` (Người 1), `docs/RETRIEVAL_HANDOFF.md` (Người 2), `docs/MODULE_CONTRACTS.md`

---

## 1. Kết quả thực hiện

### Task 8 — PageIndex Vectorless Fallback (`src/task8_pageindex_vectorless.py`)
- **Upload & Cache Document IDs (`upload_documents`):**
  - Đọc tài liệu chuẩn hóa từ `data/standardized/*/*.json`.
  - Quản lý cache mapping ID tài liệu trong `data/pageindex_cache.json` để không upload trùng lặp khi chạy lại.
- **Vectorless Search (`pageindex_search(query, top_k=5)`):**
  - Tích hợp chuẩn qua SDK/REST API với header xác thực `PAGEINDEX_API_KEY`.
  - Đặt timeout 10s và bọc xử lý ngoại lệ an toàn (`try...except`), không để lỗi provider làm sập ứng dụng.
  - Chuẩn hóa đầu ra thành danh sách `SearchResult` có `retrieval_method="pageindex"`, sắp xếp giảm dần theo điểm và không trùng lặp ID.

### Task 9 — Unified Retrieval Pipeline (`src/task9_retrieval_pipeline.py`)
- **Hàm `retrieve(query, top_k=5, score_threshold=0.35, use_reranking=True)`:**
  - Kết nối đồng thời Dense Search (`semantic_search`) và BM25 Lexical Search (`lexical_search`) từ Người 2 với `top_k * 2` ứng viên.
  - **Cơ chế quyết định Fallback:** Sử dụng duy nhất điểm Cosine Similarity gốc của Dense Search:
    $$\text{best\_dense\_score} = \text{dense}[0][\text{"score"}]$$
    Nếu $\text{best\_dense\_score} < \text{score\_threshold}$, kích hoạt fallback sang `pageindex_search`.
    > [!IMPORTANT]
    > **Tuyệt đối không sử dụng điểm RRF hay BM25 làm ngưỡng fallback** vì khác biệt về thang đo xác suất.
  - **Khả năng chịu lỗi (Error Resilience):** Khi PageIndex lỗi mạng, timeout hoặc chưa cấu hình key, pipeline tự động giữ lại kết quả Hybrid từ Dense + BM25 thay vì crash.
  - **Hợp nhất xếp hạng:** Chỉ gọi `rerank_rrf` đúng một lần duy nhất khi Dense tự tin hoặc khi fallback trả về rỗng.

#### Căn cứ hiệu chỉnh `SCORE_THRESHOLD = 0.35`:
Dựa trên bộ dữ liệu hiệu chuẩn `group_project/evaluation/fallback_dataset.json` (6 kịch bản):
1. **Truy vấn ngoài phạm vi (CAL-01: *"Làm thế nào sửa xe máy không nổ?"*):**
   - Điểm Dense Cosine Similarity cao nhất chỉ đạt $\approx 0.18 - 0.25 < 0.35 \implies$ Kích hoạt fallback hoặc từ chối an toàn.
2. **Truy vấn thiếu bằng chứng (CAL-02: *"Điểm chuẩn NEU năm 2030 là bao nhiêu?"*):**
   - Điểm Dense Cosine Similarity $\approx 0.28 - 0.32 < 0.35 \implies$ Kích hoạt fallback, LLM nhận diện không có dữ liệu năm 2030 và từ chối suy đoán.
3. **Truy vấn trong phạm vi (CAL-06: *"Thông tin liên hệ tư vấn tuyển sinh NEU năm 2026?"*):**
   - Điểm Dense Cosine Similarity đạt $\ge 0.58 > 0.35 \implies$ Dense tự tin, RRF kết hợp BM25 đưa đoạn văn bản chứa hotline `0888.128.558` lên đầu bảng xếp hạng.
$\implies$ Chọn ngưỡng `SCORE_THRESHOLD = 0.35` làm mặc định phân tách rõ ràng giữa câu hỏi in-domain và out-of-domain.

### Task 10 — Context Preparation & Generation có Citation (`src/task10_generation.py`)
- **Khắc phục Lost-in-the-Middle (`reorder_for_llm`):**
  - Sắp xếp các đoạn trích quan trọng nhất về đầu và cuối ngữ cảnh (`front = chunks[::2]`, `back = chunks[1::2]`, ghép `front + back[::-1]`).
  - Bảo toàn 100% ID và nội dung các chunk, không làm thay đổi (mutate) danh sách gốc.
- **Chuẩn hóa Ngữ cảnh (`format_context`):**
  - Gắn nhãn chuẩn hóa: `[Tài liệu X | ID: ... | Tiêu đề: ... | Nguồn: ... | Năm áp dụng: ...]`.
  - Giúp LLM dễ dàng trích dẫn chính xác theo mã tài liệu `[Tài liệu X]`.
- **Đa LLM Provider (`call_llm`):**
  - Hỗ trợ linh hoạt cả 3 provider lớn: `openai` (`gpt-4o-mini`), `gemini` (`gemini-2.5-flash`), `anthropic` (`claude-3-5-sonnet-20241022`).
  - Cấu hình chuẩn `TEMPERATURE = 0.3`, `TOP_P = 0.9` để đảm bảo câu trả lời bám sát dữ liệu, tránh hallucination.
- **Hàm `generate_with_citation(query, top_k=5)`:**
  - Trả về đúng schema `GenerationResult`:
    ```python
    {
        "answer": str,
        "sources": list[SearchResult],
        "retrieval_source": "hybrid" | "pageindex" | "none"
    }
    ```
  - **Safe Refusal:** Nếu câu hỏi ngoài phạm vi, không đủ bằng chứng hoặc không tìm thấy tài liệu, hệ thống từ chối lịch sự: *"Tôi không thể xác minh thông tin này từ nguồn hiện có."*

### Tích hợp Giao diện (`app.py`)
- Đã kết nối hàm `generate_with_citation` vào giao diện Streamlit.
- Hiển thị expander trích dẫn nguồn, cơ chế tìm kiếm, điểm similarity/RRF và đường link văn bản gốc.
- Có nút xóa lịch sử trò chuyện và thanh trượt điều chỉnh `top_k`.

---

## 2. Dữ liệu giả lập mẫu cho Người 4 (Mock GenerationResult)

Người 4 (Na) có thể sử dụng mẫu dữ liệu sau để phát triển UI hoặc viết unit test kiểm thử:

```json
{
  "answer": "Theo Đề án tuyển sinh Đại học chính quy năm 2026 của Trường Đại học Kinh tế Quốc dân, số điện thoại hotline tư vấn tuyển sinh là 0888.128.558 (trong giờ hành chính) [Tài liệu 1]. Tổng chỉ tiêu tuyển sinh đại học chính quy năm 2026 là 8.780 chỉ tiêu [Tài liệu 2].",
  "sources": [
    {
      "id": "neu2026_undergraduate-chunk-0",
      "content": "TRƯỜNG ĐẠI HỌC KINH TẾ QUỐC DÂN\nHotline tư vấn tuyển sinh đại học chính quy năm 2026: 0888.128.558 (trong giờ hành chính).\nĐịa chỉ: 207 Giải Phóng, Đồng Tâm, Hai Bà Trưng, Hà Nội.",
      "score": 0.0328,
      "metadata": {
        "source": "data/landing/legal/neu_de_an_tuyen_sinh_2026.pdf",
        "title": "Đề án tuyển sinh Đại học chính quy năm 2026",
        "doc_type": "legal",
        "url": "https://neu.edu.vn/tuyen-sinh-2026",
        "chunk_index": 0,
        "admission_year": 2026,
        "audience": "dai_hoc_chinh_quy"
      },
      "retrieval_method": "hybrid"
    },
    {
      "id": "neu2026_undergraduate-chunk-4",
      "content": "BẢNG CHỈ TIÊU TUYỂN SINH NĂM 2026\nTổng chỉ tiêu tuyển sinh đại học chính quy năm 2026 toàn trường là 8.780 sinh viên.",
      "score": 0.0315,
      "metadata": {
        "source": "data/landing/legal/neu_de_an_tuyen_sinh_2026.pdf",
        "title": "Đề án tuyển sinh Đại học chính quy năm 2026",
        "doc_type": "legal",
        "url": "https://neu.edu.vn/tuyen-sinh-2026",
        "chunk_index": 4,
        "admission_year": 2026,
        "audience": "dai_hoc_chinh_quy"
      },
      "retrieval_method": "hybrid"
    }
  ],
  "retrieval_source": "hybrid"
}
```

---

## 3. Hướng dẫn Người 4 thực hiện A/B Testing

Để đo 4 metric RAGAS và so sánh A/B trong `group_project/evaluation/RESULT.md`:

1. **Cấu hình A (Dense-only):**
   ```python
   # Truy xuất chỉ dùng Dense (bỏ qua RRF reranking)
   chunks_a = retrieve(query, top_k=5, use_reranking=False)
   ```
2. **Cấu hình B (Hybrid: Dense + BM25 + RRF):**
   ```python
   # Truy xuất Hybrid kết hợp Dense và Lexical qua RRF
   chunks_b = retrieve(query, top_k=5, use_reranking=True)
   ```
3. Cả hai cấu hình đều sử dụng chung:
   - Bộ corpus: 8 tài liệu (190 chunks) trong ChromaDB.
   - Bộ câu hỏi: `group_project/evaluation/golden_dataset.json` (20 câu).
   - Mô hình LLM, prompt hệ thống và tham số `temperature=0.3`.

---

## 4. Hướng dẫn chạy kiểm tra trên Windows

Mở PowerShell tại thư mục gốc `K4-L3B-RAG-Pipeline`:

```powershell
# 1. Chạy thử Task 8 (PageIndex fallback)
.\.venv\Scripts\python.exe -X utf8 -m src.task8_pageindex_vectorless

# 2. Chạy thử Task 9 (Retrieval Pipeline)
.\.venv\Scripts\python.exe -X utf8 -m src.task9_retrieval_pipeline

# 3. Chạy thử Task 10 (Generation có citation)
.\.venv\Scripts\python.exe -X utf8 -m src.task10_generation

# 4. Khởi chạy giao diện Streamlit Chatbot
.\.venv\Scripts\python.exe -m streamlit run app.py
```
