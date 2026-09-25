import json
import os
import re
import time
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

import src.task10_generation as generation
from src.embedding_comparison import compare_embeddings


load_dotenv()

st.set_page_config(
    page_title="HUTECH tuyển sinh 2026",
    page_icon=":material/school:",
    layout="wide",
)

REFUSAL = "Tôi chưa tìm thấy đủ thông tin trong bộ tài liệu hiện có để trả lời chắc chắn."

MOCK_DOCUMENTS = [
    {
        "id": "mock-overview",
        "title": "Tổng quan tuyển sinh HUTECH 2026",
        "source": "hutech-admission-2026-overview-mock.md",
        "content": (
            "Tài liệu tổng quan tuyển sinh HUTECH năm 2026. Thí sinh cần theo dõi "
            "đề án tuyển sinh, thông báo chính thức và các mốc đăng ký của trường "
            "để cập nhật chỉ tiêu, ngành đào tạo và điều kiện xét tuyển."
        ),
    },
    {
        "id": "mock-methods",
        "title": "Phương thức xét tuyển HUTECH 2026",
        "source": "hutech-admission-2026-methods-mock.md",
        "content": (
            "Các phương thức xét tuyển HUTECH 2026 gồm những nhóm phương thức được "
            "công bố trong đề án tuyển sinh của trường. Thí sinh cần kiểm tra điều "
            "kiện, hồ sơ và thời hạn riêng của từng phương thức trước khi đăng ký."
        ),
    },
    {
        "id": "mock-documents",
        "title": "Hồ sơ đăng ký xét tuyển HUTECH 2026",
        "source": "hutech-admission-2026-documents-mock.md",
        "content": (
            "Hồ sơ xét tuyển có thể gồm thông tin cá nhân, kết quả học tập, giấy tờ "
            "tùy thân và minh chứng theo phương thức đăng ký. Hồ sơ phải được kiểm "
            "tra đầy đủ trước khi gửi và thí sinh nên lưu lại minh chứng đăng ký."
        ),
    },
    {
        "id": "mock-timeline",
        "title": "Mốc thời gian tuyển sinh HUTECH 2026",
        "source": "hutech-admission-2026-timeline-mock.md",
        "content": (
            "Các mốc mở đăng ký, nhận hồ sơ, công bố kết quả và xác nhận nhập học "
            "có thể khác nhau theo phương thức. Thí sinh cần xem lịch tuyển sinh "
            "chính thức của HUTECH trước mỗi đợt đăng ký."
        ),
    },
    {
        "id": "mock-tuition",
        "title": "Học phí và học bổng HUTECH 2026",
        "source": "hutech-admission-2026-tuition-scholarship-mock.md",
        "content": (
            "Thông tin học phí, chính sách hỗ trợ và học bổng HUTECH 2026 cần được "
            "đối chiếu với thông báo tài chính chính thức theo ngành và chương trình. "
            "Mức học phí có thể thay đổi theo từng năm học."
        ),
    },
]

REAL_RETRIEVE = generation.retrieve


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"\w+", text.lower(), flags=re.UNICODE))


def mock_retrieve(query: str, top_k: int = 5, **_: object) -> list[dict]:
    """Mock retrieval seam; replace this function with Task 9 when data is ready."""
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    ranked = []
    for index, document in enumerate(MOCK_DOCUMENTS):
        document_tokens = _tokenize(f"{document['title']} {document['content']}")
        overlap = len(query_tokens & document_tokens)
        if overlap:
            ranked.append((overlap, index, document))

    if not ranked and any(token in query_tokens for token in {"tuyển", "sinh", "hutech"}):
        ranked = [(1, index, document) for index, document in enumerate(MOCK_DOCUMENTS[:2])]

    ranked.sort(key=lambda item: (-item[0], item[1]))
    results = []
    for rank, (overlap, _, document) in enumerate(ranked[:top_k], 1):
        results.append(
            {
                "id": document["id"],
                "content": document["content"],
                "score": overlap / rank,
                "metadata": {
                    "source": document["source"],
                    "title": document["title"],
                    "doc_type": "legal",
                    "url": None,
                    "chunk_index": 0,
                },
                "retrieval_method": "hybrid",
            }
        )
    return results


