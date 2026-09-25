# Checklist hoàn thành bài RAG Pipeline

Ngày đối chiếu repository: 25/09/2026.

## 1. Trạng thái hiện tại

Quy ước:

- `[x]`: đã có bằng chứng trong repository.
- `[ ]`: chưa hoàn thành hoặc chưa có đủ bằng chứng để xác nhận.

### Đã có

- [x] Có cấu trúc mã nguồn cho Task 1–10, `app.py`, tài liệu hướng dẫn và test.
- [x] Có schema `Document`, `SearchResult`, `GenerationResult` và các hàm kiểm tra contract trong `src/contracts.py`.
- [x] Có `.env.example`; `.env` đã được loại khỏi Git bằng `.gitignore`.
- [x] Có nhánh cá nhân hiện tại `VinhDang-02587` và commit `9b8784a`.
- [x] Có công việc Task 10 trên nhánh `origin/feat/duc-generation-ui`, nhưng chưa được tích hợp vào nhánh hiện tại.

### Chưa hoàn thành hoặc chưa xác minh được

- [ ] Chưa có tài liệu thật trong `data/landing/legal/` và `data/landing/news/`.
- [ ] Chưa có Markdown trong `data/standardized/`.
- [ ] `group_project/evaluation/golden_dataset.json` đang rỗng.
- [ ] Task 1–10 trên nhánh hiện tại còn `TODO` hoặc `NotImplementedError`.
- [ ] `app.py` chưa gọi RAG pipeline và chưa hiển thị citation/source.
- [ ] Báo cáo `reports/RESULT.md` còn toàn bộ placeholder `TODO`.
- [ ] `acceptance tests` yêu cầu `group_project/evaluation/RESULT.md`, nhưng báo cáo mẫu hiện nằm ở `reports/RESULT.md`.
- [ ] Chưa chạy được test: máy không tìm thấy Python và `.venv` hiện tham chiếu tới một Python không còn tồn tại.
- [ ] Chưa có bằng chứng calibrate `SCORE_THRESHOLD`, đánh giá 4 metric hoặc A/B comparison.

## 2. Checklist nhóm

### A. Chốt phạm vi và phân công

- [ ] Chốt một chủ đề đủ hẹp để hoàn thành trong thời gian cho phép.
- [ ] Ghi tên chủ đề và phạm vi câu hỏi chatbot được phép trả lời vào `README.md`.
- [ ] Chọn tối thiểu 3 tài liệu chính sách/quy định và 5 bài viết/page từ nguồn công khai.
- [ ] Ưu tiên nguồn chính thức, có URL và ngày công bố; tránh dữ liệu cá nhân và nội dung không có quyền sử dụng.
- [ ] Chốt `LLM_PROVIDER`, `LLM_MODEL`, `EMBEDDING_PROVIDER` và `EMBEDDING_MODEL`.
- [ ] Chốt cách triển khai PageIndex fallback; xác định có `PAGEINDEX_API_KEY` hay không.
- [ ] Phân công mỗi đầu việc cho đúng một người chịu trách nhiệm chính.
- [ ] Mỗi thành viên làm trên nhánh riêng, commit nhỏ và ghi rõ file/test liên quan.

Bảng phân công cần điền:

| Hạng mục | Người chịu trách nhiệm | Người kiểm tra | Nhánh/PR | Trạng thái |
|---|---|---|---|---|
| Thu thập tài liệu chính sách | Chưa điền | Chưa điền | Chưa điền | Chưa làm |
| Crawl bài viết/page | Chưa điền | Chưa điền | Chưa điền | Chưa làm |
| Chuẩn hóa Markdown | Chưa điền | Chưa điền | Chưa điền | Chưa làm |
| Chunking, embedding, ChromaDB | Chưa điền | Chưa điền | Chưa điền | Chưa làm |
| Dense search và BM25 | Chưa điền | Chưa điền | Chưa điền | Chưa làm |
| RRF, retrieval pipeline, fallback | Chưa điền | Chưa điền | Chưa điền | Chưa làm |
| Generation và citation | Chưa điền | Chưa điền | `feat/duc-generation-ui` cần review | Đang tách nhánh |
| Streamlit UI | Chưa điền | Chưa điền | Chưa điền | Chưa làm |
| Golden dataset và evaluation | Chưa điền | Chưa điền | Chưa điền | Chưa làm |
| README, demo và kiểm tra cuối | Chưa điền | Chưa điền | Chưa điền | Chưa làm |

### B. Khôi phục môi trường chạy

