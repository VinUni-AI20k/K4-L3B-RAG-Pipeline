import html
import os

import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation


load_dotenv()

st.set_page_config(
    page_title="Trợ lý An Khang",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


CUSTOM_CSS = """
<style>
    :root {
        --brand-900: #102a43;
        --brand-700: #1f4e78;
        --brand-500: #2f80ed;
        --brand-100: #eaf3ff;
        --surface-soft: #f5f8fc;
        --text-main: #172b4d;
        --text-muted: #62748a;
        --line: #dce6f2;
    }

    .stApp {
        background:
            radial-gradient(circle at 80% 0%, rgba(47, 128, 237, 0.09), transparent 28rem),
            var(--surface-soft);
        color: var(--text-main);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #102a43 0%, #153d5f 100%);
        border-right: 0;
    }

    [data-testid="stSidebar"] * {
        color: #f5f9ff;
    }

    [data-testid="stSidebar"] .stSlider [data-baseweb="slider"] div {
        color: #82b8ff;
    }

    .block-container {
        max-width: 960px;
        padding-bottom: 7rem;
        padding-top: 2rem;
    }

    .brand {
        align-items: center;
        display: flex;
        gap: 0.75rem;
        margin-bottom: 1.75rem;
    }

    .brand-mark {
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.22);
        border-radius: 0.9rem;
        display: grid;
        font-size: 1.35rem;
        height: 2.75rem;
        place-items: center;
        width: 2.75rem;
    }

    .brand-name {
        color: #ffffff;
        font-size: 1.05rem;
        font-weight: 750;
        line-height: 1.2;
    }

    .brand-subtitle {
        color: #bcd0e5;
        font-size: 0.78rem;
        margin-top: 0.15rem;
    }

    .sidebar-label {
        color: #bcd0e5;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        margin: 1.2rem 0 0.35rem;
        text-transform: uppercase;
    }

    .status-card {
        align-items: center;
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 0.85rem;
        display: flex;
        gap: 0.55rem;
        padding: 0.75rem 0.85rem;
    }

    .status-dot {
        background: #4ade80;
        border-radius: 999px;
        box-shadow: 0 0 0 4px rgba(74, 222, 128, 0.12);
        height: 0.5rem;
        width: 0.5rem;
    }

    .hero {
        background: linear-gradient(135deg, #102a43 0%, #1f5f95 68%, #2f80ed 100%);
        border-radius: 1.5rem;
        box-shadow: 0 18px 50px rgba(16, 42, 67, 0.16);
        color: #ffffff;
        margin-bottom: 1.5rem;
        overflow: hidden;
        padding: 2.15rem 2.25rem;
        position: relative;
    }

    .hero::after {
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 999px;
        content: "";
        height: 14rem;
        position: absolute;
        right: -4rem;
        top: -7rem;
        width: 14rem;
    }

    .hero-eyebrow {
        color: #beddff;
        font-size: 0.75rem;
        font-weight: 750;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    .hero h1 {
        color: #ffffff;
        font-size: clamp(1.8rem, 4vw, 2.65rem);
        letter-spacing: -0.035em;
        line-height: 1.1;
        margin: 0.65rem 0 0.75rem;
        padding: 0;
    }

    .hero p {
        color: #d9eaff;
        font-size: 0.98rem;
        line-height: 1.65;
        margin: 0;
        max-width: 42rem;
    }

    .section-title {
        color: var(--brand-900);
        font-size: 0.86rem;
        font-weight: 750;
        letter-spacing: 0.02em;
        margin: 1.5rem 0 0.75rem;
    }

    .feature-grid {
        display: grid;
        gap: 0.8rem;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        margin-bottom: 1.25rem;
    }

    .feature-card {
        background: rgba(255, 255, 255, 0.86);
        border: 1px solid var(--line);
        border-radius: 1rem;
        min-height: 7rem;
        padding: 1rem;
    }

    .feature-icon {
        font-size: 1.15rem;
        margin-bottom: 0.55rem;
    }

    .feature-title {
        color: var(--brand-900);
        font-size: 0.87rem;
        font-weight: 750;
    }

    .feature-copy {
        color: var(--text-muted);
        font-size: 0.78rem;
        line-height: 1.5;
        margin-top: 0.25rem;
    }

    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid var(--line);
        border-radius: 1.05rem;
        box-shadow: 0 7px 24px rgba(16, 42, 67, 0.045);
        margin-bottom: 0.8rem;
        padding: 0.35rem 0.55rem;
    }

    [data-testid="stChatInput"] {
        background: rgba(245, 248, 252, 0.94);
        border-top: 1px solid var(--line);
        padding-bottom: 1.1rem;
        padding-top: 0.8rem;
    }

    [data-testid="stChatInput"] textarea {
        color: var(--text-main);
    }

    .answer-meta {
        align-items: center;
        color: var(--text-muted);
        display: flex;
        flex-wrap: wrap;
        font-size: 0.76rem;
        gap: 0.45rem;
        margin-top: 0.75rem;
    }

    .meta-pill {
        background: var(--brand-100);
        border-radius: 999px;
        color: var(--brand-700);
        font-weight: 650;
        padding: 0.25rem 0.55rem;
    }

    .source-header {
        align-items: center;
        display: flex;
        gap: 0.55rem;
        justify-content: space-between;
        margin-bottom: 0.35rem;
    }

    .source-title {
        color: var(--brand-900);
        font-size: 0.9rem;
        font-weight: 750;
    }

    .source-meta {
        color: var(--text-muted);
        font-size: 0.74rem;
    }

    .source-divider {
        border-top: 1px solid var(--line);
        margin: 0.9rem 0;
    }

    .empty-note {
        color: var(--text-muted);
        font-size: 0.8rem;
        line-height: 1.55;
        margin-top: 0.65rem;
    }

    @media (max-width: 700px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 1rem;
        }

        .hero {
            border-radius: 1.1rem;
            padding: 1.5rem 1.25rem;
        }

        .feature-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
"""


RETRIEVAL_LABELS = {
    "hybrid": "Hybrid + RRF",
    "pageindex": "PageIndex",
    "dense": "Dense search",
    "bm25": "BM25",
    "none": "Không có nguồn",
}

SUGGESTED_QUESTIONS = [
    "Thời gian cân nhắc hợp đồng là bao lâu?",
    "Quyền lợi bệnh hiểm nghèo được chi trả thế nào?",
    "Khi nào hợp đồng có thể được khôi phục hiệu lực?",
]


def render_sidebar() -> int:
    """Render navigation and retrieval settings."""
    with st.sidebar:
        st.markdown(
            """
            <div class="brand">
                <div class="brand-mark">🛡️</div>
                <div>
                    <div class="brand-name">Trợ lý An Khang</div>
                    <div class="brand-subtitle">RAG bảo hiểm có dẫn nguồn</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sidebar-label">Trạng thái</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="status-card">
                <span class="status-dot"></span>
                <span>Giao diện sẵn sàng</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sidebar-label">Thiết lập tìm kiếm</div>', unsafe_allow_html=True)
        top_k = st.slider(
            "Số đoạn tài liệu",
            min_value=3,
            max_value=10,
            value=5,
            help="Số đoạn liên quan được đưa vào để tạo câu trả lời.",
        )
        provider = os.getenv("LLM_PROVIDER", "openai").strip().title() or "OpenAI"
        st.caption(f"Nhà cung cấp LLM: {provider}")

        st.markdown('<div class="sidebar-label">Phiên trò chuyện</div>', unsafe_allow_html=True)
        if st.button("＋ Cuộc trò chuyện mới", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.markdown(
            """
            <div class="empty-note">
                Câu trả lời chỉ dùng thông tin trong bộ quy tắc, điều khoản
                An Khang Hạnh Phúc. Hãy kiểm tra nguồn trước khi sử dụng.
            </div>
            """,
            unsafe_allow_html=True,
        )

    return top_k


def render_welcome() -> str | None:
    """Render the empty state and return a selected suggested question."""
    st.markdown(
        """
        <section class="hero">
            <div class="hero-eyebrow">Bảo Việt Nhân thọ · Tra cứu thông minh</div>
            <h1>Hiểu hợp đồng bảo hiểm<br>nhanh và rõ ràng hơn.</h1>
            <p>
                Đặt câu hỏi về quyền lợi, điều kiện, thời hạn hoặc các khoản phí.
                Mỗi câu trả lời đều đi kèm nguồn để bạn dễ dàng kiểm chứng.
            </p>
        </section>
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">⌕</div>
                <div class="feature-title">Tìm kiếm kết hợp</div>
                <div class="feature-copy">Kết hợp ngữ nghĩa và từ khóa để tìm đúng điều khoản.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">◎</div>
                <div class="feature-title">Dẫn nguồn rõ ràng</div>
                <div class="feature-copy">Hiển thị tài liệu, phương thức truy xuất và độ liên quan.</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">✓</div>
                <div class="feature-title">Trả lời có kiểm soát</div>
                <div class="feature-copy">Từ chối xác nhận khi tài liệu không cung cấp đủ bằng chứng.</div>
            </div>
        </div>
        <div class="section-title">Bạn có thể hỏi</div>
        """,
        unsafe_allow_html=True,
    )

    columns = st.columns(3)
    selected_question = None
    for index, question in enumerate(SUGGESTED_QUESTIONS):
        with columns[index]:
            if st.button(question, key=f"suggestion-{index}", use_container_width=True):
                selected_question = question
    return selected_question


def render_sources(sources: list[dict], retrieval_source: str) -> None:
    """Render source details without trusting corpus text as HTML."""
    if not sources:
        return

    retrieval_label = RETRIEVAL_LABELS.get(retrieval_source, retrieval_source)
    st.markdown(
        f"""
        <div class="answer-meta">
            <span class="meta-pill">{html.escape(retrieval_label)}</span>
            <span>{len(sources)} nguồn được sử dụng</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander(f"Xem {len(sources)} nguồn tham khảo"):
        for index, source in enumerate(sources, start=1):
            metadata = source.get("metadata") or {}
            title = str(metadata.get("title") or metadata.get("source") or f"Nguồn {index}")
            source_name = str(metadata.get("source") or "Không rõ nguồn")
            raw_method = str(source.get("retrieval_method", ""))
            method = RETRIEVAL_LABELS.get(raw_method, raw_method or "Không rõ")
            score = source.get("score")
            score_text = f"{float(score):.3f}" if isinstance(score, (int, float)) else "N/A"

            st.markdown(
                f"""
                <div class="source-header">
                    <div class="source-title">[{index}] {html.escape(title)}</div>
                    <div class="source-meta">{html.escape(method)} · {score_text}</div>
                </div>
                <div class="source-meta">{html.escape(source_name)}</div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(str(source.get("content") or "Không có nội dung trích dẫn."))

            url = metadata.get("url")
            if isinstance(url, str) and url.startswith(("https://", "http://")):
                st.link_button("Mở tài liệu gốc ↗", url)

            if index < len(sources):
                st.markdown('<div class="source-divider"></div>', unsafe_allow_html=True)


def render_message(message: dict) -> None:
    """Render a stored chat message and its retrieval evidence."""
    role = message.get("role", "assistant")
    avatar = "👤" if role == "user" else "🛡️"
    with st.chat_message(role, avatar=avatar):
        st.markdown(str(message.get("content", "")))
        if role == "assistant":
            render_sources(
                message.get("sources") or [],
                str(message.get("retrieval_source", "none")),
            )


def answer_query(query: str, top_k: int) -> dict:
    """Call the RAG pipeline and normalize provider failures for the UI."""
    try:
        result = generate_with_citation(query, top_k=top_k)
        if not isinstance(result, dict) or not str(result.get("answer", "")).strip():
            raise ValueError("Pipeline trả về kết quả không hợp lệ")
        return {
            "role": "assistant",
            "content": str(result["answer"]),
            "sources": result.get("sources") or [],
            "retrieval_source": result.get("retrieval_source", "none"),
        }
    except Exception:
        return {
            "role": "assistant",
            "content": (
                "Hệ thống tra cứu hiện chưa sẵn sàng. Vui lòng kiểm tra cấu hình "
                "pipeline và nhà cung cấp mô hình, sau đó thử lại."
            ),
            "sources": [],
            "retrieval_source": "none",
        }


st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

top_k = render_sidebar()
suggested_query = render_welcome() if not st.session_state.messages else None

for stored_message in st.session_state.messages:
    render_message(stored_message)

typed_query = st.chat_input("Hỏi về quyền lợi, điều kiện hoặc thời hạn bảo hiểm…")
query = typed_query or suggested_query

if query:
    user_message = {"role": "user", "content": query}
    st.session_state.messages.append(user_message)
    render_message(user_message)

    with st.spinner("Đang tìm điều khoản phù hợp…"):
        assistant_message = answer_query(query, top_k)

    st.session_state.messages.append(assistant_message)
    render_message(assistant_message)
