# RAG Chatbot for Household Business Tax & Declaration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship an end-to-end Vietnamese RAG chatbot focused on **tax and declaration obligations** for household businesses within a 3-hour lab, split across 4 parallel tracks (Tiên, Khoa, Chiến, Linh), passing every contract test and the full acceptance suite.

**Architecture:** 4 vertical tracks (Data, Retrieval Core, Fusion/Pipeline, Generation+UI+Eval) that begin in parallel using early mock/stub interfaces, converge in a 30-minute integration phase, then close with reports. Contracts are fixed by `src/contracts.py` and `docs/MODULE_CONTRACTS.md`.

**Tech Stack:** Python 3.10+, ChromaDB (cosine), sentence-transformers/BGE-M3, rank_bm25, OpenAI SDK (gpt-4o-mini), Streamlit, ragas, Crawl4AI, MarkItDown, PageIndex.

**Spec:** `docs/superpowers/specs/2026-09-25-spec-1-ho-kinh-doanh-rag.md`

## Global Constraints

- Python `>=3.10,<3.14`; use only libraries already in `pyproject.toml` (do not add new deps without team approval).
- Every file committed MUST be English for source code, comments, identifiers, commit messages, and PR descriptions (per `CLAUDE.md` Language Rules). Vietnamese is allowed in the corpus data, the chat UI strings shown to users, and inside spec/plan/report Markdown.
- Contracts fixed in `src/contracts.py`: `Document`, `Chunk`, `SearchResult`, `GenerationResult`. Do not change these types.
- Shared config (locked): `EMBEDDING_MODEL=BAAI/bge-m3` (dim 1024), `CHUNK_SIZE=500`, `CHUNK_OVERLAP=50`, `CHUNKING_METHOD=recursive`, `COLLECTION_NAME=rag_hkd_thue`, `SCORE_THRESHOLD=0.3` initial, `LLM_MODEL=gpt-4o-mini`, `TEMPERATURE=0.3`.
- **Content scope (narrowed):** only tax and declaration obligations for household businesses — thuế môn bài, GTGT, TNCN, phương pháp khoán/kê khai, ngưỡng doanh thu, hồ sơ và thời hạn khai thuế, hoá đơn điện tử liên quan kê khai, xử phạt vi phạm thuế. Out of scope: đăng ký hộ kinh doanh, giấy phép, TMĐT nói chung, luật lao động, thuế doanh nghiệp có pháp nhân.
- Commit trailer names the actual model that wrote that commit (Opus 4.7 while planning, Sonnet 5 while coding directly, dispatched subagent's model when dispatched).
- No `.env`, API key, or `chroma_db/` committed. `chroma_db/` must be added to `.gitignore` before any commit that would include it.
- All PRs merged with `--merge` (never `--squash`); commit format `type(scope): description`.

## Review Focus

Five input classes the spec implies but the shipped contract tests do not exercise; each is covered by a test attached to the owning task below:

1. **Task 9 `retrieve` with empty dense results** — must not crash on `dense[0]["score"]` when semantic search returns `[]`; expected: skip fallback threshold, return whatever hybrid/sparse produces (or `[]`). (Covered in Task C.3.)
2. **Task 4 `chunk_documents` on tiny content shorter than `CHUNK_SIZE`** — must still emit exactly one chunk with `chunk_index=0`, not zero. (Covered in Task B.1.)
3. **Task 7 `rerank_rrf([])` with zero ranked lists** — must return `[]`, not crash on `max` or division. (Covered in Task C.1.)
4. **Task 8 `pageindex_search` without `PAGEINDEX_API_KEY`** — must return `[]` and not raise, so Task 9 fallback path is safe when no key is provisioned. (Covered in Task C.2.)
5. **Task 10 `generate_with_citation` when `call_llm` raises** — must return the safe-refusal `GenerationResult` (`retrieval_source="none"`), not propagate the exception into the UI. (Covered in Task D.2.)

---

## File Structure

| File | Owner track | Responsibility |
|---|---|---|
| `.env` (local only, not committed) | Phase 0 | Shared secrets / provider selection |
| `.gitignore` | Phase 0 | Ensure `chroma_db/` is ignored |
| `data/landing/legal/*.pdf` | A / Tiên | Raw legal PDFs |
| `data/landing/news/*.json` | A / Tiên | Raw crawled news |
| `data/standardized/legal/*.md` | A / Tiên | Normalized legal markdown |
| `data/standardized/news/*.md` | A / Tiên | Normalized news markdown |
| `data/bm25_corpus.json` | B / Khoa | Deterministic BM25 corpus snapshot |
| `data/pageindex_cache.json` | C / Chiến | Cached `source → doc_id` mapping |
| `src/task1_collect_legal_docs.py` | A | Fill `download_documents()` |
| `src/task2_crawl_news.py` | A | Fill `ARTICLE_URLS` and `crawl_article()` |
| `src/task3_convert_markdown.py` | A | Fill `convert_legal_docs()`, `convert_news_articles()` |
| `src/task4_chunking_indexing.py` | B | Fill all `NotImplementedError`s |
| `src/task5_semantic_search.py` | B | Fill `semantic_search` |
| `src/task6_lexical_search.py` | B | Fill `build_bm25_index`, `lexical_search`, load `CORPUS` |
| `src/task7_reranking.py` | C | Fill `rerank_rrf` |
| `src/task8_pageindex_vectorless.py` | C | Fill `upload_documents`, `pageindex_search` |
| `src/task9_retrieval_pipeline.py` | C | Fill `retrieve` |
| `src/task10_generation.py` | D | Fill `reorder_for_llm`, `format_context`, `call_llm`, `generate_with_citation` |
| `app.py` | D | Wire Streamlit UI to `generate_with_citation` |
| `group_project/evaluation/golden_dataset.json` | D | ≥15 grounded Q&A |
| `group_project/evaluation/RESULT.md` | D | Fill A/B evaluation |
| `reports/RESULT.md` | D | Copy or symlink final result table |
| `reports/<student-id>-<name>.md` × 4 | All | Individual contribution reports |
| `tests/test_edge_cases.py` | mixed | 5 review-focus tests |

---

## Phase 0 — Setup (all 4 people together, ~10 min)

### Task 0.1: Bootstrap environment and shared config

**Files:**
- Create: `.env` (local, not committed)
- Modify: `.gitignore` — add `chroma_db/`
- Modify: `pyproject.toml` — restore `sentence-transformers` line (already present in tree but removed in local diff; keep it)

**Interfaces:**
- Consumes: nothing
- Produces: a working venv with all dependencies, a `.env` used by every task, an ignored `chroma_db/` folder

- [ ] **Step 1: Create venv + install deps**

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev]"
python -m playwright install chromium
```

- [ ] **Step 2: Copy `.env.example` to `.env` and fill**

```bash
cp .env.example .env
```

Edit `.env` with these values:
```
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=<team-shared-key>
EMBEDDING_PROVIDER=sentence_transformers
EMBEDDING_MODEL=BAAI/bge-m3
PAGEINDEX_API_KEY=
SCORE_THRESHOLD=0.3
```

- [ ] **Step 3: Ensure `chroma_db/` is git-ignored**

Append to `.gitignore` if not already present:
```
# Chroma persistent store
chroma_db/
```

- [ ] **Step 4: Restore sentence-transformers dependency**

Check `pyproject.toml`; if the `sentence-transformers>=2.2.0,<7` line is missing (local diff removed it), add it back. Rerun `pip install -e ".[dev]"`.

- [ ] **Step 5: Baseline contract tests**

Run: `pytest tests/test_contracts.py -q`
Expected: many FAIL (NotImplementedError) — that's the starting point.
Run: `pytest tests/test_acceptance.py -q`
Expected: FAIL (no data yet).

- [ ] **Step 6: Commit .gitignore + pyproject.toml only**

```bash
git add .gitignore pyproject.toml
git commit -m "chore(env): ignore chroma_db and pin sentence-transformers

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

