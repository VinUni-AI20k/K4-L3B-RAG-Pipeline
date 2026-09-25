import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation

load_dotenv()

# ──────────────────────── Page config ────────────────────────
st.set_page_config(
    page_title="Trợ lý Tuyển sinh Đại học",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────── Data statistics ────────────────────
STANDARDIZED_DIR = Path(__file__).parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent / "chroma_db"


def count_documents():
    """Count legal docs, news articles, and estimate chunks."""
    legal_dir = STANDARDIZED_DIR / "legal"
    news_dir = STANDARDIZED_DIR / "news"
    legal_count = len([f for f in legal_dir.glob("*.md")]) if legal_dir.exists() else 0
    news_count = len([f for f in news_dir.glob("*.md")]) if news_dir.exists() else 0
    # Estimate chunks: ~5-6 chunks per document on average
    chunk_estimate = (legal_count + news_count) * 6
    # Try to get actual count from ChromaDB if available
    try:
        import chromadb
        if CHROMA_DIR.exists():
            client = chromadb.PersistentClient(path=str(CHROMA_DIR))
            collection = client.get_collection("rag_documents")
            chunk_estimate = collection.count()
    except Exception:
        pass
    return legal_count, news_count, chunk_estimate


legal_count, news_count, chunk_count = count_documents()

# ──────────────────────── Suggested questions ────────────────
SUGGESTED_QUESTIONS = [
    "Có những phương thức xét tuyển đại học nào?",
    "Điểm ưu tiên khu vực được tính như thế nào?",
    "Học phí trường tự chủ tài chính khác gì trường chưa tự chủ?",
    "Điểm chuẩn ngành Công nghệ thông tin năm 2024 khoảng bao nhiêu?",
    "Chỉ tiêu tuyển sinh được phân bổ ra sao?",
]

# ──────────────────────── CSS ────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700;800&family=DM+Serif+Display&display=swap');

    :root {
        --primary: #2c4a7c;
        --primary-light: #3d6098;
        --primary-dark: #1e3558;
        --accent: #4a90d9;
        --accent-light: #e8f0fc;
        --teal: #087f8c;
        --gold: #e2a92b;
        --ink: #1a2332;
        --muted: #5a6a7e;
        --light-muted: #8896a8;
        --line: #dde3ea;
        --paper: #f4f6f9;
        --card-bg: #ffffff;
        --sidebar-bg: #1e2d3d;
        --sidebar-accent: #2a4058;
        --gradient-start: #2c4a7c;
        --gradient-end: #4a90d9;
    }

    html, body, [class*="css"] {
        font-family: 'Be Vietnam Pro', sans-serif !important;
    }

    /* ── App background ── */
    .stApp {
        background: var(--paper);
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a2a3a 0%, #162230 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    [data-testid="stSidebar"] * {
        color: #e0e8f0 !important;
    }
    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] .stCaption * {
        color: #8ba3b8 !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.08) !important;
    }

    /* ── Stat cards row ── */
    .stat-row {
        display: flex;
        gap: 10px;
        margin: 16px 0 20px 0;
    }
    .stat-card {
        flex: 1;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px;
        padding: 14px 10px 10px;
        text-align: center;
        transition: all 0.2s ease;
    }
    .stat-card:hover {
        background: rgba(255,255,255,0.1);
        transform: translateY(-1px);
    }
    .stat-icon {
        font-size: 16px;
        margin-bottom: 4px;
        opacity: 0.7;
    }
    .stat-number {
        font-size: 24px;
        font-weight: 800;
        color: #fff !important;
        line-height: 1.1;
    }
    .stat-label {
        font-size: 11px;
        color: #8ba3b8 !important;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-top: 3px;
    }

    /* ── Suggested questions (sidebar) ── */
    .sq-header {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #8ba3b8 !important;
        margin: 20px 0 10px 0;
    }

    /* Style for suggested question buttons */
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #c8d6e0 !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        text-align: left !important;
        font-size: 13px !important;
        font-weight: 400 !important;
        line-height: 1.4 !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(74, 144, 217, 0.15) !important;
        border-color: rgba(74, 144, 217, 0.3) !important;
        color: #fff !important;
        transform: translateX(3px);
    }

    /* ── Main chat area header ── */
    .chat-header {
        text-align: center;
        padding: 48px 20px 36px;
    }
    .chat-header-icon {
        width: 68px;
        height: 68px;
        margin: 0 auto 20px;
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 30px;
        box-shadow: 0 8px 28px rgba(44,74,124,0.25);
    }
    .chat-header h1 {
        font-family: 'DM Serif Display', Georgia, serif !important;
        font-size: clamp(1.8rem, 3.5vw, 2.6rem);
        color: var(--ink);
        margin: 0 0 12px 0;
        line-height: 1.15;
    }
    .chat-header p {
        color: var(--muted);
        font-size: 0.95rem;
        line-height: 1.7;
        max-width: 560px;
        margin: 0 auto;
    }

    /* ── Topic badge (top bar) ── */
    .top-badge {
        display: flex;
        align-items: center;
        gap: 12px;
        background: var(--card-bg);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 14px 22px;
        margin-bottom: 6px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }
    .top-badge-icon {
        width: 42px;
        height: 42px;
        background: linear-gradient(135deg, var(--primary), var(--accent));
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        flex-shrink: 0;
    }
    .top-badge-text h3 {
        margin: 0;
        font-size: 15px;
        font-weight: 700;
        color: var(--ink);
    }
    .top-badge-text span {
        font-size: 12px;
        color: var(--light-muted);
        font-weight: 400;
    }

    /* ── Topic cards ── */
    .topic-cards {
        display: flex;
        gap: 14px;
        margin: 28px 0;
        flex-wrap: wrap;
        justify-content: center;
    }
    .topic-card {
        flex: 1;
        min-width: 220px;
        max-width: 280px;
        background: var(--card-bg);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 22px 18px;
        transition: all 0.25s ease;
        cursor: default;
    }
    .topic-card:hover {
        border-color: var(--accent);
        box-shadow: 0 6px 24px rgba(74,144,217,0.12);
        transform: translateY(-3px);
    }
    .topic-card-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        margin-bottom: 12px;
    }
    .topic-card-icon.blue {
        background: var(--accent-light);
        color: var(--primary);
    }
    .topic-card-icon.teal {
        background: #e0f5f5;
        color: var(--teal);
    }
    .topic-card-icon.gold {
        background: #fdf4e0;
        color: #c48a15;
    }
    .topic-card-icon.purple {
        background: #ece5f8;
        color: #6a45a0;
    }
    .topic-card h4 {
        margin: 0 0 6px 0;
        font-size: 14px;
        font-weight: 700;
        color: var(--ink);
    }
    .topic-card p {
        margin: 0;
        font-size: 12.5px;
        color: var(--muted);
        line-height: 1.55;
    }

    /* ── Chat messages ── */
    .stChatMessage {
        border-radius: 12px !important;
        border: 1px solid var(--line) !important;
        background: var(--card-bg) !important;
        margin-bottom: 8px;
    }

    /* ── Chat input ── */
    [data-testid="stChatInput"] {
        border-color: var(--line) !important;
    }
    [data-testid="stChatInput"] textarea {
        font-family: 'Be Vietnam Pro', sans-serif !important;
    }

    /* ── Source cards ── */
    .source-card {
        border-top: 1px solid var(--line);
        padding: 10px 0;
    }
    .source-card:first-child {
        border-top: none;
    }
    .source-title {
        font-weight: 700;
        color: var(--ink);
        font-size: 13.5px;
    }
    .source-meta {
        color: var(--light-muted);
        font-size: 12px;
    }

    /* ── Footer hint ── */
    .footer-hint {
        text-align: center;
        font-size: 11.5px;
        color: var(--light-muted);
        margin-top: 6px;
        padding: 4px 0;
    }

    /* ── Metric override ── */
    div[data-testid="stMetric"] {
        background: var(--card-bg);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 10px;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        font-weight: 600 !important;
        font-size: 13px !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #c0c8d0; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #a0a8b0; }

    /* ── Hide default Streamlit header/footer ── */
    #MainMenu { visibility: hidden; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────── Session state ──────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ──────────────────────── Sidebar ────────────────────────────
with st.sidebar:
    st.markdown("## 🎓 Tuyển sinh ĐH 2026")
    st.caption("RAG chatbot · Xét tuyển · Chỉ tiêu · Học phí · Điểm chuẩn")
    st.divider()

    # ── Stat cards ──
    st.markdown(
        f"""
        <div class="stat-row">
            <div class="stat-card">
                <div class="stat-icon">📋</div>
                <div class="stat-number">{legal_count}</div>
                <div class="stat-label">Chính sách</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📰</div>
                <div class="stat-number">{news_count}</div>
                <div class="stat-label">Bài viết</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🧩</div>
                <div class="stat-number">{chunk_count}</div>
                <div class="stat-label">Chunks</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Suggested questions ──
    st.markdown(
        '<div class="sq-header">✨ CÂU HỎI GỢI Ý</div>',
        unsafe_allow_html=True,
    )

    for i, question in enumerate(SUGGESTED_QUESTIONS):
        if st.button(question, key=f"sq_{i}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": question})
            st.session_state["pending_question"] = question
            st.rerun()

    st.divider()

    # ── Document count slider ──
    st.markdown(
        '<div class="sq-header">⚙️ CÀI ĐẶT</div>',
        unsafe_allow_html=True,
    )
    top_k = st.slider("Số nguồn tham khảo", min_value=3, max_value=10, value=5)
    st.caption("Câu trả lời chỉ dựa trên bộ tài liệu đã được lập chỉ mục.")

    st.divider()

    # ── BỘ TÀI LIỆU ──
    total_docs = legal_count + news_count
    st.markdown(
        f'<div class="sq-header">📚 BỘ TÀI LIỆU ({total_docs})</div>',
        unsafe_allow_html=True,
    )
    st.caption("Dữ liệu tuyển sinh từ các nguồn chính thống đã kiểm chứng.")

    st.divider()

    if st.button("🗑️ Xóa lịch sử trò chuyện", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ──────────────────────── Main content ───────────────────────

# ── Top badge bar ──
st.markdown(
    """
    <div class="top-badge">
        <div class="top-badge-icon">🎓</div>
        <div class="top-badge-text">
            <h3>Trợ lý Tuyển sinh Đại học</h3>
            <span>RAG chatbot · Xét tuyển · Chỉ tiêu · Học phí · Điểm chuẩn</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Welcome header (only when no messages) ──
if not st.session_state.messages:
    st.markdown(
        """
        <div class="chat-header">
            <div class="chat-header-icon">🎓</div>
            <h1>Hỏi đáp về Tuyển sinh Đại học</h1>
            <p>Đặt câu hỏi về phương thức xét tuyển, chỉ tiêu, học phí và điểm chuẩn.
            Mọi câu trả lời đều dựa trên bộ tài liệu và kèm trích dẫn nguồn.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Topic cards ──
    st.markdown(
        """
        <div class="topic-cards">
            <div class="topic-card">
                <div class="topic-card-icon blue">📝</div>
                <h4>Phương thức xét tuyển</h4>
                <p>Thi THPT, học bạ, đánh giá năng lực, xét kết hợp...</p>
            </div>
            <div class="topic-card">
                <div class="topic-card-icon teal">📊</div>
                <h4>Chỉ tiêu tuyển sinh</h4>
                <p>Cách xác định và phân bổ chỉ tiêu theo phương thức.</p>
            </div>
            <div class="topic-card">
                <div class="topic-card-icon gold">💰</div>
                <h4>Học phí & chi phí</h4>
                <p>Quy định học phí theo ngành, loại hình trường.</p>
            </div>
            <div class="topic-card">
                <div class="topic-card-icon purple">🏆</div>
                <h4>Điểm chuẩn</h4>
                <p>Điểm chuẩn các năm, xu hướng và cách dự đoán.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ──────────────────────── Chat history ───────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("sources"):
            sources = message["sources"]
            with st.expander(f"📎 Nguồn tham khảo ({len(sources)})"):
                for index, source in enumerate(sources, 1):
                    metadata = source["metadata"]
                    url = metadata.get("url")
                    link = f" · [Mở nguồn]({url})" if url else ""
                    st.markdown(
                        f'<div class="source-card">'
                        f'<span class="source-title">[Document {index}] {metadata["title"]}</span><br>'
                        f'<span class="source-meta">{metadata["source"]} · '
                        f'Chunk {metadata.get("chunk_index", "-")} · '
                        f'Score {source["score"]:.3f}{link}</span></div>',
                        unsafe_allow_html=True,
                    )
                st.caption(
                    f"Retrieval method: {message.get('retrieval_source', 'unknown')}"
                )

# ──────────────────────── Chat input ─────────────────────────
query = st.chat_input("Nhập câu hỏi về tuyển sinh đại học...")

# Handle pending question from sidebar
if "pending_question" in st.session_state:
    query = st.session_state.pop("pending_question")

if query:
    # Only append user msg if not already appended (from sidebar button)
    if (
        not st.session_state.messages
        or st.session_state.messages[-1].get("content") != query
        or st.session_state.messages[-1].get("role") != "user"
    ):
        st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Đang đối chiếu tài liệu tuyển sinh..."):
            result = generate_with_citation(query, top_k=top_k)
        st.markdown(result["answer"])
        if result["sources"]:
            with st.expander(f"📎 Nguồn tham khảo ({len(result['sources'])})"):
                for index, source in enumerate(result["sources"], 1):
                    metadata = source["metadata"]
                    url = metadata.get("url")
                    link = f" · [Mở nguồn]({url})" if url else ""
                    st.markdown(
                        f'<div class="source-card">'
                        f'<span class="source-title">[Document {index}] {metadata["title"]}</span><br>'
                        f'<span class="source-meta">{metadata["source"]} · '
                        f'Chunk {metadata.get("chunk_index", "-")} · '
                        f'Score {source["score"]:.3f}{link}</span></div>',
                        unsafe_allow_html=True,
                    )
                st.caption(f"Retrieval method: {result['retrieval_source']}")
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result["answer"],
                "sources": result["sources"],
                "retrieval_source": result["retrieval_source"],
            }
        )

# ── Footer hint ──
st.markdown(
    '<div class="footer-hint">'
    "Trả lời dựa trên bộ tài liệu tuyển sinh · Nhấn Enter để gửi, Shift + Enter để xuống dòng"
    "</div>",
    unsafe_allow_html=True,
)
