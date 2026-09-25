# Spec 1 — RAG Chatbot: Thuế và Nghĩa vụ Kê khai của Hộ Kinh Doanh

- **Date:** 2026-09-25
- **Owner:** Team T040-Skynet (4 người: Tiên, Khoa, Chiến, Linh)
- **Time budget:** 3 giờ (lab session, Day 8)
- **Status:** Draft v2 — narrowed scope to tax & declaration only

## 1. Mục tiêu

Xây dựng chatbot RAG trả lời câu hỏi về **thuế và nghĩa vụ kê khai** dành cho hộ kinh doanh cá thể tại Việt Nam, dùng làm sản phẩm nộp cho bài lab Day 8. Phải chạy end-to-end trong 3 giờ với 4 người song song, đạt yêu cầu tối thiểu của rubric (`docs/GRADING_RUBRIC.md`) và tất cả contract test (`tests/test_contracts.py`) pass.

## 2. Phạm vi nội dung

- **Chủ đề (in scope):**
  - Các loại thuế hộ kinh doanh phải nộp: thuế môn bài, thuế GTGT, thuế TNCN.
  - Phương pháp tính thuế: khoán, kê khai, theo từng lần phát sinh.
  - Ngưỡng doanh thu chịu thuế / miễn thuế.
  - Nghĩa vụ kê khai: hồ sơ, biểu mẫu, thời hạn (tháng/quý/năm), nơi nộp.
  - Hoá đơn điện tử: khi nào bắt buộc, cách khởi tạo, hoá đơn khởi tạo từ máy tính tiền — vì liên quan trực tiếp đến kê khai.
  - Xử phạt vi phạm hành chính về thuế (nộp chậm, kê khai sai, không đăng ký thuế).
- **Ngôn ngữ corpus và UI:** Tiếng Việt (BGE-M3 hỗ trợ tốt).
- **Đối tượng người dùng giả định:** Chủ hộ kinh doanh nhỏ đang phải kê khai/nộp thuế, muốn tra cứu nghĩa vụ và biểu mẫu.
- **Ngoài phạm vi (out of scope):**
  - Thủ tục đăng ký hộ kinh doanh, giấy phép kinh doanh, đăng ký ngành nghề.
  - Quy định thương mại điện tử nói chung (chỉ giữ phần thuế TMĐT nếu có).
  - Doanh nghiệp có tư cách pháp nhân (Cty TNHH, CP).
  - Thuế TNCN của cá nhân không kinh doanh.
  - Luật lao động, luật đất đai, luật bảo hiểm xã hội.

## 3. Nguồn dữ liệu

### Legal (≥3 PDFs, ưu tiên nguồn chính phủ; tất cả xoay quanh thuế/kê khai)
Ứng viên (Track A tự xác nhận URL còn sống trước khi tải):
1. **Thông tư 40/2021/TT-BTC** — hướng dẫn thuế GTGT, TNCN và quản lý thuế đối với hộ kinh doanh, cá nhân kinh doanh (văn bản chính).
2. **Thông tư 100/2021/TT-BTC** — sửa đổi Thông tư 40/2021, cập nhật phương pháp tính thuế và biểu mẫu.
3. **Nghị định 126/2020/NĐ-CP** — quy định chi tiết Luật Quản lý thuế 2019 (thời hạn nộp hồ sơ, chậm nộp, ấn định thuế).
4. (Backup) **Nghị định 123/2020/NĐ-CP** — hoá đơn, chứng từ; chỉ dùng phần áp dụng cho hộ kinh doanh (chương về hoá đơn khởi tạo từ máy tính tiền).
5. (Backup) **Luật Quản lý thuế 2019 số 38/2019/QH14** — điều khoản về nghĩa vụ của người nộp thuế.

Nguồn tải: `chinhphu.vn`, `gdt.gov.vn`, `thuvienphapluat.vn`, `luatvietnam.vn`, `mof.gov.vn`.