(Adjust trailer to actual authoring model; do not commit `.env`.)

---

## Track A — Data Engineer (Tiên)

### Task A.1: Seed 3 sample markdown files to unblock B/C/D

**Files:**
- Create: `data/standardized/legal/sample_seed_thuekhoan.md` (paste 1–2 pages from Circular 40/2021 — thuế khoán / phương pháp tính thuế)
- Create: `data/standardized/legal/sample_seed_kekhai.md` (paste key articles from Decree 126/2020 — thời hạn khai thuế / hồ sơ)
- Create: `data/standardized/news/sample_seed_news.md` (paste one explainer article on "hộ kinh doanh nộp thuế thế nào 2024/2025")

**Interfaces:**
- Consumes: nothing
- Produces: 3 non-empty `.md` files under `data/standardized/` so Track B can start indexing before A finishes the real crawl

- [ ] **Step 1: Copy 1 page of real legal text into `sample_seed_thuekhoan.md`**

Structure:
```markdown
# Thông tư 40/2021/TT-BTC — Phương pháp tính thuế cho hộ kinh doanh (sample)

**Source:** https://thuvienphapluat.vn/van-ban/Thue-Phi-Le-Phi/Thong-tu-40-2021-TT-BTC
**Type:** legal

<paste 200–500 chữ nội dung thật — ví dụ Điều 5, 6, 7 về phương pháp khoán / kê khai / theo từng lần>
```

- [ ] **Step 2: Same for `sample_seed_kekhai.md` (Nghị định 126/2020 điều về thời hạn khai thuế) and `sample_seed_news.md`**

- [ ] **Step 3: Notify Khoa (Track B) that seed data is ready**

- [ ] **Step 4: Commit seed files**