- [ ] Xóa và tạo lại `.venv` sau khi xác nhận máy đã cài Python 3.10–3.13.
- [ ] Kích hoạt `.venv` và chạy `python --version` thành công.
- [ ] Cài package bằng `python -m pip install -e ".[dev]"`.
- [ ] Cài Chromium bằng `python -m playwright install chromium` nếu dùng Crawl4AI.
- [ ] Điền `.env` trên máy cá nhân; không commit API key.
- [ ] Chạy `python -m pytest tests/test_contracts.py -q` để lấy mốc lỗi ban đầu.

Tiêu chí hoàn thành: một thành viên mới clone repository có thể làm theo `README.md` để tạo môi trường mà không cần hướng dẫn miệng.

### C. Thu thập và chuẩn hóa dữ liệu

- [ ] Hoàn thiện `src/task1_collect_legal_docs.py` hoặc ghi rõ quy trình tải thủ công có thể lặp lại.
- [ ] Lưu ít nhất 3 file `.pdf`, `.doc` hoặc `.docx` vào `data/landing/legal/`; mỗi file lớn hơn 1 KB.
- [ ] Điền ít nhất 5 URL công khai vào `ARTICLE_URLS`.
- [ ] Hoàn thiện `crawl_article()` và xử lý lỗi từng URL mà không dừng toàn bộ lượt crawl.
- [ ] Tạo ít nhất 5 file JSON trong `data/landing/news/`.
- [ ] Mỗi JSON có đủ `url`, `title`, `date_crawled`, `content_markdown` và mọi giá trị đều không rỗng.
- [ ] Hoàn thiện `convert_legal_docs()` và `convert_news_articles()`.
- [ ] Tạo ít nhất 3 Markdown trong `data/standardized/legal/` và 5 Markdown trong `data/standardized/news/`.
- [ ] Mỗi Markdown có ít nhất 200 ký tự, đúng UTF-8 và giữ được title/source/URL.
- [ ] Chạy chuẩn hóa lần hai để xác nhận không tạo file trùng hoặc file rỗng.

Tiêu chí hoàn thành: ba test corpus đầu tiên trong `tests/test_acceptance.py` đều pass.

### D. Chunking, embedding và ChromaDB

- [ ] Hoàn thiện `load_documents()` theo đúng `Document` contract.
- [ ] Metadata có đủ `source`, `title`, `doc_type`, `url`; `id` ổn định qua các lần chạy.
- [ ] Hoàn thiện `chunk_documents()`; chunk không rỗng, `id` duy nhất và có `chunk_index` liên tục.
- [ ] Ghi rõ lý do chọn `CHUNK_SIZE=500`, `CHUNK_OVERLAP=50` hoặc cập nhật thông số sau thử nghiệm.
- [ ] Hoàn thiện `embed_texts()` theo provider đã chọn.
- [ ] Xác nhận Task 4 và Task 5 dùng chung `embed_texts()`, embedding model và dimension.
- [ ] Hoàn thiện `get_collection()` với cosine distance.
- [ ] Hoàn thiện `embed_chunks()` và `index_to_vectorstore()` bằng upsert.
- [ ] Chạy indexing hai lần và xác nhận ChromaDB không tăng bản ghi trùng.

Tiêu chí hoàn thành: `test_chunk_documents_preserves_identity_and_metadata` pass và có thể query collection sau khi indexing.

### E. Hybrid retrieval và fallback

- [ ] Hoàn thiện `semantic_search()`; đổi cosine distance thành similarity đúng cách.
- [ ] Kết quả dense không trùng ID, không vượt `top_k`, sort score giảm dần và có `retrieval_method="dense"`.
- [ ] Nạp đúng cùng corpus chunks vào `CORPUS` cho BM25.
- [ ] Hoàn thiện `build_bm25_index()` và `lexical_search()`.
- [ ] Kết quả BM25 tuân theo `SearchResult` và có `retrieval_method="bm25"`.
- [ ] Hoàn thiện `rerank_rrf()` theo `sum(1 / (k + rank))`, với rank bắt đầu từ 1.
- [ ] Deduplicate theo `id`, chỉ fuse một lần và gắn `retrieval_method="hybrid"`.
- [ ] Hoàn thiện upload/cache document ID và `pageindex_search()`.
- [ ] PageIndex lỗi hoặc timeout không được làm pipeline hay UI crash.
- [ ] Hoàn thiện `retrieve()`; fallback phải so sánh với cosine score gốc tốt nhất từ dense search, không dùng RRF score.
- [ ] Khi PageIndex lỗi hoặc không có kết quả, trả hybrid results; nếu không có evidence, để generation safe refusal.
- [ ] Calibrate `SCORE_THRESHOLD` bằng cả query in-domain và out-of-domain; ghi lại bộ query, score và quyết định threshold.

