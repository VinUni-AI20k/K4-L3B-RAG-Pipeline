"""
Task 4 — Chunking, embedding và indexing.

Hướng dẫn:
    1. Đọc toàn bộ dữ liệu chuẩn hoá trong data/standardized/.
    2. Chia văn bản bằng strategy RecursiveCharacterTextSplitter.
    3. Embed chunks bằng một provider duy nhất (SentenceTransformers, OpenAI, Gemini).
    4. Upsert vào ChromaDB với cosine distance.

Mỗi document/chunk tuân theo docs/MODULE_CONTRACTS.md. ID duy nhất và ổn định để
chạy lại pipeline không tạo dữ liệu trùng. Task 5 dùng chung embed_texts().
"""

import json
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

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
EMBEDDING_DIM = 1024

COLLECTION_NAME = "rag_documents"

_EMBEDDING_MODEL_CACHE = None


def _get_sentence_transformer(model_name: str):
    global _EMBEDDING_MODEL_CACHE
    if _EMBEDDING_MODEL_CACHE is None or getattr(_EMBEDDING_MODEL_CACHE, "_model_name", None) != model_name:
        from sentence_transformers import SentenceTransformer
        _EMBEDDING_MODEL_CACHE = SentenceTransformer(model_name)
        _EMBEDDING_MODEL_CACHE._model_name = model_name
    return _EMBEDDING_MODEL_CACHE


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Tạo vector embedding cho danh sách texts theo provider cấu hình trong .env."""
    if not texts:
        return []

    provider = os.getenv("EMBEDDING_PROVIDER", "sentence_transformers").lower()
    model_name = os.getenv("EMBEDDING_MODEL", EMBEDDING_MODEL)

    if provider == "sentence_transformers":
        model = _get_sentence_transformer(model_name)
        embeddings = model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()
    elif provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        res = client.embeddings.create(input=texts, model=model_name or "text-embedding-3-small")
        return [item.embedding for item in res.data]
    elif provider == "gemini":
        from google import genai
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        vectors = []
        for text in texts:
            result = client.models.embed_content(
                model=model_name or "text-embedding-004",
                contents=text,
            )
            vectors.append(result.embedding.values)
        return vectors
    else:
        raise ValueError(f"Unsupported EMBEDDING_PROVIDER: {provider}")


def get_collection():
    """Mở hoặc tạo persistent Chroma collection sử dụng cosine distance."""
    import chromadb
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def load_documents() -> list[dict]:
    """Đọc dữ liệu chuẩn hoá và trả về danh sách Document theo contract."""
    from src.contracts import validate_document

    documents = []
    # Ưu tiên đọc các file JSON chuẩn hoá có metadata và provenance từ Người 1
    json_files = sorted(STANDARDIZED_DIR.glob("*/*.json"))
    if json_files:
        for path in json_files:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
            doc_id = data.get("id", path.stem)
            content = data.get("content", "")
            meta = dict(data.get("metadata", {}))

            if "source" not in meta:
                meta["source"] = path.name
            if "title" not in meta:
                meta["title"] = path.stem
            if "doc_type" not in meta:
                meta["doc_type"] = "legal" if "legal" in path.parts else "news"
            if "url" not in meta:
                meta["url"] = None

            doc = {
                "id": doc_id,
                "content": content,
                "metadata": meta,
            }
            validate_document(doc, require_chunk=False)
            documents.append(doc)
    else:
        # Fallback đọc trực tiếp file Markdown nếu không có file JSON
        for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
            doc_type = "legal" if "legal" in path.parts else "news"
            doc = {
                "id": path.stem,
                "content": path.read_text(encoding="utf-8"),
                "metadata": {
                    "source": path.name,
                    "title": path.stem,
                    "doc_type": doc_type,
                    "url": None,
                },
            }
            validate_document(doc, require_chunk=False)
            documents.append(doc)

    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia Document thành chunks có id duy nhất, ổn định và chunk_index."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from src.contracts import validate_document

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""],
    )

    chunks = []
    for document in documents:
        doc_chunks = splitter.split_text(document["content"])
        for index, text in enumerate(doc_chunks):
            meta = dict(document["metadata"])
            meta["chunk_index"] = index
            if "url" not in meta:
                meta["url"] = None

            chunk_id = f"{document['id']}-chunk-{index}"
            chunk = {
                "id": chunk_id,
                "content": text,
                "metadata": meta,
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
    """Upsert chunks vào ChromaDB, chuẩn hoá metadata kiểu dữ liệu cho ChromaDB."""
    if not chunks:
        return

    collection = get_collection()
    ids = [chunk["id"] for chunk in chunks]
    documents = [chunk["content"] for chunk in chunks]
    embeddings = [chunk["embedding"] for chunk in chunks]

    metadatas = []
    for chunk in chunks:
        meta = {}
        for key, value in chunk["metadata"].items():
            if value is None:
                meta[key] = ""
            elif isinstance(value, (str, int, float, bool)):
                meta[key] = value
            elif isinstance(value, (list, dict)):
                meta[key] = json.dumps(value, ensure_ascii=False)
            else:
                meta[key] = str(value)
        metadatas.append(meta)

    # Upsert theo batch để tránh quá tải
    batch_size = 100
    for i in range(0, len(ids), batch_size):
        collection.upsert(
            ids=ids[i : i + batch_size],
            documents=documents[i : i + batch_size],
            embeddings=embeddings[i : i + batch_size],
            metadatas=metadatas[i : i + batch_size],
        )


def run_pipeline() -> None:
    """Chạy toàn bộ quy trình: load, chunk, embed và index vào ChromaDB."""
    print("1. Loading documents...")
    documents = load_documents()
    print(f"   Loaded {len(documents)} documents.")

    print("2. Chunking documents...")
    chunks = chunk_documents(documents)
    print(f"   Created {len(chunks)} chunks.")

    print("3. Embedding chunks...")
    embedded_chunks = embed_chunks(chunks)
    print(f"   Generated embeddings for {len(embedded_chunks)} chunks.")

    print("4. Upserting into ChromaDB...")
    index_to_vectorstore(embedded_chunks)
    print(f"   Successfully indexed {len(embedded_chunks)} chunks to collection '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    run_pipeline()