```bash
git add data/standardized/legal/sample_seed_thuekhoan.md \
        data/standardized/legal/sample_seed_kekhai.md \
        data/standardized/news/sample_seed_news.md
git commit -m "data(seed): add 3 sample markdown files to unblock track B

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

### Task A.2: Implement `task1_collect_legal_docs.py` — download ≥3 PDFs

**Files:**
- Modify: `src/task1_collect_legal_docs.py`
- Create: `data/landing/legal/*.pdf` (≥3 files)

**Interfaces:**
- Consumes: PDF URLs from `chinhphu.vn` / `thuvienphapluat.vn`
- Produces: PDF files ≥1KB each under `data/landing/legal/`; satisfies `tests/test_acceptance.py::test_corpus_has_required_legal_documents`

- [ ] **Step 1: Confirm 3 live URLs from official sources**

At execution time, Tiên finds the current live download URL for each PDF on `thuvienphapluat.vn` or `vanban.chinhphu.vn` (URLs change; the plan will not hardcode a URL that may 404 in the future). Target documents (all tax-and-declaration focused):
- **Thông tư 40/2021/TT-BTC** — thuế GTGT/TNCN và quản lý thuế cho hộ kinh doanh (văn bản chính).
- **Thông tư 100/2021/TT-BTC** — sửa đổi Thông tư 40/2021 (phương pháp tính thuế + biểu mẫu).
- **Nghị định 126/2020/NĐ-CP** — quy định chi tiết Luật Quản lý thuế 2019 (thời hạn khai/nộp, ấn định thuế).

- [ ] **Step 2: Replace `download_documents()` body with the confirmed URLs**

```python
def download_documents() -> None:
    import requests
    sources = {
        "tt40-2021-thue-ho-kinh-doanh.pdf":   "<paste-live-url-1>",
        "tt100-2021-sua-doi-tt40.pdf":        "<paste-live-url-2>",
        "nd126-2020-quan-ly-thue.pdf":        "<paste-live-url-3>",
    }
    for filename, url in sources.items():
        target = DATA_DIR / filename
        if target.exists() and target.stat().st_size > 1024:
            print(f"Skip existing: {filename}")
            continue
        response = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        target.write_bytes(response.content)
        print(f"Downloaded: {filename}")
```

- [ ] **Step 3: If any URL 403s, download manually via browser**

Drop the file into `data/landing/legal/` with the same filename. Do not commit workaround code — the manual fallback is a runtime decision, not a code change.

- [ ] **Step 4: Verify**

```bash
python -m src.task1_collect_legal_docs
ls -la data/landing/legal/
pytest tests/test_acceptance.py::test_corpus_has_required_legal_documents -v
```
Expected: PASS.

- [ ] **Step 5: Commit code (not the PDFs — check policy)**

Legal PDFs are public documents so committing them is OK; team policy on repo size: yes commit if <10MB each.
```bash
git add src/task1_collect_legal_docs.py data/landing/legal/
git commit -m "feat(data): implement legal PDF collector and land 3 decrees

Co-Authored-By: <trailer for actual model>"
```

### Task A.3: Implement `task2_crawl_news.py` — crawl ≥5 articles

**Files:**
- Modify: `src/task2_crawl_news.py`
- Create: `data/landing/news/article_*.json` (≥5 files)

**Interfaces:**
- Consumes: 5 article URLs
- Produces: JSON files with `{url, title, date_crawled, content_markdown}`; satisfies `tests/test_acceptance.py::test_corpus_has_required_news_with_metadata`

- [ ] **Step 1: Fill `ARTICLE_URLS` (5 tax/declaration-focused articles from vnexpress/luatvietnam/luatminhkhue/thoibaotaichinh)**

Suggested query terms when hunting for candidates: "hộ kinh doanh nộp thuế", "thuế khoán hộ kinh doanh", "kê khai thuế hộ kinh doanh", "hoá đơn điện tử hộ kinh doanh", "phạt chậm nộp thuế hộ kinh doanh". Pick 5 articles that together cover: (a) thuế môn bài + ngưỡng, (b) phân biệt phương pháp khoán/kê khai, (c) hồ sơ và biểu mẫu, (d) hoá đơn điện tử, (e) xử phạt.

- [ ] **Step 2: Replace `crawl_article`**

```python
async def crawl_article(url: str) -> dict:
    from datetime import datetime
    from crawl4ai import AsyncWebCrawler
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        title = (result.metadata or {}).get("title") or url
        markdown = result.markdown or ""
        if not markdown.strip():
            raise ValueError(f"Empty markdown for {url}")
        return {
            "url": url,
            "title": title,
            "date_crawled": datetime.now().isoformat(),
            "content_markdown": markdown,
        }
```

- [ ] **Step 3: Run**

```bash
python -m src.task2_crawl_news
ls data/landing/news/
pytest tests/test_acceptance.py::test_corpus_has_required_news_with_metadata -v
```

- [ ] **Step 4: Commit**

```bash
git add src/task2_crawl_news.py data/landing/news/
git commit -m "feat(data): implement news crawler and land 5 articles

Co-Authored-By: <trailer>"
```

### Task A.4: Implement `task3_convert_markdown.py`

**Files:**
- Modify: `src/task3_convert_markdown.py`
- Create: `data/standardized/legal/*.md`, `data/standardized/news/*.md`

**Interfaces:**
- Consumes: files from `data/landing/{legal,news}/`
- Produces: markdown files ≥200 chars in `data/standardized/`; satisfies `tests/test_acceptance.py::test_standardized_output_covers_both_source_types`

- [ ] **Step 1: Replace `convert_legal_docs`**

```python
def convert_legal_docs() -> None:
    from markitdown import MarkItDown
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)
    converter = MarkItDown()
    for path in sorted(legal_dir.iterdir()):
        if path.suffix.lower() not in {".pdf", ".doc", ".docx"}:
            continue
        target = output_dir / f"{path.stem}.md"
        if target.exists() and target.stat().st_size > 200:
            print(f"Skip existing: {target.name}")
            continue
        text = converter.convert(str(path)).text_content
        target.write_text(text, encoding="utf-8")
        print(f"Converted: {target.name}")
```

- [ ] **Step 2: Replace `convert_news_articles`**

```python
def convert_news_articles() -> None:
    import json
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(news_dir.glob("*.json")):
        target = output_dir / f"{path.stem}.md"
        if target.exists() and target.stat().st_size > 200:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        header = (
            f"# {data['title']}\n\n"
            f"**Source:** {data['url']}\n\n"
            f"**Crawled:** {data['date_crawled']}\n\n---\n\n"
        )
        target.write_text(header + data["content_markdown"], encoding="utf-8")
```

- [ ] **Step 3: Verify idempotency**

```bash
python -m src.task3_convert_markdown
before=$(ls data/standardized/legal data/standardized/news | wc -l)
python -m src.task3_convert_markdown  # second run
after=$(ls data/standardized/legal data/standardized/news | wc -l)
[ "$before" = "$after" ] && echo "idempotent OK"
pytest tests/test_acceptance.py::test_standardized_output_covers_both_source_types -v
```

- [ ] **Step 4: Delete the seed files from Task A.1** (real data has landed)

```bash
rm data/standardized/legal/sample_seed*.md data/standardized/news/sample_seed_news.md
git add -A data/standardized
```

- [ ] **Step 5: Commit**

```bash
git add src/task3_convert_markdown.py data/standardized/
git commit -m "feat(data): convert legal PDFs and news JSON to normalized markdown

Co-Authored-By: <trailer>"
```

---

## Track B — Retrieval Core (Khoa)

### Task B.1: Implement `task4_chunking_indexing.py` — `load_documents` + `chunk_documents`

**Files:**
- Modify: `src/task4_chunking_indexing.py`
- Test: uses existing `tests/test_contracts.py::test_chunk_documents_preserves_identity_and_metadata`
- Extend: `tests/test_edge_cases.py` (new file) — Review Focus item #2

**Interfaces:**
- Consumes: `data/standardized/**/*.md` (created by A.1 or A.4)
- Produces: `load_documents() -> list[Document]`, `chunk_documents(docs) -> list[Chunk]`

- [ ] **Step 1: Replace `load_documents`**

```python
def load_documents() -> list[dict]:
    documents = []
    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        doc_type = "legal" if "legal" in path.parts else "news"
        documents.append({
            "id": path.relative_to(STANDARDIZED_DIR).as_posix(),
            "content": path.read_text(encoding="utf-8"),
            "metadata": {
                "source": path.name,
                "title": path.stem,
                "doc_type": doc_type,
                "url": None,
            },
        })
    return documents
```

- [ ] **Step 2: Replace `chunk_documents`**

```python
def chunk_documents(documents: list[dict]) -> list[dict]:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = []
    for document in documents:
        pieces = splitter.split_text(document["content"]) or [document["content"]]
        for index, text in enumerate(pieces):
            if not text.strip():
                continue
            chunks.append({
                "id": f"{document['id']}::chunk-{index}",
                "content": text,
                "metadata": {**document["metadata"], "chunk_index": index},
            })
    return chunks
