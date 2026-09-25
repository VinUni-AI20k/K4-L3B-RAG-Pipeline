"""Streamlit chat interface for household-business tax and declaration RAG."""

import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation


load_dotenv()

SUGGESTED_QUESTIONS = [
    "Hộ kinh doanh phải kê khai thuế khi nào?",
    "Doanh thu nào được miễn thuế GTGT và TNCN?",
    "Khi nào hộ kinh doanh phải dùng hóa đơn điện tử?",
]


def source_label(source: dict, index: int) -> str:
    """Return a complete, visible label for one retrieval source."""
    metadata = source["metadata"]
    return (
        f"{index}. {metadata['title']} | {metadata['source']} | "
        f"{source['retrieval_method']} | score {source['score']:.3f}"
    )


def render_sources(sources: list[dict]) -> None:
    """Show source metadata and excerpts for answer verification."""
    if not sources:
        return
    st.markdown('<p class="sources-heading">Nguồn tham khảo</p>', unsafe_allow_html=True)
    for index, source in enumerate(sources, start=1):
        with st.expander(source_label(source, index)):
            metadata = source["metadata"]
            st.caption(
                f"Loại nguồn: {metadata['doc_type']} · Chunk: {metadata['chunk_index']}"
            )
            if metadata.get("url"):
                st.link_button("Mở nguồn gốc", metadata["url"])
            st.markdown(source["content"])


def apply_theme() -> None:
    """Apply the approved Ant Design-inspired portal visual language."""
    st.markdown(
        """
        <style>
        :root { --ink:#202124; --orange:#d55a43; --apricot:#fff0e8; --canvas:#fcfbf8; --teal:#146b62; --line:#ece7e2; }
        .stApp { background:radial-gradient(circle at 90% 0%,rgba(255,210,183,.28),transparent 26rem),var(--canvas); color:var(--ink); }
        .block-container { max-width:1180px; padding-top:1.35rem; padding-bottom:4rem; }
        #MainMenu, footer, header[data-testid="stHeader"] { visibility:hidden; }
        .portal-bar { align-items:center; background:var(--ink); border-radius:14px; box-shadow:0 10px 24px rgba(32,33,36,.22); color:#fff; display:flex; gap:.85rem; margin-bottom:1rem; padding:.9rem 1.15rem; }
        .portal-mark { align-items:center; background:var(--orange); border-radius:9px; display:inline-flex; font-weight:800; height:2.1rem; justify-content:center; width:2.1rem; }
        .portal-name { font-size:1.05rem; font-weight:700; } .portal-topic { color:#e9e1dd; font-size:.82rem; margin-left:auto; }
        .hero-panel { background:radial-gradient(circle at 84% 30%,rgba(255,245,237,.92) 0 4.5rem,transparent 4.7rem),linear-gradient(120deg,#d9563d 0%,#ed794d 52%,#f8c59b 100%); border-radius:16px; box-shadow:0 12px 30px rgba(46,36,31,.08); color:#fff; margin-bottom:1.25rem; padding:2rem 2.15rem; }
        .hero-kicker,.section-label,.sources-heading { font-size:.78rem; font-weight:800; letter-spacing:.08em; text-transform:uppercase; } .hero-kicker { margin:0 0 .6rem; } .hero-panel h1 { font-size:clamp(1.9rem,4vw,3rem); line-height:1.08; margin:0; } .hero-panel p { line-height:1.6; margin:.85rem 0 0; max-width:42rem; }
        .section-label { color:#69707a; margin:.3rem 0 .6rem; } .sources-heading { color:var(--teal); margin:1rem 0 .4rem; }
        .stButton > button { background:#fff; border:1px solid var(--line); border-radius:12px; box-shadow:0 4px 12px rgba(46,36,31,.05); color:var(--ink); font-size:.86rem; font-weight:600; min-height:4.15rem; padding:.65rem .85rem; text-align:left; white-space:normal; width:100%; }
        .stButton > button:hover,.stButton > button:focus-visible { border-color:var(--orange); box-shadow:0 6px 16px rgba(213,90,67,.18); color:#b84331; }
        [data-testid="stChatMessage"] { background:#fff; border:1px solid var(--line); border-radius:14px; box-shadow:0 5px 15px rgba(46,36,31,.05); margin-bottom:.85rem; padding:.8rem; }
        [data-testid="stExpander"] { background:#fff; border:1px solid var(--line); border-radius:10px; margin:.45rem 0; }
        [data-testid="stSidebar"] { background:#fbf7f3; border-right:1px solid var(--line); }
        @media (max-width:680px) { .block-container { padding-left:1rem; padding-right:1rem; } .hero-panel { padding:1.5rem 1.25rem; } .portal-topic { display:none; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="Thuế & Kê khai Hộ Kinh Doanh", layout="wide")
    apply_theme()
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("suggested_query", None)

    with st.sidebar:
        st.markdown("### Thiết lập tra cứu")
        st.caption("Điều chỉnh số nguồn được dùng để trả lời câu hỏi.")
        top_k = st.slider("Số nguồn tham khảo", 3, 10, 5)
        st.divider()
        st.caption("Trợ lý chỉ trả lời từ nguồn có thể kiểm chứng.")

    st.markdown(
        """
        <section class="portal-bar" aria-label="Thông tin sản phẩm">
          <span class="portal-mark" aria-hidden="true">T</span>
          <span class="portal-name">Thuế &amp; Kê khai Hộ Kinh Doanh</span>
          <span class="portal-topic">Tra cứu nghĩa vụ thuế · Hóa đơn · Kê khai</span>
        </section>
        <section class="hero-panel"><p class="hero-kicker">Trợ lý tra cứu chính sách</p>
          <h1>Hỏi đáp thuế cho hộ kinh doanh</h1>
          <p>Tra cứu nghĩa vụ thuế, thời hạn kê khai và hóa đơn điện tử từ các tài liệu nguồn đã được thu thập.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<p class="section-label">Câu hỏi gợi ý</p>', unsafe_allow_html=True)
    question_columns = st.columns(3)
    for index, question in enumerate(SUGGESTED_QUESTIONS):
        if question_columns[index].button(question, key=f"suggestion-{index}"):
            st.session_state.suggested_query = question

    st.title("Thuế & Kê khai Hộ Kinh Doanh")
    st.caption("Hỏi về thuế GTGT, TNCN, lệ phí môn bài, kê khai và hóa đơn điện tử.")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            render_sources(message.get("sources", []))

    query = st.chat_input("Nhập câu hỏi về thuế và kê khai...") or st.session_state.suggested_query
    if not query:
        return
    st.session_state.suggested_query = None
    st.session_state.messages.append({"role":"user", "content":query, "sources":[]})
    with st.chat_message("user"):
        st.markdown(query)
    with st.chat_message("assistant"):
        with st.spinner("Đang tra cứu nguồn liên quan..."):
            result = generate_with_citation(query, top_k=top_k)
        st.markdown(result["answer"])
        render_sources(result["sources"])
    st.session_state.messages.append({"role":"assistant", "content":result["answer"], "sources":result["sources"]})


if __name__ == "__main__":
    main()
