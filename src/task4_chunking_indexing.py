"""Task 4 — Đọc tài liệu, chia chunk, tạo embedding và index vào ChromaDB."""

import os
import re
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).parent.parent
STANDARDIZED_DIR = ROOT_DIR / "data" / "standardized"
CHROMA_DIR = ROOT_DIR / "chroma_db"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
EMBEDDING_DIM = 1024

COLLECTION_NAME = "rag_documents"


@lru_cache(maxsize=2)
def get_local_model(model_name: str):
    """Chỉ tải model local một lần trong mỗi tiến trình."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Tạo embedding theo provider trong .env."""
    if not texts:
        return []

    provider = os.getenv(
        "EMBEDDING_PROVIDER", "sentence_transformers"
    ).lower()
    model_name = os.getenv("EMBEDDING_MODEL", EMBEDDING_MODEL)

    if provider == "sentence_transformers":
        model = get_local_model(model_name)
        vectors = model.encode(
            texts,
            normalize_embeddings=True,
        )
        return vectors.tolist()

    if provider == "openai":
        from openai import OpenAI

        response = OpenAI().embeddings.create(
            model=model_name,
            input=texts,
        )
        return [item.embedding for item in response.data]

    if provider == "gemini":
        from google import genai

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Thiếu GEMINI_API_KEY trong .env")

        client = genai.Client(api_key=api_key)
        response = client.models.embed_content(
            model=model_name,
            contents=texts,
        )
        return [item.values for item in response.embeddings]

    raise ValueError(f"EMBEDDING_PROVIDER không hỗ trợ: {provider}")


def get_collection():
    """Mở collection ChromaDB dùng cosine distance."""
    import chromadb

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def load_documents() -> list[dict]:
    """Đọc Markdown trong legal/ và news/ theo contract."""
    documents = []

    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue

        relative_path = path.relative_to(STANDARDIZED_DIR)
        doc_type = relative_path.parts[0]

        if doc_type not in {"legal", "news"}:
            continue

        title_match = re.search(r"(?m)^#\s+(.+)$", content)
        source_match = re.search(
            r"(?m)^\*\*Source:\*\*\s*(https?://\S+)",
            content,
        )

        documents.append(
            {
                "id": relative_path.as_posix(),
                "content": content,
                "metadata": {
                    "source": relative_path.as_posix(),
                    "title": (
                        title_match.group(1).strip()
                        if title_match
                        else path.stem
                    ),
                    "doc_type": doc_type,
                    "url": (
                        source_match.group(1)
                        if source_match
                        else None
                    ),
                },
            }
        )

    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia tài liệu; ID ổn định khi chạy lại cùng một corpus."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = []

    for document in documents:
        pieces = splitter.split_text(document["content"])

        for index, text in enumerate(pieces):
            if not text.strip():
                continue

            chunks.append(
                {
                    "id": f"{document['id']}::chunk-{index}",
                    "content": text,
                    "metadata": {
                        **document["metadata"],
                        "chunk_index": index,
                    },
                }
            )

    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Tạo embedding theo batch để tránh xử lý quá nhiều đoạn một lúc."""
    embedded = []

    for start in range(0, len(chunks), 32):
        batch = chunks[start : start + 32]
        vectors = embed_texts(
            [chunk["content"] for chunk in batch]
        )

        if len(vectors) != len(batch):
            raise ValueError("Số embedding không khớp số chunk")

        for chunk, vector in zip(batch, vectors):
            embedded.append(
                {
                    **chunk,
                    "embedding": vector,
                }
            )

        print(
            f"Embedded {min(start + 32, len(chunks))}"
            f"/{len(chunks)} chunks"
        )

    return embedded


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunk mới và bỏ ID cũ không còn trong corpus."""
    if not chunks:
        raise ValueError("Không có chunk để index")

    collection = get_collection()
    current_ids = {chunk["id"] for chunk in chunks}

    # Khi corpus đổi, không giữ lại chunk thuộc bản dữ liệu cũ.
    old_ids = set(collection.get(include=[])["ids"])
    stale_ids = sorted(old_ids - current_ids)

    for start in range(0, len(stale_ids), 100):
        collection.delete(ids=stale_ids[start : start + 100])

    for start in range(0, len(chunks), 64):
        batch = chunks[start : start + 64]

        # ChromaDB không nhận giá trị None trong metadata.
        metadatas = [
            {
                key: value
                for key, value in chunk["metadata"].items()
                if value is not None
            }
            for chunk in batch
        ]

        collection.upsert(
            ids=[chunk["id"] for chunk in batch],
            documents=[chunk["content"] for chunk in batch],
            embeddings=[chunk["embedding"] for chunk in batch],
            metadatas=metadatas,
        )

    print(
        f"Indexed {len(chunks)} chunks; "
        f"removed {len(stale_ids)} stale chunks"
    )


def run_pipeline() -> None:
    """Chạy toàn bộ bước index."""
    documents = load_documents()
    if not documents:
        raise ValueError(
            "Không có Markdown trong data/standardized/legal hoặc news"
        )

    chunks = chunk_documents(documents)
    embedded_chunks = embed_chunks(chunks)
    index_to_vectorstore(embedded_chunks)

    print(f"Documents: {len(documents)}")
    print(f"Chunks: {len(chunks)}")


if __name__ == "__main__":
    run_pipeline()