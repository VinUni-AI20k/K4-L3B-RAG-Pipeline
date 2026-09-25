# Tóm tắt yêu cầu và checklist dự án RAG

Tài liệu này tổng hợp các yêu cầu quan trọng từ `README.md` và thư mục `docs/`, đồng thời sắp xếp công việc theo thứ tự triển khai.

## 1. Mục tiêu

Xây dựng chatbot RAG trả lời câu hỏi dựa trên bộ tài liệu do nhóm tự thu thập. Hệ thống cần hỗ trợ hybrid retrieval, fallback, citation, giao diện Streamlit và báo cáo đánh giá.

Pipeline tổng thể:

```text
Thu thập dữ liệu
→ Chuẩn hóa Markdown
→ Chunking
→ Embedding và ChromaDB
→ Dense search + BM25
→ RRF
→ Fallback
→ Generation có citation
→ Streamlit
→ Evaluation
```

### Đề tài đã chọn

| Đề tài | Nội dung |
| --- | --- |
| **IELTS Writing** | Band descriptors, tiêu chí chấm điểm và bài viết mẫu |

## 2. Sản phẩm bắt buộc

- [ ] Repository có thể cài đặt và chạy lại được.
- [ ] Có tối thiểu 3 tài liệu chính sách/quy định dạng PDF, DOC hoặc DOCX.
- [ ] Có tối thiểu 5 bài viết/page công khai dạng JSON.
- [ ] Dữ liệu được chuẩn hóa sang Markdown.
- [ ] Có chunking, embedding và persistent vector database.
- [ ] Có dense search và BM25 trên cùng corpus chunks.
- [ ] Có RRF để hợp nhất hai bảng xếp hạng.
- [ ] Có fallback dựa trên cosine score gốc của dense retrieval.
- [ ] Câu trả lời có citation hoặc safe refusal khi không đủ bằng chứng.
- [ ] Chatbot Streamlit hiển thị câu trả lời và nguồn đã sử dụng.
- [ ] Golden dataset có ít nhất 15 câu hỏi.
- [ ] Có đánh giá 4 metric và so sánh A/B.
- [ ] Có báo cáo kết quả evaluation.
- [ ] Mỗi thành viên có báo cáo đóng góp cá nhân.

## 3. Contract kỹ thuật bắt buộc

### Document và chunk

- `id` phải duy nhất và ổn định.
- `content` không được rỗng.
- Metadata phải giữ được `source`, `title`, `doc_type` và `url`.
- Mỗi chunk phải có `chunk_index` không âm.
- Re-index không được tạo dữ liệu trùng.

### Search result

- Kết quả phải đúng schema `SearchResult`.
- Không được có ID trùng nhau.
- Không vượt quá `top_k`.
- Phải sắp xếp theo score giảm dần.
- `retrieval_method` phải là `dense`, `bm25`, `hybrid` hoặc `pageindex`.

### Retrieval pipeline

- Task 4 và Task 5 phải dùng chung embedding model, dimension và hàm `embed_texts()`.
- RRF dùng công thức `sum(1 / (k + rank))`, trong đó rank bắt đầu từ 1.
- RRF chỉ được chạy một lần trong pipeline.
- Fallback phải so sánh threshold với dense cosine score gốc, không dùng RRF score.
- Lỗi từ PageIndex/provider không được làm giao diện crash.
- Khi fallback lỗi, pipeline cần trả hybrid result nếu vẫn còn kết quả phù hợp.

### Generation

- Reorder chunks không được làm mất hoặc thay đổi ID.
- Context phải chứa title và source để kiểm chứng citation.
- Citation phải đối chiếu được với phần tử trong `sources`.
- Khi không đủ bằng chứng, hệ thống phải trả safe refusal.
- Output phải đúng schema `GenerationResult`.

### Bảo mật và kiểm thử

- Không hard-code hoặc commit API key.
- Không commit file `.env`.
- Contract tests không được gọi network hoặc API thật.

## 4. Checklist triển khai theo từng bước

### Bước 1 — Chọn đề tài và phân công

- [x] Chọn đề tài **IELTS Writing**: band descriptors, tiêu chí chấm điểm và bài viết mẫu.
- [ ] Xác định loại câu hỏi chatbot cần trả lời.
- [ ] Chốt tối thiểu 3 tài liệu chính sách và 5 bài viết.
- [ ] Phân công module cho từng thành viên.
- [ ] Mỗi thành viên ghi lại commit, PR và file mình phụ trách.

