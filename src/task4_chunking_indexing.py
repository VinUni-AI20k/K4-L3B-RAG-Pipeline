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
import re
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

load_dotenv()

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DIM = 1024
COLLECTION_NAME = "rag_documents"

_embed_model = None


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed danh sách text bằng SentenceTransformer. Dùng chung cho Task 4 và Task 5."""
    global _embed_model
    if _embed_model is None:
        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        print(f"Loading embedding model: {model_name}...")
        _embed_model = SentenceTransformer(model_name)
    return _embed_model.encode(
        texts,
        batch_size=16,
        convert_to_numpy=True,
        show_progress_bar=False,
    ).tolist()


def get_collection():
    """Mở Chroma collection dùng cosine distance."""
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def load_documents() -> list[dict]:
    """Đọc Markdown và trả về danh sách Document."""
    documents = []
    directory = STANDARDIZED_DIR
    if not directory.exists():
        return documents

    for path in sorted(directory.rglob("*.md")):
        content = path.read_text(encoding="utf-8")
        if not content.strip():
            continue

        doc_type = "legal" if "legal" in path.parts else "news"

        url = None
        url_match = re.search(r"\*\*Source\*\*:\s*(https?://\S+)", content)
        if url_match:
            url = url_match.group(1)

        title = path.stem.replace("_", " ").replace("-", " ").title()
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()

        doc_id = path.relative_to(directory).as_posix()

        documents.append({
            "id": doc_id,
            "content": content,
            "metadata": {
                "source": path.name,
                "title": title,
                "doc_type": doc_type,
                "url": url,
            },
        })
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia Document thành chunks có id và chunk_index."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = []
    for document in documents:
        for index, text in enumerate(splitter.split_text(document["content"])):
            chunks.append({
                "id": f"{document['id']}::chunk-{index}",
                "content": text,
                "metadata": {**document["metadata"], "chunk_index": index},
            })
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Embed theo lô nhỏ, không đưa toàn bộ corpus vào model cùng lúc."""
    if not chunks:
        return []

    batch_size = 32
    result = []

    for start in range(0, len(chunks), batch_size):
        batch = chunks[start:start + batch_size]
        vectors = embed_texts([chunk["content"] for chunk in batch])

        for chunk, vector in zip(batch, vectors):
            result.append({**chunk, "embedding": vector})

        print(f"Embedded {min(start + batch_size, len(chunks))}/{len(chunks)} chunks")

    return result


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks vào ChromaDB."""
    collection = get_collection()
    batch_size = 5000
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        collection.upsert(
            ids=[chunk["id"] for chunk in batch],
            documents=[chunk["content"] for chunk in batch],
            embeddings=[chunk["embedding"] for chunk in batch],
            metadatas=[chunk["metadata"] for chunk in batch],
        )


def run_pipeline() -> None:
    """Chạy load, chunk, embed và index."""
    documents = load_documents()
    print(f"Loaded {len(documents)} documents")
    chunks = chunk_documents(documents)
    print(f"Created {len(chunks)} chunks")
    embedded_chunks = embed_chunks(chunks)
    index_to_vectorstore(embedded_chunks)
    print(f"Indexed {len(embedded_chunks)} chunks to ChromaDB successfully!")


if __name__ == "__main__":
    run_pipeline()
