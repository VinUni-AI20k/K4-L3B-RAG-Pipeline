"""
Task 4 — Chunking, embedding và indexing.

Hướng dẫn:
    1. Đọc toàn bộ Markdown trong data/standardized/.
    2. Chia văn bản bằng strategy đã chọn.
    3. Embed chunks bằng một provider duy nhất.
    4. Upsert vào ChromaDB với cosine distance.

Mỗi document/chunk phải theo docs/MODULE_CONTRACTS.md. ID cần ổn định để
chạy lại pipeline không tạo dữ liệu trùng. Task 5 phải dùng chung embed_texts().
"""

import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

# Giải thích lựa chọn tham số trong báo cáo nhóm.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "sentence_transformers")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
EMBEDDING_DIM = 1024

COLLECTION_NAME = "rag_documents"

# Cache model để không load lại nhiều lần
_st_model = None


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Dispatch theo EMBEDDING_PROVIDER trong .env."""
    global _st_model

    if EMBEDDING_PROVIDER == "sentence_transformers":
        from sentence_transformers import SentenceTransformer

        if _st_model is None:
            _st_model = SentenceTransformer(EMBEDDING_MODEL)
        return _st_model.encode(texts, show_progress_bar=False).tolist()

    elif EMBEDDING_PROVIDER == "openai":
        from openai import OpenAI

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        model = EMBEDDING_MODEL or "text-embedding-3-small"
        response = client.embeddings.create(input=texts, model=model)
        return [item.embedding for item in response.data]

    elif EMBEDDING_PROVIDER == "gemini":
        from google import genai

        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        model = EMBEDDING_MODEL or "text-embedding-004"
        embeddings = []
        for text in texts:
            result = client.models.embed_content(model=model, contents=text)
            embeddings.append(result.embeddings[0].values)
        return embeddings

    else:
        raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {EMBEDDING_PROVIDER!r}")


def get_collection():
    """Mở Chroma collection dùng cosine distance."""
    import chromadb

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def load_documents() -> list[dict]:
    """Đọc Markdown và trả về danh sách Document."""
    documents = []
    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        doc_type = "legal" if "legal" in path.parts else "news"
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue
        documents.append({
            "id": path.relative_to(STANDARDIZED_DIR).as_posix(),
            "content": content,
            "metadata": {
                "source": path.name,
                "title": path.stem.replace("-", " ").replace("_", " ").title(),
                "doc_type": doc_type,
                "url": None,
            },
        })
    return documents


def _split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Pure-Python recursive character splitter (mirrors RecursiveCharacterTextSplitter)."""
    separators = ["\n\n", "\n", ". ", " ", ""]

    def _split(text: str, seps: list[str]) -> list[str]:
        if not seps:
            return [text]
        sep = seps[0]
        if sep and sep in text:
            splits = text.split(sep)
        else:
            return _split(text, seps[1:])

        chunks: list[str] = []
        current = ""
        for part in splits:
            piece = (current + sep + part).lstrip(sep) if current else part
            if len(piece) <= chunk_size:
                current = piece
            else:
                if current:
                    chunks.append(current)
                if len(part) > chunk_size:
                    chunks.extend(_split(part, seps[1:]))
                    current = ""
                else:
                    current = part
        if current:
            chunks.append(current)
        return chunks

    raw_chunks = _split(text, separators)

    # Apply overlap: merge small consecutive chunks and add overlap between large ones
    result: list[str] = []
    for raw in raw_chunks:
        if not raw.strip():
            continue
        if result and len(result[-1]) + 1 + len(raw) <= chunk_size:
            result[-1] = result[-1] + " " + raw
        else:
            if result and chunk_overlap > 0:
                overlap_text = result[-1][-chunk_overlap:]
                raw = overlap_text + raw
            result.append(raw[:chunk_size] if len(raw) > chunk_size else raw)
    return [c for c in result if c.strip()]


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia Document thành chunks có id và chunk_index."""
    chunks = []
    for document in documents:
        texts = _split_text(document["content"], CHUNK_SIZE, CHUNK_OVERLAP)
        for index, text in enumerate(texts):
            chunks.append({
                "id": f"{document['id']}::chunk-{index}",
                "content": text,
                "metadata": {**document["metadata"], "chunk_index": index},
            })
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Thêm embedding vào từng chunk."""
    vectors = embed_texts([chunk["content"] for chunk in chunks])
    result = []
    for chunk, vector in zip(chunks, vectors):
        embedded = dict(chunk)
        embedded["embedding"] = vector
        result.append(embedded)
    return result


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks vào ChromaDB."""
    collection = get_collection()
    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=[chunk["content"] for chunk in chunks],
        embeddings=[chunk["embedding"] for chunk in chunks],
        metadatas=[chunk["metadata"] for chunk in chunks],
    )


def run_pipeline() -> None:
    """Chạy load, chunk, embed và index."""
    documents = load_documents()
    if not documents:
        print(f"No documents found in {STANDARDIZED_DIR}. Run task3 first.")
        return
    print(f"Loaded {len(documents)} documents")
    chunks = chunk_documents(documents)
    print(f"Created {len(chunks)} chunks")
    embedded_chunks = embed_chunks(chunks)
    index_to_vectorstore(embedded_chunks)
    print(f"Indexed {len(embedded_chunks)} chunks into ChromaDB at {CHROMA_DIR}")


if __name__ == "__main__":
    run_pipeline()
