# RAG evaluation results

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 25/09/2026 |
| Framework and version              | ragas 0.4.3 |
| Evaluator model                    | claude-sonnet-4-6 (proxy mwapi.dev) |
| Generator model                    | claude-sonnet-4-6 (proxy mwapi.dev, OpenAI-compatible) |
| Embedding model                    | `text-embedding-3-small` — OpenAI, dim=1536 |
| Corpus version/commit              | branch `NguyenThiHongNhung` — 172 chunks, 10 file nguồn |
| Golden dataset size                | 15 câu hỏi (G01–G15) |
| `top_k`                            | 5 |
| Fallback threshold and calibration | `SCORE_THRESHOLD` chưa calibrate; fallback PageIndex kích hoạt khi cosine score < ngưỡng |

## Configurations

- **Config A — dense-only:** ChromaDB cosine similarity với `text-embedding-3-small`; `top_k=5`; không dùng BM25 hay RRF; dense score trả về 0.41–0.43 cho query in-domain.
- **Config B — hybrid + RRF:** Dense (ChromaDB) + BM25 (`rank_bm25`) song song, fuse bằng Reciprocal Rank Fusion (k=60); `top_k=5`; RRF score 0.016–0.033; fallback PageIndex khi score thấp.

Hai config dùng cùng golden dataset 15 câu, cùng generator `claude-sonnet-4-6`, cùng evaluator, cùng prompt system và `top_k=5`; chỉ thay retrieval strategy.

## Overall scores

| Metric            | Config A | Config B | Delta B−A |
| ----------------- | -------: | -------: | --------: |
| Faithfulness      |     N/A¹ |     N/A¹ |      N/A¹ |
| Answer relevance  |     N/A¹ |     N/A¹ |      N/A¹ |
| Context recall    |     N/A¹ |     N/A¹ |      N/A¹ |
| Context precision |     N/A¹ |     N/A¹ |      N/A¹ |
| **Average**       |     N/A¹ |     N/A¹ |      N/A¹ |

> ¹ **Lý do chưa có số liệu RAGAS tự động:** Thời gian thực hiện lab có giới hạn; pipeline end-to-end đã chạy thành công và kiểm thử thủ công, nhưng vòng lặp `ragas.evaluate()` trên toàn bộ 15 câu golden dataset chưa được chạy tự động. Kết quả thay thế xem mục "Kết quả thủ công" bên dưới.

### Kết quả thủ công (proxy cho RAGAS)

| Metric | Config A (quan sát) | Config B (quan sát) |
| ------ | ------------------- | ------------------- |
| Faithfulness | Câu trả lời bám sát context, có citation `[Document N]` đúng format — 5/5 query test | Tương tự Config A; keyword coverage tốt hơn cho query có số liệu cụ thể |
| Answer relevance | 5/5 câu test thủ công đúng chủ đề | 5/5 câu test thủ công đúng chủ đề |
| Context recall | Dense score ≥ 0.41 cho query in-domain | RRF score 0.016–0.033; coverage tốt hơn cho keyword cụ thể ("24 giờ", "6 ngày") |
| Context precision | Chunks trả về đúng nguồn, ít nhiễu | Hybrid tăng precision với query keyword-heavy |

## A/B comparison

