import uuid
import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation


load_dotenv()

st.set_page_config(
    page_title="Trợ lý Học vụ UET-VNU",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------
# CSS
# ------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
.main, div[data-testid="stBottom"] {
    background-color: #f5f7fa !important;
    font-family: 'Inter', sans-serif !important;
    color: #1a1a2e !important;
}

section[data-testid="stSidebar"] {
    background-color: #1a1a2e !important;
}
section[data-testid="stSidebar"] * {
    color: #e8eaf6 !important;
}
section[data-testid="stSidebar"] .stSlider > label {
    color: #e8eaf6 !important;
}

div[data-testid="stChatInput"] > div {
    background-color: #ffffff !important;
    border: 1px solid #c5cae9 !important;
    border-radius: 8px !important;
}
div[data-testid="stChatInput"] textarea {
    color: #1a1a2e !important;
}

.user-bubble {
    background: #3f51b5;
    color: white;
    padding: 12px 18px;
    border-radius: 18px 18px 4px 18px;
    max-width: 75%;
    margin-left: auto;
    margin-bottom: 16px;
    font-size: 14.5px;
    line-height: 1.6;
}

.bot-answer {
    background: #ffffff;
    border: 1px solid #e8eaf6;
    border-left: 4px solid #3f51b5;
    padding: 16px 20px;
    border-radius: 4px 12px 12px 4px;
    margin-bottom: 8px;
    font-size: 15px;
    line-height: 1.7;
    color: #1a1a2e;
}

.source-badge {
    display: inline-block;
    background: #e8eaf6;
    color: #3f51b5;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 12px;
    margin: 2px 3px;
    border: 1px solid #c5cae9;
}

.method-tag {
    display: inline-block;
    background: #e3f2fd;
    color: #1565c0;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 4px;
    margin-left: 6px;
}

.chip-row { margin: 12px 0 4px 0; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Session state
# ------------------------------------------------------------------
if "sessions" not in st.session_state:
    st.session_state.sessions = []
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None


def save_current_session():
    if not st.session_state.messages:
        return
    cur_id = st.session_state.current_session_id
    title = "Hội thoại mới"
    for m in st.session_state.messages:
        if m["role"] == "user":
            title = m["content"][:40] + ("…" if len(m["content"]) > 40 else "")
            break
    for s in st.session_state.sessions:
        if s["id"] == cur_id:
            s["title"] = title
            s["messages"] = list(st.session_state.messages)
            return
    st.session_state.sessions.insert(0, {
        "id": cur_id,
        "title": title,
        "messages": list(st.session_state.messages),
    })


def load_session(sid: str):
    save_current_session()
    for s in st.session_state.sessions:
        if s["id"] == sid:
            st.session_state.current_session_id = s["id"]
            st.session_state.messages = list(s["messages"])
            st.session_state.pending_query = None
            st.rerun()


def new_chat():
    save_current_session()
    st.session_state.current_session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.pending_query = None


# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎓 Trợ lý Học vụ UET")
    st.caption("Quy chế đào tạo & Dịch vụ sinh viên — VNU-UET")
    st.divider()

    if st.button("＋  Hội thoại mới", use_container_width=True):
        new_chat()
        st.rerun()

    st.markdown("**⚙️ Cấu hình Retrieval**")
    top_k = st.slider("Số chunks (top_k)", 3, 10, 5)
    use_hybrid = st.toggle("Hybrid (BM25 + Dense)", value=True)

    st.divider()
    st.markdown("**📚 Kho tài liệu**")
    st.markdown("""
- QĐ 3626 — Quy chế đào tạo ĐHQGHN  
- QĐ 4618 — Quy định học bổng  
- QĐ 2244 — Cảnh báo học vụ  
- 6 Thông báo UET (tốt nghiệp, BHYT, học bổng…)
""")

    st.divider()
    save_current_session()
    st.markdown("**🕓 Lịch sử hội thoại**")
    if not st.session_state.sessions:
        st.caption("Chưa có hội thoại nào.")
    else:
        for idx, s in enumerate(st.session_state.sessions):
            is_active = s["id"] == st.session_state.current_session_id
            label = ("▶ " if is_active else "") + s["title"]
            if st.button(label, key=f"sess_{s['id']}_{idx}", use_container_width=True):
                load_session(s["id"])
        if st.button("🗑 Xóa lịch sử", use_container_width=True):
            st.session_state.sessions = []
            st.session_state.messages = []
            st.session_state.current_session_id = str(uuid.uuid4())
            st.rerun()

# ------------------------------------------------------------------
# Main header
# ------------------------------------------------------------------
st.markdown("""
<div style="border-bottom:2px solid #3f51b5; padding-bottom:12px; margin-bottom:20px;">
  <h2 style="margin:0; color:#1a1a2e;">🎓 Trợ lý Học vụ UET-VNU</h2>
  <p style="margin:4px 0 0 0; color:#5c6bc0; font-size:14px;">
    Giải đáp quy chế đào tạo, học bổng, cảnh báo học vụ và thông báo tốt nghiệp
  </p>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# Welcome state
# ------------------------------------------------------------------
if not st.session_state.messages:
    st.info(
        "Bạn có thể hỏi về: điều kiện tốt nghiệp, xét học bổng, "
        "cảnh báo học vụ, nộp ảnh làm bằng, BHYT, lịch bế giảng…",
        icon="💡"
    )

# ------------------------------------------------------------------
# Render message history
# ------------------------------------------------------------------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="user-bubble">{msg["content"]}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="bot-answer">{msg["content"]}</div>',
            unsafe_allow_html=True,
        )
        sources = msg.get("sources", [])
        retrieval_source = msg.get("retrieval_source", "hybrid")

        if sources:
            # Source badges
            seen = set()
            badges = ""
            for src in sources:
                t = src.get("metadata", {}).get("title", "Tài liệu")
                if t not in seen:
                    seen.add(t)
                    badges += f'<span class="source-badge">📄 {t}</span>'
            badges += f'<span class="method-tag">{retrieval_source.upper()}</span>'
            st.markdown(badges, unsafe_allow_html=True)

            # Expandable sources
            with st.expander(f"📚 Xem {len(sources)} chunks nguồn"):
                for i, src in enumerate(sources, 1):
                    meta = src.get("metadata", {})
                    score = src.get("score", 0.0)
                    method = src.get("retrieval_method", "")
                    st.markdown(
                        f"**[{i}] {meta.get('title','?')}** "
                        f"`{meta.get('doc_type','').upper()}` "
                        f"— score: `{score:.4f}` ({method})"
                    )
                    st.caption(f"File: {meta.get('source','?')} | ID: {src.get('id','?')}")
                    snippet = src.get("content", "")[:300]
                    st.markdown(f"> {snippet}…")
                    st.divider()

# ------------------------------------------------------------------
# Quick-reply chips
# ------------------------------------------------------------------
st.markdown('<div class="chip-row"></div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
chips = [
    ("🎓 Điều kiện tốt nghiệp", "Điều kiện để sinh viên được công nhận tốt nghiệp đại học tại ĐHQGHN là gì?"),
    ("📅 Nộp ảnh làm bằng", "Sinh viên tốt nghiệp đợt tháng 01/2026 nộp ảnh làm bằng ở đâu và hạn chót khi nào?"),
    ("💰 Mức học bổng", "Học bổng khuyến khích học tập tại UET được xét như thế nào và mức bao nhiêu?"),
    ("⚠️ Cảnh báo học vụ", "Điều kiện về điểm trung bình để sinh viên không bị cảnh báo học vụ là gì?"),
]
for col, (label, query) in zip([c1, c2, c3, c4], chips):
    with col:
        if st.button(label, use_container_width=True):
            st.session_state.pending_query = query
            st.rerun()

# ------------------------------------------------------------------
# Input & generation
# ------------------------------------------------------------------
user_input = st.chat_input("Nhập câu hỏi về quy chế, học bổng, thi cử, tốt nghiệp…")

active_query = None
if st.session_state.pending_query:
    active_query = st.session_state.pending_query
    st.session_state.pending_query = None
elif user_input:
    active_query = user_input

if active_query:
    st.session_state.messages.append({"role": "user", "content": active_query})
    save_current_session()
    st.rerun()

# Generate response if last message is from user
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_query = st.session_state.messages[-1]["content"]

    with st.spinner("Đang tra cứu quy chế và kiểm chứng nguồn…"):
        try:
            gen = generate_with_citation(last_query, top_k=top_k)
            answer = gen.get("answer", "Tôi không thể xác minh thông tin này từ nguồn hiện có.")
            sources = gen.get("sources", [])
            retrieval_source = gen.get("retrieval_source", "hybrid")
        except Exception as e:
            answer = f"Đã xảy ra lỗi khi xử lý: {e}"
            sources = []
            retrieval_source = "none"

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "retrieval_source": retrieval_source,
    })
    save_current_session()
    st.rerun()

# ------------------------------------------------------------------
# Footer
# ------------------------------------------------------------------
st.markdown(
    "<div style='text-align:center; color:#9e9e9e; font-size:12px; margin-top:24px;'>"
    "Thông tin mang tính tham khảo từ quy chế chính thức ĐHQGHN & UET. "
    "Liên hệ P.Đào tạo (P.107-G2) hoặc P.CTSV (P.210-G2) để xác nhận chính thức."
    "</div>",
    unsafe_allow_html=True,
)
