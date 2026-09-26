import streamlit as st
from dotenv import load_dotenv
from src.task10_generation import generate_with_citation

load_dotenv()

st.set_page_config(page_title="RAG Chatbot", page_icon="🤖", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("RAG Chatbot")
    st.caption("Chatbot hỏi đáp về Du lịch Việt Nam")
    top_k = st.slider("Số chunks", 3, 10, 5)

st.title("RAG Chatbot")
st.caption("Chatbot hỏi đáp về Du lịch Việt Nam")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("Nguồn tham khảo"):
                for idx, src in enumerate(message["sources"]):
                    st.write(f"**Nguồn {idx+1}:** {src['metadata']['title']} ({src['metadata']['source']})")
                    st.write(f"*Score: {src.get('score', 0):.4f} | Phương pháp: {src.get('retrieval_method', 'unknown')}*")
                    st.write(src["content"])

query = st.chat_input("Nhập câu hỏi...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)
        
    with st.chat_message("assistant"):
        try:
            result = generate_with_citation(query, top_k=top_k)
            answer = result["answer"]
            sources = result["sources"]
            retrieval_source = result.get("retrieval_source", "none")
            
            st.markdown(answer)
            
            if sources:
                with st.expander("Nguồn tham khảo"):
                    for idx, src in enumerate(sources):
                        st.write(f"**Nguồn {idx+1}:** {src['metadata']['title']} ({src['metadata']['source']})")
                        st.write(f"*Score: {src.get('score', 0):.4f} | Phương pháp: {src.get('retrieval_method', 'unknown')}*")
                        st.write(src["content"])
                        
            st.session_state.messages.append({
                "role": "assistant", 
                "content": answer,
                "sources": sources,
                "retrieval_source": retrieval_source
            })
        except Exception as e:
            error_msg = f"Đã xảy ra lỗi: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