### Bước 2 — Chuẩn hóa cấu trúc repository

- [ ] Tạo `data/landing/legal/`.
- [ ] Tạo `data/landing/news/`.
- [ ] Tạo `data/standardized/legal/`.
- [ ] Tạo `data/standardized/news/`.
- [ ] Đặt evaluation report tại `group_project/evaluation/RESULT.md` để khớp acceptance test.
- [ ] Đồng bộ đường dẫn báo cáo cá nhân trong README với thư mục thực tế.
- [ ] Kiểm tra `.gitignore` loại trừ `.env`, cache và index sinh tự động.

### Bước 3 — Cài đặt môi trường

- [ ] Tạo và kích hoạt `.venv`.
- [ ] Chạy `python -m pip install -e ".[dev]"`.
- [ ] Chạy `python -m playwright install chromium`.
- [ ] Copy `.env.example` thành `.env`.
- [ ] Chọn embedding provider/model.
- [ ] Chọn LLM provider/model.

### Bước 4 — Thu thập dữ liệu: Task 1 và Task 2

- [ ] Hoàn thiện `download_documents()`.
- [ ] Lưu ít nhất 3 PDF/DOC/DOCX vào `data/landing/legal/`.
- [ ] Đảm bảo mỗi tài liệu lớn hơn 1 KB.
- [ ] Thêm ít nhất 5 URL bài viết công khai.
- [ ] Hoàn thiện `crawl_article()`.
- [ ] Lưu bài viết vào `data/landing/news/`.
- [ ] Mỗi JSON có `url`, `title`, `date_crawled` và `content_markdown`.

### Bước 5 — Chuẩn hóa Markdown: Task 3

- [ ] Convert toàn bộ tài liệu legal sang Markdown.
- [ ] Convert toàn bộ JSON bài viết sang Markdown.
- [ ] Loại bỏ menu, footer và nội dung rác.
- [ ] Giữ lại title, source, URL và `doc_type`.
- [ ] Đảm bảo mỗi file chuẩn hóa có ít nhất 200 ký tự.
- [ ] Kiểm tra đủ ít nhất 3 legal và 5 news Markdown.

### Bước 6 — Chunk, embedding và index: Task 4

- [ ] Hoàn thiện `load_documents()`.
- [ ] Sinh document ID ổn định.
- [ ] Hoàn thiện `chunk_documents()`.
- [ ] Sinh chunk ID duy nhất và `chunk_index` liên tục.
- [ ] Hoàn thiện `embed_texts()` theo provider trong `.env`.
- [ ] Hoàn thiện `embed_chunks()`.
- [ ] Tạo hoặc mở persistent Chroma collection.
- [ ] Upsert dữ liệu để re-index không bị trùng.
- [ ] Chạy contract tests liên quan đến Task 4.

### Bước 7 — Hybrid retrieval: Task 5, Task 6 và Task 7

- [ ] Hoàn thiện `semantic_search()`.
- [ ] Chuyển Chroma distance thành similarity score đúng cách.
- [ ] Hoàn thiện BM25 trên cùng corpus chunks.
- [ ] Chọn cách tokenize phù hợp với dữ liệu tiếng Việt.
- [ ] Hoàn thiện `lexical_search()`.
- [ ] Hoàn thiện `rerank_rrf()` đúng công thức.
- [ ] Deduplicate kết quả theo chunk ID.
- [ ] Đặt `retrieval_method="hybrid"` cho kết quả RRF.

### Bước 8 — Fallback và retrieval pipeline: Task 8 và Task 9

- [ ] Hoàn thiện `pageindex_search()` hoặc provider fallback đã chọn.
- [ ] Đảm bảo fallback trả đúng schema `SearchResult`.
- [ ] Gọi dense search và BM25 trên cùng query.
- [ ] Chỉ gọi RRF một lần.
- [ ] Dùng dense score gốc để quyết định fallback.
- [ ] Hiệu chỉnh threshold bằng query in-domain và out-of-domain.
- [ ] Bắt exception của provider fallback.
- [ ] Trả hybrid result hoặc kết quả rỗng an toàn khi fallback lỗi.

### Bước 9 — Generation và citation: Task 10

- [ ] Hoàn thiện `reorder_for_llm()` mà không mutate input.
- [ ] Hoàn thiện `format_context()` với title, source và chunk ID.
- [ ] Dispatch LLM theo `LLM_PROVIDER`.
- [ ] Prompt yêu cầu chỉ trả lời dựa trên context.
- [ ] Citation map chính xác về `sources`.
- [ ] Trả safe refusal khi không có đủ evidence.
- [ ] Trả đúng `GenerationResult`.

