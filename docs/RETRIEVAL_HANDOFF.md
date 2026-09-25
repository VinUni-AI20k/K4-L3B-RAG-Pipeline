# Bàn giao Người 2 — Chunking, Indexing & Hybrid Retrieval (Task 4–7)

**Người thực hiện:** Nguyễn Đức Đông (Người 2)  
**Nhánh Git:** `nguyenducdong`  
**PR:** https://github.com/vietbui000/K4-L3B-RAG-Pipeline/compare/main...nguyenducdong?expand=1  
**Người nhận bàn giao:** Người 3 (Duyên — Task 8–10: Fallback & Generation), Người 4 (Na — Evaluation & UI)

---

## 1. Kết quả thực hiện

- **Task 4 (Chunking & Vector Indexing):**
  - Đọc toàn bộ 8 văn bản chuẩn hóa (`data/standardized/legal/`, `data/standardized/news/`).
  - Áp dụng recursive chunking (`CHUNK_SIZE = 500`, `CHUNK_OVERLAP = 50`), tạo ra **190 chunks**.
  - ID của chunk ổn định và có quan hệ trực tiếp với tài liệu gốc: `{doc_id}-chunk-{chunk_index}`.
  - Sử dụng model embedding đa ngữ `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (dimension: 384) qua SentenceTransformer.
  - Lập chỉ mục thành công vào ChromaDB collection `rag_documents` (lưu tại `chroma_db/`).
  - Hỗ trợ **upsert idempotent**: chạy lại nhiều lần không sinh trùng lặp dữ liệu (số chunk luôn duy trì 190).
  - Đã làm sạch metadata (loại bỏ `None`, map kiểu dữ liệu tương thích ChromaDB) và tự động phục hồi `url: None` khi retrieve để tuân thủ `docs/MODULE_CONTRACTS.md`.

- **Task 5 (Dense Semantic Search):**
  - Tái sử dụng chính xác hàm `embed_texts()` của Task 4 để encode query (tránh lệch dimension và không gian vector).
  - Chuyển đổi khoảng cách Cosine Distance từ ChromaDB sang Cosine Similarity: `similarity = max(0.0, 1.0 - distance)`.
  - Kết quả trả về danh sách `SearchResult` có `retrieval_method="dense"`, sắp xếp giảm dần theo `score`, deduplicate ID.

- **Task 6 (Lexical Search - BM25):**
  - Khởi tạo chỉ mục `BM25Okapi` từ thư viện `rank_bm25` trên toàn bộ 190 chunks của corpus.
  - Caching index để tối ưu tốc độ truy vấn liên tục.
  - Hỗ trợ tìm kiếm từ khóa chính xác, mã văn bản, tên riêng, trả về `retrieval_method="bm25"`.

- **Task 7 (Reranking - Reciprocal Rank Fusion):**
  - Hợp nhất các danh sách xếp hạng từ Dense và BM25 theo công thức chuẩn:
    $$\text{RRF Score}(d) = \sum_{m \in M} \frac{1.0}{k + \text{rank}_m(d)}$$
    (với $k = 60$ mặc định, thứ hạng 1-based).
  - Trả về danh sách `SearchResult` có `retrieval_method="hybrid"`, sắp xếp điểm giảm dần, cắt đúng `top_k`.

- **Contract Tests & Kiểm thử:**
  - `pytest tests/test_contracts.py -k "chunk or semantic or lexical or rrf"`: **100% Passed (4/4 tests)**.
  - Test trực tiếp đầu ra thực tế cho các truy vấn tuyển sinh NEU 2026.

---

## 2. Hướng dẫn chạy lại trên Windows

Mở PowerShell tại thư mục gốc repository:

```powershell
# 1. Chạy lập chỉ mục và nạp 190 chunks vào ChromaDB
.\.venv\Scripts\python.exe -X utf8 -m src.task4_chunking_indexing

# 2. Kiểm tra tìm kiếm Dense (Semantic Search)
.\.venv\Scripts\python.exe -X utf8 -m src.task5_semantic_search

