"""Streamlit UI for the NEU admissions RAG assistant."""
import streamlit as st
from dotenv import load_dotenv
from src.task10_generation import generate_with_citation

load_dotenv()
st.set_page_config(page_title="Hỏi đáp tuyển sinh NEU 2026", page_icon="🎓", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Quicksand', sans-serif; }
.stApp { background: #fbf7f2; color: #3f342d; }
.block-container { max-width: 1080px; padding-top: 2.5rem; padding-bottom: 5rem; }
[data-testid="stHeader"] { background: #fbf7f2; }
[data-testid="stSidebar"] { background: #f3ede5; border-right: 1px solid #e4d8ca; }
[data-testid="stSidebar"] h1 { color: #5c4031; font-weight: 700; }
h1 { color: #4d382d; letter-spacing: -0.03em; }
[data-testid="stCaptionContainer"] { color: #806d60; }
[data-testid="stChatMessage"] { border-radius: 14px; border: 1px solid #e7ddd3; background: #ffffff; box-shadow: 0 3px 12px rgba(73, 51, 36, .05); margin: 0 auto 12px; max-width: 900px; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { background: #f7efe6; }
[data-testid="stChatInput"] { border: 1px solid #d9b79b; border-radius: 12px; background: #ffffff; }
button[kind="primary"], .stButton > button { border-radius: 10px; border: 1px solid #c7774b; background: #c7774b; color: #ffffff; font-weight: 600; }
.stButton > button:hover { border-color: #a85c36; background: #a85c36; color: #ffffff; }
[data-testid="stExpander"] { border: 1px solid #e3d5c7; border-radius: 12px; background: #fffdfa; }
[data-testid="stAlert"] { border-radius: 10px; background: #f8eee5; border: 1px solid #e3c7b2; color: #654738; }
.cheese-card { max-width: 900px; padding: 18px 22px; border-radius: 16px; background: #ffffff; border: 1px solid #e5d6c8; box-shadow: 0 5px 16px rgba(73,51,36,.06); margin: 0 auto 20px; }
.cheese-card h3 { margin: 0 0 5px; color: #5c4031; }
.cheese-card p { margin: 0; color: #806d60; }
.mini-badge { display: inline-block; padding: 3px 9px; margin: 8px 4px 0 0; border-radius: 999px; background: #f4e4d6; color: #76513d; font-size: .78rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

def render_sources(sources: list[dict], retrieval_source: str) -> None:
    if not sources:
        return
    with st.expander(f"{len(sources)} nguồn | retrieval: {retrieval_source}"):
        for index, source in enumerate(sources, 1):
            meta = source.get("metadata", {})
            title = meta.get("title", "Tài liệu không có tiêu đề")
            method = source.get("retrieval_method", "unknown")
            score = float(source.get("score", 0.0))
            st.markdown(f"**[Tài liệu {index}] {title}** · method `{method}` · score `{score:.4f}`")
            if meta.get("source"):
                st.caption(f"Nguồn file: {meta['source']}")
            if meta.get("url"):
                st.markdown(f"[Mở nguồn gốc]({meta['url']})")
            st.code(source.get("content", "").strip(), language="text")

with st.sidebar:
    st.title("Tuyển sinh NEU")
    st.caption("Giúp bạn tìm đúng thông tin tuyển sinh.")
    top_k = st.slider("Số chunks truy xuất (top_k)", 1, 10, 5)
    st.info("Phạm vi: đề án, hướng dẫn và tin tuyển sinh NEU 2026 trong corpus hiện có.")
    if st.button("Xóa lịch sử hội thoại"):
        st.session_state.messages = []
        st.rerun()

st.markdown("""
<div class="cheese-card">
  <h3>Tuyển sinh NEU 2026</h3>
  <p>Hỏi nhẹ nhàng, tìm thông tin chắc chắn, luôn kèm nguồn để bạn kiểm tra lại.</p>
  <span class="mini-badge">Dense + BM25 + RRF</span>
  <span class="mini-badge">Có trích dẫn</span>
  <span class="mini-badge">Phạm vi NEU 2026</span>
</div>
""", unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        render_sources(message.get("sources", []), message.get("retrieval_source", "none"))

query = st.chat_input("Nhập câu hỏi về tuyển sinh NEU 2026...")
if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)
    with st.chat_message("assistant"):
        with st.spinner("Đang truy xuất tài liệu và tạo câu trả lời..."):
            try:
                result = generate_with_citation(query, top_k=top_k)
            except Exception as exc:
                st.error("Không thể xử lý câu hỏi. Hãy kiểm tra index và cấu hình LLM trong file .env.")
                st.caption(f"Chi tiết kỹ thuật: {type(exc).__name__}: {exc}")
                result = {"answer": "Hệ thống chưa thể trả lời câu hỏi này.", "sources": [], "retrieval_source": "none"}
        st.markdown(result["answer"])
        render_sources(result["sources"], result["retrieval_source"])
    st.session_state.messages.append({"role": "assistant", "content": result["answer"], "sources": result["sources"], "retrieval_source": result["retrieval_source"]})
