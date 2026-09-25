"""Giao diện Streamlit cho chatbot thuế và nghĩa vụ kê khai hộ kinh doanh."""

import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation


load_dotenv()

SUGGESTED_QUESTIONS = [
    "Hộ kinh doanh phải kê khai thuế khi nào?",
    "Doanh thu nào được miễn thuế GTGT và TNCN?",
    "Khi nào hộ kinh doanh phải dùng hóa đơn điện tử?",
    "Điều kiện để đăng ký hộ kinh doanh là gì?",
]

KNOWLEDGE_CATEGORIES = [
    "Thủ tục hành chính",
    "Chính sách thuế",
    "Biểu mẫu và hồ sơ",
    "Văn bản pháp lý",
    "Câu hỏi thường gặp",
]


def source_label(source: dict, index: int) -> str:
    """Tạo nhãn đầy đủ, hiển thị được cho một nguồn truy xuất."""
    metadata = source["metadata"]
    return (
        f"{index}. Tiêu đề: {metadata['title']} | Nguồn: {metadata['source']} | "
        f"Phương thức: {source['retrieval_method']} | Điểm: {source['score']:.3f}"
    )


def render_sources(sources: list[dict]) -> None:
    """Hiển thị metadata và trích đoạn nguồn để kiểm chứng câu trả lời."""
    if not sources:
        return
    st.markdown(
        '<div class="citation-header"><p class="sources-heading">Nguồn tham khảo</p>'
        '<span class="status-badge official">Nguồn chính thức</span>'
        '<span class="status-badge verified">Đã xác thực</span></div>',
        unsafe_allow_html=True,
    )
    for index, source in enumerate(sources, start=1):
        with st.expander(source_label(source, index)):
            metadata = source["metadata"]
            st.caption(
                f"Loại nguồn: {metadata['doc_type']} · Đoạn: {metadata['chunk_index']}"
            )
            if metadata.get("url"):
                st.link_button("Mở nguồn gốc", metadata["url"])
            st.markdown(source["content"])


