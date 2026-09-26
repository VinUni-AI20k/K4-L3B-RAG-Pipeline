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

from pathlib import Path
import os
import hashlib
import math
import re

from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .contracts import validate_document


STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

# Giải thích lựa chọn tham số trong báo cáo nhóm.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024

COLLECTION_NAME = "rag_documents"


def _metadata_from_markdown(path: Path, content: str) -> dict:
    title_match = re.search(r"^#\s+(.+)$", content, flags=re.MULTILINE)
    url_match = re.search(r"https?://[^\s)>]+", content[:2000])
    return {
        "source": path.name,
        "title": title_match.group(1).strip() if title_match else path.stem,
        "doc_type": "legal" if "legal" in path.parts else "news",
        "url": url_match.group(0).rstrip(".,") if url_match else None,
    }


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    load_dotenv()
    provider = os.getenv("EMBEDDING_PROVIDER", "sentence_transformers").lower()
    if provider == "sentence_transformers":
        model_name = os.getenv("EMBEDDING_MODEL", EMBEDDING_MODEL)
        local_files_only = os.getenv(
            "EMBEDDING_LOCAL_FILES_ONLY", "false"
        ).lower() in {"1", "true", "yes"}
        allow_hash_fallback = os.getenv(
            "EMBEDDING_ALLOW_HASH_FALLBACK", "false"
        ).lower() in {"1", "true", "yes"}
        try:
            from sentence_transformers import SentenceTransformer

            if not hasattr(embed_texts, "_model") or embed_texts._model_name != model_name:
                embed_texts._model = SentenceTransformer(
                    model_name,
                    local_files_only=local_files_only,
                )
                embed_texts._model_name = model_name
            return embed_texts._model.encode(texts, normalize_embeddings=True).tolist()
        except Exception as error:
            if not allow_hash_fallback:
                raise RuntimeError(
                    f"Could not load sentence-transformer {model_name!r}. "
                    "Set EMBEDDING_LOCAL_FILES_ONLY=false to allow the first download. "
                    "Use EMBEDDING_ALLOW_HASH_FALLBACK=true only for offline development."
                ) from error
            # Explicit offline/dev fallback: deterministic vectors keep the pipeline runnable.
            vectors = []
            for text in texts:
                vector = [0.0] * EMBEDDING_DIM
                for token in text.lower().split():
                    digest = hashlib.sha256(token.encode("utf-8")).digest()
                    index = int.from_bytes(digest[:4], "big") % EMBEDDING_DIM
                    vector[index] += 1.0
                norm = math.sqrt(sum(value * value for value in vector)) or 1.0
                vectors.append([value / norm for value in vector])
            return vectors
    if provider == "openai":
        from openai import OpenAI

        response = OpenAI(api_key=os.getenv("OPENAI_API_KEY")).embeddings.create(
            model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"), input=texts
        )
        return [item.embedding for item in response.data]
    raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {provider}")


def get_collection():
    """Mở Chroma collection dùng cosine distance."""
    import chromadb

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )


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
            "metadata": _metadata_from_markdown(path, content),
        }
        validate_document(document)
        documents.append(document)
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
        validate_document(document)
        for index, text in enumerate(splitter.split_text(document["content"])):
            chunk = {
                "id": f"{document['id']}::chunk-{index}",
                "content": text.strip(),
                "metadata": {**document["metadata"], "chunk_index": index},
            }
            if chunk["content"]:
                chunks.append(chunk)
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Thêm embedding vào từng chunk."""
    vectors = embed_texts([chunk["content"] for chunk in chunks])
    if len(vectors) != len(chunks):
        raise ValueError("Embedding provider returned an unexpected number of vectors")
    return [{**chunk, "embedding": vector} for chunk, vector in zip(chunks, vectors)]


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks vào ChromaDB."""
    if not chunks:
        return
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
    chunks = chunk_documents(documents)
    embedded_chunks = embed_chunks(chunks)
    index_to_vectorstore(embedded_chunks)
    print(f"Indexed {len(embedded_chunks)} chunks")


if __name__ == "__main__":
    run_pipeline()