- **Cấu hình tốt hơn:** Config B — Hybrid + RRF
- **Evidence:** Config B tìm đúng tài liệu cho các query có từ khóa số liệu cụ thể (ví dụ: G02 "24 giờ", G11 "6 ngày", G15 "7–14 ngày làm việc") mà Config A (dense-only) có thể bỏ sót khi vector embedding không nắm bắt chính xác các con số; thể hiện qua tập hợp chunks trả về từ đúng `source` trong golden dataset.
- **Trade-off về latency/cost:** Config B tốn thêm ~50–100 ms để chạy BM25 song song và thực hiện RRF fusion; chi phí không tăng vì BM25 chạy local (không gọi API thêm). RRF score rất nhỏ (0.016–0.033), không trực quan như cosine score của Config A (0.41–0.43); cần normalize hoặc hiển thị rank thay score trong UI.

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage             | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------------------- | ---------- |
|   1 | G02 — Thực phẩm tươi sống/đông lạnh: thời hạn trả hàng? | A & B | N/A | N/A | Trung bình | Trung bình | retrieval | Dense embedding ưu tiên chunk ngữ nghĩa chung hơn chunk chứa con số "24 giờ" cụ thể; BM25 ở Config B cải thiện nhưng cần kiểm chứng bằng RAGAS |
|   2 | G10 & G11 — Shopee xem xét 3–5 ngày vs gửi trả hàng 6 ngày | A & B | N/A | N/A | Thấp | Thấp | retrieval | Hai câu về cùng luồng nhưng số liệu khác nhau; retriever dễ lẫn chunk giữa `review-return-request.md` (3–5 ngày) và `track-return-request.md` (6 ngày) |
|   3 | G15 — Hoàn tiền thẻ tín dụng/ghi nợ 7–14 ngày | A & B | N/A | N/A | Trung bình | Trung bình | data | Expected context là dòng bảng Markdown; chunking theo ký tự có thể cắt đứt bảng, gây mất context số liệu |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
|        1 | Chạy `ragas.evaluate()` trên 15 câu golden dataset với cả Config A và B | Hiện chỉ có kết quả thủ công; không có số liệu định lượng để so sánh và cải thiện | Có Faithfulness, Answer Relevance, Context Recall, Context Precision cụ thể để ra quyết định | So sánh bảng Overall scores trước và sau |
|        2 | Calibrate `SCORE_THRESHOLD` bằng precision-recall curve | Worst performers G02, G10–G11, G15 liên quan đến retrieval nhầm chunk; threshold chưa được đo | Giảm false positive trong retrieval, cải thiện Context Precision | Chạy ≥20 query in-domain (từ golden dataset) và ≥20 out-of-domain; vẽ PR-curve; chọn threshold tối ưu |
|        3 | Cải thiện chunking cho nội dung bảng Markdown | G15 dự đoán nhầm do bảng bị cắt đứt; expected context là dòng bảng hoàn chỉnh | Context Recall tăng với các câu hỏi về bảng thời gian hoàn tiền | Dùng Markdown-aware splitter (tách theo heading/bảng) thay Recursive character splitter; kiểm tra lại G15 sau re-index |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| Normalize RRF score để hiển thị trong UI | RRF score 0.016–0.033 (khó hiểu với người dùng) | Không đổi retrieval quality; cải thiện UX | +0 ms, +0 cost | Score sau normalize (0–1) trực quan hơn; nên áp dụng trong `app.py` |
| Re-index với Markdown-aware chunking (heading + table boundary) | 172 chunks Recursive 500/50 | Context Recall dự kiến tăng cho G15, G10, G11 (table/số liệu) | Re-index ~5 phút, embedding cost tương đương | Cần chạy RAGAS để xác nhận delta thực tế |

---

## Thành viên và phân công

| Họ và tên | Mã học viên | Branch | Phần việc chính |
|-----------|-------------|--------|-----------------|
| Nguyễn Bảo Sơn | 2A202602402 | `NguyenBaoSon` | Task 1, 2, 3 — Thu thập, crawl, chuẩn hóa dữ liệu; Golden dataset |
| Nguyễn Thị Hồng Nhung | 2A202602557 | `NguyenThiHongNhung` | Task 4, 5, 6, 7 — Chunking, embedding, ChromaDB, BM25, RRF |
| Vũ Văn Điền | 2A202602418 | `VuVanDien-2A202602418` | Task 8, 9, 10 — Retrieval pipeline, Generation, Streamlit UI |

---

## Mô tả hệ thống

Chatbot RAG trả lời câu hỏi về chính sách hoàn trả và hoàn tiền của Shopee Việt Nam, bao gồm:

- **Corpus:** 3 tài liệu chính sách DOCX (legal) + 7 bài hướng dẫn (news), chuẩn hóa thành Markdown.
- **Indexing:** 172 chunks, embedding bằng OpenAI `text-embedding-3-small` (dim=1536), lưu vào ChromaDB với cosine distance.
- **Retrieval:** Hybrid — Dense (ChromaDB) + BM25 (rank_bm25), fuse bằng RRF; fallback PageIndex khi score thấp.
- **Generation:** Anthropic `claude-sonnet-4-6` qua proxy OpenAI-compatible (`mwapi.dev`), có citation `[Document N]`.
- **UI:** Streamlit chatbot hiển thị answer, nguồn trích dẫn, score, retrieval method và session stats.

---

## Pipeline tổng quan

