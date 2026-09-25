# Individual contribution report

---

## Thông tin

- Họ và tên: Nguyễn Công Duẩn
- Mã học viên: 2A202602716
- Nhóm: Soul
- Repository/branch: `duannc`

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| **Lead / DevOps — Setup môi trường** | Khởi tạo repo, cấu hình `pyproject.toml`, sửa lỗi TOML syntax , fix deps `sentence-transformers` constraint | `c70b473` | Done |
| **Lead / DevOps — `.env` & embedding config** | Cấu hình `.env`, chuyển `EMBEDDING_PROVIDER` từ `sentence_transformers` → `gemini` để tránh tải torch 124MB, giảm batch size 50→20 và tăng retry để xử lý Gemini rate limit 429 | `.env`| Done |
| **Lead / DevOps — Chạy test cuối** | Chạy `pytest -q` toàn bộ 20 test, xác nhận pass 100% | `tests/` — `d68b48f` | Done |
| **QA/Eval — Chatbot UI (`app.py`)** | Viết toàn bộ `app.py` từ skeleton TODO, tích hợp `generate_with_citation()`, hiển thị answer + source badges + score chunks, sidebar lịch sử hội thoại, 4 quick-reply chips | `app.py` — `d68b48f` | Done |
| **QA/Eval — Golden dataset** | Tạo 15 cặp Q&A dựa trên corpus thực (14 in-domain + 1 out-of-domain safe refusal), đảm bảo đủ fields `question`, `expected_answer`, `expected_context` | `group_project/evaluation/golden_dataset.json` — `d68b48f` | Done |
| **QA/Eval — Evaluation report** | Viết `RESULT.md` đầy đủ: overall scores 4 metrics, A/B comparison dense vs hybrid, worst performers, error analysis, recommendations | `group_project/evaluation/RESULT.md` — `7beec93` | Done |
| **QA/Eval — Individual report template** | Tạo `group_project/individual/INDIVIDUAL_REPORT.md` | `group_project/individual/INDIVIDUAL_REPORT.md` — `7beec93` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Chuyển embedding provider từ `sentence_transformers (BAAI/bge-m3)` sang `gemini-embedding-001`  
   **Lý do/evidence:** `sentence_transformers` yêu cầu tải `torch` ~124MB và timeout sau 5 phút trên mạng chậm. Gemini API đã có key sẵn trong `.env`, không cần tải model về local.  
   **Trade-off:** Phụ thuộc vào API key và quota Gemini. Cần retry logic khi gặp rate limit 429. Đã xử lý bằng cách giảm batch size 50→20, tăng wait giữa batch 1s→3s, tăng max_retries 5→8.

2. **Quyết định:** Thiết kế `app.py` với session state lưu lịch sử hội thoại nhiều phiên  
   **Lý do/evidence:**  Streamlit không có multi-session built-in nên phải tự quản lý qua `st.session_state.sessions`.  
   **Trade-off:** Lịch sử chỉ tồn tại trong RAM của session Streamlit, mất khi reload trang. Chấp nhận được với scope lab, không cần persistent storage.

## Kiểm thử và kết quả

- **Test chạy:** `pytest tests/ -q` — 20 tests (15 contract tests + 5 acceptance tests)
- **Kết quả:** `20 passed in 5.06s` — pass 100%
- **RAGAS Evaluation thực tế:** chạy `python tests/run_ragas_evaluation.py` trên 14 in-domain cases, LLM judge `gemini-3.5-flash-lite`:

| Metric | Score |
|---|---|
| Faithfulness | **1.0000** |
| Answer Relevance | **0.7857** |
| Context Recall | **0.7964** |
| Context Precision | **0.2929** |
| **Average** | **0.7188** |

- **Lỗi đã phát hiện và xử lý:**
  - `golden_dataset.json` câu #15 có `expected_context` rỗng → test acceptance fail → sửa thành chuỗi mô tả out-of-domain
  - Gemini embedding rate limit 429 → giảm batch size và tăng wait time
  - Script RAGAS lần đầu dùng `gemini-2.0-flash` (deprecated) → đổi sang `gemini-3.5-flash-lite`
  - `langchain_text_splitters` top-level import crash do `transformers 5.17` không tương thích `torch 2.3.1` → sửa thành lazy import trong `chunk_documents()`

## Điều còn hạn chế

- **Hạn chế:** Context Precision thấp (0.29) do top_k=5 kéo nhiều chunks không liên quan. Hai câu hỏi (học bổng tiêu chí, BHYT) bị Context Recall = 0 do thông tin phân tán qua nhiều điều khoản và nội dung crawl thiếu.
- **Nếu có thêm thời gian:** Giảm top_k xuống 3, tăng chunk overlap lên 100, re-crawl bài BHYT với Playwright render mode để cải thiện recall.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 25/09/2026
- Tên thành viên: Nguyễn Công Duẩn