### News (≥5 bài giải thích thực tế về thuế/kê khai)
Ưu tiên bài "hộ kinh doanh nộp thuế thế nào", "hộ kinh doanh phải kê khai gì", "thuế khoán 2024/2025", "hoá đơn điện tử hộ kinh doanh", "phạt chậm nộp thuế".
Nguồn: VnExpress (mục Kinh doanh), Thời báo Tài chính, VietnamNet Kinh tế, LuatVietnam blog, Luật Minh Khuê blog. Tránh forum, wiki, mạng xã hội.

## 4. Kiến trúc

Contracts đã fix trong `docs/MODULE_CONTRACTS.md`. Kiến trúc cấp cao:

```
data/landing/{legal,news}     →  task1/task2      (raw)
        │
        ▼
data/standardized/{legal,news} →  task3           (markdown chuẩn hoá)
        │
        ▼
ChromaDB (cosine, BGE-M3)      →  task4           (chunk + embed + index)
        │
        ├─▶ semantic_search  (task5, dense)
        │           ╲
        │            ▶ rerank_rrf  (task7) ──▶ retrieve  (task9)
        │           ╱                                │
        └─▶ lexical_search   (task6, BM25)           │
                                                     │  fallback nếu best cosine < threshold
                                                     ▼
                                              pageindex_search (task8)
                                                     │
                                                     ▼
                                     generate_with_citation (task10) ──▶ Streamlit app.py
```

**Config chung (chốt trước, tránh conflict):**
- `EMBEDDING_PROVIDER=sentence_transformers`, `EMBEDDING_MODEL=BAAI/bge-m3`, `EMBEDDING_DIM=1024`.
- `LLM_PROVIDER=openai`, `LLM_MODEL=gpt-4o-mini` (rẻ, đủ cho lab; đổi sang gemini/anthropic nếu người dùng ưu tiên).
- Chunk size 500, overlap 50, recursive.
- `SCORE_THRESHOLD=0.3` (giá trị khởi đầu, Track C calibrate sau Phase 2).
- Collection name: `rag_hkd_thue`.

## 5. Chia việc song song 4 người (Approach 1 — track dọc)

### Track A — Data Engineer — **Tiên**
**File owns:** `src/task1_collect_legal_docs.py`, `src/task2_crawl_news.py`, `src/task3_convert_markdown.py`, `data/landing/**`, `data/standardized/**`.

**Deliverables:**
- ≥3 PDF hợp lệ trong `data/landing/legal/`, đặt tên không dấu (vd `nd01-2021-dang-ky-doanh-nghiep.pdf`).
- ≥5 file JSON trong `data/landing/news/` đúng schema `{url, title, date_crawled, content_markdown}`.
- Toàn bộ markdown chuẩn hoá trong `data/standardized/{legal,news}/*.md` (news có header Source + Crawled).
- Chạy lại `task3` không tạo file trùng.

**Definition of done:** `ls data/standardized/legal/*.md | wc -l` ≥ 3 và `ls data/standardized/news/*.md | wc -l` ≥ 5, mỗi file không rỗng.

### Track B — Retrieval Core — **Khoa**
**File owns:** `src/task4_chunking_indexing.py`, `src/task5_semantic_search.py`, `src/task6_lexical_search.py`, thư mục `chroma_db/`.

**Deliverables:**
- `embed_texts`, `get_collection`, `load_documents`, `chunk_documents`, `embed_chunks`, `index_to_vectorstore` — theo contract.
- `semantic_search(query, top_k)` trả `retrieval_method="dense"`, score = `1 - cosine_distance`, sort giảm dần, không trùng ID.
- `lexical_search(query, top_k)` dùng cùng corpus với task4, tokenize `lower().split()` (baseline), `retrieval_method="bm25"`.
- **Chia sẻ CORPUS:** task6 phải load lại cùng chunks task4 tạo (đọc từ Chroma hoặc cache JSON `data/bm25_corpus.json` để thứ tự deterministic).

**Definition of done:** `pytest tests/test_contracts.py -k "task4 or semantic or lexical" -q` pass; `python -m src.task5_semantic_search` in ra kết quả cho 1 query mẫu.

### Track C — Fusion, Fallback & Pipeline — **Chiến**
**File owns:** `src/task7_reranking.py`, `src/task8_pageindex_vectorless.py`, `src/task9_retrieval_pipeline.py`, tuning `SCORE_THRESHOLD`.