# 3. Kiểm tra tìm kiếm Lexical (BM25 Search)
.\.venv\Scripts\python.exe -X utf8 -m src.task6_lexical_search

# 4. Kiểm tra hợp nhất RRF (Reranking)
.\.venv\Scripts\python.exe -X utf8 -m src.task7_reranking

# 5. Chạy kiểm thử Contract Invariant
.\.venv\Scripts\python.exe -m pytest tests/test_contracts.py -k "chunk or semantic or lexical or rrf" -v
```

---

## 3. Vị trí bàn giao và Tài nguyên

| File / Thư mục | Nội dung bàn giao | Người nhận sử dụng |
| --- | --- | --- |
| `src/task4_chunking_indexing.py` | Hàm `load_documents`, `chunk_documents`, `embed_texts`, `embed_chunks`, `get_collection`, `index_to_vectorstore` | Người 3, 4 |
| `src/task5_semantic_search.py` | Hàm `semantic_search(query, top_k)` | Người 3 (Task 9 Pipeline) |
| `src/task6_lexical_search.py` | Hàm `build_bm25_index(chunks)`, `lexical_search(query, top_k)` | Người 3 (Task 9 Pipeline) |
| `src/task7_reranking.py` | Hàm `rerank_rrf(ranked_lists, top_k, k)` | Người 3 (Task 9 Pipeline) |
| `chroma_db/` | Vector database ChromaDB cục bộ chứa 190 chunks | Người 3, 4 (Local testing) |
| `.gitignore` | Đã bổ sung `chroma_db/` để tránh đẩy binary nặng lên git | Cả nhóm |

---

## 4. Hướng dẫn cho Người 3 (Duyên — Task 8, 9, 10)

1. **Kết nối vào `src/task9_retrieval_pipeline.py`:**
   - Trong hàm `retrieve(query, top_k, score_threshold, use_reranking)`:
     ```python
     dense = semantic_search(query, top_k=top_k * 2)
     sparse = lexical_search(query, top_k=top_k * 2)
     hybrid = rerank_rrf([dense, sparse], top_k=top_k) if use_reranking else dense[:top_k]
     ```
   - Điểm kích hoạt Fallback: Dùng `dense[0]["score"] < score_threshold` (lưu ý không dùng BM25 score để so với threshold).
   - Khi fallback kích hoạt, gọi `pageindex_search(query, top_k=top_k)`.

2. **Quy ước SearchResult Schema:**
   - Mỗi kết quả trả về từ `semantic_search`, `lexical_search`, và `rerank_rrf` đều tuân thủ chặt chẽ:
     ```python
     {
         "id": str,               # VD: "neu2026_undergraduate-chunk-23"
         "content": str,          # Nội dung chunk
         "metadata": dict,        # Giữ nguyên title, url, admission_year, audience, source
         "score": float,          # Điểm độ tương đồng / BM25 / RRF
         "retrieval_method": str  # "dense" | "bm25" | "hybrid"
     }
     ```
   - Trường `metadata["url"]` sẽ là `None` nếu tài liệu không có URL, đúng theo yêu cầu của `validate_document(require_chunk=True)`.

---

## 5. Hướng dẫn cho Người 4 (Na — Task 11 UI & Task 12 Evaluation)

1. **A/B Testing Retrieval:**
   - Pipeline hỗ trợ so sánh:
     - **Branch A (Dense only):** `use_reranking=False` $\rightarrow$ chỉ dùng `semantic_search`.
     - **Branch B (Hybrid + RRF):** `use_reranking=True` $\rightarrow$ kết hợp `semantic_search` + `lexical_search` qua `rerank_rrf`.
2. **Đo lường Metrics:**
   - 190 chunks đã có ID ổn định dạng `{doc_id}-chunk-{chunk_index}`. Các câu hỏi trong `golden_dataset.json` có thể đối chiếu chính xác context dựa trên `doc_id` và đoạn trích.