Tiêu chí hoàn thành: toàn bộ test liên quan Task 5–9 trong `tests/test_contracts.py` pass.

### F. Generation có citation

- [ ] Review hai commit `fb66ca7` và `5c171c1` trên `origin/feat/duc-generation-ui` trước khi merge/cherry-pick.
- [ ] Hoàn thiện `reorder_for_llm()` nhưng không thay đổi đầu vào và không làm mất ID.
- [ ] `format_context()` luôn chứa title và source của từng chunk.
- [ ] `call_llm()` dispatch đúng theo `LLM_PROVIDER`: OpenAI, Gemini hoặc Anthropic.
- [ ] Prompt yêu cầu chỉ trả lời từ context và gắn citation có thể đối chiếu với `sources`.
- [ ] `generate_with_citation()` trả đúng `GenerationResult`.
- [ ] Khi không có evidence hoặc provider lỗi, trả safe refusal thay vì bịa câu trả lời.
- [ ] Kiểm tra citation vẫn trỏ đúng source sau khi reorder chunks.

Tiêu chí hoàn thành: test Task 10 pass; với một câu hỏi đúng domain, từng citation có thể đối chiếu đến một phần tử trong `sources`.

### G. Streamlit UI

- [ ] Thay title/caption theo chủ đề của nhóm.
- [ ] Gọi `generate_with_citation(query, top_k)` thay cho câu trả lời placeholder.
- [ ] Lưu cả answer, sources và retrieval source vào `st.session_state`.
- [ ] Hiển thị answer, citation, title/source, retrieval method và score.
- [ ] Hiển thị lỗi thân thiện khi provider không sẵn sàng; ứng dụng không crash.
- [ ] Thử một query đúng domain, một query ngoài domain và một follow-up nếu làm bonus memory.

Tiêu chí hoàn thành: `streamlit run app.py` chạy end-to-end và người demo có thể mở nguồn từ câu trả lời.

### H. Golden dataset và evaluation

- [ ] Điền `group_project/evaluation/golden_dataset.json` thành JSON hợp lệ.
- [ ] Có ít nhất 15 phần tử; mỗi phần tử có `question`, `expected_answer`, `expected_context` không rỗng.
- [ ] Mỗi câu hỏi được tạo từ corpus thật và có thể truy ngược về tài liệu nguồn.
- [ ] Cố định cùng golden dataset, generator, evaluator, prompt và `top_k` cho hai cấu hình.
- [ ] Chạy Config A: dense-only.
- [ ] Chạy Config B: hybrid + RRF.
- [ ] Tính đủ faithfulness, answer relevance, context recall và context precision.
- [ ] Ghi model, phiên bản framework, commit corpus, threshold và ngày chạy.
- [ ] Phân tích ít nhất 3 trường hợp kém nhất theo failure stage và root cause.
- [ ] Đề xuất ít nhất 3 cải tiến có evidence và cách kiểm chứng.
- [ ] Ghi latency/cost hoặc nêu rõ cách đo nếu chưa đủ dữ liệu.

Tiêu chí hoàn thành: báo cáo không còn `TODO`, có số liệu A/B tái lập được và giải thích được vì sao một cấu hình tốt hơn.

### I. Báo cáo, test và nộp bài

- [ ] Thống nhất vị trí báo cáo đánh giá. Ưu tiên tạo `group_project/evaluation/RESULT.md` vì `tests/test_acceptance.py` kiểm tra đúng đường dẫn này.
- [ ] Nếu vẫn giữ `reports/RESULT.md`, đồng bộ nội dung sang đường dẫn mà test yêu cầu.
- [ ] Cập nhật `README.md` với chủ đề, nguồn dữ liệu, cách cấu hình, cách chạy pipeline, cách chạy UI và cách chạy evaluation.
- [ ] Mỗi thành viên có `reports/<student-id>-<short-name>.md` và không còn placeholder.
- [ ] Chạy `python -m pytest tests/test_contracts.py -q`.
- [ ] Chạy `python -m pytest tests/test_acceptance.py -q`.
- [ ] Chạy `python -m pytest -q` và lưu kết quả làm bằng chứng.
- [ ] Chạy `rg -n "TODO|NotImplementedError" src app.py reports group_project` và xử lý mọi kết quả thuộc sản phẩm nộp.
- [ ] Kiểm tra `git status`, không commit `.env`, API key, cache, `chroma_db` tạm hoặc dữ liệu nhạy cảm.
- [ ] Merge các nhánh, xử lý conflict, rồi chạy lại toàn bộ test trên nhánh nộp cuối.
- [ ] Chuẩn bị demo: query đúng domain, query ngoài domain, citation/source và kết quả A/B.
- [ ] Push repository và xác nhận commit cuối có thể clone/chạy lại.