```

- [ ] **Step 3: Create `tests/test_edge_cases.py` and add Review Focus #2 test**

```python
def test_chunk_documents_handles_tiny_content():
    from src.task4_chunking_indexing import chunk_documents
    doc = {
        "id": "tiny",
        "content": "Hộ kinh doanh nộp thuế môn bài hàng năm.",
        "metadata": {"source": "tiny.md", "title": "Tiny", "doc_type": "legal", "url": None},
    }
    chunks = chunk_documents([doc])
    assert len(chunks) == 1
    assert chunks[0]["metadata"]["chunk_index"] == 0
    assert chunks[0]["content"].strip()
```

- [ ] **Step 4: Run the two tests**

```bash
pytest tests/test_contracts.py::test_chunk_documents_preserves_identity_and_metadata \
       tests/test_edge_cases.py::test_chunk_documents_handles_tiny_content -v
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/task4_chunking_indexing.py tests/test_edge_cases.py
git commit -m "feat(task4): implement load_documents and chunk_documents

Co-Authored-By: <trailer>"
```

### Task B.2: Implement `task4` — `embed_texts`, `get_collection`, `embed_chunks`, `index_to_vectorstore`

**Files:**
- Modify: `src/task4_chunking_indexing.py`

**Interfaces:**
- Consumes: `EMBEDDING_MODEL` from `.env`, chunks from B.1
- Produces: `embed_texts(list[str]) -> list[list[float]]`, `get_collection()`, `embed_chunks(chunks) -> list[EmbeddedChunk]`, `index_to_vectorstore(chunks) -> None`

- [ ] **Step 1: Pre-download the model in background**

```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')"
```

- [ ] **Step 2: Fill `embed_texts`**

```python
_MODEL = None

def embed_texts(texts: list[str]) -> list[list[float]]:
    global _MODEL
    if _MODEL is None:
        from sentence_transformers import SentenceTransformer
        _MODEL = SentenceTransformer(EMBEDDING_MODEL)
    return _MODEL.encode(texts, normalize_embeddings=True).tolist()
```

- [ ] **Step 3: Fill `get_collection`**

```python
def get_collection():
    import chromadb
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
```

- [ ] **Step 4: Fill `embed_chunks` and `index_to_vectorstore`**

```python
def embed_chunks(chunks: list[dict]) -> list[dict]:
    vectors = embed_texts([chunk["content"] for chunk in chunks])
    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector
    return chunks


def index_to_vectorstore(chunks: list[dict]) -> None:
    collection = get_collection()
    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=[chunk["content"] for chunk in chunks],
        embeddings=[chunk["embedding"] for chunk in chunks],
        metadatas=[chunk["metadata"] for chunk in chunks],
    )
```

- [ ] **Step 5: Run the full pipeline**

```bash
python -m src.task4_chunking_indexing
```
Expected: `Indexed N chunks` where N > 0.

- [ ] **Step 6: Commit**

```bash
git add src/task4_chunking_indexing.py
git commit -m "feat(task4): embed with BGE-M3 and index chunks into ChromaDB

Co-Authored-By: <trailer>"
```

### Task B.3: Implement `task5_semantic_search.py`

**Files:**
- Modify: `src/task5_semantic_search.py`
- Test: existing `tests/test_contracts.py::test_semantic_search_uses_shared_embedding_and_contract`

**Interfaces:**
- Consumes: `embed_texts`, `get_collection` (from B.2)
- Produces: `semantic_search(query, top_k) -> list[SearchResult]` with `retrieval_method="dense"`

- [ ] **Step 1: Fill `semantic_search`**

```python
def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    query_vector = embed_texts([query])[0]
    response = get_collection().query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    results = []
    for item_id, content, metadata, distance in zip(
        response["ids"][0],
        response["documents"][0],
        response["metadatas"][0],
        response["distances"][0],
    ):
        results.append({
            "id": item_id,
            "content": content,
            "score": max(0.0, 1.0 - float(distance)),
            "metadata": metadata,
            "retrieval_method": "dense",
        })
    return sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]
```

- [ ] **Step 2: Run contract test**

```bash
pytest tests/test_contracts.py::test_semantic_search_uses_shared_embedding_and_contract -v
```
Expected: PASS.

- [ ] **Step 3: Smoke-test on real Chroma**

```bash
python -m src.task5_semantic_search
```
Expected: prints ≥1 result dict.

- [ ] **Step 4: Commit**

```bash
git add src/task5_semantic_search.py
git commit -m "feat(task5): implement dense semantic search over ChromaDB

Co-Authored-By: <trailer>"
```

### Task B.4: Implement `task6_lexical_search.py` with shared corpus

**Files:**
- Modify: `src/task6_lexical_search.py`
- Create: `data/bm25_corpus.json` (produced side-effect of task4 run)

**Interfaces:**
- Consumes: same chunks task4 produced (via a cached JSON so ordering is deterministic)
- Produces: `lexical_search(query, top_k) -> list[SearchResult]` with `retrieval_method="bm25"`, plus a `CORPUS` module-level list that tests can monkeypatch

- [ ] **Step 1: Add a corpus dump in `task4`** (small addition)

Append to `run_pipeline` in `src/task4_chunking_indexing.py`:
```python
import json
CORPUS_CACHE = Path(__file__).parent.parent / "data" / "bm25_corpus.json"
CORPUS_CACHE.write_text(
    json.dumps([{k: v for k, v in c.items() if k != "embedding"} for c in chunks],
               ensure_ascii=False, indent=2),
    encoding="utf-8",
)
```

- [ ] **Step 2: Load `CORPUS` in `task6`**

```python
import json
from pathlib import Path

CORPUS_PATH = Path(__file__).parent.parent / "data" / "bm25_corpus.json"
CORPUS: list[dict] = (
    json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    if CORPUS_PATH.exists() else []
)
```

- [ ] **Step 3: Fill `build_bm25_index` and `lexical_search`**

```python
def build_bm25_index(corpus: list[dict]):
    from rank_bm25 import BM25Okapi
    tokenized = [item["content"].lower().split() for item in corpus]
    return BM25Okapi(tokenized) if tokenized else None


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    import numpy as np
    if not CORPUS:
        return []
    bm25 = build_bm25_index(CORPUS)
    scores = bm25.get_scores(query.lower().split())
    order = np.argsort(scores)[::-1]
    results = []
    for index in order:
        if scores[index] <= 0 or len(results) >= top_k:
            break
        item = CORPUS[index]
        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": float(scores[index]),
            "metadata": item["metadata"],
            "retrieval_method": "bm25",
        })
    return results
