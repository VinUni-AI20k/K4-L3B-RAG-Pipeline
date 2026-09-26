import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation


load_dotenv()

st.set_page_config(
    page_title="Trợ lý Du lịch Việt Nam",
    page_icon="🧭",
    layout="wide",
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("Trợ lý Du lịch Việt Nam")
    st.caption("Dense + BM25 + RRF, fallback và citation kiểm chứng được")
    top_k = st.slider("Số chunks", 3, 10, 5)

st.title("Trợ lý Du lịch Việt Nam")
st.caption("Hỏi về cẩm nang, ẩm thực và quy định du lịch trong corpus của nhóm")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            st.caption(f"Nguồn truy hồi: {message.get('retrieval_source', 'unknown')}")
            with st.expander("Xem nguồn"):
                for source in message["sources"]:
                    metadata = source.get("metadata", {})
                    title = metadata.get("title", metadata.get("source", "Unknown"))
                    url = metadata.get("url")
                    st.markdown(f"**[{title}]({url})**" if url else f"**{title}**")
                    st.caption(
                        f"Phương thức: {source.get('retrieval_method', 'unknown')} | "
                        f"Score: {source.get('score', 0):.4f}"
                    )

query = st.chat_input("Nhập câu hỏi...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        try:
            generation = generate_with_citation(query, top_k=top_k)
        except Exception:
            generation = {
                "answer": "Tôi không thể xác minh thông tin này từ nguồn hiện có.",
                "sources": [],
                "retrieval_source": "none",
            }
        answer = generation["answer"]
        sources = generation.get("sources", [])
        st.markdown(answer)
        if sources:
            st.caption(f"Nguồn truy hồi: {generation.get('retrieval_source', 'unknown')}")
            with st.expander("Xem nguồn"):
                for source in sources:
                    metadata = source.get("metadata", {})
                    title = metadata.get("title", metadata.get("source", "Unknown"))
                    url = metadata.get("url")
                    st.markdown(f"**[{title}]({url})**" if url else f"**{title}**")
                    st.caption(
                        f"Phương thức: {source.get('retrieval_method', 'unknown')} | "
                        f"Score: {source.get('score', 0):.4f}"
                    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources,
            "retrieval_source": generation.get("retrieval_source", "none"),
        }
    )
