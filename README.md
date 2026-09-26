# Vietnamese Tourism RAG Pipeline

Chatbot RAG trả lời câu hỏi về du lịch Việt Nam từ 3 văn bản pháp luật và 5 bài cẩm nang công khai. Pipeline gồm chuẩn hóa dữ liệu, recursive chunking, multilingual sentence-transformer, ChromaDB cosine search, BM25, Reciprocal Rank Fusion (RRF), fallback và generation có citation.

## Dữ liệu và nguồn

- `data/landing/legal/`: 3 PDF ký số; `sources.json` lưu URL trang Công báo và bản PDF có text layer.
- `data/landing/news/`: 5 JSON có đủ `url`, `title`, `date_crawled`, `content_markdown`.
- `data/standardized/legal/` và `data/standardized/news/`: Markdown UTF-8 dùng để chunk/index.
- Chủ đề: Luật Du lịch, quy định hướng dẫn/xử phạt và cẩm nang Hà Nội, Ninh Bình, Huế, ẩm thực Việt Nam.

## Kiến trúc

```text
landing -> standardized Markdown -> chunks -> embeddings -> ChromaDB
                                             |             |
                                             +-> BM25      +-> dense
                                                    \       /
                                                     RRF
                                                      |
                                        dense-score fallback
                                                      |
                                      LLM answer + [n] citations
```

Các interface và invariant nằm trong `docs/MODULE_CONTRACTS.md`. ID chunk có dạng `<document-id>::chunk-<index>` và Chroma dùng `upsert`, nên chạy lại không tạo bản ghi trùng.

## Cài đặt

Yêu cầu Python 3.10–3.13 và Node.js 18+ nếu dùng giao diện React.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

Playwright/Chromium chỉ cần khi chạy lại crawler. Corpus đã crawl sẵn nên người làm retrieval, evaluation hoặc demo không bắt buộc cài browser.

### Cấu hình 9Router

```dotenv
LLM_PROVIDER=openai
LLM_MODEL=cx/gpt-5.6-luna
OPENAI_BASE_URL=http://127.0.0.1:20128/v1
OPENAI_API_KEY=<key được tạo trong 9Router>

EMBEDDING_PROVIDER=sentence_transformers
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

Tên biến vẫn là `OPENAI_API_KEY` vì dự án dùng OpenAI-compatible SDK; giá trị phải là key gateway do 9Router cấp. Không commit `.env`.

## Chạy pipeline

Không cần crawl lại để demo. Với corpus hiện có:

```powershell
python -m src.task3_convert_markdown
python -m src.task4_chunking_indexing
python -m pytest -q
```

Nếu cần thu thập lại từ đầu:

```powershell
python -m playwright install chromium
python -m src.task1_collect_legal_docs
python -m src.task2_crawl_news
python -m src.task3_convert_markdown
```

## Chạy chatbot

### Streamlit

```powershell
streamlit run app.py
```

### React + FastAPI

Terminal 1:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.api:app --reload --port 8000
```

Terminal 2:

```powershell
cd frontend
npm ci
npm run dev
```

Mở `http://localhost:5173`. Khi backend online, giao diện gọi pipeline thật; trạng thái mock chỉ là chế độ dự phòng khi backend không kết nối được. Tab chat hỗ trợ click citation `[1]`, `[2]` để highlight và mở chi tiết nguồn.

## Evaluation A/B

Golden dataset có 18 câu; lần đo chính thức trong báo cáo dùng 15 câu đầu, đáp ứng ngưỡng tối thiểu của rubric. Hai cấu hình dùng cùng corpus, embedding, prompt, model và `top_k=5`:

- A: dense-only.
- B: dense + BM25, hợp nhất một lần bằng RRF (`k=60`).

Bốn metric Ragas: Faithfulness, Answer Relevance, Context Recall và Context Precision.

```powershell
.\.venv\Scripts\python.exe -m group_project.evaluation.run_evaluation --skip-index --limit 15
```

Kết quả chi tiết được lưu tại `group_project/evaluation/evaluation_details.json`; báo cáo tổng hợp được sinh vào `group_project/evaluation/RESULT.md`. Runner checkpoint câu trả lời trong `evaluation_inputs.json`, nên lần chạy lại không phải gọi generator cho các mẫu đã hoàn thành.

## Kiểm thử và demo

```powershell
python -m pytest tests/test_contracts.py -q
python -m pytest tests/test_acceptance.py -q
python -m pytest -q
```

Kịch bản demo tối thiểu:

1. Một câu trong phạm vi và mở citation/source card.
2. Một câu ngoài phạm vi để kiểm tra fallback/safe refusal.
3. Tab A/B hoặc `RESULT.md` để trình bày số đo dense-only so với hybrid + RRF.

## Báo cáo

- Báo cáo nhóm: `group_project/evaluation/RESULT.md`.
- Báo cáo cá nhân: `reports/`.
- Rubric: `docs/GRADING_RUBRIC.md`.

Bonus có thể kiểm chứng trong repo: UI citation/source highlighting. HyDE/query expansion, reranker nâng cao và conversation memory không được tuyên bố nếu chưa có code cùng kết quả đo/demo.