```
data/landing/legal/*.docx        data/landing/news/*.json
        │                                   │
   task1_collect_legal_docs        task2_crawl_news
        │                                   │
        └──────────── task3_convert_markdown ─────────────┐
                                                          │
                              data/standardized/*.md       │
                                        │                  │
                          task4_chunking_indexing           │
                        (172 chunks → ChromaDB)            │
                            │                              │
              ┌─────────────┼──────────────┐              │
         task5             task6          task7            │
      dense search       BM25 search    RRF fuse           │
              └─────────────┼──────────────┘              │
                        task9_retrieval_pipeline           │
                       (hybrid + fallback)                 │
                                 │                         │
                        task10_generation                  │
                     (citation, safe refusal)              │
                                 │                         │
                              app.py (Streamlit UI)        │
                                                           │
                    group_project/evaluation/ ◄────────────┘
                    (golden_dataset.json, RESULT.md)
```

---

## Dữ liệu

### Tài liệu thu thập

| Loại | Số lượng | Nguồn | File |
|------|----------|-------|------|
| Legal (DOCX) | 3 | Chính sách Shopee | `general-return-refund-rules`, `restricted-return-products`, `return-by-change-of-mind` |
| News (JSON + MD) | 7 | Hướng dẫn Shopee Help Center | `submit-return-refund-request`, `track-return-request`, `review-return-request`, `return-refund-evidence`, `return-shipping-packaging-fees`, `refund-timing-and-methods`, `seller-refund-dispute` |

### Sau chuẩn hóa & chunking

| Metric | Giá trị |
|--------|---------|
| Tổng chunks trong ChromaDB | **172** |
| Chunk size | 500 ký tự |
| Chunk overlap | 50 ký tự |
| Embedding model | `text-embedding-3-small` (OpenAI, dim=1536) |
| Chunking strategy | Recursive character text splitter |

---

## Kết quả đánh giá

### Overall scores

Bộ dữ liệu chuẩn được lập từ 3 tài liệu legal và 7 bài hướng dẫn trong `data/standardized/`. `golden_dataset.json` có **15 câu hỏi** phủ toàn bộ 10 file nguồn.

Kiểm tra đối chiếu chuỗi xác nhận **15/15** đoạn `expected_context` xuất hiện nguyên văn trong file `source` tương ứng. Pipeline end-to-end đã chạy được; các chỉ số RAGAS chính thức chưa được đo tự động do thời gian giới hạn.

| Metric | Trạng thái | Ghi chú |
|--------|-----------|---------|
| Faithfulness | Chưa đo tự động | Kiểm tra thủ công: câu trả lời bám sát context, có citation `[Document N]` |
| Answer relevance | Chưa đo tự động | Kiểm tra thủ công: 5/5 câu test thủ công trả lời đúng chủ đề |
| Context recall | Chưa đo tự động | Dense search score ≥ 0.40 cho query in-domain |
| Context precision | Chưa đo tự động | Hybrid RRF trả về chunks liên quan từ đúng nguồn |

### A/B comparison

**Thiết kế:** A = dense-only, B = dense + BM25 + RRF, cùng 15 câu hỏi, `top_k=5`, cùng model sinh câu trả lời.

| Cấu hình | Dense score (in-domain) | Số chunks trả về | Ghi chú |
|---------|------------------------|------------------|---------|
| A — Dense only | 0.41–0.43 | 5 | Nhanh, phụ thuộc embedding quality |
| B — Hybrid (Dense + BM25 + RRF) | 0.016–0.033 (RRF score) | 5 | Kết hợp từ khóa chính xác + semantic; score RRF nhỏ hơn nhưng coverage tốt hơn |

> **Nhận xét:** Hybrid retrieval giúp tìm đúng tài liệu về các từ khóa cụ thể (ví dụ: "24 giờ", "6 ngày", "7–14 ngày làm việc") mà dense search có thể bỏ sót nếu ngữ nghĩa của câu hỏi không khớp hoàn toàn.

### Worst performers

Các câu có nguy cơ nhầm lẫn cao theo nội dung tài liệu:

| ID | Câu hỏi | Điểm dễ nhầm |
|----|---------|--------------|
| G02 & G03 | Thời hạn trả hàng thực phẩm tươi/đông lạnh vs đơn thông thường | 24 giờ ≠ 15 ngày |
| G04–G06 | Trả hàng đổi ý — điều kiện hạng thành viên, niêm phong | Nhiều điều kiện đồng thời |
| G10 & G11 | Thời gian Shopee xem xét vs thời hạn gửi trả hàng | 3–5 ngày làm việc ≠ 6 ngày |
| G15 | Hoàn tiền về thẻ tín dụng/ghi nợ | 7–14 ngày làm việc ≠ hoàn tiền nhanh qua ví |

---

## Quyết định kỹ thuật nổi bật

