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
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

from .contracts import validate_document


STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

# Giải thích lựa chọn tham số trong báo cáo nhóm.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

load_dotenv(Path(__file__).parent.parent / ".env")
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "sentence_transformers").strip().lower()
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3").strip()
# text-embedding-004 was retired in January 2026; keep old .env files usable
# by mapping that legacy value to Google's current text-only Gemini embedder.
if EMBEDDING_PROVIDER == "gemini" and EMBEDDING_MODEL == "text-embedding-004":
    EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIM = 768 if EMBEDDING_PROVIDER == "gemini" else 1024
EMBEDDING_BATCH_SIZE = 32

COLLECTION_NAME = "rag_documents"


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed strings with the configured provider and a shared model contract."""
    if not texts:
        return []
    if any(not isinstance(text, str) or not text.strip() for text in texts):
        raise ValueError("texts must contain only non-empty strings")

    if EMBEDDING_PROVIDER == "sentence_transformers":
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(EMBEDDING_MODEL)
        vectors = model.encode(texts, normalize_embeddings=True)
        return vectors.tolist()

    if EMBEDDING_PROVIDER == "openai":
        from openai import OpenAI

        client = OpenAI()
        vectors: list[list[float]] = []
        for start in range(0, len(texts), EMBEDDING_BATCH_SIZE):
            response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=texts[start : start + EMBEDDING_BATCH_SIZE],
            )
            vectors.extend(item.embedding for item in sorted(response.data, key=lambda item: item.index))
        return vectors

    if EMBEDDING_PROVIDER == "gemini":
        from google import genai
        from google.genai import types

        client = genai.Client()
        vectors = []
        for start in range(0, len(texts), EMBEDDING_BATCH_SIZE):
            batch = texts[start : start + EMBEDDING_BATCH_SIZE]
            for attempt in range(4):
                try:
                    response = client.models.embed_content(
                        model=EMBEDDING_MODEL,
                        contents=batch,
                        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIM),
                    )
                    break
                except Exception as error:
                    if getattr(error, "code", None) != 429 or attempt == 3:
                        raise
                    # Gemini free-tier limits are per minute; let the quota window reset.
                    retry_seconds = 60
                    details = getattr(error, "details", None) or []
                    for detail in details:
                        retry_info = detail.get("retryDelay") if isinstance(detail, dict) else None
                        if retry_info:
                            try:
                                retry_seconds = max(1, int(float(retry_info.rstrip("s"))))
                            except ValueError:
                                pass
                    time.sleep(retry_seconds + 1)
            vectors.extend(item.values for item in response.embeddings)
        return vectors

    raise ValueError(
        "Unsupported EMBEDDING_PROVIDER. Choose sentence_transformers, openai, or gemini."
    )


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
    if not STANDARDIZED_DIR.is_dir():
        raise FileNotFoundError(f"Standardized corpus directory not found: {STANDARDIZED_DIR}")
    documents = []
    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        if not path.is_file() or path.name.startswith("."):
            continue
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue
        relative_path = path.relative_to(STANDARDIZED_DIR)
        doc_type = relative_path.parts[0] if relative_path.parts else "unknown"
        if doc_type not in {"legal", "news"}:
            continue
        source_url = re.search(r"(?mi)^\*\*Source:\*\*\s*(https?://\S+)", content)
        document = {
            "id": relative_path.as_posix(),
            "content": content,
            "metadata": {
                "source": path.name,
                "title": path.stem,
                "doc_type": doc_type,
                "url": source_url.group(1) if source_url else None,
            },
        }
        validate_document(document)
        documents.append(document)
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia Document thành chunks có id và chunk_index."""
    if not 0 <= CHUNK_OVERLAP < CHUNK_SIZE:
        raise ValueError("CHUNK_OVERLAP must be non-negative and smaller than CHUNK_SIZE")

    def recursive_split(text: str) -> list[str]:
        # Prefer paragraph and line boundaries, then sentence/word boundaries.
        separators = ("\n\n", "\n", ". ", " ")
        pieces: list[str] = []
        start = 0
        text = text.strip()
        while start < len(text):
            end = min(start + CHUNK_SIZE, len(text))
            if end < len(text):
                boundary = -1
                for separator in separators:
                    position = text.rfind(separator, start + CHUNK_SIZE // 2, end)
                    if position > boundary:
                        boundary = position + len(separator)
                if boundary > start:
                    end = boundary
            piece = text[start:end].strip()
            if piece:
                pieces.append(piece)
            if end >= len(text):
                break
            next_start = max(start + 1, end - CHUNK_OVERLAP)
            # Avoid a whitespace-only overlap while preserving a stable boundary.
            while next_start < end and text[next_start].isspace():
                next_start += 1
            start = next_start
        return pieces

    chunks = []
    seen_ids: set[str] = set()
    for document in documents:
        validate_document(document)
        pieces = recursive_split(document["content"])
        for index, content in enumerate(pieces):
            chunk_id = f"{document['id']}::chunk-{index}"
            if chunk_id in seen_ids:
                raise ValueError(f"Duplicate chunk id: {chunk_id}")
            chunk = {
                "id": chunk_id,
                "content": content,
                "metadata": {**document["metadata"], "chunk_index": index},
            }
            validate_document(chunk, require_chunk=True)
            chunks.append(chunk)
            seen_ids.add(chunk_id)
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Thêm embedding vào từng chunk."""
    if not chunks:
        return []
    embedded: list[dict] = []
    for start in range(0, len(chunks), EMBEDDING_BATCH_SIZE):
        batch = chunks[start : start + EMBEDDING_BATCH_SIZE]
        vectors = embed_texts([chunk["content"] for chunk in batch])
        if len(vectors) != len(batch):
            raise ValueError("Embedding provider returned a different number of vectors than inputs")
        for chunk, vector in zip(batch, vectors):
            if not vector or any(not isinstance(value, (int, float)) for value in vector):
                raise ValueError(f"Invalid embedding returned for chunk {chunk['id']}")
            embedded.append({**chunk, "embedding": [float(value) for value in vector]})
    dimensions = {len(item["embedding"]) for item in embedded}
    if len(dimensions) != 1:
        raise ValueError("Embedding provider returned inconsistent vector dimensions")
    return embedded


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks vào ChromaDB."""
    collection = get_collection()
    expected_ids = {chunk["id"] for chunk in chunks}
    existing_ids = collection.get(include=[]).get("ids", [])
    stale_ids = [item_id for item_id in existing_ids if item_id not in expected_ids]
    if stale_ids:
        collection.delete(ids=stale_ids)
    for start in range(0, len(chunks), EMBEDDING_BATCH_SIZE):
        batch = chunks[start : start + EMBEDDING_BATCH_SIZE]
        if not batch:
            continue
        metadatas = []
        for chunk in batch:
            validate_document(chunk, require_chunk=True)
            if "embedding" not in chunk or not chunk["embedding"]:
                raise ValueError(f"Missing embedding for chunk {chunk['id']}")
            metadata = dict(chunk["metadata"])
            # Chroma metadata fields cannot contain null; preserve contract on
            # load/search by representing an unknown source URL as empty text.
            if metadata.get("url") is None:
                metadata["url"] = ""
            metadatas.append(metadata)
        collection.upsert(
            ids=[chunk["id"] for chunk in batch],
            documents=[chunk["content"] for chunk in batch],
            embeddings=[chunk["embedding"] for chunk in batch],
            metadatas=metadatas,
        )


def run_pipeline() -> None:
    """Chạy load, chunk, embed và index."""
    documents = load_documents()
    if not documents:
        raise RuntimeError(f"No Markdown documents found under {STANDARDIZED_DIR}")
    chunks = chunk_documents(documents)
    if not chunks:
        raise RuntimeError("The Markdown corpus produced no chunks")
    embedded_chunks = embed_chunks(chunks)
    index_to_vectorstore(embedded_chunks)
    print(f"Indexed {len(embedded_chunks)} chunks")
    inspect_index()


def inspect_index(sample_size: int = 3) -> None:
    """Print index size and a few source/chunk metadata records for validation."""
    collection = get_collection()
    print(f"Chroma collection {COLLECTION_NAME}: {collection.count()} chunks")
    sample = collection.get(limit=max(0, sample_size), include=["metadatas"])
    for item_id, metadata in zip(sample.get("ids", []), sample.get("metadatas", [])):
        print(f"{item_id}: {metadata}")


if __name__ == "__main__":
    if "--inspect" in sys.argv[1:]:
        inspect_index()
    else:
        run_pipeline()
