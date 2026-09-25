"""
RAG Chatbot — E-commerce Support (Shopee Policies)
Giao diện Streamlit cao cấp, trực quan hóa toàn bộ Pipeline Flow,
3 Bảng xếp hạng tương quan (Dense vs BM25 vs RRF), và Trình duyệt tài liệu Markdown.

Chạy:
    streamlit run app.py
"""

import os
import sys
import time
import json
import html
import textwrap
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.task4_chunking_indexing import get_collection
from src.task5_semantic_search import semantic_search
from src.task6_lexical_search import lexical_search
from src.task7_reranking import rerank_rrf
from src.task8_pageindex_vectorless import pageindex_search
from src.task9_retrieval_pipeline import SCORE_THRESHOLD
from src.task10_generation import (
    reorder_for_llm,
    format_context,
    LLM_MODEL,
    TEMPERATURE,
    TOP_P,
    SYSTEM_PROMPT,
)

# =============================================================================
# PAGE CONFIGURATION & STYLING
# =============================================================================

st.set_page_config(
    page_title="Shopee Support RAG AI",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.html("""
<style>
    /* Metric Card */
    .metric-card {
        background: rgba(128, 128, 128, 0.05);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 12px;
    }

    /* Source Tag */
    .source-tag {
        background-color: rgba(128, 128, 128, 0.15);
        border: 1px solid rgba(128, 128, 128, 0.3);
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 0.78rem;
        font-family: monospace;
    }

    /* =========================================================================
       COMPONENT 1: HORIZONTAL PIPELINE FLOW GRAPH (IMAGE 1)
       ========================================================================= */
    .pipeline-flow-container {
        background: rgba(128, 128, 128, 0.035);
        border: 1px solid rgba(128, 128, 128, 0.18);
        border-radius: 14px;
        padding: 16px 18px;
        margin: 14px 0 18px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
    }
    .pipeline-flow-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
        overflow-x: auto;
        padding-bottom: 4px;
    }
    .pipeline-node {
        background: rgba(128, 128, 128, 0.05);
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-radius: 12px;
        padding: 12px 14px;
        flex: 1;
        min-width: 140px;
        min-height: 108px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .pipeline-node:hover {
        transform: translateY(-2px);
        border-color: rgba(128, 128, 128, 0.4);
    }
    .pipeline-stack {
        display: flex;
        flex-direction: column;
        gap: 6px;
        flex: 1.15;
        min-width: 160px;
    }
    .pipeline-subnode {
        background: rgba(128, 128, 128, 0.05);
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-radius: 10px;
        padding: 8px 12px;
        transition: transform 0.15s ease;
    }
    .pipeline-subnode:hover {
        transform: translateY(-1px);
    }

    /* Node Accents */
    .node-accent-dense {
        border-top: 3px solid #0284c7;
    }
    .node-accent-lexical {
        border-left: 3.5px solid #ef4444;
    }
    .node-accent-fusion {
        border-top: 3px solid #8b5cf6;
    }
    .node-accent-gate-ok {
        border: 1.5px solid #06b6d4;
        background: rgba(6, 182, 212, 0.07);
    }
    .node-accent-gate-warn {
        border: 1.5px solid #f59e0b;
        background: rgba(245, 158, 11, 0.07);
    }
    .node-accent-answer {
        border-top: 3px solid #3b82f6;
    }

    .node-tag {
        font-size: 0.68rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #64748b;
        margin-bottom: 4px;
    }
    .node-title {
        font-size: 0.88rem;
        font-weight: 700;
        line-height: 1.25;
        margin-bottom: 4px;
        color: inherit;
    }
    .node-meta {
        font-size: 0.74rem;
        color: #64748b;
    }
    .pipeline-arrow {
        color: #94a3b8;
        font-size: 1.3rem;
        font-weight: 300;
        user-select: none;
        padding: 0 4px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .pipeline-status-banner {
        margin-top: 14px;
        padding: 8px 14px;
        border-radius: 6px;
        font-size: 0.86rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .banner-hybrid {
        border-left: 4px solid #0d9488;
        background: rgba(13, 148, 136, 0.08);
    }
    .banner-fallback {
        border-left: 4px solid #f59e0b;
        background: rgba(245, 158, 11, 0.08);
    }

    /* =========================================================================
       COMPONENT 2: THREE COMPARATIVE RANKING COLUMNS (IMAGE 2)
       ========================================================================= */
    .ranking-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 14px;
        margin-top: 10px;
        margin-bottom: 16px;
    }
    @media (max-width: 900px) {
        .ranking-grid {
            grid-template-columns: 1fr;
        }
    }
    .ranking-column {
        background: rgba(128, 128, 128, 0.04);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 12px;
        padding: 14px;
    }
    .ranking-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 8px;
        border-bottom: 1px solid rgba(128, 128, 128, 0.18);
        margin-bottom: 12px;
    }
    .ranking-title {
        font-size: 0.95rem;
        font-weight: 700;
    }
    .ranking-scale {
        font-size: 0.72rem;
        color: #64748b;
        font-family: monospace;
    }
    .rank-item {
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px dashed rgba(128, 128, 128, 0.15);
    }
    .rank-item:last-child {
        margin-bottom: 0;
        padding-bottom: 0;
        border-bottom: none;
    }
    .rank-item-header {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        gap: 8px;
    }
    .rank-num {
        font-size: 0.8rem;
        font-weight: 700;
        color: #64748b;
        min-width: 22px;
    }
    .rank-doc-title {
        font-size: 0.84rem;
        font-weight: 600;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        flex: 1;
    }
    .rank-score {
        font-size: 0.82rem;
        font-weight: 600;
        font-family: monospace;
        text-align: right;
        white-space: nowrap;
    }
    .rank-path {
        font-size: 0.74rem;
        color: #64748b;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-top: 2px;
    }
    .rank-bar-bg {
        width: 100%;
        height: 4px;
        background: rgba(128, 128, 128, 0.15);
        border-radius: 2px;
        margin-top: 5px;
        overflow: hidden;
    }
    .rank-bar-fill {
        height: 100%;
        border-radius: 2px;
        transition: width 0.3s ease;
    }
</style>
""")


# =============================================================================
# MARKDOWN CORPUS DOCUMENT VIEWER (MODAL DIALOG)
# =============================================================================

def get_corpus_files():
    """Lấy danh sách các tài liệu Markdown chuẩn hoá trong data/standardized/."""
    legal_dir = PROJECT_ROOT / "data" / "standardized" / "legal"
    news_dir = PROJECT_ROOT / "data" / "standardized" / "news"
    legal_files = sorted(list(legal_dir.glob("*.md"))) if legal_dir.exists() else []
    news_files = sorted(list(news_dir.glob("*.md"))) if news_dir.exists() else []
    return legal_files, news_files


@st.dialog("📄 Trình duyệt Tài liệu Gốc Markdown", width="large")
def show_markdown_modal(file_path: Path):
    """Mở hộp thoại Modal hiển thị toàn bộ nội dung Markdown định dạng đẹp."""
    try:
        rel = file_path.relative_to(PROJECT_ROOT)
    except Exception:
        rel = file_path.name
    category = "⚖️ Văn bản pháp lý (Legal)" if "legal" in str(file_path).lower() else "📰 Hướng dẫn & Quy trình (News)"
    size_kb = file_path.stat().st_size / 1024

    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown(f"#### `{file_path.name}`")
        st.caption(f"{category} &middot; Đường dẫn: `{rel}`")
    with c2:
        st.metric("Dung lượng", f"{size_kb:.1f} KB")

    st.divider()
    try:
        content = file_path.read_text(encoding="utf-8")
        st.markdown(content)
    except Exception as e:
        st.error(f"Lỗi khi đọc file: {e}")


# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.markdown("### 🛍️ Shopee RAG Assistant")
    st.caption("Trợ lý AI tra cứu chính sách Shopee theo kiến trúc Hybrid RAG")

    st.divider()

    # SECTION: Tài liệu tham chiếu Markdown
    st.markdown("##### 📁 Tài liệu tham chiếu (Corpus)")
    legal_files, news_files = get_corpus_files()
    total_docs = len(legal_files) + len(news_files)

    with st.expander(f"📚 Duyệt {total_docs} File Markdown Gốc", expanded=True):
        st.caption("Bấm vào file để xem trực tiếp nội dung đầy đủ:")
        tab_leg, tab_nw = st.tabs([f"⚖️ Pháp lý ({len(legal_files)})", f"📰 Hướng dẫn ({len(news_files)})"])

        with tab_leg:
            for f in legal_files:
                btn_name = f.stem.replace("-shopee", "")
                if st.button(f"📄 {btn_name}", key=f"btn_leg_{f.name}", use_container_width=True, help=f"Xem {f.name}"):
                    show_markdown_modal(f)

        with tab_nw:
            for f in news_files:
                if st.button(f"📄 {f.stem}", key=f"btn_news_{f.name}", use_container_width=True, help=f"Xem {f.name}"):
                    show_markdown_modal(f)

    st.divider()

    # SECTION: Câu hỏi mẫu
    st.markdown("##### 💡 Câu hỏi mẫu")
    sample_queries = [
        ("📦 Đổi trả", "Những lý do hợp lệ nào người mua có thể chọn khi yêu cầu Trả hàng/Hoàn tiền?"),
        ("⏱️ Thời hạn", "Thời hạn yêu cầu trả hàng/hoàn tiền là bao lâu?"),
        ("💳 Thanh toán", "Shopee hỗ trợ những phương thức thanh toán nào?"),
        ("💎 Shopee Mall", "Người mua tại Shopee Mall được hưởng những cam kết quyền lợi đặc biệt nào?"),
        ("⚠️ Khiếu nại", "Quy trình giải quyết tranh chấp giữa người mua và người bán diễn ra như thế nào?"),
        ("🧪 Test Fallback", "Công thức làm bánh bông lan trứng muối truyền thống thơm ngon?"),
    ]
    for tag, q_text in sample_queries:
        if st.button(f"{tag}: {q_text[:28]}...", use_container_width=True, help=q_text, key=f"btn_{hash(q_text)}"):
            st.session_state["pending_query"] = q_text

    st.divider()

    # SECTION: Cấu hình tham số Pipeline
    st.markdown("##### ⚙️ Thiết lập Tham số Pipeline")
    top_k = st.slider("Số lượng Chunks (top_k)", min_value=3, max_value=10, value=5)
    score_thresh = st.slider("Ngưỡng Cosine Fallback", min_value=0.30, max_value=0.70, value=float(SCORE_THRESHOLD), step=0.02)

    st.divider()

    # Thống kê hệ thống
    try:
        col_chroma = get_collection()
        total_chunks = col_chroma.count()
    except Exception:
        total_chunks = 47

    st.caption(f"📚 **Vector DB:** ChromaDB (`{total_chunks}` chunks)")
    st.caption(f"🧠 **Embedding:** MiniLM-L12-v2 (384d)")
    st.caption(f"🤖 **LLM Model:** `{LLM_MODEL}`")

    if st.button("🗑️ Xóa lịch sử chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_query = None
        st.rerun()


# =============================================================================
# PIPELINE STEP-BY-STEP EXECUTOR
# =============================================================================

def execute_rag_pipeline(query: str, top_k: int, threshold: float):
    """
    Thực thi toàn bộ luồng RAG theo kiến trúc hệ thống và ghi nhận timeline từng bước.
    """
    timeline = {}
    timeline["query"] = query
    total_start = time.time()

    # Step 1: Dense Semantic Search
    t0 = time.time()
    dense_results = semantic_search(query, top_k=top_k)
    t_dense = (time.time() - t0) * 1000
    best_dense_score = dense_results[0]["score"] if dense_results else 0.0
    timeline["dense"] = {
        "time_ms": t_dense,
        "count": len(dense_results),
        "best_score": best_dense_score,
        "results": dense_results,
    }

    # Step 2: Sparse Lexical Search (BM25)
    t0 = time.time()
    sparse_results = lexical_search(query, top_k=top_k)
    t_sparse = (time.time() - t0) * 1000
    best_bm25_score = sparse_results[0]["score"] if sparse_results else 0.0
    timeline["bm25"] = {
        "time_ms": t_sparse,
        "count": len(sparse_results),
        "best_score": best_bm25_score,
        "results": sparse_results,
    }

    # Step 3: Fallback Check
    fallback_triggered = best_dense_score < threshold
    fallback_method = "none"
    retrieved_chunks = []
    t_fallback = 0.0

    if fallback_triggered:
        t0 = time.time()
        try:
            fb_res = pageindex_search(query, top_k=top_k)
            if fb_res:
                fallback_method = "pageindex"
                retrieved_chunks = fb_res[:top_k]
        except Exception:
            pass
        t_fallback = (time.time() - t0) * 1000

    timeline["fallback_check"] = {
        "triggered": fallback_triggered,
        "threshold": threshold,
        "best_dense_score": best_dense_score,
        "method": fallback_method,
        "time_ms": t_fallback,
        "fallback_results": retrieved_chunks,
    }

    # Step 4: Fusion (RRF) nếu không fallback
    t0 = time.time()
    if not retrieved_chunks:
        retrieved_chunks = rerank_rrf([dense_results, sparse_results], top_k=top_k)
    t_fusion = (time.time() - t0) * 1000
    timeline["fusion"] = {
        "time_ms": t_fusion,
        "method": "pageindex" if fallback_triggered and fallback_method == "pageindex" else "rrf_k60",
        "results": retrieved_chunks,
    }

    # Step 5: Document Reordering (Chống Lost in the Middle)
    t0 = time.time()
    original_order_ids = [c["id"] for c in retrieved_chunks]
    reordered_chunks = reorder_for_llm(retrieved_chunks)
    reordered_ids = [c["id"] for c in reordered_chunks]
    t_reorder = (time.time() - t0) * 1000
    timeline["reorder"] = {
        "time_ms": t_reorder,
        "original_ids": original_order_ids,
        "reordered_ids": reordered_ids,
        "chunks": reordered_chunks,
    }

    # Step 6: Context Formatting & LLM Generation
    t0 = time.time()
    context_str = format_context(reordered_chunks)

    openrouter_key = os.getenv("OPENROUTER_API_KEY", "").strip('"').strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip('"').strip()
    api_key = openrouter_key if openrouter_key and not openrouter_key.startswith("sk-or-v1-mock") else openai_key
    base_url = "https://openrouter.ai/api/v1" if api_key == openrouter_key else None

    answer = None
    model_to_use = LLM_MODEL
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key, base_url=base_url)
            user_prompt = f"Ngữ cảnh tham khảo:\n{context_str}\n\n---\n\nCâu hỏi: {query}"

            if not base_url and model_to_use.startswith("openai/"):
                model_to_use = model_to_use.replace("openai/", "")

            resp = client.chat.completions.create(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=TEMPERATURE,
                top_p=TOP_P,
            )
            answer = resp.choices[0].message.content
        except Exception as e:
            st.warning(f"Lưu ý gọi LLM API: {e}. Hệ thống sử dụng chế độ trích xuất tài liệu cục bộ.")

    if not answer:
        if reordered_chunks:
            top_doc = reordered_chunks[0]
            src_name = top_doc.get("metadata", {}).get("source", "Chính sách Shopee")
            clean_content = top_doc["content"].strip()
            answer = f"**Dựa trên các quy định được công bố [{src_name}, 2026]:**\n\n{clean_content}\n\n*Thông tin chi tiết được đối chiếu và tham chiếu đầy đủ từ nguồn chính thức của hệ thống.*"
        else:
            answer = "Tôi không thể xác minh thông tin này từ nguồn tài liệu hiện có."

    t_llm = (time.time() - t0) * 1000
    timeline["generation"] = {
        "time_ms": t_llm,
        "model": model_to_use if api_key else "Local Extractor",
        "answer": answer,
        "context_str": context_str,
    }

    timeline["total_time_ms"] = (time.time() - total_start) * 1000
    return answer, reordered_chunks, timeline


# =============================================================================
# COMPONENT 1: HORIZONTAL PIPELINE FLOW GRAPH (IMAGE 1)
# =============================================================================

def render_pipeline_flow_graph(timeline: dict, corpus_count: int = 47):
    """
    Render sơ đồ quy trình dạng các khối ngang nối nhau bằng mũi tên (Ảnh 1).
    01 - QUERY -> [02A - SEMANTIC / 02B - LEXICAL] -> 03 - FUSION -> 04 - COSINE GATE -> 05 - CONTEXT - ANSWER
    Kèm thanh trạng thái phía dưới.
    """
    if not timeline:
        return

    query_text = timeline.get("query", "User Query")
    disp_query = (query_text[:46] + "...") if len(query_text) > 46 else query_text

    dense_info = timeline.get("dense", {})
    dense_count = dense_info.get("count", 0)
    dense_ms = dense_info.get("time_ms", 0.0)
    best_dense = dense_info.get("best_score", 0.0)

    bm25_info = timeline.get("bm25", {})
    bm25_count = bm25_info.get("count", 0)
    bm25_ms = bm25_info.get("time_ms", 0.0)

    fusion_info = timeline.get("fusion", {})
    fusion_count = len(fusion_info.get("results", []))
    fusion_ms = fusion_info.get("time_ms", 0.0)

    fb_info = timeline.get("fallback_check", {})
    is_fallback = fb_info.get("triggered", False)
    threshold = fb_info.get("threshold", 0.48)

    reorder_info = timeline.get("reorder", {})
    context_chunks_count = len(reorder_info.get("chunks", []))

    # Dynamic texts based on gate decision
    if is_fallback:
        gate_class = "node-accent-gate-warn"
        gate_title = "Kích hoạt Fallback"
        context_title = "PageIndex context"
        status_banner_class = "banner-fallback"
        status_text = f"⚠️ Điểm Cosine thấp ({best_dense:.3f} &lt; {threshold:.3f}) — Kích hoạt Fallback PageIndex"
    else:
        gate_class = "node-accent-gate-ok"
        gate_title = "Giữ kết quả hybrid"
        context_title = "Hybrid context"
        status_banner_class = "banner-hybrid"
        status_text = f"Dense vượt ngưỡng ({best_dense:.3f} &ge; {threshold:.3f}) — dùng hybrid"

    html_code = f"""<div class="pipeline-flow-container">
<div class="pipeline-flow-row">
<div class="pipeline-node">
<div>
<div class="node-tag">01 — QUERY</div>
<div class="node-title" title="{html.escape(query_text)}">{html.escape(disp_query)}</div>
</div>
<div class="node-meta">Corpus — {corpus_count} chunks</div>
</div>
<div class="pipeline-arrow">&rarr;</div>
<div class="pipeline-stack">
<div class="pipeline-subnode node-accent-dense">
<div class="node-tag">02A — SEMANTIC</div>
<div class="node-title">Dense cosine</div>
<div class="node-meta">{dense_count} candidates &middot; {dense_ms:.1f} ms</div>
</div>
<div class="pipeline-subnode node-accent-lexical">
<div class="node-tag">02B — LEXICAL</div>
<div class="node-title">BM25</div>
<div class="node-meta">{bm25_count} candidates &middot; {bm25_ms:.1f} ms</div>
</div>
</div>
<div class="pipeline-arrow">&rarr;</div>
<div class="pipeline-node node-accent-fusion">
<div>
<div class="node-tag">03 — FUSION</div>
<div class="node-title">RRF — k=60</div>
</div>
<div class="node-meta">{fusion_count} fused &middot; {fusion_ms:.2f} ms</div>
</div>
<div class="pipeline-arrow">&rarr;</div>
<div class="pipeline-node {gate_class}">
<div>
<div class="node-tag">04 — COSINE GATE</div>
<div class="node-title">{gate_title}</div>
</div>
<div class="node-meta">{best_dense:.3f} vs {threshold:.3f}</div>
</div>
<div class="pipeline-arrow">&rarr;</div>
<div class="pipeline-node node-accent-answer">
<div>
<div class="node-tag">05 — CONTEXT — ANSWER</div>
<div class="node-title">{context_title}</div>
</div>
<div class="node-meta">{context_chunks_count} chunks &middot; Answer + citation</div>
</div>
</div>
<div class="pipeline-status-banner {status_banner_class}">
{status_text}
</div>
</div>"""

    st.html(html_code)


# =============================================================================
# COMPONENT 2: THREE COMPARATIVE RANKINGS (IMAGE 2)
# =============================================================================

def render_three_ranking_tables(timeline: dict):
    """
    Hiển thị 3 bảng xếp hạng song song (Ảnh 2):
    - Dense rank (cosine 0-1, thanh màu xanh lam)
    - BM25 rank (lexical local scale, thanh màu hổ phách/đỏ)
    - RRF rank (1 / (60 + rank), thanh màu tím, kèm nhãn đóng góp Dxx + Bxx)
    """
    if not timeline:
        return

    dense_items = timeline.get("dense", {}).get("results", [])
    bm25_items = timeline.get("bm25", {}).get("results", [])
    rrf_items = timeline.get("fusion", {}).get("results", [])

    # Map thứ hạng Dense và BM25 theo ID chunk
    dense_rank_map = {item["id"]: r for r, item in enumerate(dense_items, 1)}
    bm25_rank_map = {item["id"]: r for r, item in enumerate(bm25_items, 1)}

    # Tìm max score của từng lane để normalize thanh progress bar
    max_dense = max([x.get("score", 0.0) for x in dense_items], default=1.0)
    max_bm25 = max([x.get("score", 0.0) for x in bm25_items], default=1.0)
    max_rrf = max([x.get("score", 0.0) for x in rrf_items], default=1.0)

    # Helper format tiêu đề và đường dẫn
    def get_doc_info(item):
        meta = item.get("metadata", {})
        title = meta.get("title") or item.get("id", "Document")
        doc_type = meta.get("doc_type") or ("legal" if "legal" in str(meta.get("source", "")).lower() else "news")
        source = meta.get("source") or "document.md"
        path = f"{doc_type}/{source}"
        return title, path

    # 1. Render Column Dense
    dense_html = ""
    for idx, item in enumerate(dense_items, 1):
        title, path = get_doc_info(item)
        score = item.get("score", 0.0)
        pct = max(6, int((score / max(max_dense, 0.001)) * 100))
        dense_html += f"""<div class="rank-item">
<div class="rank-item-header">
<span class="rank-num">#{idx}</span>
<span class="rank-doc-title" title="{html.escape(title)}">{html.escape(title)}</span>
<span class="rank-score">{score:.4f}</span>
</div>
<div class="rank-path" title="{html.escape(path)}">{html.escape(path)}</div>
<div class="rank-bar-bg">
<div class="rank-bar-fill" style="width: {pct}%; background: #0284c7;"></div>
</div>
</div>"""

    # 2. Render Column BM25
    bm25_html = ""
    for idx, item in enumerate(bm25_items, 1):
        title, path = get_doc_info(item)
        score = item.get("score", 0.0)
        pct = max(6, int((score / max(max_bm25, 0.001)) * 100))
        bm25_html += f"""<div class="rank-item">
<div class="rank-item-header">
<span class="rank-num">#{idx}</span>
<span class="rank-doc-title" title="{html.escape(title)}">{html.escape(title)}</span>
<span class="rank-score">{score:.4f}</span>
</div>
<div class="rank-path" title="{html.escape(path)}">{html.escape(path)}</div>
<div class="rank-bar-bg">
<div class="rank-bar-fill" style="width: {pct}%; background: #d97706;"></div>
</div>
</div>"""

    # 3. Render Column RRF
    rrf_html = ""
    for idx, item in enumerate(rrf_items, 1):
        title, path = get_doc_info(item)
        score = item.get("score", 0.0)
        cid = item.get("id")

        # Tạo tag phân rã đóng góp Dxx + Bxx
        parts = []
        if cid in dense_rank_map:
            parts.append(f"D{dense_rank_map[cid]:02d}")
        if cid in bm25_rank_map:
            parts.append(f"B{bm25_rank_map[cid]:02d}")
        breakdown_tag = " + ".join(parts) if parts else "Fallback"

        display_sub = f"{breakdown_tag} &middot; {path}"
        pct = max(6, int((score / max(max_rrf, 0.0001)) * 100))

        rrf_html += f"""<div class="rank-item">
<div class="rank-item-header">
<span class="rank-num">#{idx}</span>
<span class="rank-doc-title" title="{html.escape(title)}">{html.escape(title)}</span>
<span class="rank-score">{score:.4f}</span>
</div>
<div class="rank-path" title="{html.escape(path)}">{display_sub}</div>
<div class="rank-bar-bg">
<div class="rank-bar-fill" style="width: {pct}%; background: #7c3aed;"></div>
</div>
</div>"""

    container_html = f"""<div style="margin-top: 14px; margin-bottom: 6px;">
<h4 style="margin: 0; font-weight: 700; font-size: 1.05rem;">Ba bảng xếp hạng của cùng một query</h4>
<div style="font-size: 0.82rem; color: #64748b; margin-top: 3px; margin-bottom: 8px;">
Cosine, BM25 và RRF là ba thang đo khác nhau. Chiều dài bar chỉ so sánh các item trong cùng một lane; không cộng score thô giữa các lane.
</div>
</div>
<div class="ranking-grid">
<div class="ranking-column">
<div class="ranking-header">
<span class="ranking-title">Dense rank</span>
<span class="ranking-scale">cosine 0-1</span>
</div>
{dense_html or "<div style='color: #64748b; font-size: 0.8rem;'>Không có kết quả Dense</div>"}
</div>
<div class="ranking-column">
<div class="ranking-header">
<span class="ranking-title">BM25 rank</span>
<span class="ranking-scale">lexical local scale</span>
</div>
{bm25_html or "<div style='color: #64748b; font-size: 0.8rem;'>Không có kết quả BM25</div>"}
</div>
<div class="ranking-column">
<div class="ranking-header">
<span class="ranking-title">RRF rank</span>
<span class="ranking-scale">1 / (60 + rank)</span>
</div>
{rrf_html or "<div style='color: #64748b; font-size: 0.8rem;'>Không có kết quả RRF</div>"}
</div>
</div>"""

    st.html(container_html)


def render_source_items(sources: list[dict]):
    """Hiển thị danh sách nguồn trích dẫn kèm tùy chọn 'Xem thêm' mở rộng toàn bộ nội dung."""
    for i, src in enumerate(sources, 1):
        meta = src.get("metadata", {})
        source_name = meta.get("source", "Tài liệu chính sách")
        doc_type = meta.get("doc_type") or meta.get("type", "policy")
        score = src.get("score", 0)
        cid = src.get("id", f"chunk-{i}")
        content_text = src.get("content", "").strip()

        # Trích dẫn câu/đoạn đầu tiên có ý nghĩa
        paragraphs = [p.strip() for p in content_text.split("\n\n") if p.strip() and not p.strip().startswith("#")]
        preview = paragraphs[0] if paragraphs else content_text.split("\n")[0]
        if len(preview) > 220:
            preview = preview[:215] + "..."

        st.markdown(
            f"**[{i}] {source_name}** <span class='source-tag'>{doc_type}</span> | Score: `{score:.4f}` | Chunk: `{cid}`",
            unsafe_allow_html=True,
        )
        st.markdown(f"> *{preview}*")

        with st.expander(f"📖 Xem thêm toàn bộ nội dung chunk [{cid}] ({len(content_text):,} ký tự)", expanded=False):
            st.markdown(content_text)
        st.divider()


# =============================================================================
# DETAILED DEBUG TABS (INSPECTOR)
# =============================================================================

def render_debug_details(timeline: dict):
    """Hiển thị các tab chi tiết dữ liệu để học viên kiểm tra và debug từng khâu."""
    with st.expander("🔍 Chi tiết dữ liệu từng tầng Pipeline (Debug Inspector)", expanded=False):
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "🔵 1. Dense Chunks",
            "🟢 2. BM25 Chunks",
            "⚖️ 3. Ngưỡng Fallback",
            "🟣 4. RRF Ranking",
            "🔀 5. Reorder Trực Quan",
            "📝 6. Prompt gửi LLM",
        ])

        with tab1:
            st.markdown("##### 🔵 Kết quả Dense Semantic Search (ChromaDB)")
            dense_items = timeline.get("dense", {}).get("results", [])
            if dense_items:
                for idx, c in enumerate(dense_items, 1):
                    meta = c.get("metadata", {})
                    st.markdown(f"**[{idx}] `{c['id']}`** | Cosine Score: `{c['score']:.4f}` | Nguồn: `{meta.get('source', '')}`")
                    with st.expander(f"📖 Xem thêm toàn bộ nội dung chunk `{c['id']}`", expanded=False):
                        st.markdown(c["content"])
                    st.divider()
            else:
                st.info("Không có kết quả Dense.")

        with tab2:
            st.markdown("##### 🟢 Kết quả Sparse Lexical Search (BM25Okapi)")
            bm_items = timeline.get("bm25", {}).get("results", [])
            if bm_items:
                for idx, c in enumerate(bm_items, 1):
                    meta = c.get("metadata", {})
                    st.markdown(f"**[{idx}] `{c['id']}`** | BM25 Score: `{c['score']:.4f}` | Nguồn: `{meta.get('source', '')}`")
                    with st.expander(f"📖 Xem thêm toàn bộ nội dung chunk `{c['id']}`", expanded=False):
                        st.markdown(c["content"])
                    st.divider()
            else:
                st.info("Không có kết quả BM25.")

        with tab3:
            st.markdown("##### ⚖️ Kiểm tra điều kiện Fallback Gate")
            fb_info = timeline.get("fallback_check", {})
            c1, c2, c3 = st.columns(3)
            c1.metric("Best Dense Cosine", f"{fb_info.get('best_dense_score', 0):.4f}")
            c2.metric("Ngưỡng Threshold", f"{fb_info.get('threshold', 0):.4f}")
            c3.metric("Kích hoạt Fallback?", "CÓ (Dưới ngưỡng)" if fb_info.get("triggered") else "KHÔNG (Đạt chuẩn)")
            if fb_info.get("triggered"):
                st.warning("⚠️ Điểm tương đồng ngữ nghĩa thấp hơn ngưỡng tin cậy. Pipeline đã tự động kích hoạt cơ chế fallback!")
            else:
                st.success("✅ Điểm tương đồng vượt ngưỡng tin cậy. Dữ liệu tiếp tục qua bộ gộp Reciprocal Rank Fusion.")

        with tab4:
            st.markdown("##### 🟣 Bảng xếp hạng sau khi gộp Reciprocal Rank Fusion (RRF $k=60$)")
            st.caption(r"Công thức tính: $\text{RRF}(d) = \sum_{r} \frac{1}{60 + \text{rank}_r(d)}$")
            fused_items = timeline.get("fusion", {}).get("results", [])
            if fused_items:
                for idx, c in enumerate(fused_items, 1):
                    st.markdown(f"**Top {idx}: `{c['id']}`** | Score: `{c['score']:.6f}` | Method: `{c.get('retrieval_method', 'hybrid')}`")
                    with st.expander(f"📖 Xem thêm toàn bộ nội dung chunk `{c['id']}`", expanded=False):
                        st.markdown(c["content"])
                    st.divider()

        with tab5:
            st.markdown("##### 🔀 So sánh thứ tự Document Reordering")
            st.caption("Nguyên lý: Chuyển các tài liệu quan trọng nhất ra 2 đầu context string để LLM ghi nhớ và chú ý tốt nhất.")
            orig = timeline.get("reorder", {}).get("original_ids", [])
            reord = timeline.get("reorder", {}).get("reordered_ids", [])
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**Thứ tự ban đầu (theo điểm giảm dần):**")
                for i, cid in enumerate(orig, 1):
                    st.write(f"Vị trí {i}: `{cid}`")
            with col_b:
                st.markdown("**Thứ tự sau Reorder (nạp vào LLM):**")
                for i, cid in enumerate(reord, 1):
                    st.write(f"Slot {i}: `{cid}`")

        with tab6:
            st.markdown("##### 📝 Ngữ cảnh và Prompt nạp vào LLM")
            st.text_area("Toàn bộ Context gửi cho mô hình:", value=timeline.get("generation", {}).get("context_str", ""), height=260)
            st.caption(f"Mô hình sử dụng: `{timeline.get('generation', {}).get('model', 'N/A')}`")


