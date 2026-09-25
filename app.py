"""Streamlit workspace for the IELTS Writing RAG lab.

The UI depends on the public ``generate_with_citation`` contract only, so the
retrieval/generation implementation can evolve without changing the layout.
"""

from __future__ import annotations

from html import escape
from urllib.parse import urlparse

import streamlit as st
from dotenv import load_dotenv

from src.ui_support import AGENT_STAGES, get_project_snapshot, run_rag_query


load_dotenv()
st.set_page_config(
    page_title="IELTS Writing · RAG Lab",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
          --ink:#142847; --muted:#4c6280; --line:rgba(255,255,255,.76);
          --cyan:#087f9b; --violet:#725cc9; --success:#116b60;
          --warning:#885d0a; --danger:#9d3d52;
          --glass:rgba(255,255,255,.62);
          --shadow:0 20px 55px rgba(37,67,117,.11);
        }
        html,body,[class*="css"] { font-family:"Aptos","Segoe UI",sans-serif; }
        .stApp {
          color:var(--ink);
          background:
            radial-gradient(circle at 85% 8%,rgba(176,155,255,.34),transparent 27%),
            radial-gradient(circle at 16% 34%,rgba(105,218,226,.33),transparent 31%),
            linear-gradient(145deg,#ecf7fb 0%,#e9f1fb 48%,#f3edfc 100%);
          background-attachment:fixed;
        }
        [data-testid="stHeader"] { background:transparent; }
        [data-testid="stSidebar"] {
          background:linear-gradient(160deg,rgba(20,43,79,.92),rgba(38,45,93,.88));
          border-right:1px solid rgba(255,255,255,.22);
          box-shadow:12px 0 40px rgba(25,46,89,.12);
          backdrop-filter:blur(28px); -webkit-backdrop-filter:blur(28px);
        }
        [data-testid="stSidebar"] h1 { color:#fff!important; font-size:2.15rem!important;
          line-height:1.03!important; max-width:9ch; margin-bottom:.25rem; }
        [data-testid="stSidebar"] p,[data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span { color:#e2edff; }
        [data-testid="stSidebar"] hr { border-color:rgba(255,255,255,.2); }
        [data-testid="stSidebar"] .stRadio label {
          border:1px solid transparent; border-radius:13px; padding:.55rem .7rem;
        }
        [data-testid="stSidebar"] .stRadio label:has(input:checked) {
          background:rgba(255,255,255,.15); border-color:rgba(255,255,255,.22);
          box-shadow:inset 0 1px 0 rgba(255,255,255,.18);
        }
        [data-testid="stSidebar"] button {
          color:#fff; background:rgba(255,255,255,.12);
          border:1px solid rgba(255,255,255,.25); border-radius:12px;
        }
        .block-container { max-width:1210px; padding-top:2.7rem; padding-bottom:4rem; }
        h1,h2,h3 { letter-spacing:-.035em; }
        .hero {
          position:relative; overflow:hidden; border:1px solid rgba(255,255,255,.86);
          border-radius:30px; padding:clamp(1.5rem,4vw,3rem);
          background:linear-gradient(115deg,rgba(255,255,255,.79),rgba(255,255,255,.38));
          box-shadow:var(--shadow),inset 0 1px 0 #fff;
          backdrop-filter:blur(24px); -webkit-backdrop-filter:blur(24px);
          margin-bottom:1.25rem;
        }
        .hero::after {
          content:""; position:absolute; width:255px; height:255px; right:-60px; top:-105px;
          border-radius:50%; border:1px solid rgba(255,255,255,.8);
          box-shadow:0 0 0 22px rgba(255,255,255,.11),0 0 0 50px rgba(255,255,255,.09);
          pointer-events:none;
        }
        .hero-kicker { color:var(--cyan); font-weight:750; margin-bottom:.75rem; }
        .hero h1 { color:var(--ink); font-size:clamp(2rem,4vw,3.55rem);
          line-height:1.05; margin:0 0 .85rem; max-width:17ch; }
        .hero p { color:var(--muted); font-size:1.07rem; line-height:1.65;
          max-width:65ch; margin:0; }
        .flow-summary { display:flex; flex-wrap:wrap; align-items:center; gap:.5rem;
          padding:.9rem 1rem; margin-bottom:1rem; background:rgba(255,255,255,.4);
          border:1px solid var(--line); border-radius:18px;
          backdrop-filter:blur(16px); -webkit-backdrop-filter:blur(16px);
        }
        .flow-node { color:#244469; font-size:.89rem; font-weight:700; }
        .flow-arrow { color:var(--cyan); font-weight:900; }
        [data-testid="stMetric"] {
          min-height:115px; padding:1rem 1.2rem; border-radius:20px;
          background:var(--glass); border:1px solid var(--line);
          box-shadow:0 12px 32px rgba(43,70,113,.08),inset 0 1px 0 #fff;
          backdrop-filter:blur(20px); -webkit-backdrop-filter:blur(20px);
        }
        [data-testid="stMetricLabel"] { color:var(--muted); }
        [data-testid="stMetricValue"] { color:var(--ink); font-weight:800; }
        .trace-stage {
          position:relative; margin:0 0 1.1rem 3.7rem; padding:1.25rem 1.4rem;
          border-radius:22px; border:1px solid rgba(255,255,255,.87);
          background:linear-gradient(130deg,rgba(255,255,255,.77),rgba(255,255,255,.48));
          box-shadow:var(--shadow),inset 0 1px 0 #fff;
          backdrop-filter:blur(22px); -webkit-backdrop-filter:blur(22px);
        }
        .trace-stage::before { content:""; position:absolute; left:-2.6rem; top:2.7rem;
          bottom:-1.35rem; width:2px; background:rgba(39,111,149,.25); }
        .trace-number { position:absolute; left:-3.3rem; top:1.05rem;
          display:grid; place-items:center; width:2.05rem; height:2.05rem;
          border-radius:12px; color:#fff; font-size:.82rem; font-weight:800;
          background:linear-gradient(145deg,#107f9e,#6857bd);
          box-shadow:0 0 0 6px #eaf3fa,0 8px 17px rgba(71,94,152,.22);
        }
        .trace-heading { display:flex; align-items:start; justify-content:space-between;
          gap:1rem; margin-bottom:1rem; }
        .trace-title { color:var(--ink); font-size:1.2rem; font-weight:800; }
        .trace-module { color:var(--muted); font-size:.82rem; margin-top:.18rem; }
        .io-grid { display:grid; grid-template-columns:1fr 1.35fr 1fr; gap:1rem;
          padding:1rem 0; border-top:1px solid rgba(45,77,113,.12);
          border-bottom:1px solid rgba(45,77,113,.12); }
        .io-label { color:#476383; font-size:.78rem; font-weight:800; margin-bottom:.3rem; }
        .io-value { color:#1e3656; font-size:.94rem; line-height:1.5; }
        .method-band { display:grid; grid-template-columns:1fr 1fr; gap:1rem;
          margin-top:1rem; padding:.85rem 1rem; border-radius:14px;
          background:rgba(223,240,252,.56); border:1px solid rgba(255,255,255,.68);
          color:#2c496b; font-size:.9rem; line-height:1.55; }
        .method-band strong { color:var(--ink); }
        .state { display:inline-block; padding:.32rem .7rem; border-radius:999px;
          font-size:.75rem; font-weight:750; white-space:nowrap; }
        .state-ready { color:var(--success); background:rgba(189,244,222,.6); }
        .state-progress { color:var(--warning); background:rgba(255,233,171,.66); }
        .state-missing { color:var(--danger); background:rgba(255,216,226,.68); }
        [data-testid="stChatMessage"],.source-card {
          background:var(--glass); border:1px solid var(--line); border-radius:18px;
          box-shadow:0 12px 30px rgba(44,72,119,.08);
          backdrop-filter:blur(18px); -webkit-backdrop-filter:blur(18px);
        }
        [data-testid="stChatMessage"] { margin-bottom:.85rem; }
        .source-card { padding:.85rem 1rem; margin:.55rem 0; }
        .source-card strong { color:var(--ink); }
        .source-meta { color:var(--muted); font-size:.84rem; margin-top:.25rem; }
        [data-testid="stExpander"] { border-radius:14px; overflow:hidden; }
        .stMain .stButton>button {
          min-height:3rem; border-radius:14px; color:#183c62;
          background:rgba(255,255,255,.56); border:1px solid rgba(255,255,255,.92);
          box-shadow:0 8px 24px rgba(48,86,133,.1),inset 0 1px 0 #fff;
          backdrop-filter:blur(16px); -webkit-backdrop-filter:blur(16px);
          font-weight:700;
        }
        .stMain .stButton>button:hover {
          color:#fff; background:#186f94; border-color:#186f94;
        }
        .stMain button:focus-visible,[data-testid="stSidebar"] button:focus-visible,
        [data-testid="stSidebar"] label:focus-within {
          outline:3px solid #27b8cf; outline-offset:3px;
        }
        [data-testid="stChatInput"] { border-radius:16px; overflow:hidden; }
        [data-testid="stChatInput"] textarea { color:var(--ink); }
        a { color:#0a648f!important; }
        @media (max-width:760px) {
          .block-container { padding-top:1.25rem; }
          .hero { border-radius:22px; }
          .hero::after { opacity:.45; }
          .io-grid,.method-band { grid-template-columns:1fr; }
          .trace-stage { margin-left:2.8rem; padding:1rem; }
          .trace-number { left:-2.7rem; }
          .trace-stage::before { left:-2rem; }
          .trace-heading { display:block; }
          .trace-heading .state { margin-top:.55rem; }
        }
        @media (prefers-reduced-motion:reduce) {
          *,*::before,*::after { scroll-behavior:auto!important; transition:none!important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def header(title: str, description: str) -> None:
    st.markdown(
        f'<section class="hero"><div class="hero-kicker">IELTS Writing · RAG agent</div>'
        f'<h1>{escape(title)}</h1><p>{escape(description)}</p></section>',
        unsafe_allow_html=True,
    )


def status_label(status: str) -> tuple[str, str]:
    return {
        "ready": ("Đã triển khai", "ready"),
        "progress": ("Placeholder · đang làm", "progress"),
        "missing": ("Chưa có dữ liệu", "missing"),
    }[status]


def render_agent_workflow(snapshot: dict) -> None:
    header(
        "Agent biến dữ liệu thành câu trả lời như thế nào?",
        "Theo dõi từng hoạt động của hệ thống từ lúc lấy tài liệu IELTS, chuẩn hóa, "
        "chunk và truy xuất cho đến khi tạo câu trả lời có thể kiểm chứng.",
    )
    st.markdown(
        """<div class="flow-summary">
        <span class="flow-node">Nguồn IELTS</span><span class="flow-arrow">›</span>
        <span class="flow-node">Markdown</span><span class="flow-arrow">›</span>
        <span class="flow-node">Chunks</span><span class="flow-arrow">›</span>
        <span class="flow-node">Vector index</span><span class="flow-arrow">›</span>
        <span class="flow-node">Hybrid retrieval</span><span class="flow-arrow">›</span>
        <span class="flow-node">Grounded answer</span>
        </div>""",
        unsafe_allow_html=True,
    )
    counts = st.columns(3)
    counts[0].metric("Legal sources", f"{snapshot['legal_count']} / 3")
    counts[1].metric("Article sources", f"{snapshot['news_count']} / 5")
    counts[2].metric("Golden questions", f"{snapshot['golden_count']} / 15")
    st.caption("Trạng thái được đọc từ code và artifact hiện có. Placeholder không được tính là đã chạy.")

    for stage in AGENT_STAGES:
        status = snapshot["step_status"].get(stage["id"], "progress")
        label, css = status_label(status)
        st.markdown(
            f"""<section class="trace-stage">
              <div class="trace-number">{stage['number']}</div>
              <div class="trace-heading"><div>
                <div class="trace-title">{stage['title']}</div>
                <div class="trace-module">{stage['module']}</div>
              </div><span class="state state-{css}">{label}</span></div>
              <div class="io-grid">
                <div><div class="io-label">Đầu vào</div><div class="io-value">{stage['input']}</div></div>
                <div><div class="io-label">Agent thực hiện</div><div class="io-value">{stage['action']}</div></div>
                <div><div class="io-label">Đầu ra</div><div class="io-value">{stage['output']}</div></div>
              </div>
              <div class="method-band">
                <div><strong>Phương pháp</strong><br>{stage['method']}</div>
                <div><strong>Cấu hình hiện tại</strong><br>{stage['config']}</div>
              </div>
            </section>""",
            unsafe_allow_html=True,
        )


def render_sources(sources: list[dict], retrieval_source: str) -> None:
    if not sources:
        st.caption("Chưa có nguồn được sử dụng cho câu trả lời này.")
        return
    with st.expander(f"Nguồn đã dùng · {len(sources)} · {retrieval_source}", expanded=True):
        for index, source in enumerate(sources, 1):
            metadata = source.get("metadata", {})
            title = escape(str(metadata.get("title", "Không có tiêu đề")))
            origin = escape(str(metadata.get("source", "Không rõ nguồn")))
            url = metadata.get("url")
            method = escape(str(source.get("retrieval_method", "unknown")))
            score = source.get("score")
            score_text = f"{score:.4f}" if isinstance(score, (int, float)) else "n/a"
            parsed_url = urlparse(url) if isinstance(url, str) else None
            safe_url = escape(url, quote=True) if parsed_url and parsed_url.scheme in {"http", "https"} else None
            link = f'<a href="{safe_url}" target="_blank" rel="noopener">Mở nguồn</a>' if safe_url else "Không có URL"
            st.markdown(
                f"""<div class="source-card"><strong>[{index}] {title}</strong>
                <div class="source-meta">{origin} · {method} · score {score_text} · {link}</div></div>""",
                unsafe_allow_html=True,
            )


def render_chat(top_k: int) -> None:
    header(
        "Hỏi bộ tài liệu IELTS Writing.",
        "Câu trả lời chỉ nên dựa trên evidence đã truy xuất. Mỗi nguồn hiển thị title, "
        "URL, retrieval method và score để có thể kiểm chứng khi demo.",
    )
    examples = (
        "Band 7 Task Response khác Band 6 ở điểm nào?",
        "Coherence and Cohesion được đánh giá như thế nào?",
        "Bài mẫu này cần cải thiện Lexical Resource ở đâu?",
    )
    st.caption("Câu hỏi gợi ý")
    for index, (column, example) in enumerate(zip(st.columns(3), examples)):
        if column.button(example, use_container_width=True, key=f"example-{index}"):
            st.session_state.pending_query = example
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                render_sources(message["sources"], message.get("retrieval_source", "none"))
    typed_query = st.chat_input("Nhập câu hỏi về IELTS Writing…")
    query = typed_query or st.session_state.pop("pending_query", None)
    if not query:
        return
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)
    with st.chat_message("assistant"):
        with st.spinner("Đang truy xuất evidence và tạo câu trả lời…"):
            result = run_rag_query(query, top_k=top_k)
        st.markdown(result["answer"])
        if result.get("ui_notice"):
            st.info(result["ui_notice"])
        render_sources(result["sources"], result["retrieval_source"])
    st.session_state.messages.append({
        "role": "assistant", "content": result["answer"],
        "sources": result["sources"], "retrieval_source": result["retrieval_source"],
    })


inject_styles()
if "messages" not in st.session_state:
    st.session_state.messages = []
snapshot = get_project_snapshot()
with st.sidebar:
    st.markdown("# IELTS Writing")
    st.caption("RAG agent workspace")
    page = st.radio("Đi đến", ("Quy trình Agent", "Chat demo"), label_visibility="collapsed")
    st.divider()
    if page == "Chat demo":
        top_k = st.slider("Số chunks truy xuất", 3, 10, 5)
        st.caption("Dùng chung cho dense, BM25 và generation khi pipeline được nối.")
        if st.button("Xóa lịch sử chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    else:
        top_k = 5
        st.caption("Mỗi bước hiển thị đầu vào, hoạt động, đầu ra và kỹ thuật đang dùng.")

if page == "Chat demo":
    render_chat(top_k)
else:
    render_agent_workflow(snapshot)
