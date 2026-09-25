import time

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Shopee RAG Chatbot — Chính sách Hoàn trả",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Main background ── */
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    min-height: 100vh;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.04);
    border-right: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(20px);
}
[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

/* ── Header banner ── */
.hero-banner {
    background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 24px;
    box-shadow: 0 8px 32px rgba(238,9,121,0.35);
    display: flex;
    align-items: center;
    gap: 16px;
}
.hero-banner h1 {
    color: white !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    margin: 0 !important;
    text-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
.hero-banner p {
    color: rgba(255,255,255,0.85) !important;
    font-size: 0.9rem !important;
    margin: 4px 0 0 0 !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
    backdrop-filter: blur(10px) !important;
    margin-bottom: 12px !important;
    padding: 4px !important;
    color: #e2e8f0 !important;
}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span {
    color: #e2e8f0 !important;
}

/* ── User message ── */
[data-testid="stChatMessage"][data-testid*="user"] {
    background: linear-gradient(135deg, rgba(238,9,121,0.15) 0%, rgba(255,106,0,0.15) 100%) !important;
    border-color: rgba(238,9,121,0.3) !important;
}

/* ── Source cards ── */
.source-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 10px;
    transition: all 0.2s ease;
}
.source-card:hover {
    background: rgba(255,255,255,0.1);
    border-color: rgba(238,9,121,0.4);
    transform: translateX(4px);
}
.source-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    margin-right: 6px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.badge-dense   { background: rgba(99,102,241,0.25); color: #a5b4fc; border: 1px solid rgba(99,102,241,0.4); }
.badge-bm25    { background: rgba(34,197,94,0.2);   color: #86efac; border: 1px solid rgba(34,197,94,0.4); }
.badge-hybrid  { background: rgba(251,146,60,0.2);  color: #fed7aa; border: 1px solid rgba(251,146,60,0.4); }
.badge-pageindex { background: rgba(236,72,153,0.2); color: #f9a8d4; border: 1px solid rgba(236,72,153,0.4); }
.badge-legal   { background: rgba(59,130,246,0.2);  color: #93c5fd; border: 1px solid rgba(59,130,246,0.4); }
.badge-news    { background: rgba(168,85,247,0.2);  color: #d8b4fe; border: 1px solid rgba(168,85,247,0.4); }

.score-bar-bg {
    background: rgba(255,255,255,0.08);
    border-radius: 4px;
    height: 5px;
    margin-top: 8px;
    overflow: hidden;
}
.score-bar-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, #ee0979, #ff6a00);
    transition: width 0.6s ease;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    padding: 12px !important;
}
[data-testid="metric-container"] label,
[data-testid="metric-container"] [data-testid="stMetricValue"],
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    color: #e2e8f0 !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(238,9,121,0.4) !important;
    border-radius: 14px !important;
    color: #e2e8f0 !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(238,9,121,0.8) !important;
    box-shadow: 0 0 0 3px rgba(238,9,121,0.15) !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] p,
[data-testid="stExpander"] span {
    color: #cbd5e1 !important;
}

/* ── Buttons ── */
.stButton button {
    background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
.stButton button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(238,9,121,0.4) !important;
}

/* ── Slider ── */
[data-testid="stSlider"] * { color: #e2e8f0 !important; }
[data-testid="stSlider"] [data-testid="stTickBar"] { background: rgba(238,9,121,0.4) !important; }

/* ── Welcome screen ── */
.welcome-card {
    background: rgba(255,255,255,0.04);
    border: 1px dashed rgba(238,9,121,0.35);
    border-radius: 16px;
    padding: 40px 32px;
    text-align: center;
    margin: 32px 0;
}
.welcome-card h2 { color: #e2e8f0 !important; font-size: 1.4rem; margin-bottom: 12px; }
.welcome-card p  { color: #94a3b8 !important; font-size: 0.95rem; }
.suggested-chip {
    display: inline-block;
    background: rgba(238,9,121,0.12);
    border: 1px solid rgba(238,9,121,0.3);
    color: #fda4af !important;
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.85rem;
    margin: 4px;
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ───────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "stats" not in st.session_state:
    st.session_state.stats = {"total": 0, "hybrid": 0, "pageindex": 0, "none": 0}

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛍️ Shopee RAG")
    st.markdown("**Chính sách Hoàn trả & Hoàn tiền**")
    st.divider()

    st.markdown("#### ⚙️ Cấu hình Retrieval")
    top_k = st.slider("Số chunks truy xuất (top-k)", 3, 10, 5)
    score_threshold = st.slider("Score threshold (fallback)", 0.1, 0.9, 0.3, 0.05)
    use_reranking = st.toggle("Dùng RRF Reranking", value=True)

    st.divider()
    st.markdown("#### 📊 Thống kê phiên")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Tổng câu hỏi", st.session_state.stats["total"])
        st.metric("Hybrid hits", st.session_state.stats["hybrid"])
    with col2:
        st.metric("PageIndex", st.session_state.stats["pageindex"])
        st.metric("No result", st.session_state.stats["none"])

    st.divider()
    if st.button("🗑️ Xóa lịch sử chat"):
        st.session_state.messages = []
        st.session_state.stats = {"total": 0, "hybrid": 0, "pageindex": 0, "none": 0}
        st.rerun()

    st.divider()
    st.markdown("#### 📚 Nguồn tài liệu")
    st.markdown("""
    - 📄 Chính sách hoàn trả chung  
    - 📄 Sản phẩm không được hoàn  
    - 📄 Hoàn trả do đổi ý  
    - 📰 Quy trình gửi yêu cầu  
    - 📰 Tracking đơn hoàn  
    - 📰 Xét duyệt yêu cầu  
    - 📰 Bằng chứng hoàn trả  
    - 📰 Phí vận chuyển hoàn  
    - 📰 Thời gian & phương thức  
    - 📰 Tranh chấp với người bán  
    """)

# ── Hero Banner ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div style="font-size:3rem">🛍️</div>
    <div>
        <h1>Shopee — Tư vấn Hoàn trả & Hoàn tiền</h1>
        <p>Powered by RAG Pipeline · Hybrid Retrieval · Anthropic Claude · ChromaDB + BM25</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Helper functions ─────────────────────────────────────────────────────────
METHOD_BADGE = {
    "dense":     '<span class="source-badge badge-dense">Dense</span>',
    "bm25":      '<span class="source-badge badge-bm25">BM25</span>',
    "hybrid":    '<span class="source-badge badge-hybrid">Hybrid</span>',
    "pageindex": '<span class="source-badge badge-pageindex">PageIndex</span>',
}
TYPE_BADGE = {
    "legal": '<span class="source-badge badge-legal">Legal</span>',
    "news":  '<span class="source-badge badge-news">News</span>',
}

SUGGESTED = [
    "Tôi có thể trả hàng trong bao nhiêu ngày?",
    "Những sản phẩm nào không được hoàn trả?",
    "Làm thế nào để gửi yêu cầu hoàn tiền?",
    "Hoàn tiền mất bao lâu để nhận được?",
    "Người bán từ chối hoàn trả thì phải làm gì?",
    "Phí vận chuyển hoàn hàng ai chịu?",
]


def render_sources(sources: list[dict]) -> None:
    if not sources:
        return
    with st.expander(f"📎 Nguồn trích dẫn ({len(sources)} tài liệu)", expanded=False):
        for i, src in enumerate(sources, 1):
            meta = src.get("metadata", {})
            title = meta.get("title", "Không rõ tiêu đề")
            source = meta.get("source", "")
            doc_type = meta.get("doc_type", "news")
            url = meta.get("url")
            score = src.get("score", 0.0)
            method = src.get("retrieval_method", "hybrid")
            content_preview = src.get("content", "")[:220].replace("\n", " ")

            badge_method = METHOD_BADGE.get(method, "")
            badge_type = TYPE_BADGE.get(doc_type, "")
            score_pct = int(min(score * 100, 100))
            score_color = "#ee0979" if score >= 0.5 else "#fb923c" if score >= 0.3 else "#64748b"

            url_html = f'<a href="{url}" target="_blank" style="color:#f9a8d4;font-size:0.78rem">🔗 Xem nguồn</a>' if url else ""

            st.markdown(f"""
<div class="source-card">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
        <div>
            <span style="color:#e2e8f0;font-weight:600;font-size:0.9rem">[{i}] {title}</span><br>
            <span style="color:#64748b;font-size:0.78rem">{source}</span>
        </div>
        <div style="text-align:right">
            <span style="color:{score_color};font-weight:700;font-size:0.9rem">{score:.3f}</span><br>
            <span style="color:#64748b;font-size:0.75rem">score</span>
        </div>
    </div>
    <div style="margin-bottom:8px">{badge_method}{badge_type} {url_html}</div>
    <div style="color:#94a3b8;font-size:0.82rem;line-height:1.5">{content_preview}…</div>
    <div class="score-bar-bg"><div class="score-bar-fill" style="width:{score_pct}%"></div></div>
</div>
""", unsafe_allow_html=True)


# ── Welcome screen ────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
<div class="welcome-card">
    <h2>👋 Xin chào! Tôi có thể giúp gì cho bạn?</h2>
    <p>Tôi được xây dựng trên dữ liệu chính sách hoàn trả & hoàn tiền Shopee.<br>
    Hãy đặt câu hỏi bên dưới hoặc chọn gợi ý có sẵn:</p>
</div>
""", unsafe_allow_html=True)
    cols = st.columns(3)
    for idx, suggestion in enumerate(SUGGESTED):
        with cols[idx % 3]:
            if st.button(f"💬 {suggestion}", key=f"suggest_{idx}", use_container_width=True):
                st.session_state["pending_query"] = suggestion
                st.rerun()

# ── Render chat history ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources") is not None:
            # Metadata bar
            retrieval_src = msg.get("retrieval_source", "none")
            latency = msg.get("latency", 0)
            num_sources = len(msg["sources"])
            c1, c2, c3 = st.columns(3)
            c1.metric("📡 Retrieval", retrieval_src.upper())
            c2.metric("📚 Chunks", num_sources)
            c3.metric("⏱️ Latency", f"{latency:.1f}s")
            render_sources(msg["sources"])

# ── Process pending suggestion query ─────────────────────────────────────────
if "pending_query" in st.session_state:
    query = st.session_state.pop("pending_query")
else:
    query = st.chat_input("Nhập câu hỏi về chính sách hoàn trả Shopee...")

# ── Handle query ──────────────────────────────────────────────────────────────
if query:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("🔍 Đang truy xuất tài liệu và tạo câu trả lời..."):
            t0 = time.perf_counter()
            try:
                from src.task10_generation import generate_with_citation

                result = generate_with_citation(
                    query,
                    top_k=top_k,
                )
                # Override threshold and reranking via direct retrieve call
                # (re-use result from task10, which uses .env threshold)
                answer = result["answer"]
                sources = result["sources"]
                retrieval_source = result["retrieval_source"]
                error = None
            except Exception as exc:
                answer = f"⚠️ Lỗi hệ thống: {exc}\n\nVui lòng thử lại hoặc kiểm tra cấu hình."
                sources = []
                retrieval_source = "none"
                error = str(exc)

            latency = time.perf_counter() - t0

        # Display answer
        st.markdown(answer)

        # Metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("📡 Retrieval", retrieval_source.upper())
        c2.metric("📚 Chunks", len(sources))
        c3.metric("⏱️ Latency", f"{latency:.1f}s")

        # Sources
        render_sources(sources)

    # Update stats
    st.session_state.stats["total"] += 1
    st.session_state.stats[retrieval_source] = (
        st.session_state.stats.get(retrieval_source, 0) + 1
    )

    # Save to history
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "retrieval_source": retrieval_source,
        "latency": latency,
    })
