import time
import streamlit as st
from dotenv import load_dotenv
from src.contracts import GenerationResult, SearchResult, ChunkMetadata

load_dotenv()

st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide",
)

def mock_generate_with_citation(query: str, top_k: int) -> GenerationResult:
    """Hàm giả lập trả về kết quả giống hệt GenerationResult thật."""
    time.sleep(1) # Giả lập độ trễ API
    mock_metadata: ChunkMetadata = {
        "source": "thong-tu-06-2026-quy-che-tuyen-sinh-dai-hoc.md",
        "title": "Thông tư 06/2026 - Quy chế tuyển sinh đại học",
        "doc_type": "legal",
        "url": "https://vnu.edu.vn/tuyensinh2026",
        "chunk_index": 2
    }
    
    mock_source: SearchResult = {
        "id": "chunk_123",
        "content": f"Đây là đoạn văn bản giả lập được tìm thấy. Đại học Quốc gia Hà Nội năm 2026 sẽ tuyển sinh dựa trên 4 phương thức chính. (Câu hỏi của bạn: {query})",
        "score": 0.92,
        "metadata": mock_metadata,
        "retrieval_method": "dense"
    }

    return {
        "answer": f"Theo quy chế mới nhất, ĐHQGHN có 4 phương thức xét tuyển chính. \n\nTôi đã tìm thấy thông tin này dựa trên câu hỏi '{query}' của bạn.",
        "sources": [mock_source, mock_source][:top_k], # Giả lập trả về danh sách tài liệu
        "retrieval_source": "hybrid"
    }

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("⚙️ Cài đặt")
    st.caption("Tìm kiếm văn bản tuyển sinh ĐHQGHN")
    top_k = st.slider("Số lượng tài liệu tham khảo (top_k)", 1, 10, 3)

st.title("🤖 Chatbot Tuyển sinh ĐHQGHN 2026")
st.caption("Hỏi đáp thông tin tuyển sinh Đại học Quốc gia Hà Nội (Mock UI)")

# Hiển thị lịch sử chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("sources"):
            with st.expander(f"📚 Xem tài liệu tham khảo (Nguồn: {message['retrieval_source']})"):
                for idx, src in enumerate(message["sources"]):
                    st.markdown(f"**Tài liệu {idx+1}: {src['metadata']['title']}** (Điểm: `{src['score']:.2f}`)")
                    st.info(src["content"])

query = st.chat_input("Nhập câu hỏi của bạn về tuyển sinh ĐHQGHN...")

if query:
    # 1. Hiển thị câu hỏi của user
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # 2. Sinh câu trả lời với mock data
    with st.chat_message("assistant"):
        with st.spinner("Đang tìm kiếm và tổng hợp..."):
            result = mock_generate_with_citation(query, top_k)
            
        answer = result["answer"]
        sources = result["sources"]
        retrieval_source = result["retrieval_source"]
        
        st.markdown(answer)
        
        # Hiển thị sources ngay lúc vừa sinh xong
        if sources:
            with st.expander(f"📚 Xem tài liệu tham khảo (Nguồn: {retrieval_source})"):
                for idx, src in enumerate(sources):
                    st.markdown(f"**Tài liệu {idx+1}: {src['metadata']['title']}** (Điểm: `{src['score']:.2f}`)")
                    st.info(src["content"])

    # 3. Lưu lại vào session state
    st.session_state.messages.append({
        "role": "assistant", 
        "content": answer,
        "sources": sources,
        "retrieval_source": retrieval_source
    })
