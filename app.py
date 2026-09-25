import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation


load_dotenv()

st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="",
    layout="wide",
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("RAG Chatbot")
    st.caption("Trợ lý hỏi đáp dựa trên bộ tài liệu đã được lập chỉ mục")
    top_k = st.slider("Số chunks", 3, 10, 5)

st.title("RAG Chatbot")
st.caption("Câu trả lời chỉ sử dụng thông tin từ các nguồn được hiển thị.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        for source in message.get("sources", []):
            metadata = source["metadata"]
            with st.expander(metadata["title"]):
                st.caption(
                    f"{metadata['source']} · {source['retrieval_method']} · "
                    f"score={source['score']:.4f}"
                )
                if metadata.get("url"):
                    st.markdown(f"[Mở nguồn]({metadata['url']})")
                st.write(source["content"])

query = st.chat_input("Nhập câu hỏi...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Đang tìm tài liệu và tạo câu trả lời..."):
            result = generate_with_citation(query, top_k=top_k)
        st.markdown(result["answer"])
        for source in result["sources"]:
            metadata = source["metadata"]
            with st.expander(metadata["title"]):
                st.caption(
                    f"{metadata['source']} · {source['retrieval_method']} · "
                    f"score={source['score']:.4f}"
                )
                if metadata.get("url"):
                    st.markdown(f"[Mở nguồn]({metadata['url']})")
                st.write(source["content"])

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"],
    })