```

- [ ] **Step 4: Run contract test**

```bash
pytest tests/test_contracts.py::test_lexical_search_returns_bm25_contract -v
```
Expected: PASS (the test monkeypatches `CORPUS`).

- [ ] **Step 5: Commit**

```bash
git add src/task6_lexical_search.py src/task4_chunking_indexing.py
git commit -m "feat(task6): BM25 lexical search with shared JSON corpus

Co-Authored-By: <trailer>"
```

---

## Track C — Fusion / Fallback / Pipeline (Chiến)

### Task C.1: Implement `rerank_rrf` in `task7_reranking.py`

**Files:**
- Modify: `src/task7_reranking.py`
- Test: existing `tests/test_contracts.py::test_rrf_uses_rank_deduplicates_and_marks_hybrid`
- Extend: `tests/test_edge_cases.py` — Review Focus item #3

**Interfaces:**
- Consumes: any `list[list[SearchResult]]`
- Produces: `rerank_rrf(ranked_lists, top_k=5, k=60) -> list[SearchResult]` marked `hybrid`

- [ ] **Step 1: Fill `rerank_rrf`**

```python
def rerank_rrf(ranked_lists: list[list[dict]], top_k: int = 5, k: int = 60) -> list[dict]:
    scores: dict[str, float] = {}
    items: dict[str, dict] = {}
    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, 1):
            item_id = item["id"]
            scores[item_id] = scores.get(item_id, 0.0) + 1.0 / (k + rank)
            items.setdefault(item_id, item)
    ranked_ids = sorted(scores, key=lambda i: scores[i], reverse=True)
    results = []
    for item_id in ranked_ids[:top_k]:
        result = dict(items[item_id])
        result["score"] = scores[item_id]
        result["retrieval_method"] = "hybrid"
        results.append(result)
    return results
```

- [ ] **Step 2: Run contract test**

```bash
pytest tests/test_contracts.py::test_rrf_uses_rank_deduplicates_and_marks_hybrid -v
```
Expected: PASS.

- [ ] **Step 3: Add Review Focus #3 edge test**

Append to `tests/test_edge_cases.py`:
```python
def test_rerank_rrf_handles_empty_input():
    from src.task7_reranking import rerank_rrf
    assert rerank_rrf([], top_k=5) == []
    assert rerank_rrf([[]], top_k=5) == []
```

- [ ] **Step 4: Run new test**

```bash
pytest tests/test_edge_cases.py::test_rerank_rrf_handles_empty_input -v
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/task7_reranking.py tests/test_edge_cases.py
git commit -m "feat(task7): implement RRF fusion for hybrid retrieval

Co-Authored-By: <trailer>"
```

### Task C.2: Implement `task8_pageindex_vectorless.py`

**Files:**
- Modify: `src/task8_pageindex_vectorless.py`
- Create: `data/pageindex_cache.json` (produced at runtime; add to `.gitignore` if not already)
- Extend: `tests/test_edge_cases.py` — Review Focus item #4

**Interfaces:**
- Consumes: `PAGEINDEX_API_KEY` from `.env`; PDFs in `data/landing/legal/` (optional)
- Produces: `pageindex_search(query, top_k=5) -> list[SearchResult]` with method `pageindex`; returns `[]` when key missing

- [ ] **Step 1: Add cache path to `.gitignore`**

Append to `.gitignore`:
```
data/pageindex_cache.json
```

- [ ] **Step 2: Fill `upload_documents` and `pageindex_search`**

```python
import json
from pathlib import Path

CACHE_PATH = Path(__file__).parent.parent / "data" / "pageindex_cache.json"


def _load_cache() -> dict:
    return json.loads(CACHE_PATH.read_text()) if CACHE_PATH.exists() else {}


def _save_cache(cache: dict) -> None:
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2))


def upload_documents() -> None:
    if not PAGEINDEX_API_KEY:
        print("PAGEINDEX_API_KEY missing; skip upload")
        return
    from pageindex import PageIndexClient  # SDK class name may differ; adjust to actual SDK
    client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
    cache = _load_cache()
    for path in sorted((Path(__file__).parent.parent / "data" / "landing" / "legal").glob("*.pdf")):
        if path.name in cache:
            continue
        with open(path, "rb") as f:
            doc = client.upload(file=f, filename=path.name, timeout=60)
        cache[path.name] = doc["id"] if isinstance(doc, dict) else str(doc)
        _save_cache(cache)


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    if not PAGEINDEX_API_KEY:
        return []
    cache = _load_cache()
    if not cache:
        return []
    try:
        from pageindex import PageIndexClient
        client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
        raw = client.search(document_ids=list(cache.values()), query=query, top_k=top_k, timeout=30)
    except Exception as error:
        print(f"pageindex_search failed: {error}")
        return []
    results = []
    for rank, item in enumerate(raw or [], 1):
        results.append({
            "id": f"pageindex::{item.get('id', rank)}",
            "content": item.get("text") or item.get("content") or "",
            "score": float(item.get("score", 1.0 / rank)),
            "metadata": {
                "source": item.get("source", "pageindex"),
                "title": item.get("title", "PageIndex result"),
                "doc_type": "legal",
                "url": item.get("url"),
                "chunk_index": rank - 1,
            },
            "retrieval_method": "pageindex",
        })
    return sorted(results, key=lambda i: i["score"], reverse=True)[:top_k]
```

Note: the exact `pageindex` SDK API may vary. Confirm attribute names with the installed 0.2.8 package before shipping; adjust `.upload()`/`.search()` calls to match.

- [ ] **Step 3: Add Review Focus #4 test**

Append to `tests/test_edge_cases.py`:
```python
def test_pageindex_search_returns_empty_without_key(monkeypatch):
    import src.task8_pageindex_vectorless as pi
    monkeypatch.setattr(pi, "PAGEINDEX_API_KEY", "")
    assert pi.pageindex_search("anything", top_k=5) == []
```

- [ ] **Step 4: Run test**

```bash
pytest tests/test_edge_cases.py::test_pageindex_search_returns_empty_without_key -v
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/task8_pageindex_vectorless.py tests/test_edge_cases.py .gitignore
git commit -m "feat(task8): PageIndex fallback with safe no-key path