## 3. Checklist cá nhân cho mỗi thành viên

Mỗi thành viên copy phần này vào issue cá nhân hoặc dùng để hoàn thiện báo cáo.

### Trước khi làm

- [ ] Ghi họ tên, mã học viên, nhóm và nhánh cá nhân.
- [ ] Nhận một đầu việc có đầu ra và tiêu chí hoàn thành rõ ràng.
- [ ] Xác định các file mình sở hữu; tránh hai người sửa cùng một file mà chưa thống nhất.
- [ ] Đồng bộ nhánh mới nhất trước khi bắt đầu.
- [ ] Ghi mốc test ban đầu của phần mình phụ trách.

### Trong khi làm

- [ ] Hoàn thiện code, dữ liệu hoặc báo cáo đúng contract chung.
- [ ] Không đổi public function signature nếu chưa thống nhất với nhóm.
- [ ] Thêm hoặc cập nhật test cho tình huống chính và ít nhất một tình huống lỗi.
- [ ] Chạy test liên quan trực tiếp sau mỗi thay đổi lớn.
- [ ] Commit theo từng thay đổi có thể kiểm tra; message mô tả kết quả, không chỉ mô tả thao tác.
- [ ] Ghi lại file, commit/PR, test và kết quả để làm bằng chứng đóng góp.
- [ ] Báo sớm dependency hoặc interface thay đổi cho các thành viên liên quan.

### Trước khi bàn giao

- [ ] Tự review diff, xóa debug code và placeholder do mình tạo.
- [ ] Kiểm tra không lộ API key, dữ liệu cá nhân hoặc file cache.
- [ ] Chạy test của module và test contract liên quan.
- [ ] Mở PR hoặc cung cấp commit rõ ràng để người khác review.
- [ ] Mô tả cách chạy lại phần việc và dữ liệu đầu vào cần thiết.
- [ ] Sửa lỗi sau review và xác nhận phần việc đã được tích hợp vào nhánh nộp.

### Báo cáo cá nhân

- [ ] Copy `reports/INDIVIDUAL_REPORT.md` thành `reports/<student-id>-<short-name>.md`.
- [ ] Chỉ kê khai phần trực tiếp thực hiện, có file/commit/PR/test/evaluation đối chiếu được.
- [ ] Mô tả tối đa hai quyết định kỹ thuật quan trọng, kèm evidence và trade-off.
- [ ] Nêu test hoặc query đã dùng và kết quả trước/sau nếu có.
- [ ] Nêu lỗi đã phát hiện và cách xử lý.
- [ ] Nêu một hạn chế cụ thể và cải tiến ưu tiên nếu có thêm thời gian.
- [ ] Điền ngày và tên xác nhận; bảo đảm có thể giải thích hoặc chạy lại trong demo.

### Việc cần bổ sung cho nhánh cá nhân hiện tại

- [x] Có nhánh `VinhDang-02587`.
- [x] Có commit `9b8784a` thay đổi dependency trong `pyproject.toml`.
- [ ] Ghi rõ lý do kỹ thuật và ảnh hưởng của việc bỏ dependency trong báo cáo cá nhân.
- [ ] Bổ sung đầu việc tạo giá trị trực tiếp cho deliverable của nhóm; một commit dependency chưa đủ bằng chứng cho phần đóng góp cá nhân.
- [ ] Chọn module cụ thể, hoàn thành code/test và tạo thêm commit có thể kiểm chứng.
- [ ] Tạo báo cáo đúng tên `reports/<student-id>-<short-name>.md`.

## 4. Thứ tự ưu tiên để về đích

1. Sửa môi trường Python và chạy được test.
2. Chốt chủ đề, nguồn dữ liệu, provider và phân công.
3. Hoàn thành dữ liệu landing/standardized.
4. Hoàn thành Task 4–7 để có hybrid retrieval.
5. Hoàn thành Task 8–10 và tích hợp nhánh generation.
6. Hoàn thành Streamlit UI.
7. Tạo golden dataset, chạy A/B evaluation và hoàn thiện báo cáo.
8. Chạy toàn bộ test, hoàn thiện báo cáo cá nhân và demo.

## 5. Thông tin nhóm cần điền để checklist thành kế hoạch cụ thể

- Chủ đề và phạm vi chatbot.
- Danh sách thành viên, mã học viên và nhánh của từng người.
- Thời hạn nộp và thời lượng còn lại.
- LLM provider/model, embedding provider/model và API key nào nhóm có thể dùng.
- Người sở hữu từng Task 1–10, UI và evaluation.

