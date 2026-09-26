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
    st.title("🧭 RAG Du lịch")
    st.caption("Tra cứu Luật Du lịch, quản lý di sản và thông tin điểm đến Việt Nam.")
    top_k = st.slider("Số đoạn ngữ cảnh", 3, 10, 5)
    st.info("Câu trả lời chỉ sử dụng tài liệu trong kho và có nhãn nguồn [S#].")
    if st.button("Xóa lịch sử", icon=":material/delete:", width="stretch"):
        st.session_state.messages = []
        st.rerun()

st.title("Trợ lý thông tin Du lịch Việt Nam")
st.caption("Hỏi về quy định pháp luật, điểm đến, trải nghiệm và ẩm thực trong bộ tài liệu.")


def render_sources(sources: list[dict], retrieval_source: str) -> None:
    if not sources:
        return
    with st.expander(f"Nguồn tham khảo · {retrieval_source}", expanded=False):
        for index, source in enumerate(sources, start=1):
            metadata = source["metadata"]
            page = f" · trang {metadata['page']}" if metadata.get("page") is not None else ""
            score = f"{source['score']:.4f}"
            label = f"**[S{index}] {metadata['title']}**{page} · score {score}"
            if metadata.get("url"):
                st.markdown(f"{label} · [mở nguồn]({metadata['url']})")
            else:
                st.markdown(label)
            st.caption(source["content"][:320].replace("\n", " ") + ("…" if len(source["content"]) > 320 else ""))

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            render_sources(message.get("sources", []), message.get("retrieval_source", "none"))

query = st.chat_input("Nhập câu hỏi...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Đang tìm kiếm và đối chiếu nguồn..."):
            result = generate_with_citation(query, top_k=top_k)
        st.markdown(result["answer"])
        render_sources(result["sources"], result["retrieval_source"])

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
            "retrieval_source": result["retrieval_source"],
        }
    )