Co-Authored-By: <trailer>"
```

### Task C.3: Implement `retrieve` in `task9_retrieval_pipeline.py`

**Files:**
- Modify: `src/task9_retrieval_pipeline.py`
- Test: existing 3 contract tests (`test_retrieve_uses_dense_score_for_fallback`, `test_retrieve_fuses_once_when_dense_is_confident`, `test_retrieve_survives_fallback_provider_error`)
- Extend: `tests/test_edge_cases.py` — Review Focus item #1

**Interfaces:**
- Consumes: `semantic_search`, `lexical_search`, `rerank_rrf`, `pageindex_search`
- Produces: `retrieve(query, top_k=5, score_threshold=0.3, use_reranking=True) -> list[SearchResult]`

- [ ] **Step 1: Fill `retrieve`**

```python
def retrieve(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = SCORE_THRESHOLD,
    use_reranking: bool = True,
) -> list[dict]:
    dense = semantic_search(query, top_k=top_k * 2)
    sparse = lexical_search(query, top_k=top_k * 2)
    hybrid = (
        rerank_rrf([dense, sparse], top_k=top_k)
        if use_reranking else dense[:top_k]
    )
    best_dense_score = dense[0]["score"] if dense else 0.0
    if best_dense_score < score_threshold:
        try:
            fallback = pageindex_search(query, top_k=top_k)
            if fallback:
                return fallback
        except Exception:
            pass
    return hybrid[:top_k]
```

- [ ] **Step 2: Run the 3 contract tests**

```bash
pytest tests/test_contracts.py -k retrieve -v
```
Expected: all PASS.

- [ ] **Step 3: Add Review Focus #1 test**

Append to `tests/test_edge_cases.py`:
```python
def test_retrieve_does_not_crash_on_empty_dense(monkeypatch):
    import src.task9_retrieval_pipeline as pipeline
    monkeypatch.setattr(pipeline, "semantic_search", lambda q, top_k: [])
    monkeypatch.setattr(pipeline, "lexical_search", lambda q, top_k: [])
    monkeypatch.setattr(pipeline, "rerank_rrf", lambda lists, top_k: [])
    monkeypatch.setattr(pipeline, "pageindex_search", lambda q, top_k: [])
    assert pipeline.retrieve("x", top_k=3, score_threshold=0.5) == []
```

- [ ] **Step 4: Run test**

```bash
pytest tests/test_edge_cases.py::test_retrieve_does_not_crash_on_empty_dense -v
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/task9_retrieval_pipeline.py tests/test_edge_cases.py
git commit -m "feat(task9): retrieval pipeline with dense-score fallback

Co-Authored-By: <trailer>"
```

### Task C.4: Calibrate `SCORE_THRESHOLD` on real data

**Files:**
- Modify: `.env` (local only, not committed) — set `SCORE_THRESHOLD` to calibrated value
- Modify: `group_project/evaluation/RESULT.md` — note calibration reasoning (D writes rest of the report)

**Interfaces:**
- Consumes: real Chroma index from Track B
- Produces: an evidence-backed threshold value

- [ ] **Step 1: Wait for B to finish indexing real data (Phase 2 gate)**

- [ ] **Step 2: Run a small calibration script**

```bash
python - <<'PY'
from src.task5_semantic_search import semantic_search
in_domain = [
    "hộ kinh doanh có phải nộp thuế môn bài không",
    "thời hạn kê khai thuế của hộ khoán",
    "hộ kinh doanh khi nào bắt buộc xuất hoá đơn điện tử",
]
out_domain = [
    "cách nướng cá basa",
    "thủ tục đăng ký hộ kinh doanh cần giấy tờ gì",   # out of the narrowed scope
    "công thức pha cà phê espresso",
]
for label, qs in [("in", in_domain), ("out", out_domain)]:
    for q in qs:
        r = semantic_search(q, top_k=3)
        top = r[0]["score"] if r else 0.0
        print(f"{label}\t{top:.3f}\t{q}")
PY
```

- [ ] **Step 3: Pick a threshold between the highest out-of-domain and lowest in-domain**

Update `.env`: `SCORE_THRESHOLD=<value>`.

Note the reasoning in `group_project/evaluation/RESULT.md` under "Fallback threshold and calibration".

- [ ] **Step 4: Commit** (only the report note; `.env` is not committed)

```bash
git add group_project/evaluation/RESULT.md
git commit -m "docs(eval): calibrate score threshold with in/out domain queries

Co-Authored-By: <trailer>"
```

---

## Track D — Generation / UI / Evaluation (Linh)

### Task D.1: Implement `reorder_for_llm` + `format_context`

**Files:**
- Modify: `src/task10_generation.py`
- Test: existing `tests/test_contracts.py::test_reorder_is_non_mutating_and_context_contains_source`

**Interfaces:**
- Consumes: `list[SearchResult]`
- Produces: `reorder_for_llm(chunks) -> list[SearchResult]`, `format_context(chunks) -> str`

- [ ] **Step 1: Fill both functions**

```python
def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    if len(chunks) <= 2:
        return list(chunks)
    front = chunks[::2]
    back = chunks[1::2]
    return front + back[::-1]


def format_context(chunks: list[dict]) -> str:
    parts = []
    for index, chunk in enumerate(chunks, 1):
        m = chunk["metadata"]
        parts.append(
            f"[Document {index} | Title: {m['title']} | Source: {m['source']}]\n"
            f"{chunk['content']}"
        )
    return "\n\n---\n\n".join(parts)
```

- [ ] **Step 2: Run contract test**

```bash
pytest tests/test_contracts.py::test_reorder_is_non_mutating_and_context_contains_source -v
```
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add src/task10_generation.py
git commit -m "feat(task10): implement chunk reorder and context formatter

Co-Authored-By: <trailer>"
```

### Task D.2: Implement `call_llm` + `generate_with_citation`

**Files:**
- Modify: `src/task10_generation.py`
- Extend: `tests/test_edge_cases.py` — Review Focus item #5

**Interfaces:**
- Consumes: `retrieve` (from Track C), `LLM_PROVIDER`, `LLM_MODEL`, API keys
- Produces: `call_llm(system, user) -> str`, `generate_with_citation(query, top_k) -> GenerationResult`

- [ ] **Step 1: Fill `call_llm` (multi-provider)**