**Deliverables:**
- `rerank_rrf`: đúng công thức `sum(1/(k+rank))`, rank từ 1, dedupe theo ID, output `retrieval_method="hybrid"`.
- `pageindex_search`: upload lazy (cache mapping `source → doc_id` trong `data/pageindex_cache.json`), có timeout + try/except; nếu không có `PAGEINDEX_API_KEY` → return `[]` không raise.
- `retrieve`: chạy dense + sparse với `top_k*2`, RRF **một lần**, so sánh best cosine gốc từ `dense[0]["score"]` (không phải RRF score) với `SCORE_THRESHOLD`; nếu dưới → thử pageindex → nếu pageindex rỗng/lỗi → trả hybrid.
- Calibrate threshold: chạy 3 query in-domain + 3 query out-of-domain, chọn ngưỡng phân tách tốt nhất, ghi vào `.env` và note lý do trong `RESULT.md`.

**Definition of done:** `pytest tests/test_contracts.py -k "rrf or retrieve or pageindex" -q` pass; `retrieve("thuế môn bài hộ kinh doanh bao nhiêu")` trả hybrid, `retrieve("cách nướng cá basa")` trả pageindex hoặc hybrid với top1 score thấp (không crash).

### Track D — Generation, UI & Evaluation — **Linh**
**File owns:** `src/task10_generation.py`, `app.py`, `group_project/evaluation/golden_dataset.json`, `reports/RESULT.md`.

**Deliverables:**
- `reorder_for_llm`: front `[::2]` + reversed back `[1::2][::-1]`, giữ nguyên ID.
- `format_context`: label `[Document i | Title: ... | Source: ...]`, chunk phân tách bằng `\n\n---\n\n`.
- `call_llm`: dispatch theo `LLM_PROVIDER`, `TEMPERATURE=0.3`, timeout 30s, raise rõ ràng.
- `generate_with_citation`: nếu `retrieve` rỗng hoặc `call_llm` fail → safe refusal `"Tôi không thể xác minh thông tin này từ nguồn hiện có."`, `retrieval_source="none"`.
- `app.py`: hiển thị answer, list sources với `title | source | retrieval_method | score`, lưu `st.session_state.messages`.
- **Golden dataset:** ≥15 câu — 10 in-domain xoay quanh thuế/kê khai (thuế môn bài, ngưỡng doanh thu, hồ sơ khai thuế, thời hạn nộp, hoá đơn điện tử, phạt chậm nộp) + 3 hard case in-domain (đòi hỏi nhiều chunk / multi-hop: vd "hộ khoán vượt ngưỡng doanh thu giữa năm thì phải làm gì") + 2 out-of-domain (safe refusal, vd "cách nướng cá basa", "thủ tục đăng ký hộ kinh doanh"). Mỗi câu theo schema của `tests/test_acceptance.py::test_golden_dataset_has_15_grounded_cases`: `{question, expected_answer, expected_context}`.
- **Evaluation:** dùng `ragas` với 4 metric (faithfulness, answer_relevance, context_recall, context_precision). Chạy 2 config (dense-only bằng `retrieve(..., use_reranking=False)` vs hybrid+RRF), điền `RESULT.md` không còn TODO.

**Definition of done:** `streamlit run app.py` chạy 1 query đúng + 1 query out-of-domain OK; `RESULT.md` có bảng 4 metric × 2 config điền số thật.

## 6. Tiên lược song song hoá (unblocking)

**Vấn đề:** B/C/D phụ thuộc data của A. Giải quyết bằng **mock/stub sớm**.

**Phase 0 (10 phút đầu — cả team cùng nhau):**
- Cả team setup env: `python -m venv .venv && pip install -e ".[dev]" && playwright install chromium`.
- Chốt `.env` chung (LLM_PROVIDER, một OPENAI_API_KEY dùng chung; embedding local nên không tốn).
- Tiên tạo 2-3 file `.md` mẫu (copy-paste 1 trang từ Thông tư 40/2021 — điều khoản thuế khoán / kê khai) vào `data/standardized/legal/` — **đủ để B/C/D bắt đầu**.