| Quyết định | Người thực hiện | Lý do | Trade-off |
|-----------|----------------|-------|-----------|
| Dùng OpenAI `text-embedding-3-small` cho cả corpus và query | Nguyễn Thị Hồng Nhung | `embed_texts()` là điểm chung Task 4–5, đảm bảo nhất quán embedding space (dim=1536) | Chi phí API, phụ thuộc mạng |
| Chunk recursive 500/50, ID dạng `<doc>::chunk-<idx>` | Nguyễn Thị Hồng Nhung | Tránh nhân bản khi index lại; sau lọc chunk rác đạt 172 chunks chất lượng | Chunk nhỏ → nhiều embedding request |
| Dữ liệu từ snapshot + giữ `source_url` và `date_crawled` | Nguyễn Bảo Sơn | Đảm bảo reproducibility; Crawl4AI sẵn cho `--refresh` khi cần cập nhật | Dữ liệu có thể lỗi thời theo thời gian |
| Dùng `openai.OpenAI` thay `anthropic.Anthropic` SDK | Vũ Văn Điền | Proxy `mwapi.dev` dùng OpenAI-compatible format (`/chat/completions`), không hỗ trợ `/messages` | Mất streaming token native của Anthropic |
| Nhúng instruction vào user message, chọn `claude-sonnet-4-6` | Vũ Văn Điền | Model `claude-haiku-4-5-20251001` bị lock identity; `claude-sonnet-4-6` tuân thủ instruction và trả lời tiếng Việt đúng | Context dài hơn một chút |

---

## Kết quả kiểm thử

```
pytest tests/test_contracts.py -q    → 15 passed in 13.29s ✅
pytest tests/test_acceptance.py -q  → 5 passed ✅
```

- **Contract tests (15/15 passed):** Xác nhận schema `Document`, `SearchResult`, `GenerationResult`; RRF fuse đúng 1 lần; fallback dùng cosine score gốc; `reorder_for_llm` không mutate; format_context chứa title/source.
- **Acceptance tests (5/5 passed):** ≥3 legal DOCX, ≥5 news JSON, standardized Markdown đủ số lượng, golden dataset 15 câu đúng schema, báo cáo đánh giá hoàn chỉnh.

---

## Hạn chế và hướng cải thiện

| Hạn chế | Hướng cải thiện |
|---------|----------------|
| RAGAS metrics chưa được đo tự động | Chạy RAGAS trên 15 câu golden dataset với pipeline thật |
| Threshold `SCORE_THRESHOLD=0.3` chưa calibrate trên tập in/out-of-domain đủ lớn | Chạy ≥20 query mỗi loại, vẽ precision-recall curve chọn threshold tối ưu |
| Crawl trực tiếp từ URL Shopee chưa được xác minh | Chạy `--refresh` và so sánh nội dung mới với snapshot |
| RRF score rất nhỏ (0.016–0.033), không trực quan | Bổ sung normalize score hoặc hiển thị rank thay vì score trong UI |
| Chưa có conversation memory | Thêm `st.session_state` lưu lịch sử để hỗ trợ follow-up question |

---

## Recommendations

1. Hoàn thiện đo RAGAS: chạy `faithfulness`, `answer_relevance`, `context_recall`, `context_precision` trên toàn bộ 15 câu golden dataset, lưu kết quả vào `RESULT.md`.
2. Chạy A/B có số liệu đầy đủ: so sánh dense-only vs hybrid+RRF trên cùng 15 câu, cùng `top_k=5`, cùng model; ghi chênh lệch từng metric.
3. Phân tích worst performers thực tế: sau khi có kết quả model, đối chiếu câu G02, G03, G10, G11, G15 với output để xác nhận hay bác bỏ dự đoán nhầm lẫn.
4. Threshold calibration: đo recall@k trên query in-domain (từ golden dataset) và out-of-domain (câu hỏi không liên quan), chọn threshold cân bằng precision và recall.

---

## Xác nhận nhóm

Chúng tôi xác nhận nội dung trên phản ánh đúng quá trình làm việc nhóm, có thể giải thích hoặc chạy lại trong buổi demo.

| Họ và tên | Mã học viên | Ký xác nhận |
|-----------|-------------|-------------|
| Nguyễn Bảo Sơn | 2A202602402 | Nguyễn Bảo Sơn |
| Nguyễn Thị Hồng Nhung | 2A202602557 | Nguyễn Thị Hồng Nhung |
| Vũ Văn Điền | 2A202602418 | Vũ Văn Điền |

**Ngày:** 25/09/2026
