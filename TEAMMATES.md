# Danh sách thành viên nhóm Gene — Day 08 RAG Pipeline

**Tên nhóm**: Gene  
**Đề tài**: Hệ thống RAG Hỏi đáp Tuyển sinh Đại học (Hybrid Retrieval + Citation + Streamlit UI)  
**Repository**: `K4-L3B-RAG-Pipeline`

---

## Bảng phân công vai trò và nhiệm vụ

| STT | Họ và tên | Mã học viên | Vai trò (Role) | Nhánh (Branch) | Module & Phần việc phụ trách |
| :---: | :--- | :---: | :--- | :--- | :--- |
| **1** | **Dương Đức Vương** | **2A202602944** | **Data & Ingestion Engineer** (Role A) | `feat/data-ingestion` | - Task 1: Thu thập ≥3 tài liệu pháp lý/quy chế tuyển sinh (`.pdf`, `.docx`).<br>- Task 2: Crawl ≥5 tin tức/thông báo tuyển sinh (`.json`).<br>- Task 3: Chuẩn hóa toàn bộ dữ liệu sang Markdown (`.md`).<br>- Task 4: Chunking văn bản, embedding và nạp vào ChromaDB vector database. |
| **2** | **Lục Tiến Đạt** | **2A202602969** | **Search & Retrieval Engineer** (Role B) | `feat/retrieval-pipeline` | - Task 5: Semantic Search (ChromaDB + Cosine similarity).<br>- Task 6: Lexical Search (BM25Okapi + IDF floor calibration).<br>- Task 7: Reranking thuật toán Reciprocal Rank Fusion (RRF $k=60$).<br>- Task 8: PageIndex vectorless search & caching fallback.<br>- Task 9: Retrieval Pipeline tích hợp và kiểm soát ngưỡng tin cậy. |
| **3** | **Nguyễn Thành Tiến** | **2A202603003** | **LLM & Application Engineer** (Role C) | `feat/generation-ui` | - Task 10: Generation có Citation, Context reordering chống Lost-in-the-middle, LLM dispatch (OpenAI/Gemini) và Safe refusal khi thiếu bằng chứng.<br>- `app.py`: Xây dựng giao diện Chatbot tương tác trên Streamlit (hiển thị câu trả lời, trích dẫn nguồn, retrieval method và điểm số). |
| **4** | **Nguyễn Văn Thân** | **2A202602859** | **Evaluation & QA Engineer** (Role D) | `feat/evaluation-benchmark` | - Xây dựng Golden Dataset (≥15 test cases grounded trong corpus).<br>- Đánh giá định lượng qua 4 chỉ số (Faithfulness, Answer Relevance, Context Recall, Context Precision).<br>- Thực nghiệm so sánh A/B (Config A: Dense-only vs Config B: Hybrid+RRF).<br>- Hoàn thiện báo cáo nhóm `group_project/evaluation/RESULT.md` và triển khai tính năng Bonus. |

---

## Chi tiết nhiệm vụ theo từng thành viên

### 1. Thành viên A — Dương Đức Vương (2A202602944)
* **Vai trò**: Data & Ingestion Engineer
* **File phụ trách**:
  - `src/task1_collect_legal_docs.py`
  - `src/task2_crawl_news.py`
  - `src/task3_convert_markdown.py`
  - `src/task4_chunking_indexing.py`
* **Tiêu chí nghiệm thu**: Pass các test chấp nhận dữ liệu trong `tests/test_acceptance.py`.
* **Báo cáo cá nhân**: `reports/2A202602944-DuongDucVuong.md`.

### 2. Thành viên B — Lục Tiến Đạt (2A202602969)
* **Vai trò**: Search & Retrieval Engineer
* **File phụ trách**:
  - `src/task5_semantic_search.py`
  - `src/task6_lexical_search.py`
  - `src/task7_reranking.py`
  - `src/task8_pageindex_vectorless.py`
  - `src/task9_retrieval_pipeline.py`
* **Tiêu chí nghiệm thu**: Pass 100% (7/7) các bài test hợp đồng trong `tests/test_contracts.py`.
* **Báo cáo cá nhân**: `reports/2A202602969-LucTienDat.md`.

### 3. Thành viên C — Nguyễn Thành Tiến (2A202603003)
* **Vai trò**: LLM & Application Engineer
* **File phụ trách**:
  - `src/task10_generation.py`
  - `app.py`
* **Tiêu chí nghiệm thu**: Pass `test_reorder_is_non_mutating_and_context_contains_source` và ứng dụng Streamlit chạy trơn tru end-to-end.
* **Báo cáo cá nhân**: `reports/2A202603003-NguyenThanhTien.md`.

### 4. Thành viên D — Nguyễn Văn Thân (2A202602859)
* **Vai trò**: Evaluation & QA Engineer
* **File phụ trách**:
  - `group_project/evaluation/golden_dataset.json`
  - `group_project/evaluation/RESULT.md`
* **Tiêu chí nghiệm thu**: Hoàn thành không còn chữ `TODO` trong file đánh giá, chạy `pytest -q` pass toàn bộ hệ thống.
* **Báo cáo cá nhân**: `reports/2A202602859-NguyenVanThan.md`.
