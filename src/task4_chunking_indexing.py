"""
Task 4: load standardized Markdown, recursively chunk, embed and upsert.
Task 5 reuses embed_texts() and get_collection() with the same model.
"""

import math
import os
import re
from functools import lru_cache
from pathlib import Path

from .contracts import validate_document


STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024
COLLECTION_NAME = "rag_documents"
BATCH_SIZE = 32


@lru_cache(maxsize=1)
def _get_embedding_model():
    """Load one local model per process; never silently switch vector spaces."""
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).parent.parent / ".env", override=False)
    provider = os.getenv("EMBEDDING_PROVIDER", "sentence_transformers").strip()
    model_name = os.getenv("EMBEDDING_MODEL", EMBEDDING_MODEL).strip()
    if provider != "sentence_transformers" or model_name != EMBEDDING_MODEL:
        raise ValueError(
            "Task 4 uses EMBEDDING_PROVIDER=sentence_transformers and "
            f"EMBEDDING_MODEL={EMBEDDING_MODEL}. Changing the embedding space "
            "requires an explicit configuration change and reindexing."
        )

    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(EMBEDDING_MODEL)
    if model.get_sentence_embedding_dimension() != EMBEDDING_DIM:
        raise ValueError(f"Expected embedding dimension {EMBEDDING_DIM}")
    return model


def _validate_vectors(vectors: list[list[float]], expected_count: int) -> None:
    if len(vectors) != expected_count:
        raise ValueError("Embedding count does not match text/chunk count")
    for vector in vectors:
        if len(vector) != EMBEDDING_DIM:
            raise ValueError(f"Expected embedding dimension {EMBEDDING_DIM}")
        if not all(
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
            for value in vector
        ):
            raise ValueError("Embeddings must contain finite numeric values")


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Shared document/query embedding function, using normalized BGE-M3."""
    if not texts:
        return []
    if any(not isinstance(text, str) or not text.strip() for text in texts):
        raise ValueError("Embedding inputs must be non-empty strings")
    vectors = _get_embedding_model().encode(
        texts,
        batch_size=BATCH_SIZE,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    ).tolist()
    _validate_vectors(vectors, len(texts))
    return vectors


def get_collection():
    """Open a persistent cosine collection without an automatic embedder."""
    import chromadb

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=None,
        metadata={
            "hnsw:space": "cosine",
            "embedding_model": EMBEDDING_MODEL,
            "embedding_dim": EMBEDDING_DIM,
        },
    )
    metadata = collection.metadata or {}
    if (
        metadata.get("hnsw:space") != "cosine"
        or metadata.get("embedding_model") != EMBEDDING_MODEL
        or metadata.get("embedding_dim") != EMBEDDING_DIM
    ):
        raise ValueError(
            "Existing collection has incompatible or unknown embedding settings; "
            "use a separate collection or explicitly rebuild the index."
        )
    return collection


def load_documents() -> list[dict]:
    """Read Task 3 Markdown and preserve its source header as metadata."""
    documents = []
    for doc_type in ("legal", "news"):
        for path in sorted((STANDARDIZED_DIR / doc_type).rglob("*.md")):
            if not path.is_file():
                continue
            content = path.read_text(encoding="utf-8-sig").strip()
            if not content:
                raise ValueError(f"Empty standardized document: {path}")
            relative_path = path.relative_to(STANDARDIZED_DIR).as_posix()
            title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            metadata = {
                "source": relative_path,
                "title": title_match.group(1).strip() if title_match else path.stem,
                "doc_type": doc_type,
                "url": None,
            }

            # Task 3 writes this exact header for news. Do not confuse a
            # horizontal rule inside a legal document with a metadata header.
            if doc_type == "news":
                header = re.match(
                    r"\A# (?P<title>[^\n]+)\n\s*"
                    r"\*\*Source:\*\* (?P<url>[^\n]+)\n\s*"
                    r"\*\*Crawled:\*\* (?P<date>[^\n]+)\n\s*"
                    r"---[ \t]*(?:\n|$)",
                    content,
                )
                if header:
                    metadata.update(
                        title=header["title"].strip(),
                        url=header["url"].strip(),
                        date_crawled=header["date"].strip(),
                    )
                    content = content[header.end():].strip()

            document = {"id": relative_path, "content": content, "metadata": metadata}
            validate_document(document)
            documents.append(document)

    if not documents:
        raise FileNotFoundError(
            f"No Markdown documents found under {STANDARDIZED_DIR / 'legal'} "
            f"or {STANDARDIZED_DIR / 'news'}. Run Task 3 first."
        )
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Keep source metadata and derive stable chunk IDs from document IDs."""
    if not documents:
        return []
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = []
    seen_ids = set()
    for document in documents:
        validate_document(document)
        if document["id"] in seen_ids:
            raise ValueError(f"Duplicate document ID: {document['id']}")
        seen_ids.add(document["id"])
        for index, text in enumerate(splitter.split_text(document["content"])):
            chunk = {
                "id": f"{document['id']}::chunk-{index}",
                "content": text,
                "metadata": {
                    **document["metadata"],
                    "document_id": document["id"],
                    "chunk_index": index,
                },
            }
            validate_document(chunk, require_chunk=True)
            chunks.append(chunk)
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Embed bounded batches and return copies, leaving input chunks unchanged."""
    for chunk in chunks:
        validate_document(chunk, require_chunk=True)
    embedded = []
    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start:start + BATCH_SIZE]
        vectors = embed_texts([chunk["content"] for chunk in batch])
        _validate_vectors(vectors, len(batch))
        for chunk, vector in zip(batch, vectors):
            embedded.append({
                **chunk,
                "metadata": dict(chunk["metadata"]),
                "embedding": vector,
            })
    return embedded


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert stable IDs in batches; reject bad inputs before writing."""
    if not chunks:
        return
    seen_ids = set()
    metadatas = []
    for chunk in chunks:
        validate_document(chunk, require_chunk=True)
        if chunk["id"] in seen_ids:
            raise ValueError(f"Duplicate chunk ID: {chunk['id']}")
        seen_ids.add(chunk["id"])
        _validate_vectors([chunk.get("embedding", [])], 1)
        metadata = dict(chunk["metadata"])
        # Chroma versions in this repo's supported range reject None values.
        # Keep the required URL key; an empty string denotes an unknown URL.
        if metadata["url"] is None:
            metadata["url"] = ""
        if any(
            not isinstance(value, (str, int, float, bool))
            for value in metadata.values()
        ):
            raise ValueError("Chroma metadata must contain scalar values")
        metadatas.append(metadata)

    collection = get_collection()
    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start:start + BATCH_SIZE]
        collection.upsert(
            ids=[chunk["id"] for chunk in batch],
            documents=[chunk["content"] for chunk in batch],
            embeddings=[chunk["embedding"] for chunk in batch],
            metadatas=metadatas[start:start + BATCH_SIZE],
        )


def run_pipeline() -> None:
    """Run load, chunk, embed and index; do not report success on empty data."""
    documents = load_documents()
    chunks = chunk_documents(documents)
    embedded_chunks = embed_chunks(chunks)
    index_to_vectorstore(embedded_chunks)
    print(
        f"Indexed {len(documents)} documents / {len(embedded_chunks)} chunks "
        f"into {COLLECTION_NAME} at {CHROMA_DIR}"
    )


if __name__ == "__main__":
    run_pipeline()