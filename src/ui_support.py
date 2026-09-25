"""Read-only project inspection and the single UI-to-RAG integration seam."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .contracts import validate_generation_result


ROOT = Path(__file__).resolve().parent.parent

AGENT_STAGES = (
    {
        "id": "collect", "number": "01", "title": "Thu thập dữ liệu nguồn",
        "module": "task1_collect_legal_docs.py · task2_crawl_news.py",
        "input": "URL tài liệu IELTS, PDF/DOCX và các trang bài viết công khai",
        "action": "Tải tài liệu gốc; crawl nội dung và metadata của từng bài viết.",
        "output": "data/landing/legal/* và data/landing/news/*.json",
        "method": "Requests / Crawl4AI hoặc công cụ crawler được nhóm chốt",
        "config": "≥ 3 legal documents · ≥ 5 articles",
    },
    {
        "id": "standardize", "number": "02", "title": "Chuẩn hóa tài liệu",
        "module": "task3_convert_markdown.py",
        "input": "PDF, DOCX và article JSON từ landing zone",
        "action": "Chuyển về Markdown, loại nội dung rác và giữ metadata truy vết nguồn.",
        "output": "data/standardized/legal/*.md và news/*.md",
        "method": "MarkItDown hoặc converter tương đương",
        "config": "title · source · URL · doc_type · nội dung ≥ 200 ký tự",
    },
    {
        "id": "index", "number": "03", "title": "Chunking",
        "module": "task4_chunking_indexing.py",
        "input": "Markdown đã chuẩn hóa",
        "action": "Chia tài liệu thành các đoạn có ngữ nghĩa đủ nhỏ và giữ stable ID.",
        "output": "Chunk[] có chunk_index và metadata nguồn",
        "method": "RecursiveCharacterTextSplitter",
        "config": "chunk_size=500 · overlap=50 · separators theo paragraph → sentence → word",
    },
    {
        "id": "index", "number": "04", "title": "Embedding & vector index",
        "module": "task4_chunking_indexing.py",
        "input": "Danh sách chunks",
        "action": "Mã hóa chunk thành vector và upsert theo ID ổn định.",
        "output": "ChromaDB persistent collection",
        "method": "BAAI/bge-m3 · cosine similarity",
        "config": "dimension=1024 · collection=rag_documents · provider chờ teammate xác nhận",
    },
    {
        "id": "retrieve", "number": "05", "title": "Hybrid retrieval",
        "module": "task5_semantic_search.py · task6_lexical_search.py",
        "input": "Câu hỏi của người dùng",
        "action": "Chạy dense search và BM25 độc lập trên cùng corpus chunks.",
        "output": "Hai danh sách SearchResult đã xếp hạng",
        "method": "Dense cosine search + BM25 lexical search",
        "config": "top_k theo UI · BM25 tokenizer chờ teammate xác nhận",
    },
    {
        "id": "fusion", "number": "06", "title": "Fusion & fallback",
        "module": "task7_reranking.py · task8_pageindex_vectorless.py · task9_retrieval_pipeline.py",
        "input": "Dense results và BM25 results",
        "action": "Gộp ranking bằng RRF; dùng dense cosine gốc để quyết định fallback.",
        "output": "Hybrid hoặc PageIndex SearchResult",
        "method": "Reciprocal Rank Fusion · PageIndex vectorless fallback",
        "config": "RRF k=60 · score_threshold=0.3 · chỉ fuse một lần",
    },
    {
        "id": "generate", "number": "07", "title": "Grounded generation",
        "module": "task10_generation.py",
        "input": "Top chunks đã truy xuất",
        "action": "Reorder context, gọi LLM và buộc câu trả lời dựa trên evidence.",
        "output": "GenerationResult gồm answer, sources và retrieval_source",
        "method": "Context-grounded generation với citation",
        "config": "temperature=0.3 · top_p=0.9 · model/provider đọc từ .env",
    },
    {
        "id": "ui", "number": "08", "title": "Trả lời & kiểm chứng",
        "module": "app.py · ui_support.py",
        "input": "GenerationResult",
        "action": "Hiển thị answer, nguồn, URL, retrieval method và score; giữ chat history.",
        "output": "Câu trả lời có citation hoặc safe refusal",
        "method": "Streamlit session state + contract validation",
        "config": "Provider/index lỗi không làm giao diện crash",
    },
    {
        "id": "evaluate", "number": "09", "title": "Đánh giá chất lượng",
        "module": "group_project/evaluation/*",
        "input": "Golden dataset dùng chung cho Config A và Config B",
        "action": "So sánh dense-only với hybrid + RRF và phân tích các case thấp nhất.",
        "output": "4 metrics, latency, cost và error analysis",
        "method": "Faithfulness · relevance · context recall · context precision",
        "config": "≥ 15 questions · evaluator/prompt/top_k giống nhau giữa hai config",
    },
)

def _count_files(relative: str, suffixes: set[str]) -> int:
    directory = ROOT / relative
    if not directory.is_dir():
        return 0
    return sum(path.is_file() and path.suffix.lower() in suffixes for path in directory.iterdir())


def _implemented(relative: str) -> bool:
    path = ROOT / relative
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return "NotImplementedError" not in text and "TODO:" not in text


def _golden_count() -> int:
    path = ROOT / "group_project/evaluation/golden_dataset.json"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return len(value) if isinstance(value, list) else 0
    except (OSError, json.JSONDecodeError):
        return 0


def get_project_snapshot() -> dict[str, Any]:
    """Return conservative, read-only evidence indicators for the dashboard."""
    legal_count = _count_files("data/landing/legal", {".pdf", ".doc", ".docx"})
    news_count = _count_files("data/landing/news", {".json"})
    std_legal = _count_files("data/standardized/legal", {".md"})
    std_news = _count_files("data/standardized/news", {".md"})
    golden_count = _golden_count()
    names = {
        1: "collect_legal_docs", 2: "crawl_news", 3: "convert_markdown",
        4: "chunking_indexing", 5: "semantic_search", 6: "lexical_search",
        7: "reranking", 8: "pageindex_vectorless", 9: "retrieval_pipeline",
        10: "generation",
    }
    modules = {number: _implemented(f"src/task{number}_{name}.py") for number, name in names.items()}
    data_ready = legal_count >= 3 and news_count >= 5
    standardized = std_legal >= 3 and std_news >= 5
    evaluation_report = (
        _implemented("reports/RESULT.md")
        or _implemented("group_project/evaluation/RESULT.md")
    )
    step_status = {
        "collect": "ready" if data_ready else ("progress" if legal_count + news_count else "missing"),
        "standardize": "ready" if standardized else ("progress" if std_legal + std_news else "missing"),
        "index": "ready" if modules[4] else "progress",
        "retrieve": "ready" if modules[5] and modules[6] else "progress",
        "fusion": "ready" if modules[7] and modules[8] and modules[9] else "progress",
        "generate": "ready" if modules[10] else "progress",
        "ui": "ready",
        "evaluate": "ready" if golden_count >= 15 and evaluation_report else ("progress" if golden_count else "missing"),
    }
    return {
        "legal_count": legal_count, "news_count": news_count,
        "golden_count": golden_count, "step_status": step_status,
    }


def run_rag_query(query: str, top_k: int) -> dict[str, Any]:
    """Call the public generation contract and keep the UI alive during handoff."""
    try:
        # Lazy import prevents unfinished provider/index setup from breaking app load.
        from .task10_generation import generate_with_citation

        result = generate_with_citation(query, top_k=top_k)
        validate_generation_result(result)
        return result
    except NotImplementedError:
        return {
            "answer": "Pipeline generation chưa được nối xong, nên tôi chưa thể trả lời từ corpus.",
            "sources": [], "retrieval_source": "none",
            "ui_notice": "UI đã sẵn sàng. Hoàn thiện src/task10_generation.py để dùng dữ liệu thật.",
        }
    except Exception as exc:  # Provider/index failures must not crash Streamlit.
        return {
            "answer": "Không thể truy xuất nguồn ở lần thử này. Vui lòng kiểm tra index và cấu hình provider.",
            "sources": [], "retrieval_source": "none",
            "ui_notice": f"Chi tiết kỹ thuật: {type(exc).__name__}: {exc}",
        }
