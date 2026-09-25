# Phân công nhóm — Chatbot RAG Du lịch Việt Nam

Thành viên: **Vinh, Cường, Hình, Đức**.

## 1. Đề tài và phạm vi

**Tên đề tài: Trợ lý hỏi đáp Du lịch Việt Nam có trích dẫn nguồn.**

Chatbot trả lời bằng tiếng Việt về điểm đến, văn hóa, ẩm thực, di chuyển và quy định du lịch dựa trên tài liệu nhóm thu thập. Mỗi câu trả lời phải đối chiếu được với nguồn; khi tài liệu không đủ thì thông báo chưa đủ thông tin.

Đề xuất bản demo tập trung vào **Huế – Đà Nẵng – Hội An** để bộ dữ liệu nhỏ vẫn đủ chiều sâu. Đây là phạm vi triển khai đề xuất trong đề tài Du lịch Việt Nam, có thể mở rộng sau khi pipeline chạy đầy đủ.

Ví dụ câu hỏi dự kiến, chỉ đưa vào bộ đánh giá khi corpus có bằng chứng:

- Tài liệu giới thiệu những điểm tham quan nào ở Hội An?
- Những món ăn nào được giới thiệu trong bài viết về Đà Nẵng?
- Nội quy tham quan được tài liệu của điểm đến quy định như thế nào?
- Dựa trên các nguồn đã thu thập, có thể kết hợp những điểm nào trong một ngày tham quan Huế?

Thông tin biến động như giá vé, giờ mở cửa hoặc lịch hoạt động phải gắn với thời điểm của nguồn; không mặc định dữ liệu đã thu thập là thông tin thời gian thực.

## 2. Hiện trạng repo và yêu cầu phải đạt

Đã đối chiếu [README](../README.md), [hướng dẫn triển khai](STEP_BY_STEP.md), [module contracts](MODULE_CONTRACTS.md), [rubric](GRADING_RUBRIC.md), các module và bộ test.

- Repo là bộ khung bài tập: các hàm nghiệp vụ chính của Task 1–10 chưa triển khai; `app.py` còn placeholder.
- `src/contracts.py` đã có schema và validator để các thành viên dùng chung.
- `group_project/evaluation/golden_dataset.json` hiện rỗng; chưa có script chạy evaluation.
- Sản phẩm phải có: dữ liệu → Markdown → chunks → embeddings/ChromaDB → dense + BM25 → RRF → fallback → generation có citation → Streamlit.
- Đầu ra tối thiểu: **3 tài liệu chính sách, 5 bài viết/page, 15 golden Q&A, 4 metrics, so sánh A/B, báo cáo nhóm và 4 báo cáo cá nhân**.
- RRF thuộc phần bắt buộc. Reranker nâng cao như Jina/BGE là phần bổ sung, thực hiện sau khi hoàn thành yêu cầu chính.

## 3. Phân công chính

| Thành viên | Vai trò | File phụ trách | Đầu ra bàn giao |
| --- | --- | --- | --- |
| **Vinh** | Thu thập, chuẩn hóa dữ liệu; quản lý golden dataset và báo cáo kết quả | `src/task1_collect_legal_docs.py`, `src/task2_crawl_news.py`, `src/task3_convert_markdown.py`; `data/`; `group_project/evaluation/golden_dataset.json`, `group_project/evaluation/RESULT.md` | Corpus có nguồn rõ ràng, Markdown và metadata; bộ câu hỏi có đáp án/bằng chứng; báo cáo dựa trên số liệu Hình chạy |
| **Cường** | Chunking, embedding, ChromaDB, dense search và BM25 | `src/task4_chunking_indexing.py`, `src/task5_semantic_search.py`, `src/task6_lexical_search.py`; đầu mối `pyproject.toml`, `.env.example` | Corpus chunks dùng chung, index bền vững, hai hàm tìm kiếm đúng `SearchResult`, môi trường chạy thống nhất |
| **Hình** | RRF, PageIndex fallback, retrieval pipeline và chương trình đánh giá | `src/task7_reranking.py`, `src/task8_pageindex_vectorless.py`, `src/task9_retrieval_pipeline.py`; đề xuất tạo mới `scripts/evaluate.py` | `retrieve()` hoạt động; ngưỡng fallback có bằng chứng hiệu chỉnh; số liệu 4 metrics cho A/B và các câu trả lời truy xuất được |
| **Đức** | Generation có citation, giao diện Streamlit, tích hợp và demo | `src/task10_generation.py`, `app.py`, `README.md` | Chatbot end-to-end, câu trả lời có nguồn, xử lý thiếu bằng chứng/lỗi provider; README chạy lại được và kịch bản demo |