def render_sources(sources: list[dict]) -> None:
    if not sources:
        return
    with st.expander(f"Nguồn tham khảo ({len(sources)})"):
        for source in sources:
            metadata = source["metadata"]
            st.markdown(f"**{metadata['title']}**")
            st.caption(
                f"{metadata['source']} · retrieval score {source['score']:.3f} · "
                f"{source['retrieval_method']}"
            )
            st.write(source["content"])


def render_embedding_comparison(query: str, top_k: int) -> None:
    """Show two vectorization methods on the same real corpus query."""
    with st.status("Đang so sánh hai embedding methods", type="step") as status:
        comparison = compare_embeddings(query, top_k=top_k)
        status.update(label="Đã so sánh embedding", state="complete")

    left, right = st.columns(2)
    panels = ((left, "MiniLM dense", comparison["MiniLM"]), (right, "BGE-M3 / TF-IDF fallback", comparison["BGE-M3"]))
    for panel, title, results in panels:
        with panel:
            st.markdown(f"**{title}**")
            for rank, result in enumerate(results, 1):
                metadata = result["metadata"]
                st.caption(
                    f"{rank}. {metadata['source']} · score {result['score']:.3f}"
                )
                st.write(result["content"][:280] + ("..." if len(result["content"]) > 280 else ""))
    if comparison["BGE-M3_status"] != "ready":
        st.warning(
            "BGE-M3 chưa sẵn sàng trong cache; đang hiển thị TF-IDF sparse embedding "
            f"làm baseline thứ hai. ({comparison['BGE-M3_status']})"
        )


def generate_from_retrieved(query: str, sources: list[dict]) -> dict:
    """Generate from already retrieved chunks so the live pipeline runs once."""
    if not sources:
        return {"answer": REFUSAL, "sources": [], "retrieval_source": "none"}
    context = generation.format_context(generation.reorder_for_llm(sources))
    try:
        answer = generation.call_llm(
            generation.SYSTEM_PROMPT,
            f"Context:\n{context}\n\nQuestion: {query}",
        ).strip()
    except Exception:
        answer = ""
    method = sources[0]["retrieval_method"]
    return {
        "answer": answer or REFUSAL,
        "sources": sources,
        "retrieval_source": method if method in {"hybrid", "pageindex"} else "hybrid",
    }


def analyze_golden_dataset(top_k: int) -> None:
    path = Path(__file__).parent / "group_project" / "evaluation" / "golden_dataset.json"
    dataset = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    hits = 0
    scores = []
    with st.status(f"Đang chạy {len(dataset)} golden queries", type="step") as status:
        for index, item in enumerate(dataset, 1):
            results = REAL_RETRIEVE(item["question"], top_k=top_k)
            expected_source = Path(item["expected_context"]).name
            hit = any(result["metadata"].get("source") == expected_source for result in results)
            best_score = max((float(result["score"]) for result in results), default=0.0)
            hits += int(hit)
            scores.append(best_score)
            rows.append({
                "#": index,
                "question": item["question"],
                "expected_source": expected_source,
                "top_source": results[0]["metadata"].get("source", "") if results else "",
                "hit": hit,
                "best_score": round(best_score, 4),
                "method": results[0]["retrieval_method"] if results else "none",
            })
        status.update(label="Đã phân tích golden dataset", state="complete")
    metric_left, metric_mid, metric_right = st.columns(3)
    metric_left.metric("Context hit rate", f"{hits / len(dataset):.1%}")
    metric_mid.metric("Queries", len(dataset))
    metric_right.metric("Average top score", f"{sum(scores) / len(scores):.3f}")
    st.dataframe(rows, hide_index=True, width="stretch")