### Bước 10 — Chatbot Streamlit

- [ ] Kết nối UI với `generate_with_citation()`.
- [ ] Lưu lịch sử chat trong session state.
- [ ] Hiển thị answer.
- [ ] Hiển thị source, title và URL.
- [ ] Hiển thị retrieval method và score.
- [ ] Hiển thị loading và xử lý exception thân thiện.
- [ ] Kiểm tra query đúng domain, ngoài domain và provider lỗi.

### Bước 11 — Golden dataset và evaluation

- [ ] Viết ít nhất 15 case có `question`, `expected_answer` và `expected_context`.
- [ ] Đảm bảo từng case dựa trên corpus thật.
- [ ] Tạo Config A: dense-only.
- [ ] Tạo Config B: hybrid + RRF.
- [ ] Hai config dùng chung dataset, generator, evaluator, prompt và `top_k`.
- [ ] Đánh giá faithfulness.
- [ ] Đánh giá answer relevance.
- [ ] Đánh giá context recall.
- [ ] Đánh giá context precision.
- [ ] So sánh metric, latency và cost giữa hai config.
- [ ] Phân tích ít nhất 3 case có kết quả thấp nhất.
- [ ] Phân loại nguyên nhân lỗi: data, retrieval hoặc generation.
- [ ] Điền đầy đủ `group_project/evaluation/RESULT.md` và xóa mọi placeholder.

### Bước 12 — Kiểm thử và nộp bài

- [ ] Chạy `pytest tests/test_contracts.py -q`.
- [ ] Chạy `pytest tests/test_acceptance.py -q`.
- [ ] Chạy toàn bộ `pytest -q`.
- [ ] Hoàn thiện báo cáo cá nhân của từng thành viên.
- [ ] Cập nhật README với hướng dẫn chạy lại từ đầu.
- [ ] Kiểm tra repository không chứa `.env`, API key hoặc cache.
- [ ] Demo một query đúng domain.
- [ ] Demo một query ngoài domain và safe refusal.
- [ ] Demo citation và nguồn.
- [ ] Demo kết quả A/B và fallback.

## 5. Rubric và thứ tự ưu tiên

| Hạng mục | Điểm |
| --- | ---: |
| Dữ liệu có nguồn rõ ràng và được chuẩn hóa | 10 |
| Chunking, embedding và vector database | 10 |
| Dense search, BM25 và RRF | 20 |
| Retrieval pipeline và fallback | 10 |
| Generation có citation và safe refusal | 15 |
| Chatbot end-to-end và hiển thị nguồn | 10 |
| Golden dataset, 4 metrics, A/B và phân tích lỗi | 10 |
| README, khả năng chạy lại và báo cáo cá nhân | 5 |
| **Tổng** | **90** |

Thứ tự ưu tiên đề xuất:

1. Dense search, BM25 và RRF.
2. Generation có citation và safe refusal.
3. Dữ liệu, chunking, embedding và vector database.
4. Retrieval pipeline và fallback.
5. Golden dataset và evaluation.
6. Streamlit UI.
7. README và báo cáo cá nhân.

## 6. Bonus

Chỉ thực hiện sau khi các yêu cầu chính đã chạy ổn định và có kết quả đánh giá.

- [ ] HyDE hoặc query expansion có A/B chứng minh cải thiện: tối đa +3.
- [ ] Reranker nâng cao có so sánh với RRF: tối đa +3.
- [ ] Conversation memory cho follow-up question: tối đa +2.
- [ ] Deploy online hoặc UI source highlighting: tối đa +2.

## 7. Definition of Done

Dự án được coi là hoàn thành khi:

- [ ] Pipeline chạy end-to-end từ dữ liệu thô đến câu trả lời.
- [ ] Citation truy ngược được về đúng nguồn.
- [ ] Query ngoài domain được từ chối an toàn.
- [ ] Re-index không tạo chunk trùng.
- [ ] Contract tests và acceptance tests đều pass.
- [ ] Golden dataset có ít nhất 15 case hợp lệ.
- [ ] Báo cáo có đủ 4 metric và kết quả A/B.
- [ ] Không còn `TODO`, placeholder hoặc `NotImplementedError` trong phần cần nộp.
- [ ] Không có secret trong Git.
- [ ] Mỗi thành viên có bằng chứng đóng góp và báo cáo cá nhân.
