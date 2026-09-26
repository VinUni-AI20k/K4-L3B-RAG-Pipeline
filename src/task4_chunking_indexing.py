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

import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv

from .contracts import validate_document


STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"
CORPUS_CACHE = Path(__file__).parent.parent / "data" / "bm25_corpus.json"

load_dotenv()

# Giải thích lựa chọn tham số trong báo cáo nhóm.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIM = 1024

COLLECTION_NAME = "rag_hkd_thue"

_MODEL = None
_OPENAI_CLIENT = None
_SOURCE_PATTERN = re.compile(r"^\*\*Source:\*\*\s*(.+?)\s*$", re.MULTILINE)
_TITLE_PATTERN = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed texts with the configured provider and a shared model."""
    global _MODEL, _OPENAI_CLIENT

    if not texts:
        return []
    if EMBEDDING_PROVIDER == "openai":
        from openai import OpenAI

        if _OPENAI_CLIENT is None:
            _OPENAI_CLIENT = OpenAI()
        result = []
        for start in range(0, len(texts), 128):
            response = _OPENAI_CLIENT.embeddings.create(
                model=EMBEDDING_MODEL,
                input=texts[start : start + 128],
                dimensions=EMBEDDING_DIM,
                encoding_format="float",
            )
            ordered = sorted(response.data, key=lambda item: item.index)
            result.extend(item.embedding for item in ordered)
    elif EMBEDDING_PROVIDER == "sentence_transformers":
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "sentence-transformers is required for local embeddings"
            ) from exc
        if _MODEL is None:
            _MODEL = SentenceTransformer(EMBEDDING_MODEL)
        vectors = _MODEL.encode(
            texts,
            batch_size=16,
            normalize_embeddings=True,
            show_progress_bar=len(texts) > 32,
        )
        result = vectors.tolist()
    else:
        raise ValueError(
            "EMBEDDING_PROVIDER must be 'openai' or 'sentence_transformers'; "
            f"received {EMBEDDING_PROVIDER!r}"
        )
    if any(len(vector) != EMBEDDING_DIM for vector in result):
        raise ValueError(
            f"Expected {EMBEDDING_DIM}-dimensional embeddings from {EMBEDDING_MODEL}"
        )
    return result


def get_collection():
    """Mở Chroma collection dùng cosine distance."""
    import chromadb

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def _document_metadata(path: Path, content: str) -> dict:
    """Build citation metadata from a standardized Markdown file."""
    relative = path.relative_to(STANDARDIZED_DIR)
    doc_type = "legal" if relative.parts[0] == "legal" else "news"
    source_match = _SOURCE_PATTERN.search(content)
    title_match = _TITLE_PATTERN.search(content)
    return {
        "source": path.name,
        "title": title_match.group(1).strip() if title_match else path.stem,
        "doc_type": doc_type,
        "url": source_match.group(1).strip() if source_match else None,
    }


def load_documents() -> list[dict]:
    """Đọc Markdown và trả về danh sách Document."""
    documents = []
    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue
        document = {
            "id": path.relative_to(STANDARDIZED_DIR).as_posix(),
            "content": content,
            "metadata": _document_metadata(path, content),
        }
        validate_document(document)
        documents.append(document)
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia Document thành chunks có id và chunk_index."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = []
    for document in documents:
        validate_document(document)
        pieces = splitter.split_text(document["content"]) or [document["content"]]
        chunk_index = 0
        for text in pieces:
            text = text.strip()
            if not text:
                continue
            chunk = {
                "id": f"{document['id']}::chunk-{chunk_index}",
                "content": text,
                "metadata": {**document["metadata"], "chunk_index": chunk_index},
            }
            validate_document(chunk, require_chunk=True)
            chunks.append(chunk)
            chunk_index += 1
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Thêm embedding vào từng chunk."""
    if not chunks:
        return []
    vectors = embed_texts([chunk["content"] for chunk in chunks])
    if len(vectors) != len(chunks):
        raise ValueError("Embedding provider returned an unexpected vector count")
    return [dict(chunk, embedding=vector) for chunk, vector in zip(chunks, vectors)]


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks vào ChromaDB."""
    collection = get_collection()
    desired_ids = {chunk["id"] for chunk in chunks}
    existing_ids = set(collection.get(include=[])["ids"])
    stale_ids = sorted(existing_ids - desired_ids)
    if stale_ids:
        collection.delete(ids=stale_ids)
    if not chunks:
        return

    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=[chunk["content"] for chunk in chunks],
        embeddings=[chunk["embedding"] for chunk in chunks],
        metadatas=[
            {
                key: ("" if value is None else value)
                for key, value in chunk["metadata"].items()
            }
            for chunk in chunks
        ],
    )


def write_bm25_corpus(chunks: list[dict]) -> None:
    """Persist the exact Task 4 chunks in deterministic order for Task 6."""
    serializable = [
        {key: value for key, value in chunk.items() if key != "embedding"}
        for chunk in chunks
    ]
    CORPUS_CACHE.write_text(
        json.dumps(serializable, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def run_pipeline() -> None:
    """Chạy load, chunk, embed và index."""
    documents = load_documents()
    chunks = chunk_documents(documents)
    embedded_chunks = embed_chunks(chunks)
    index_to_vectorstore(embedded_chunks)
    write_bm25_corpus(chunks)
    print(f"Indexed {len(embedded_chunks)} chunks")


if __name__ == "__main__":
    run_pipeline()