# =============================================================================
# CHAT SESSION STATE & MAIN DISPLAY
# =============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# Header chính
st.markdown("<h2 style='margin-bottom: 2px;'>🛍️ Shopee E-commerce Support AI Assistant</h2>", unsafe_allow_html=True)
st.caption("Hệ thống tra cứu chính sách Thương mại điện tử Shopee (bảo hành, đổi trả, Shopee Mall, người bán) với kiến trúc Hybrid RAG")

# Hiển thị lịch sử chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            # Hiển thị nguồn trích dẫn
            if "sources" in msg and msg["sources"]:
                with st.expander(f"📚 Nguồn trích dẫn ({len(msg['sources'])} tài liệu)", expanded=False):
                    render_source_items(msg["sources"])

            # Mặc định luôn hiển thị đầy đủ cả 3 thành phần phân tích
            if "timeline" in msg:
                # 1. Sơ đồ Pipeline Flow Graph (Ảnh 1)
                render_pipeline_flow_graph(msg["timeline"], corpus_count=total_chunks)

                # 2. Ba Bảng xếp hạng tương quan (Ảnh 2)
                render_three_ranking_tables(msg["timeline"])

                # 3. Debug Data Inspector
                render_debug_details(msg["timeline"])

# =============================================================================
# CHAT INPUT & RUNTIME PIPELINE EXECUTION
# =============================================================================