### Vinh — dữ liệu và bằng chứng

1. Chọn ít nhất 3 tài liệu chính sách/quy định liên quan đến du lịch, hoạt động tham quan hoặc ứng xử tại điểm đến. Xác minh nguồn và phiên bản khi thu thập.
2. Thu thập ít nhất 5 bài/page: gợi ý gồm điểm đến Huế, điểm đến Đà Nẵng, điểm đến Hội An, ẩm thực và hướng dẫn di chuyển/tham quan. Ưu tiên tài liệu của cơ quan du lịch hoặc đơn vị quản lý điểm đến.
3. Hoàn thiện tải tài liệu, crawl bài viết và chuyển Markdown; loại nội dung điều hướng không liên quan, giữ tiêu đề và nguồn.
4. Bàn giao sớm 1 tài liệu chính sách và 1 bài viết đã chuẩn hóa để Cường chạy thử. Chốt cách lưu metadata cùng Cường trước khi làm hàng loạt.
5. Tổng hợp 16 golden Q&A từ đóng góp của cả nhóm; kiểm tra đáp án và đoạn bằng chứng thực sự tồn tại trong corpus.
6. Điền báo cáo nhóm từ kết quả evaluation của Hình và phân tích lỗi của từng người.

**Nghiệm thu:** `data/landing/legal/` có ≥3 PDF/DOC/DOCX, mỗi file >1.024 byte; `data/landing/news/` có ≥5 JSON chứa `url`, `title`, `date_crawled`, `content_markdown`. `data/standardized/legal/` và `data/standardized/news/` có tương ứng ≥3 và ≥5 Markdown, mỗi file ≥200 ký tự. Nội dung phải có giá trị sử dụng, không chỉ đủ kích thước.

### Cường — index và hai nhánh tìm kiếm

1. Hoàn thiện `load_documents()`, `chunk_documents()`, `embed_texts()`, `embed_chunks()`, `get_collection()`, `index_to_vectorstore()`.
2. Tạo ID chunk ổn định, giữ metadata nguồn và `chunk_index`; upsert lại không tạo bản ghi trùng.
3. Hoàn thiện `semantic_search()`, `build_bm25_index()` và `lexical_search()` trên cùng tập chunks và cùng ID.
4. Dùng chung hàm embedding, model và dimension giữa index và query. Ghi nhận lựa chọn chunk size/overlap và embedding trong báo cáo.
5. Chốt provider/dependencies cho nhóm. Nếu dùng `sentence_transformers` theo `.env.example`, kiểm tra và bổ sung dependency phù hợp vì `pyproject.toml` hiện chưa khai báo trực tiếp thư viện này.
6. Bàn giao hai hàm search và cách nạp lại corpus/index cho Hình; không để BM25 phụ thuộc vào biến `CORPUS` rỗng sau khi khởi động lại.

**Nghiệm thu:** tìm theo ngữ nghĩa và từ khóa/tên riêng đều trả đúng schema; kết quả không trùng ID, giảm dần theo score, không vượt `top_k`; index chạy lại không tăng số chunk do trùng dữ liệu.

### Hình — retrieval hoàn chỉnh và evaluation

1. Hoàn thiện `rerank_rrf()` với công thức `sum(1 / (k + rank))`, rank bắt đầu từ 1; gộp theo ID và chỉ fuse một lần.
2. Hoàn thiện `upload_documents()` và `pageindex_search()`; kết quả fallback có `retrieval_method="pageindex"`.
3. Hoàn thiện `retrieve()`: dense + BM25 → RRF; dùng **cosine score gốc của dense** để quyết định fallback.
4. Hiệu chỉnh threshold bằng tập câu hỏi đúng phạm vi và ngoài phạm vi; ghi rõ tập thử và quyết định, không mặc định giá trị mẫu `0.3` phù hợp mọi corpus.
5. Khi PageIndex lỗi hoặc không có kết quả, trả kết quả hybrid đã tính; chỉ trả rỗng khi không có kết quả truy xuất khả dụng để generation xử lý. Không làm giao diện crash.
6. Tạo chương trình evaluation có thể chạy lại, xuất kết quả từng câu và tổng hợp 4 metrics. Phối hợp Đức để dùng cùng logic generation cho hai cấu hình.

**Nghiệm thu:** kiểm chứng RRF chỉ chạy một lần, fallback không so với RRF score, lỗi fallback được xử lý; bàn giao kết quả A/B thực đo cho Vinh, kèm cấu hình và các trường hợp kém nhất.

### Đức — câu trả lời, giao diện và tích hợp

