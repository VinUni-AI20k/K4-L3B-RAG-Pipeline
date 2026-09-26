from src.task4_chunking_indexing import load_documents
from src.task8_pageindex_vectorless import _local_search
from src.task10_generation import format_context, generate_with_citation


def test_all_standardized_documents_keep_public_source_urls():
    documents = load_documents()

    assert len(documents) >= 8
    assert all(document["metadata"]["url"] for document in documents)


def test_local_fallback_rejects_out_of_domain_queries():
    assert _local_search("Viết mã Python sắp xếp danh sách", top_k=5) == []
    assert _local_search("Giá cổ phiếu Apple hôm nay", top_k=5) == []


def test_generation_citation_order_matches_returned_sources(monkeypatch):
    chunks = [
        {
            "id": f"doc::chunk-{index}",
            "content": f"Evidence {index}",
            "score": 1.0 - index / 10,
            "metadata": {
                "source": "source.md",
                "title": f"Source {index}",
                "doc_type": "news",
                "url": "https://example.com/source",
                "chunk_index": index,
            },
            "retrieval_method": "hybrid",
        }
        for index in range(5)
    ]
    observed = {}

    monkeypatch.setattr("src.task10_generation.retrieve", lambda *args, **kwargs: chunks)

    def fake_llm(system_prompt, user_message):
        observed["context"] = user_message
        return "Câu trả lời có căn cứ [1]."

    monkeypatch.setattr("src.task10_generation.call_llm", fake_llm)
    result = generate_with_citation("question", top_k=5)

    assert result["sources"][0]["id"] == "doc::chunk-0"
    assert "[1] Title: Source 0" in observed["context"]
    assert format_context(result["sources"]) in observed["context"]