```python
def call_llm(system_prompt: str, user_message: str) -> str:
    if LLM_PROVIDER == "openai":
        from openai import OpenAI
        client = OpenAI()
        resp = client.chat.completions.create(
            model=LLM_MODEL or "gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=TEMPERATURE,
            top_p=TOP_P,
            timeout=30,
        )
        return resp.choices[0].message.content or ""
    if LLM_PROVIDER == "gemini":
        from google import genai
        client = genai.Client()
        resp = client.models.generate_content(
            model=LLM_MODEL or "gemini-2.0-flash",
            contents=f"{system_prompt}\n\n{user_message}",
        )
        return resp.text or ""
    if LLM_PROVIDER == "anthropic":
        import anthropic
        client = anthropic.Anthropic()
        resp = client.messages.create(
            model=LLM_MODEL or "claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return resp.content[0].text
    raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER}")
```

- [ ] **Step 2: Fill `generate_with_citation`**

```python
SAFE_REFUSAL = "Tôi không thể xác minh thông tin này từ nguồn hiện có."


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    try:
        chunks = retrieve(query, top_k=top_k)
    except Exception:
        chunks = []
    if not chunks:
        return {"answer": SAFE_REFUSAL, "sources": [], "retrieval_source": "none"}
    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)
    user_message = f"Context:\n{context}\n\nCâu hỏi: {query}"
    try:
        answer = call_llm(SYSTEM_PROMPT, user_message)
    except Exception:
        return {"answer": SAFE_REFUSAL, "sources": [], "retrieval_source": "none"}
    return {
        "answer": answer or SAFE_REFUSAL,
        "sources": chunks,
        "retrieval_source": chunks[0]["retrieval_method"] if chunks[0]["retrieval_method"] in {"hybrid", "pageindex"} else "hybrid",
    }
```

- [ ] **Step 3: Add Review Focus #5 test**

Append to `tests/test_edge_cases.py`:
```python
def test_generate_returns_safe_refusal_on_llm_error(monkeypatch):
    import src.task10_generation as gen
    from src.contracts import validate_generation_result
    fake_chunk = {
        "id": "chunk-0", "content": "x", "score": 0.9,
        "metadata": {"source": "a.md", "title": "A", "doc_type": "legal", "url": None, "chunk_index": 0},
        "retrieval_method": "hybrid",
    }
    monkeypatch.setattr(gen, "retrieve", lambda q, top_k: [fake_chunk])
    def boom(*a, **k): raise RuntimeError("provider down")
    monkeypatch.setattr(gen, "call_llm", boom)
    result = gen.generate_with_citation("test", top_k=1)
    assert result["retrieval_source"] == "none"
    assert result["answer"] == gen.SAFE_REFUSAL
    validate_generation_result(result)
```

- [ ] **Step 4: Run edge-case test + contract test**

```bash
pytest tests/test_edge_cases.py::test_generate_returns_safe_refusal_on_llm_error \
       tests/test_contracts.py::test_generation_result_validator_accepts_safe_refusal -v
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/task10_generation.py tests/test_edge_cases.py
git commit -m "feat(task10): generate_with_citation with safe refusal on LLM errors

Co-Authored-By: <trailer>"
```

### Task D.3: Wire Streamlit UI in `app.py`

**Files:**
- Modify: `app.py`

**Interfaces:**
- Consumes: `generate_with_citation` from Task D.2
- Produces: a chat UI showing answer + sources + retrieval method + score

- [ ] **Step 1: Replace mock body with real integration**

```python
import streamlit as st
from dotenv import load_dotenv
from src.task10_generation import generate_with_citation

load_dotenv()

st.set_page_config(page_title="Chatbot Pháp luật Hộ Kinh Doanh", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("RAG Chatbot")
    st.caption("Tư vấn pháp luật cho hộ kinh doanh cá thể")
    top_k = st.slider("Số chunks", 3, 10, 5)

st.title("Chatbot Pháp luật Hộ Kinh Doanh")
st.caption("Hỏi về đăng ký hộ kinh doanh, thuế, hoá đơn điện tử...")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        for source in message.get("sources", []):
            with st.expander(
                f"{source['metadata']['title']} · {source['retrieval_method']} · score {source['score']:.3f}"
            ):
                st.caption(source["metadata"]["source"])
                st.markdown(source["content"])

query = st.chat_input("Nhập câu hỏi...")

if query:
    st.session_state.messages.append({"role": "user", "content": query, "sources": []})
    with st.chat_message("user"):
        st.markdown(query)
    with st.chat_message("assistant"):
        with st.spinner("Đang tìm..."):
            result = generate_with_citation(query, top_k=top_k)
        st.markdown(result["answer"])
        for source in result["sources"]:
            with st.expander(
                f"{source['metadata']['title']} · {source['retrieval_method']} · score {source['score']:.3f}"
            ):
                st.caption(source["metadata"]["source"])
                st.markdown(source["content"])
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"],
    })
```

- [ ] **Step 2: Smoke-test locally**

```bash
streamlit run app.py
```
Manually run:
1. In-domain: "Hộ kinh doanh phải nộp thuế môn bài bao nhiêu?"
2. Out-of-domain: "Cách nướng cá basa?"
Expected: (1) shows sources with retrieval method + score. (2) safe refusal or hybrid with low top-1 score.

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "feat(app): wire Streamlit UI to RAG pipeline with source display

