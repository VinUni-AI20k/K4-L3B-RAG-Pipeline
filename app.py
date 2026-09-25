import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation

load_dotenv()

st.set_page_config(
    page_title="Hỏi đáp Tuyển sinh NEU 2026",
    page_icon="🎓",
    layout="wide",
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("🎓 Tuyển sinh NEU 2026")
    st.caption("Hệ thống hỏi đáp RAG Pipeline thông minh về quy chế và đề án tuyển sinh NEU năm 2026.")
    top_k = st.slider("Số lượng tài liệu truy xuất (top_k)", min_value=1, max_value=10, value=5)
    st.markdown("---")
    st.markdown("""
    **Phạm vi tài liệu:**
    - Đề án tuyển sinh Đại học chính quy 2026
    - Tuyển sinh liên thông cao đẳng / đại học 2026
    - Tin tức và hướng dẫn tuyển sinh FIT NEU 2026
    """)
    if st.button("Xóa lịch sử hội thoại"):
        st.session_state.messages = []
        st.rerun()

st.title("Trợ lý Hỏi đáp Tuyển sinh NEU 2026")
st.caption("Chatbot RAG sử dụng phương pháp tìm kiếm lai (Hybrid Dense + BM25 + RRF) và trích dẫn bằng chứng chính xác.")

# Hiển thị lịch sử chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        sources = message.get("sources", [])
        if sources:
            retrieval_source = message.get("retrieval_source", "hybrid")
            with st.expander(f"📚 Xem {len(sources)} nguồn tài liệu trích dẫn (Phương thức: {retrieval_source})"):
                for idx, src in enumerate(sources, 1):
                    meta = src.get("metadata", {})
                    title = meta.get("title", "Tài liệu")
                    source_file = meta.get("source", "Không rõ")
                    score = src.get("score", 0.0)
                    method = src.get("retrieval_method", "hybrid")
                    url = meta.get("url")
                    
                    header = f"**[Tài liệu {idx}] {title}** — Nguồn: `{source_file}` | Điểm: `{score:.4f}` | Cơ chế: `{method}`"
                    if url:
                        header += f" | [Link gốc]({url})"
                    st.markdown(header)
                    st.text(src.get("content", "").strip())
                    st.markdown("---")

query = st.chat_input("Nhập câu hỏi về tuyển sinh NEU 2026...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Đang tìm kiếm thông tin và tổng hợp câu trả lời..."):
            result = generate_with_citation(query, top_k=top_k)
            answer = result["answer"]
            sources = result["sources"]
            retrieval_source = result["retrieval_source"]

            st.markdown(answer)

            if sources:
                with st.expander(f"📚 Xem {len(sources)} nguồn tài liệu trích dẫn (Phương thức: {retrieval_source})"):
                    for idx, src in enumerate(sources, 1):
                        meta = src.get("metadata", {})
                        title = meta.get("title", "Tài liệu")
                        source_file = meta.get("source", "Không rõ")
                        score = src.get("score", 0.0)
                        method = src.get("retrieval_method", "hybrid")
                        url = meta.get("url")

                        header = f"**[Tài liệu {idx}] {title}** — Nguồn: `{source_file}` | Điểm: `{score:.4f}` | Cơ chế: `{method}`"
                        if url:
                            header += f" | [Link gốc]({url})"
                        st.markdown(header)
                        st.text(src.get("content", "").strip())
                        st.markdown("---")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "retrieval_source": retrieval_source,
    })