1. Hoàn thiện `reorder_for_llm()`, `format_context()`, `call_llm()` và `generate_with_citation()`.
2. Context có tiêu đề, nguồn và nhãn citation; reorder không làm mất ID hoặc khiến citation trỏ nhầm đoạn.
3. Dispatch provider theo cấu hình. Không đủ bằng chứng hoặc provider lỗi phải trả lời an toàn theo contract.
4. Đổi giao diện thành chatbot Du lịch Việt Nam, nối pipeline thật; hiển thị answer, nguồn/link, retrieval method và score.
5. Lưu cả câu trả lời và nguồn trong lịch sử hội thoại để nguồn vẫn hiển thị sau khi Streamlit chạy lại.
6. Cập nhật README về đề tài, dữ liệu, setup, cách chạy index/chatbot/evaluation; tích hợp các phần đã bàn giao và chuẩn bị demo.

**Nghiệm thu:** `streamlit run app.py` chạy được luồng hoàn chỉnh; citation map được về `sources`; câu hỏi thiếu dữ liệu không tạo thông tin không có bằng chứng; `GenerationResult` đúng schema.

## 4. Quy ước phối hợp

Luồng bàn giao: **Vinh → Cường → Hình → Đức**. Vinh nhận lại số liệu từ Hình để hoàn thiện báo cáo. Khi đang chờ đầu vào, mỗi người dùng fixture đúng contract để phát triển phần mình; tích hợp cuối phải chạy trên corpus thật.

| Điểm bàn giao | Nội dung thống nhất |
| --- | --- |
| Vinh → Cường | Markdown và metadata `source`, `title`, `doc_type`, `url`; thống nhất cách lưu/đọc metadata. Giữ `doc_type` là `legal` hoặc `news` theo contract hiện tại. |
| Cường → Hình | `semantic_search(query, top_k)` và `lexical_search(query, top_k)` trả `list[SearchResult]`; cùng corpus, ID và nguồn. |
| Hình → Đức | `retrieve(query, top_k, score_threshold, use_reranking)` trả danh sách kết quả hybrid/pageindex hoặc rỗng. |
| Đức → UI | `generate_with_citation(query, top_k)` trả `answer`, `sources`, `retrieval_source`; giá trị `retrieval_source` thuộc `hybrid`, `pageindex`, `none`. |
| Hình → Vinh | Cấu hình chạy, câu trả lời/context từng câu, 4 metrics cho A/B, lỗi và số liệu thực tế để viết `RESULT.md`. |

- Giữ interface trong [MODULE_CONTRACTS.md](MODULE_CONTRACTS.md); muốn đổi schema phải thống nhất với người nhận đầu ra trước.
- Mỗi người làm trên nhánh riêng, gợi ý: `feat/vinh-data`, `feat/cuong-index-search`, `feat/hinh-retrieval-eval`, `feat/duc-generation-ui`.
- Mỗi người kiểm tra module mình; Đức là đầu mối tích hợp. Các file chung như `src/contracts.py` và `tests/test_contracts.py` cần trao đổi trước khi cùng sửa.
- Contract tests dùng mock/fixture, không gọi API hoặc network thật. Không commit `.env`, API key hay cache.
- Mỗi người ghi lại commit/PR và bằng chứng kiểm tra để viết báo cáo cá nhân.

## 5. Golden dataset, A/B và báo cáo

**Bộ câu hỏi:** đặt mục tiêu 16 câu có bằng chứng, mỗi người đóng góp 4 câu để vượt yêu cầu tối thiểu 15. Vinh kiểm tra và tổng hợp vào `group_project/evaluation/golden_dataset.json`.

- Vinh: 4 câu về chính sách/nội quy có trong tài liệu.
- Cường: 4 câu về tên điểm đến, địa danh và thông tin cụ thể.
- Hình: 4 câu diễn đạt lại hoặc cần kết hợp nhiều đoạn nguồn.
- Đức: 4 câu về trải nghiệm/ẩm thực/gợi ý tham quan, có câu trả lời tham chiếu dựa trên corpus.

Mỗi phần tử phải có `question`, `expected_answer`, `expected_context`; đáp án và context không để rỗng. Chuẩn bị thêm ít nhất 3 tình huống ngoài phạm vi hoặc thiếu bằng chứng để thử fallback/từ chối, tách khỏi 16 câu có bằng chứng. Hiệu chỉnh threshold trước khi chạy đánh giá cuối; không sửa đáp án chuẩn để khớp câu trả lời của mô hình.

**Phép so sánh:** A = dense-only; B = dense + BM25 + RRF. Dùng cùng corpus, golden dataset, embedding, generator, evaluator, prompt và `top_k`. Để cô lập tác động retrieval, không bật fallback ở cả hai nhánh của phép A/B này; kiểm tra fallback riêng trong pipeline đầy đủ. Chỉ đặt `use_reranking=False` chưa chắc tạo baseline dense-only vì `retrieve()` vẫn có thể kích hoạt fallback.

