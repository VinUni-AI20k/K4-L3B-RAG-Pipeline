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

from .contracts import validate_document


load_dotenv()

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "gemini").lower()
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
COLLECTION_NAME = "rag_documents"

_gemini_client = None
_openai_client = None
_st_model = None


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed texts theo EMBEDDING_PROVIDER trong .env."""
    if not texts:
        return []

    global _gemini_client, _openai_client, _st_model
    provider = os.getenv("EMBEDDING_PROVIDER", EMBEDDING_PROVIDER).lower()
    model = os.getenv("EMBEDDING_MODEL", EMBEDDING_MODEL)

    if provider == "gemini":
        from google import genai

        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required for Gemini embedding")
        if _gemini_client is None:
            _gemini_client = genai.Client(api_key=api_key)

        embeddings: list[list[float]] = []
        batch_size = 50
        import time

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    response = _gemini_client.models.embed_content(
                        model=model,
                        contents=batch,
                    )
                    for item in response.embeddings:
                        embeddings.append(list(item.values))
                    break
                except Exception as err:
                    err_str = str(err)
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        wait_sec = 5 * (attempt + 1)
                        print(f"Rate limited (429). Retrying batch {i // batch_size + 1} in {wait_sec}s...")
                        time.sleep(wait_sec)
                    else:
                        raise err
            else:
                raise RuntimeError(f"Failed to embed batch starting at index {i} after {max_retries} retries")

            if i + batch_size < len(texts):
                time.sleep(1.0)

        return embeddings

    elif provider == "openai":
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI embedding")
        if _openai_client is None:
            _openai_client = OpenAI(api_key=api_key)

        embeddings = []
        batch_size = 50
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = _openai_client.embeddings.create(
                input=batch,
                model=model or "text-embedding-3-small",
            )
            for item in response.data:
                embeddings.append(item.embedding)
        return embeddings

    elif provider == "sentence_transformers":
        from sentence_transformers import SentenceTransformer

        if _st_model is None:
            _st_model = SentenceTransformer(model or "BAAI/bge-m3")
        return _st_model.encode(texts).tolist()

    else:
        raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {provider}")


def get_collection():
    """Mở Chroma collection dùng cosine distance."""
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def load_documents() -> list[dict]:
    """Đọc Markdown và trả về danh sách Document theo contract."""
    documents: list[dict] = []
    if not STANDARDIZED_DIR.exists():
        return documents

    paths = sorted(
        [
            p
            for p in STANDARDIZED_DIR.rglob("*.md")
            if p.is_file() and not p.name.startswith(".")
        ]
    )

    for path in paths:
        doc_type = "legal" if "legal" in path.parts else "news"
        content = path.read_text(encoding="utf-8")
        if not content.strip():
            continue

        title = path.stem
        url = None

        for line in content.splitlines():
            line_stripped = line.strip()
            if not url and line_stripped.startswith("**Source:**"):
                url_match = re.search(r"https?://\S+", line_stripped)
                if url_match:
                    url = url_match.group(0).rstrip(")")
            if title == path.stem and line_stripped.startswith("# "):
                title_cand = line_stripped.lstrip("# ").strip()
                if title_cand:
                    title = title_cand

        doc_id = path.relative_to(STANDARDIZED_DIR).as_posix()
        document = {
            "id": doc_id,
            "content": content,
            "metadata": {
                "source": path.name,
                "title": title,
                "doc_type": doc_type,
                "url": url,
            },
        }
        validate_document(document, require_chunk=False)
        documents.append(document)

    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia Document thành chunks có id và chunk_index."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks: list[dict] = []
    for document in documents:
        split_texts = splitter.split_text(document["content"])
        if not split_texts and document["content"].strip():
            split_texts = [document["content"].strip()]

        for index, text in enumerate(split_texts):
            chunk = {
                "id": f"{document['id']}::chunk-{index}",
                "content": text,
                "metadata": {
                    **document["metadata"],
                    "chunk_index": index,
                },
            }
            validate_document(chunk, require_chunk=True)
            chunks.append(chunk)

    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Thêm embedding vào từng chunk."""
    if not chunks:
        return []
    texts = [chunk["content"] for chunk in chunks]
    vectors = embed_texts(texts)
    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector
    return chunks


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks vào ChromaDB."""
    if not chunks:
        return
    collection = get_collection()
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        collection.upsert(
            ids=[chunk["id"] for chunk in batch],
            documents=[chunk["content"] for chunk in batch],
            embeddings=[chunk["embedding"] for chunk in batch],
            metadatas=[chunk["metadata"] for chunk in batch],
        )


def run_pipeline() -> None:
    """Chạy load, chunk, embed và index."""
    print("Loading documents...")
    documents = load_documents()
    print(f"Loaded {len(documents)} documents.")

    print(f"Chunking with {CHUNKING_METHOD} (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
    chunks = chunk_documents(documents)
    print(f"Generated {len(chunks)} chunks.")

    print(f"Embedding chunks using {os.getenv('EMBEDDING_PROVIDER', EMBEDDING_PROVIDER)} ({os.getenv('EMBEDDING_MODEL', EMBEDDING_MODEL)})...")
    embedded_chunks = embed_chunks(chunks)

    print("Indexing into ChromaDB...")
    index_to_vectorstore(embedded_chunks)
    print(f"Successfully indexed {len(embedded_chunks)} chunks to collection '{COLLECTION_NAME}'!")


if __name__ == "__main__":
    run_pipeline()