**Phase 1 (song song 4 người, ~2h):**
| Người | Bắt đầu ngay với... |
|---|---|
| Tiên (A) | Tải PDF thật + crawl news, chạy task3 |
| Khoa (B)  | Dùng 3 file .md mẫu của Tiên → implement task4→5→6, index vào Chroma local |
| Chiến (C)  | Viết task7 với 2 list mock; task9 với mock `semantic_search` + `lexical_search` trong test riêng; task8 stub trả `[]` |
| Linh (D)  | task10 với mock `retrieve` (list chunks giả); app.py với mock `generate_with_citation`; viết 15 câu golden Q&A xoay quanh thuế/kê khai (Thông tư 40/2021 + Nghị định 126/2020) |

**Phase 2 (integration ~30 phút):**
- Tiên xong data thật → Khoa re-index → Chiến tune threshold trên data thật → Linh chạy eval thật.
- Chạy `pytest -q` toàn bộ; ai fail thì fix.
- Ai xong sớm hỗ trợ code review + fill `RESULT.md`.

**Phase 3 (~20 phút):**
- Mỗi thành viên viết individual report (`reports/<student-id>-<name>.md`).
- Cleanup: đảm bảo `.env` không commit, `chroma_db/` có trong `.gitignore`.
- Demo 3 query: đúng-domain, hard (cần RRF), out-of-domain.

## 7. Integration contract giữa các track

Để 4 track không giẫm chân nhau, mỗi ranh giới được đóng bằng contract test:

- **A → B:** files `data/standardized/**/*.md` với header markdown; B chỉ đọc `standardized/`, không đọc `landing/`.
- **B → C:** `semantic_search(query, top_k)` và `lexical_search(query, top_k)` — schema `SearchResult`, sort giảm dần.
- **C → D:** `retrieve(query, top_k, score_threshold, use_reranking)` — trả `list[SearchResult]` hoặc `[]`.
- **D:** consume `retrieve` + gọi LLM, không được biết chi tiết dense/sparse bên trong.

**Git strategy:** mỗi track làm ở branch `feat/track-<A|B|C|D>-<short>`, PR về `main` khi track xong. Owner track review PR của track khác.

## 8. Rủi ro & mitigation

| Rủi ro | Mitigation |
|---|---|
| Website luật chặn crawler | Tiên tải thủ công qua browser, drop vào `data/landing/legal/` |
| BGE-M3 model download lâu (~2GB) | Khoa pre-download trong Phase 0 khi Tiên còn tải data |
| OpenAI API key hết quota giữa lab | Backup: đổi `LLM_PROVIDER=gemini`, `LLM_MODEL=gemini-2.0-flash` (free tier) |
| PageIndex không có API key | Task8 return `[]` — fallback không chạy nhưng contract test vẫn pass; ghi note trong `RESULT.md` |
| Ragas eval quá chậm (>10 phút) | Giảm về 10 câu golden để chạy A/B, tăng lại nếu còn thời gian |
| BM25 tokenization tiếng Việt kém | Chấp nhận baseline `lower().split()`; note trong report; nếu dư thời gian dùng `underthesea` |

## 9. Bonus (nếu dư thời gian, không phải MVP)

- **+3 điểm:** HyDE — sinh 1 giả-thuyết trước khi embed query, so sánh A/B.
- **+2 điểm:** UI highlight citation trong source panel (Streamlit expander).
- **+2 điểm:** Conversation memory cho follow-up ("còn thuế môn bài thì sao?").

Ai làm bonus phải đảm bảo MVP đã pass trước.

## 10. Definition of "lab done"

Toàn team ✅ khi và chỉ khi:
1. `pytest -q` xanh toàn bộ (`test_contracts.py` + `test_acceptance.py`).
2. `streamlit run app.py` chạy được demo 3 query.
3. `group_project/evaluation/golden_dataset.json` có ≥15 câu.
4. `reports/RESULT.md` không còn `TODO`.
5. 4/4 individual reports đã commit.
6. Repo push lên `main` không kèm `.env`, API key, hay `chroma_db/`.
