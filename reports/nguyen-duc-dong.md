# Individual contribution report — Nguyễn Đức Đông

---

## Thông tin

- **Họ và tên:** Nguyễn Đức Đông
- **Mã học viên / SV:** 2A202602367
- **Nhóm:** Nhóm K4-L3B (RAG Pipeline tuyển sinh NEU 2026)
- **Repository/branch:** `vietbui000/K4-L3B-RAG-Pipeline` (branch: `nguyenducdong`)

---

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| **Task 4 — Chunking & Vector Indexing** | Chia 190 chunks từ 8 văn bản chuẩn hóa (`CHUNK_SIZE=500`, `OVERLAP=50`), tạo ID ổn định `{doc_id}-chunk-{chunk_index}`, nhúng vector bằng `paraphrase-multilingual-MiniLM-L12-v2` (`dim=384`), lập chỉ mục ChromaDB (`chroma_db/`) hỗ trợ upsert idempotent | `src/task4_chunking_indexing.py`, `chroma_db/` | Done |
| **Task 5 — Dense Semantic Search** | Triển khai hàm `semantic_search(query, top_k)`, tái sử dụng `embed_texts()`, chuyển đổi Cosine Distance sang Cosine Similarity (`1 - distance`), chuẩn hóa `SearchResult` | `src/task5_semantic_search.py` | Done |
| **Task 6 — Lexical Search (BM25)** | Khởi tạo chỉ mục `BM25Okapi` từ `rank_bm25` trên 190 chunks, caching index tối ưu tốc độ, truy vấn chính xác từ khóa, số hiệu, hotline | `src/task6_lexical_search.py` | Done |
| **Task 7 — Reranking (RRF)** | Xây dựng hàm `rerank_rrf` hợp nhất Dense Search và BM25 Search theo thuật toán Reciprocal Rank Fusion ($k=60$), deduplicate ID và cắt đúng `top_k` | `src/task7_reranking.py` | Done |
| **Retrieval Handoff Documentation** | Viết tài liệu hướng dẫn bàn giao chi tiết cho Người 3 (Pipeline) và Người 4 (Evaluation) | `docs/RETRIEVAL_HANDOFF.md` | Done |

---

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Sử dụng chiến lược Recursive Character Chunking (`CHUNK_SIZE = 500`, `CHUNK_OVERLAP = 50`) kết hợp thuật toán sinh ID cố định dạng `{doc_id}-chunk-{chunk_index}`.  
   **Lý do/evidence:** Kích thước 500 ký tự vừa đủ chứa trọn vẹn ngữ cảnh của 1 quy định tuyển sinh mà không vượt quá context window của mô hình embedding. ID cố định giúp ChromaDB hỗ trợ **upsert idempotent** (chạy lại script không bị trùng lặp dữ liệu, luôn giữ đúng 190 chunks).  
   **Trade-off:** 500 ký tự đôi khi cắt ngang một dòng bảng chỉ tiêu dài, nhưng đảm bảo tính nhất quán và khả năng chống nhân bản vector 100%.

2. **Quyết định:** Áp dụng phương pháp hợp nhất Reciprocal Rank Fusion (RRF với $k=60$) để kết hợp Dense Search và BM25 Search.  
   **Lý do/evidence:** RRF không phụ thuộc vào sự khác biệt về thang điểm (score scale) giữa Cosine Similarity ($0 \to 1$) và BM25 Score ($0 \to +\infty$). Giúp kết hợp hoàn hảo khả năng bắt từ khóa chính xác (mã ngành, hotline, ngày tháng) của BM25 và khả năng hiểu ngữ nghĩa của Dense Search.  
   **Trade-off:** Phải chạy cả Dense Search và BM25 Search trước khi rerank (thêm $\approx 15\text{ms}$ latency), nhưng giúp nâng chỉ số Context Recall từ 73.70% lên 87.94%.

---

## Kiểm thử và kết quả

- **Test hoặc query tôi đã dùng:**  
  `pytest tests/test_contracts.py -k "chunk or semantic or lexical or rrf"`  
  `python -m src.task4_chunking_indexing`  
  `python -m src.task5_semantic_search`  
  `python -m src.task6_lexical_search`  
  `python -m src.task7_reranking`
- **Kết quả trước/sau nếu có:**  
  - *Trước:* Dữ liệu Markdown thô chưa được tạo vector, chưa có cơ chế tìm kiếm từ khóa và ngữ nghĩa.  
  - *Sau:* 190 chunks được lập chỉ mục ChromaDB thành công; **100% Passed (4/4 contract tests)**; kết quả tìm kiếm Hybrid trả đúng định dạng `SearchResult` contract.
- **Lỗi đã phát hiện và cách xử lý:**  
  - *Lỗi:* ChromaDB báo lỗi crash khi nạp metadata có chứa giá trị `None` (như `url: None`).  
  - *Cách xử lý:* Lọc sạch metadata trước khi upsert vào ChromaDB (chuyển `None` thành chuỗi phù hợp) và tự động khôi phục `url: None` khi trả về kết quả để tuân thủ `docs/MODULE_CONTRACTS.md`.

---

## Điều còn hạn chế

- **Một hạn chế cụ thể của phần tôi làm:**  
  Việc chia chunk 500 ký tự cố định đôi khi ngắt đôi đoạn văn bản chứa bảng quy đổi điểm chứng chỉ ngoại ngữ hoặc bảng chỉ tiêu ngành.
- **Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện:**  
  Xây dựng bộ phân đoạn theo cấu trúc tiêu đề (Header-based Section Chunking) để giữ toàn vẹn từng bảng biểu và điều khoản quy định.

---

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- **Ngày:** 25/09/2026
- **Tên thành viên:** Nguyễn Đức Đông