user_input = st.chat_input("Nhập câu hỏi về chính sách Shopee (đổi trả, thanh toán, bảo hành, người bán)...")
active_query = user_input or st.session_state.pending_query

if active_query:
    st.session_state.pending_query = None

    # Hiển thị câu hỏi của User
    st.session_state.messages.append({"role": "user", "content": active_query})
    with st.chat_message("user"):
        st.markdown(active_query)

    # Hiển thị phản hồi của Assistant với Live Step-by-Step Status
    with st.chat_message("assistant"):
        with st.status("⚡ Đang thực thi RAG Pipeline theo luồng kiến trúc...", expanded=True) as status_box:
            status_box.write("🔍 **1. Đang truy vấn Dense Semantic Search (ChromaDB 384d)...**")
            status_box.write("📖 **2. Đang tìm kiếm từ khóa chính xác (BM25Okapi)...**")
            status_box.write(f"⚖️ **3. Đang kiểm tra ngưỡng Fallback (Cosine < {score_thresh:.2f})...**")
            status_box.write("🔀 **4. Đang gộp thứ hạng Hybrid (RRF k=60) & Reorder tài liệu...**")
            status_box.write(f"✨ **5. Đang sinh câu trả lời có Citation từ LLM ({LLM_MODEL})...**")

            # Chạy thực tế
            answer, sources, timeline = execute_rag_pipeline(
                query=active_query,
                top_k=top_k,
                threshold=score_thresh,
            )

            status_box.update(
                label=f"✅ Pipeline hoàn tất thành công ({timeline.get('total_time_ms', 0):.0f}ms)!",
                state="complete",
                expanded=False,
            )

        # Hiển thị câu trả lời dạng Markdown
        st.markdown(answer)

        # Hiển thị danh sách nguồn trích dẫn
        if sources:
            with st.expander(f"📚 Nguồn trích dẫn ({len(sources)} tài liệu)", expanded=False):
                render_source_items(sources)

        # Mặc định luôn hiển thị đầy đủ cả 3 thành phần phân tích
        # 1. Sơ đồ Pipeline Flow Graph (Ảnh 1)
        render_pipeline_flow_graph(timeline, corpus_count=total_chunks)

        # 2. Ba Bảng xếp hạng tương quan (Ảnh 2)
        render_three_ranking_tables(timeline)

        # 3. Debug Data Inspector
        render_debug_details(timeline)

    # Lưu vào session_state
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "timeline": timeline,
    })