def apply_theme() -> None:
    """Áp dụng ngôn ngữ thị giác cho cổng thông tin RAG chính thức."""
    st.markdown(
        """
        <style>
        :root { --navy:#17324d; --navy-deep:#102638; --ivory:#fffdf8; --beige:#f7f2ea; --saffron:#c87932; --green:#4e6b57; --ink:#24313b; --muted:#65717a; --line:#dfd8cd; --white:#fff; }
        .stApp { background:var(--beige); color:var(--ink); font-family:Arial, sans-serif; }
        .main .block-container { background:var(--ivory); box-shadow:0 18px 42px rgba(23,50,77,.12); max-width:1180px; min-height:100vh; padding:1rem 2rem 0; }
        #MainMenu, footer, header[data-testid="stHeader"] { visibility:hidden; }
        [data-testid="stHeading"] { height:1px; margin:0; overflow:hidden; position:absolute; width:1px; }
        .utility-bar { background:var(--navy-deep); color:#dbe6eb; display:flex; font-size:.68rem; justify-content:flex-end; padding:.32rem 1.05rem; }
        .official-header { border:1px solid var(--line); border-top:0; }
        .brand-row { align-items:center; display:flex; gap:.75rem; padding:.72rem 1.05rem; }
        .agency-mark { align-items:center; background:var(--navy); border-radius:50%; color:var(--white); display:inline-flex; font-family:Georgia, serif; font-size:.68rem; font-weight:700; height:2.35rem; justify-content:center; letter-spacing:.05em; width:2.35rem; }
        .brand-copy { line-height:1.25; } .brand-copy strong { color:var(--navy); display:block; font-family:Georgia, serif; font-size:1.05rem; } .brand-copy span { color:var(--muted); font-size:.72rem; }
        .language-control { border:1px solid var(--line); border-radius:999px; color:var(--navy); font-size:.72rem; font-weight:700; margin-left:auto; padding:.4rem .75rem; }
        .access-control { background:var(--saffron); border-radius:5px; color:var(--white); font-size:.72rem; font-weight:700; margin-left:.5rem; padding:.45rem .75rem; }
        .portal-nav { border-top:1px solid var(--line); display:flex; gap:1.25rem; overflow:auto; padding:.58rem 1.05rem; white-space:nowrap; }
        .portal-nav a { color:var(--ink); font-size:.76rem; font-weight:700; text-decoration:none; } .portal-nav a:first-child { color:var(--saffron); }
        .hero-panel { background:var(--navy); border-radius:0 0 12px 12px; color:var(--white); margin-bottom:1rem; min-height:220px; overflow:hidden; padding:1.7rem 2.25rem; position:relative; }
        .hero-panel::before { background:#f6ecdf; content:""; height:100%; position:absolute; right:0; top:0; width:38%; }
        .hero-panel::after { border:1px solid rgba(255,255,255,.2); border-radius:50%; content:""; height:14rem; left:47%; position:absolute; top:-8rem; width:14rem; }
        .hero-copy { box-sizing:border-box; max-width:none; position:relative; width:58%; z-index:1; }
        .hero-kicker,.section-label,.sources-heading { font-size:.72rem; font-weight:800; letter-spacing:.11em; text-transform:uppercase; }
        .hero-kicker { color:#f5cd9e; margin:0 0 .4rem; } .hero-panel h1 { font-family:Georgia, serif; font-size:clamp(1.85rem,3vw,2.65rem); line-height:1.08; margin:0; } .hero-panel p { color:#e8eff1; font-size:.92rem; line-height:1.5; margin:.55rem 0 .8rem; max-width:36rem; }
        .hero-prompt { align-items:center; background:var(--white); border-radius:7px; box-shadow:0 8px 18px rgba(8,26,39,.18); color:#758089; display:flex; font-size:.82rem; gap:.6rem; max-width:500px; padding:.62rem .85rem; } .hero-prompt b { color:var(--saffron); font-size:1rem; }
        .suggestion-grid { margin-bottom:.8rem; } .section-label { color:var(--navy); margin:.1rem 0 .45rem; }
        .stButton > button { background:var(--white); border:1px solid var(--line); border-radius:7px; box-shadow:0 3px 9px rgba(23,50,77,.05); color:var(--navy); font-size:.78rem; font-weight:700; min-height:3.35rem; padding:.55rem .7rem; text-align:left; white-space:normal; width:100%; }
        .stButton > button:hover,.stButton > button:focus-visible { border-color:var(--saffron); box-shadow:0 5px 14px rgba(200,121,50,.18); color:var(--saffron); }
        .workspace-title { border-top:1px solid var(--line); padding-top:1rem; text-align:center; } .workspace-title h2,.feature-title h2,.trust-title h2 { color:var(--navy); font-family:Georgia, serif; font-size:1.35rem; margin:0; } .workspace-title p,.feature-title p,.trust-title p { color:var(--muted); font-size:.84rem; margin:.3rem auto .75rem; max-width:650px; }
        .category-panel { background:#f3ede4; border:1px solid var(--line); border-radius:8px; padding:.8rem; } .category-panel h3 { color:var(--navy); font-family:Georgia, serif; font-size:1rem; margin:0 0 .2rem; } .category-panel p { color:var(--muted); font-size:.72rem; line-height:1.4; margin:.2rem 0; } .category-list { list-style:none; margin:.45rem 0 .65rem; padding:0; } .category-list li { border-bottom:1px solid #e3dbd0; color:var(--navy); font-size:.78rem; font-weight:700; padding:.48rem 0; }
        .chat-panel { background:var(--white); border:1px solid var(--line); border-radius:8px; min-height:0; padding:.8rem; } .chat-panel-title { align-items:center; display:flex; justify-content:space-between; margin-bottom:.55rem; } .chat-panel-title h3 { color:var(--navy); font-family:Georgia, serif; margin:0; } .status-badge { border-radius:999px; display:inline-block; font-size:.64rem; font-weight:800; margin-right:.25rem; padding:.24rem .45rem; } .official { background:#f4e4d2; color:#8c531e; } .verified { background:#e3ebe4; color:#355540; } .latest { background:#e7eef3; color:#234d6d; }
        .assistant-empty { background:#f7f3ed; border-left:3px solid var(--saffron); color:var(--ink); font-size:.84rem; line-height:1.5; padding:.75rem; } .assistant-empty strong { color:var(--navy); display:block; margin-bottom:.2rem; }
        [data-testid="stChatMessage"] { background:var(--white); border:1px solid var(--line); border-radius:8px; box-shadow:none; margin-bottom:.85rem; padding:.85rem; }
        .citation-header { align-items:center; display:flex; gap:.3rem; margin-top:1rem; } .sources-heading { color:var(--navy); margin:0 .5rem 0 0; }
        [data-testid="stExpander"] { background:var(--ivory); border:1px solid var(--line); border-radius:7px; margin:.45rem 0; }
        .feedback-row { align-items:center; border-top:1px solid var(--line); display:flex; gap:.5rem; margin-top:.7rem; padding-top:.55rem; } .feedback-row span { color:var(--muted); font-size:.72rem; margin-right:auto; } .feedback-row .stButton > button { min-height:auto; padding:.32rem .55rem; }
        .feature-grid { margin-top:1.6rem; } .feature-title,.trust-title { text-align:center; } .feature-card { background:var(--white); border:1px solid var(--line); border-radius:7px; box-shadow:none; min-height:104px; padding:.75rem; } .feature-number { color:var(--saffron); font-family:Georgia, serif; font-size:1.2rem; } .feature-card h3 { color:var(--navy); font-family:Georgia, serif; font-size:.83rem; margin:.18rem 0; } .feature-card p { color:var(--muted); font-size:.7rem; line-height:1.35; margin:0; }
        .trust-panel { background:var(--navy); border-radius:8px; color:var(--white); margin:1.5rem 0 0; padding:1.2rem 1.35rem; text-align:center; } .trust-title h2 { color:var(--white); } .trust-title p { color:#d8e3e9; } .trust-items { display:grid; gap:.75rem; grid-template-columns:repeat(4,1fr); text-align:left; } .trust-items strong { color:#f7cf9b; display:block; font-size:.77rem; } .trust-items span { color:#d8e3e9; display:block; font-size:.68rem; line-height:1.35; margin-top:.18rem; }
        .portal-footer { background:var(--navy-deep); color:#d8e3e9; display:grid; gap:1rem; grid-template-columns:1.4fr 1fr 1fr; margin:1.5rem -2rem 0; padding:1.2rem 2.5rem; } .portal-footer strong { color:var(--white); font-family:Georgia, serif; font-size:.82rem; } .portal-footer span { display:block; font-size:.68rem; line-height:1.55; }
        [data-testid="stChatInput"] { border-color:var(--line); }
        @media (max-width:768px) { .main .block-container { padding-left:1rem; padding-right:1rem; } .hero-panel { background:var(--navy); padding:2rem 1.35rem; } .hero-copy { width:100%; } .portal-nav { gap:1rem; } .trust-items,.portal-footer { grid-template-columns:1fr; } .portal-footer { margin-left:-1rem; margin-right:-1rem; padding:1.6rem; } .utility-bar { padding-right:1rem; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_portal_header() -> None:
    """Hiển thị điều hướng và hero của cổng thông tin chính thức."""
    st.markdown(
        """
        <div class="utility-bar">Cổng thông tin tra cứu chính thức · Bảo mật và minh bạch</div>
        <header class="official-header">
          <div class="brand-row"><span class="agency-mark" aria-hidden="true">GKA</span>
            <div class="brand-copy"><strong>Government Knowledge Assistant</strong><span>Trợ lý tri thức dành cho công dân và hộ kinh doanh</span></div>
            <span class="language-control">Tiếng Việt</span><span class="access-control">Truy cập hệ thống</span>
          </div>
          <nav class="portal-nav" aria-label="Điều hướng chính"><a href="#trang-chu">Trang chủ</a><a href="#dich-vu">Dịch vụ</a><a href="#van-ban">Văn bản</a><a href="#huong-dan">Hướng dẫn</a><a href="#lien-he">Liên hệ</a></nav>
        </header>
        <section class="hero-panel" id="trang-chu"><div class="hero-copy"><p class="hero-kicker">Cổng tri thức có căn cứ</p>
          <h1>Trợ lý Tra cứu Thông tin Chính thức</h1>
          <p>Hỗ trợ hỏi đáp về thuế, thủ tục và nghĩa vụ kê khai dựa trên tài liệu đã xác thực. Mỗi câu trả lời đều kèm nguồn để bạn kiểm chứng.</p>
          <div class="hero-prompt" aria-label="Gợi ý cách đặt câu hỏi"><b>⌕</b> Hãy nhập câu hỏi của bạn...</div>
        </div></section>
        """,
        unsafe_allow_html=True,
    )


def render_category_panel() -> int:
    """Hiển thị danh mục và bộ lọc độc lập với pipeline truy xuất."""
    st.markdown('<aside class="category-panel"><h3>Danh mục tri thức</h3><p>Khoanh vùng nội dung trước khi đặt câu hỏi.</p><ul class="category-list">' + "".join(f"<li>{category}</li>" for category in KNOWLEDGE_CATEGORIES) + "</ul></aside>", unsafe_allow_html=True)
    st.markdown('<p class="section-label">Bộ lọc tra cứu</p>', unsafe_allow_html=True)
    st.selectbox("Loại tài liệu", ["Tất cả tài liệu", "Văn bản pháp lý", "Hướng dẫn", "Biểu mẫu"], key="document-type")
    st.selectbox("Thời điểm ban hành", ["Không giới hạn", "12 tháng gần đây", "Theo năm"], key="publication-date")
    return st.slider("Số nguồn tham khảo", 3, 10, 5)


def render_feature_cards() -> None:
    """Trình bày bốn năng lực chính của RAG chatbot."""
    cards = [
        ("01", "Tra cứu chính xác theo tài liệu gốc", "Đối chiếu câu trả lời với những đoạn tài liệu đã được truy xuất."),
        ("02", "Tóm tắt văn bản dài", "Làm rõ nội dung chính, giúp đọc nhanh tài liệu hành chính và chính sách."),
        ("03", "Trích dẫn nguồn rõ ràng", "Mở nguồn gốc, xem metadata và kiểm tra căn cứ của từng câu trả lời."),
        ("04", "Hỗ trợ công dân", "Diễn đạt dễ hiểu, phù hợp với nhu cầu tra cứu của hộ kinh doanh."),
    ]
    st.markdown('<section class="feature-title"><h2>Năng lực của trợ lý</h2><p>Hệ thống được thiết kế để hỗ trợ tra cứu có trách nhiệm, không thay thế văn bản gốc.</p></section>', unsafe_allow_html=True)
    columns = st.columns(4)
    for column, (number, title, description) in zip(columns, cards):
        column.markdown(f'<article class="feature-card"><span class="feature-number">{number}</span><h3>{title}</h3><p>{description}</p></article>', unsafe_allow_html=True)


def render_trust_section() -> None:
    """Hiển thị cam kết tin cậy của cổng tra cứu."""
    st.markdown(
        """
        <section class="trust-panel"><div class="trust-title"><h2>Thông tin có căn cứ, sử dụng có trách nhiệm</h2><p>RAG chatbot kết hợp AI với tài liệu được kiểm duyệt để phục vụ tra cứu minh bạch.</p></div>
          <div class="trust-items"><div><strong>Dữ liệu chính thức</strong><span>Ưu tiên tài liệu có nguồn rõ ràng.</span></div><div><strong>Dẫn nguồn minh bạch</strong><span>Hiển thị nguồn đã dùng để tạo câu trả lời.</span></div><div><strong>Bảo mật người dùng</strong><span>Không yêu cầu cung cấp thông tin nhạy cảm để tra cứu.</span></div><div><strong>AI có kiểm duyệt</strong><span>Từ chối trả lời khi thiếu bằng chứng phù hợp.</span></div></div>
        </section>
        <footer class="portal-footer" id="lien-he"><div><strong>Government Knowledge Assistant</strong><span>Trợ lý tra cứu thông tin chính thức cho công dân và hộ kinh doanh.</span></div><div><strong>Thông tin</strong><span>Chính sách bảo mật<br>Điều khoản sử dụng<br>Trợ giúp tiếp cận</span></div><div><strong>Hỗ trợ</strong><span>Liên hệ hỗ trợ<br>Hướng dẫn sử dụng<br>Bản quyền hệ thống</span></div></footer>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="Thuế & Kê khai Hộ Kinh Doanh", layout="wide")
    apply_theme()
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("suggested_query", None)

    render_portal_header()
    st.markdown('<p class="section-label suggestion-grid">Câu hỏi gợi ý</p>', unsafe_allow_html=True)
    question_columns = st.columns(3)
    for index, question in enumerate(SUGGESTED_QUESTIONS):
        if question_columns[index % 3].button(question, key=f"suggestion-{index}"):
            st.session_state.suggested_query = question

    st.markdown('<section class="workspace-title" id="dich-vu"><h2>Không gian tra cứu có trích nguồn</h2><p>Chọn danh mục, đặt câu hỏi và kiểm tra căn cứ của câu trả lời.</p></section>', unsafe_allow_html=True)
    category_column, chat_column = st.columns([1, 2.35], gap="large")
    with category_column:
        top_k = render_category_panel()
    with chat_column:
        st.markdown('<section class="chat-panel" id="van-ban"><div class="chat-panel-title"><h3>Trợ lý tra cứu</h3><span class="status-badge latest">Cập nhật mới nhất</span></div><div class="assistant-empty"><strong>Nguồn chính thức · Đã xác thực</strong>Tôi chỉ trả lời dựa trên tài liệu có thể kiểm chứng. Hãy đặt câu hỏi để bắt đầu tra cứu.</div></section>', unsafe_allow_html=True)
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                render_sources(message.get("sources", []))
        feedback_label, feedback_left, feedback_right = st.columns([2.3, 1, 1])
        with feedback_label:
            st.markdown('<div class="feedback-row"><span>Thông tin này có hữu ích không?</span></div>', unsafe_allow_html=True)
        with feedback_left:
            st.button("Hữu ích", key="feedback-helpful")
        with feedback_right:
            st.button("Chưa hữu ích", key="feedback-unhelpful")

    st.title("Thuế & Kê khai Hộ Kinh Doanh")
    query = st.chat_input("Hãy nhập câu hỏi của bạn...") or st.session_state.suggested_query
    render_feature_cards()
    render_trust_section()
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
