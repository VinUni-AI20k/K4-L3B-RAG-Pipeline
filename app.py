import streamlit as st
from dotenv import load_dotenv


load_dotenv()

st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide",
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("🤖 RAG Chatbot")
    st.caption("Chatbot trả lời từ tài liệu của nhóm")
    top_k = st.slider("Số chunks", 3, 10, 5)
    st.divider()
    st.markdown("**Cách sử dụng:**")
    st.markdown("1. Đặt câu hỏi liên quan đến chủ đề tài liệu")
    st.markdown("2. Bot trả lời kèm citation rõ nguồn")
    st.markdown("3. Xem sources để kiểm chứng")

st.title("🤖 RAG Chatbot")
st.caption("Trả lời dựa trên tài liệu đã thu thập — kèm citation kiểm chứng được")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander(f"📚 {len(message['sources'])} nguồn tài liệu"):
                for idx, src in enumerate(message["sources"], 1):
                    meta = src.get("metadata", {})
                    score = src.get("score", 0)
                    method = src.get("retrieval_method", "")
                    st.markdown(
                        f"**[{idx}] {meta.get('title', 'N/A')}** "
                        f"(`{meta.get('source', 'N/A')}`) — "
                        f"score: `{score:.3f}` | method: `{method}`"
                    )
                    st.caption(src.get("content", "")[:300] + "...")

query = st.chat_input("Nhập câu hỏi...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Đang tìm kiếm và tổng hợp..."):
            try:
                from src.task10_generation import generate_with_citation

                result = generate_with_citation(query, top_k=top_k)
                answer = result["answer"]
                sources = result.get("sources", [])
                retrieval_source = result.get("retrieval_source", "none")
            except Exception as error:
                answer = f"⚠️ Lỗi hệ thống: {error}"
                sources = []
                retrieval_source = "none"

        st.markdown(answer)

        if sources:
            st.caption(f"🔍 Retrieval: `{retrieval_source}` — {len(sources)} chunks")
            with st.expander(f"📚 {len(sources)} nguồn tài liệu"):
                for idx, src in enumerate(sources, 1):
                    meta = src.get("metadata", {})
                    score = src.get("score", 0)
                    method = src.get("retrieval_method", "")
                    st.markdown(
                        f"**[{idx}] {meta.get('title', 'N/A')}** "
                        f"(`{meta.get('source', 'N/A')}`) — "
                        f"score: `{score:.3f}` | method: `{method}`"
                    )
                    st.caption(src.get("content", "")[:300] + "...")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "retrieval_source": retrieval_source,
    })
