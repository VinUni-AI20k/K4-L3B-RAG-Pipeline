"""
Task 4 — Chunking & Indexing vào Vector Store.

Hướng dẫn:
    1. Đọc toàn bộ markdown files từ data/standardized/
    2. Chọn 1 chunking strategy (RecursiveCharacterTextSplitter)
    3. Chọn 1 embedding model (sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)
    4. Index vào vector store ChromaDB
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

# =============================================================================
# CONFIGURATION
# =============================================================================

# Chunk size 500 ký tự với overlap 50 ký tự:
# - Phù hợp với độ dài các điều khoản quy định/chính sách TMĐT
# - Đủ ngữ cảnh cho từng điều kiện bảo hành, đổi trả, tranh chấp
# - Tránh vượt quá context window khi inject nhiều chunks vào LLM
CHUNK_SIZE = 750
CHUNK_OVERLAP = 100
CHUNKING_METHOD = "recursive"

# Embedding Model: paraphrase-multilingual-MiniLM-L12-v2
# - Hỗ trợ tốt đa ngôn ngữ (tiếng Việt, tiếng Anh)
# - Kích thước vector 384 chiều, tốc độ mã hoá nhanh, độ chính xác cao
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIM = 384

VECTOR_STORE = "chromadb"
COLLECTION_NAME = "ecommerce_support_docs"

_EMBED_MODEL = None


def get_embedding_model():
    """Singleton getter cho SentenceTransformer model."""
    global _EMBED_MODEL
    if _EMBED_MODEL is None:
        from sentence_transformers import SentenceTransformer
        _EMBED_MODEL = SentenceTransformer(EMBEDDING_MODEL)
    return _EMBED_MODEL


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Mã hoá danh sách text thành vector embedding."""
    model = get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=False)
    return [emb.tolist() for emb in embeddings]


def get_collection():
    """Lấy hoặc tạo ChromaDB collection với metric cosine similarity."""
    import chromadb
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    return collection


# =============================================================================
# IMPLEMENTATION
# =============================================================================

def load_documents() -> list[dict]:
    """
    Đọc toàn bộ markdown files từ data/standardized/.

    Returns:
        List of Document dictionaries theo schema hợp đồng:
        {'id': str, 'content': str, 'metadata': {'source': str, 'title': str, 'doc_type': str, 'url': str | None}}
    """
    documents = []
    if not STANDARDIZED_DIR.exists():
        return documents

    for md_file in STANDARDIZED_DIR.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        doc_type = "legal" if "legal" in str(md_file).lower() else "news"
        lines = [line.strip() for line in content.split("\n") if line.strip().startswith("#")]
        title = lines[0].lstrip("#").strip() if lines else md_file.stem.replace("-", " ").title()
        documents.append({
            "id": md_file.stem,
            "content": content,
            "metadata": {
                "source": md_file.name,
                "title": title,
                "doc_type": doc_type,
                "url": None,
            },
        })
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """
    Chunk documents sử dụng RecursiveCharacterTextSplitter.

    Returns:
        List of Chunk dictionaries theo schema hợp đồng:
        {'id': str, 'content': str, 'metadata': {'source': str, 'title': str, 'doc_type': str, 'url': str | None, 'chunk_index': int}}
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = []
    for doc in documents:
        doc_id = doc.get("id") or Path(doc.get("metadata", {}).get("source", "doc")).stem
        splits = splitter.split_text(doc["content"])
        for i, chunk_text in enumerate(splits):
            if chunk_text.strip():
                chunks.append({
                    "id": f"{doc_id}-{i}",
                    "content": chunk_text.strip(),
                    "metadata": {
                        **doc.get("metadata", {}),
                        "chunk_index": i,
                    }
                })
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """
    Embed toàn bộ chunks và gắn key 'embedding'.
    """
    texts = [c["content"] for c in chunks]
    vectors = embed_texts(texts)
    for chunk, vec in zip(chunks, vectors):
        chunk["embedding"] = vec
    return chunks


def index_to_vectorstore(chunks: list[dict]):
    """
    Index chunks vào ChromaDB.
    """
    if not chunks:
        print("Không có chunks để index.")
        return

    collection = get_collection()

    # Xóa các chunk cũ nếu có để tránh tồn đọng stale chunks từ các lần chunking trước
    try:
        existing = collection.get()
        if existing and existing.get("ids"):
            collection.delete(ids=existing["ids"])
    except Exception:
        pass

    ids = []
    docs = []
    embeddings = []
    metadatas = []

    for i, c in enumerate(chunks):
        chunk_id = c.get("id") or f"chunk-{i}"
        ids.append(chunk_id)
        docs.append(c["content"])
        embeddings.append(c["embedding"])
        # Đảm bảo metadata chỉ chứa kiểu dữ liệu hợp lệ cho ChromaDB (str, int, float, bool)
        safe_meta = {k: v for k, v in c["metadata"].items() if isinstance(v, (str, int, float, bool))}
        metadatas.append(safe_meta)

    # Upsert theo batch để đảm bảo ổn định
    batch_size = 100
    for start_idx in range(0, len(ids), batch_size):
        end_idx = start_idx + batch_size
        collection.upsert(
            ids=ids[start_idx:end_idx],
            documents=docs[start_idx:end_idx],
            embeddings=embeddings[start_idx:end_idx],
            metadatas=metadatas[start_idx:end_idx],
        )


def run_pipeline():
    """Chạy toàn bộ pipeline: load → chunk → embed → index."""
    print("=" * 50)
    print("Task 4: Chunking & Indexing")
    print(f"  Chunking: {CHUNKING_METHOD} (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    print(f"  Embedding: {EMBEDDING_MODEL} (dim={EMBEDDING_DIM})")
    print(f"  Vector Store: {VECTOR_STORE}")
    print("=" * 50)

    docs = load_documents()
    print(f"\n✓ Loaded {len(docs)} documents")

    chunks = chunk_documents(docs)
    print(f"✓ Created {len(chunks)} chunks")

    chunks = embed_chunks(chunks)
    print(f"✓ Embedded {len(chunks)} chunks")

    index_to_vectorstore(chunks)
    print("✓ Indexed to ChromaDB vector store successfully")


if __name__ == "__main__":
    run_pipeline()