**Bốn chỉ số:** faithfulness, answer relevance, context recall, context precision. Ghi số đo thực tế, chênh lệch B−A, các câu kém nhất, nguyên nhân và hướng cải thiện; không giả định hybrid luôn tốt hơn dense-only.

**Đường dẫn nộp bài:**

- Copy template [reports/RESULT.md](../reports/RESULT.md) để điền vào `group_project/evaluation/RESULT.md` — đây là đường dẫn acceptance test đọc. Giữ các mục `Overall scores`, `A/B comparison`, `Worst performers`, `Recommendations`; không còn `TODO`.
- Mỗi người dùng [reports/INDIVIDUAL_REPORT.md](../reports/INDIVIDUAL_REPORT.md), lưu thành `reports/<ma-hoc-vien>-<ten>.md` theo chỉ dẫn của template. Không tự điền mã học viên khi chưa có.
- README hiện trỏ tới đường dẫn individual report không tồn tại (`group_project/ịndividual/INDIVIDUAL_REPORT.md`); Đức sửa link khi cập nhật README để khớp nơi nhóm lưu báo cáo.

## 6. Thứ tự thực hiện theo buổi lab 3 giờ

Đây là lịch mục tiêu theo README, phụ thuộc tốc độ thu thập dữ liệu, cài môi trường và quyền truy cập provider.

| Thời gian | Mốc chung | Việc có thể làm song song |
| --- | --- | --- |
| 0–10 phút | Chốt phạm vi, schema và môi trường | Vinh chọn nguồn; Cường kiểm tra dependency/embedding; Hình đọc contract và chuẩn bị fixture; Đức dựng UI và cấu hình LLM. |
| 10–35 phút | Có ≥3 tài liệu, ≥5 bài và Markdown | Vinh bàn giao mẫu sớm; Cường viết index/search; Hình viết RRF/fallback; Đức viết generation/UI bằng fixture. |
| 35–65 phút | Index, dense và BM25 chạy được | Cường bàn giao hai hàm search; Vinh tổng hợp golden Q&A; Hình nối retrieval; Đức kiểm tra citation. |
| 65–90 phút | RRF và fallback chạy đầy đủ | Hình hiệu chỉnh threshold; Cường xử lý lỗi search; Vinh rà nguồn; Đức nối retrieval thật. |
| 90–120 phút | Chatbot end-to-end có citation | Đức chủ trì tích hợp; Hình hoàn thiện runner; Vinh chốt 16 Q&A; Cường kiểm tra khả năng chạy lại index. |
| 120–150 phút | Có 4 metrics và A/B | Hình chạy evaluation; Vinh điền báo cáo; Cường và Đức phân tích, sửa lỗi phần mình khi cần. |
| 150–180 phút | Kiểm tra, báo cáo cá nhân và demo | Cả nhóm kiểm tra bản cuối, ghi giới hạn còn lại; Đức hướng dẫn chạy/demo; từng người hoàn thiện báo cáo cá nhân. |

Nếu thay đổi corpus hoặc logic sau khi đo, phải cập nhật dữ liệu liên quan và chạy lại phép đánh giá bị ảnh hưởng trước khi chốt số liệu.

## 7. Checklist hoàn thành

- [ ] Đủ dữ liệu gốc và Markdown chuẩn hóa, có nguồn rõ ràng.
- [ ] Task 1–10 hoàn thiện, index lại không tạo chunk trùng.
- [ ] Dense + BM25 dùng cùng corpus; RRF một lần; fallback dùng dense cosine score.
- [ ] Chatbot hiển thị câu trả lời, citation, nguồn và thông tin retrieval.
- [ ] Thiếu bằng chứng hoặc lỗi provider không làm UI crash.
- [ ] Golden dataset ≥15 câu có đáp án và context; có số đo 4 metrics và A/B.
- [ ] `group_project/evaluation/RESULT.md` hoàn thiện; đủ 4 báo cáo cá nhân.
- [ ] Chạy `pytest tests/test_contracts.py -q`, `pytest tests/test_acceptance.py -q` và `pytest -q` khi triển khai xong.
- [ ] Demo được câu hỏi có bằng chứng, câu hỏi ngoài phạm vi và kết quả A/B.
- [ ] README hướng dẫn chạy lại chính xác; repository không chứa secrets/cache.

Tài liệu này là kế hoạch phân công; các ô nghiệm thu chưa được xác nhận và không đại diện cho tính năng đã triển khai.