Co-Authored-By: <trailer>"
```

### Task D.4: Build golden dataset (≥15 items)

**Files:**
- Modify: `group_project/evaluation/golden_dataset.json`

**Interfaces:**
- Consumes: source corpus in `data/standardized/` (or seed data early on)
- Produces: 15+ items with keys `question`, `expected_answer`, `expected_context`; passes `tests/test_acceptance.py::test_golden_dataset_has_15_grounded_cases`

- [ ] **Step 1: Draft 15 items in JSON**

Structure per item (matching `test_golden_dataset_has_15_grounded_cases`):
```json
{
  "question": "Hộ kinh doanh nộp thuế môn bài mức bao nhiêu?",
  "expected_answer": "Mức thuế môn bài của hộ kinh doanh phụ thuộc doanh thu năm: doanh thu trên 500 triệu → 1 triệu/năm; 300–500 triệu → 500 nghìn/năm; 100–300 triệu → 300 nghìn/năm; ≤100 triệu → miễn.",
  "expected_context": "Trích một đoạn từ Thông tư 40/2021 hoặc Nghị định 139/2016 về mức thuế môn bài..."
}
```

Mix (narrowed scope: tax & declaration only):
- **10 in-domain easy** — thuế môn bài + ngưỡng, phân biệt phương pháp khoán vs kê khai, hồ sơ khai thuế theo phương pháp khoán, thời hạn nộp thuế tháng/quý, cách xác định doanh thu tính thuế, khi nào phải xuất hoá đơn điện tử, mã số thuế cho hộ kinh doanh, hộ khoán ổn định trong bao lâu, mức phạt chậm nộp thuế, hồ sơ khi ngừng kinh doanh.
- **3 in-domain hard** (multi-hop, cần ≥2 chunk): vd "hộ khoán vượt ngưỡng doanh thu giữa năm phải làm gì", "sự khác nhau khi tính thuế TNCN theo khoán so với kê khai", "hộ kinh doanh bán online có phải xuất hoá đơn điện tử không".
- **2 out-of-domain** (`expected_answer` = safe refusal string): vd "thủ tục đăng ký hộ kinh doanh cần giấy tờ gì" (nằm ngoài scope thuế), "cách nướng cá basa".

- [ ] **Step 2: Validate**

```bash
pytest tests/test_acceptance.py::test_golden_dataset_has_15_grounded_cases -v
```
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add group_project/evaluation/golden_dataset.json
git commit -m "test(eval): add 15 grounded golden Q&A for household business

Co-Authored-By: <trailer>"
```

### Task D.5: Run A/B evaluation and fill `RESULT.md`

**Files:**
- Create: `scripts/run_ab_eval.py` (throwaway helper, may live in root or `scripts/`)
- Modify: `group_project/evaluation/RESULT.md`

**Interfaces:**
- Consumes: `generate_with_citation`, `retrieve`, `golden_dataset.json`
- Produces: two runs (dense-only and hybrid+RRF) scored by ragas; a filled report with no `TODO`

- [ ] **Step 1: Write a small A/B script**

The contract test freezes the `generate_with_citation(query, top_k)` signature, so we do NOT add a `use_reranking` parameter. Instead, the A/B script calls `retrieve` + `format_context` + `call_llm` directly for each config so both branches share exactly the same generation step.

```python
# scripts/run_ab_eval.py
import json
from pathlib import Path
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall, context_precision

from src.task9_retrieval_pipeline import retrieve
from src.task10_generation import (
    call_llm, format_context, reorder_for_llm, SYSTEM_PROMPT, SAFE_REFUSAL,
)

GOLDEN = Path(__file__).parent.parent / "group_project" / "evaluation" / "golden_dataset.json"
items = json.loads(GOLDEN.read_text(encoding="utf-8"))


def run_one(question: str, use_reranking: bool) -> dict:
    chunks = retrieve(question, top_k=5, use_reranking=use_reranking)
    if not chunks:
        return {"answer": SAFE_REFUSAL, "contexts": []}
    context = format_context(reorder_for_llm(chunks))
    user_message = f"Context:\n{context}\n\nCâu hỏi: {question}"
    try:
        answer = call_llm(SYSTEM_PROMPT, user_message)
    except Exception:
        answer = SAFE_REFUSAL
    return {"answer": answer or SAFE_REFUSAL, "contexts": [c["content"] for c in chunks]}


def run_config(use_reranking: bool):
    rows = []
    for item in items:
        result = run_one(item["question"], use_reranking)
        rows.append({
            "question": item["question"],
            "answer": result["answer"],
            "contexts": result["contexts"],
            "ground_truth": item["expected_answer"],
        })
    ds = Dataset.from_list(rows)
    return evaluate(ds, metrics=[faithfulness, answer_relevancy, context_recall, context_precision])


if __name__ == "__main__":
    print("Config A (dense-only)")
    print(run_config(use_reranking=False))
    print("Config B (hybrid+RRF)")
    print(run_config(use_reranking=True))
```

- [ ] **Step 2: Run the script**

```bash
python scripts/run_ab_eval.py | tee eval_ab.log
```

- [ ] **Step 3: Fill `group_project/evaluation/RESULT.md`**

Replace every `TODO` with real values from the run: run info (date, models, corpus commit sha, threshold), 2 configs, 4-metric table, delta, A/B verdict, 3 worst performers, 3 recommendations.

- [ ] **Step 4: Verify no TODO remains**

```bash
pytest tests/test_acceptance.py::test_evaluation_report_is_completed -v
```
Expected: PASS.

- [ ] **Step 5: Sync to `reports/RESULT.md`** if the grading rubric requires it

```bash
cp group_project/evaluation/RESULT.md reports/RESULT.md
```

- [ ] **Step 6: Commit**

```bash
git add group_project/evaluation/RESULT.md reports/RESULT.md scripts/run_ab_eval.py
git commit -m "feat(eval): run dense vs hybrid+RRF A/B and fill RESULT.md

Co-Authored-By: <trailer>"
```

---

## Phase 2 — Integration (~30 min, after all 4 tracks land initial code)

### Task Z.1: End-to-end pytest

**Files:** none new; runs everything

- [ ] **Step 1: Full test run**

```bash
pytest -q
```
Expected: all green.

- [ ] **Step 2: If any fail, owner track fixes; commit fix**

Each fix is its own `fix(<scope>): ...` commit with the trailer.

### Task Z.2: Streamlit demo verification

- [ ] **Step 1: `streamlit run app.py`**
- [ ] **Step 2: Try 3 queries — easy in-domain, hard in-domain (needs RRF), out-of-domain — screenshot for report**

### Task Z.3: Individual reports × 4

**Files:**
- Create: `reports/<student-id>-chien.md`, `-khoa.md`, `-tien.md`, `-linh.md`

- [ ] **Step 1: Each member fills the `reports/INDIVIDUAL_REPORT.md` template**

- [ ] **Step 2: Commit each report separately**

```bash
git add reports/<id>-<name>.md
git commit -m "docs(report): add individual report for <name>

Co-Authored-By: <trailer>"
```

### Task Z.4: Final push

- [ ] **Step 1: Verify no secrets**

```bash
git ls-files | xargs grep -lE "sk-|OPENAI|GEMINI|ANTHROPIC" || echo "clean"
git ls-files | grep -E "^\.env$|chroma_db/" && echo "LEAK" || echo "no leak"
```

- [ ] **Step 2: Push to origin/main via PR**

Team lead opens PR from `main` (or the integration branch) — merge with `--merge` (not `--squash`) per project rules.