def reset_chat() -> None:
    st.session_state.messages = []


st.session_state.setdefault("messages", [])
st.session_state.setdefault("use_mock_data", False)
st.session_state.setdefault("show_embedding_comparison", True)

with st.sidebar:
    st.header("Cấu hình")
    use_mock_data = st.toggle(
        "Dùng mock retrieval",
        value=st.session_state.use_mock_data,
        help="Tắt tùy chọn này khi Task 1–6 đã có data thật và vector index.",
    )
    st.session_state.use_mock_data = use_mock_data
    st.session_state.show_embedding_comparison = st.checkbox(
        "So sánh hai embedding methods",
        value=st.session_state.show_embedding_comparison,
    )
    top_k = st.slider("Số tài liệu tham khảo", min_value=2, max_value=5, value=3)
    st.button("Xóa cuộc trò chuyện", icon=":material/delete:", on_click=reset_chat)
    analyze_golden = st.button("Phân tích golden dataset", icon=":material/analytics:")

    st.divider()
    st.caption(f"LLM provider: `{generation.LLM_PROVIDER or 'chưa cấu hình'}`")
    st.caption(
        "LLM key: "
        + ("đã cấu hình" if any(os.getenv(key) for key in (
            "OPENAI_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY"
        )) else "chưa cấu hình")
    )
    if use_mock_data:
        st.info("Mock tài liệu đang bật. Phần trả lời vẫn gọi LLM thật.")
    else:
        st.success("Real retrieval đang bật: ChromaDB + BM25 + RRF")

generation.retrieve = mock_retrieve if use_mock_data else REAL_RETRIEVE

st.title("Tư vấn tuyển sinh HUTECH 2026")
st.caption(
    "Hỏi đáp dựa trên corpus tuyển sinh HUTECH 2026 với real retrieval và citation từ nguồn."
)

if analyze_golden:
    st.subheader("Phân tích golden dataset")
    analyze_golden_dataset(top_k)

if not st.session_state.messages:
    with st.container(border=True):
        st.subheader("Bạn muốn tìm hiểu điều gì?")
        st.write(
            "Chatbot có thể hỗ trợ tra cứu phương thức xét tuyển, hồ sơ, mốc thời gian, "
            "học phí và học bổng từ context được cung cấp."
        )
        suggestions = {
            ":material/list_alt: Hồ sơ xét tuyển cần gì?": "Hồ sơ xét tuyển HUTECH 2026 cần những gì?",
            ":material/calendar_month: Mốc thời gian": "Các mốc thời gian tuyển sinh HUTECH 2026 là gì?",
            ":material/payments: Học phí và học bổng": "Học phí và học bổng HUTECH 2026 thế nào?",
        }
        selected = st.pills("Câu hỏi gợi ý", list(suggestions), label_visibility="collapsed")
    prompt = suggestions.get(selected) if selected else None
else:
    prompt = None

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            render_sources(message["sources"])

chat_prompt = st.chat_input(
    "Ví dụ: HUTECH 2026 có những phương thức xét tuyển nào?",
    submit_mode="disable",
)
prompt = chat_prompt or prompt

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.status("Luồng xử lý real retrieval", type="compact") as flow:
            with st.status("1. Dense + BM25 + RRF", type="step"):
                sources = generation.retrieve(prompt, top_k=top_k)
                st.caption(f"Đã lấy {len(sources)} source từ {sources[0]['retrieval_method'] if sources else 'none'}")
            if st.session_state.show_embedding_comparison:
                render_embedding_comparison(prompt, top_k)
            with st.status("2. Generate answer với citation", type="step"):
                result = generate_from_retrieved(prompt, sources)
            flow.update(label="Đã hoàn tất real retrieval pipeline", state="complete")
        answer = result["answer"] or REFUSAL
        st.markdown(answer)
        render_sources(result["sources"])

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": result["sources"],
        }
    )
