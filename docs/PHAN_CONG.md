# Phân công nhóm Manngusidan

**Chủ đề:** Tuyển sinh Đại học Quốc gia Hà Nội 2026 — phương thức xét tuyển, chỉ tiêu, học phí, điểm chuẩn.

## Thành viên và phần việc

| Thành viên | Mã học viên | Role | Task / file phụ trách | Điểm rubric |
|---|---|---|---|---:|
| Ngô Đinh Minh Nhật | 2A202602569 | Data & Indexing | Task 1–3 (`task1_collect_legal_docs.py`, `task2_crawl_news.py`, `task3_convert_markdown.py`) ✅ đã xong; Task 4 (`task4_chunking_indexing.py`); README + hướng dẫn chạy lại | 10 + 10 + 5 |
| Đinh Văn Bình | 2A202602830 | Retrieval | Task 5 dense (`task5_semantic_search.py`), Task 6 BM25 (`task6_lexical_search.py`), Task 7 RRF (`task7_reranking.py`); bonus: reranker nâng cao so với RRF | 20 (+3) |
| Trần Gia Khánh | 2A202602689 | Pipeline & Generation | Task 8 PageIndex fallback (`task8_pageindex_vectorless.py`), Task 9 retrieval pipeline + calibrate threshold (`task9_retrieval_pipeline.py`), Task 10 generation có citation + safe refusal (`task10_generation.py`) | 10 + 15 |
| Tô Huy Thông | 2A202602608 | UI & Evaluation | Chatbot Streamlit (`app.py`); golden dataset ≥15 câu (`group_project/evaluation/golden_dataset.json`); chạy 4 metric + A/B dense-only vs hybrid; `RESULT.md`; bonus: source highlighting | 10 + 10 (+2) |

Mỗi người tự viết báo cáo cá nhân `reports/<mã-học-viên>-<tên-ngắn>.md` theo `reports/INDIVIDUAL_REPORT.md`.

## Interface bàn giao (theo `docs/MODULE_CONTRACTS.md`)

| Người giao → nhận | Bàn giao | Ghi chú |
|---|---|---|
| Nhật → Bình | `embed_texts()`, `get_collection()`, `load_documents()`, `chunk_documents()`, ChromaDB đã index | Bình dùng **chung** `embed_texts()` cho dense search; BM25 chạy trên cùng danh sách chunk |
| Bình → Khánh | `semantic_search()`, `lexical_search()`, `rerank_rrf()` trả `list[SearchResult]` | Dense trả **cosine score gốc** — Khánh dùng score này cho fallback, không dùng RRF score |
| Khánh → Thông | `retrieve()`, `generate_with_citation()` trả `GenerationResult` | UI hiển thị answer, sources, `retrieval_source`, score |
| Nhật → Thông | Corpus `data/standardized/` | Golden Q&A phải lấy câu trả lời + context từ đúng corpus này |

Trong lúc chờ module phía trước, mỗi người dùng dữ liệu giả đúng schema (xem `tests/test_contracts.py`) để code song song.

## Thứ tự và mốc

1. **Setup (tất cả):** venv Python 3.12 (`py -3.12 -m venv .venv`), `pip install -e ".[dev]"`, thống nhất `EMBEDDING_PROVIDER` và `LLM_PROVIDER` trong `.env` (không commit `.env`).
2. **Nhật:** hoàn thành Task 4 sớm nhất — đây là điểm nghẽn của cả nhóm.
3. **Bình ∥ Thông:** Bình làm Task 5–7; Thông viết golden dataset từ corpus và dựng khung `app.py`.
4. **Khánh:** Task 8–10 khi đã có Task 5–7; calibrate threshold bằng query trong domain (ĐHQGHN) và ngoài domain.
5. **Thông:** chạy evaluation A/B, điền `RESULT.md`.
6. **Tất cả:** `pytest -q` pass, báo cáo cá nhân, demo 1 query đúng + 1 query ngoài domain + kết quả A/B.

## Quy tắc làm việc

- Mỗi người làm trên branch riêng (`nhat/data-index`, `binh/retrieval`, `khanh/generation`, `thong/ui-eval`), merge vào `main` qua PR.
- Ghi lại commit/PR của mình để đưa vào báo cáo cá nhân.
- Chạy `pytest tests/test_contracts.py -q` trước khi mở PR.
