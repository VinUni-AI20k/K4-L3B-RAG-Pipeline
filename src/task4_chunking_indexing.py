"""Task 4: source-aware chunking, shared local embeddings and cosine Chroma.

Run with --prepare to inspect chunks without downloading models or indexing.
Task 5 imports embed_texts and get_collection from this module unchanged.
"""

import argparse
import hashlib
import importlib.util
import json
import math
import os
import re
from functools import lru_cache
from pathlib import Path

from .contracts import validate_document

ROOT = Path(__file__).resolve().parent.parent
try:
    from dotenv import load_dotenv
except ImportError:
    raise ImportError("Install python-dotenv (see docs/TASK4.md).") from None
load_dotenv(ROOT / ".env", override=False)

STANDARDIZED_DIR = ROOT / "data" / "standardized"
CHROMA_DIR = Path(os.getenv("CHROMA_DB_PATH", ROOT / "chroma_db"))
CHUNKS_PATH = ROOT / "data" / "index" / "chunks.jsonl"
REPORT_PATH = ROOT / "reports" / "task4_index.json"
EMBEDDING_CACHE = Path(os.getenv("EMBEDDING_CACHE_DIR", ROOT / ".cache" / "task4-embeddings"))
MODEL_CACHE = Path(os.getenv("EMBEDDING_MODEL_CACHE", ROOT / ".cache" / "huggingface"))

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "separator_window_per_page"
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "sentence_transformers")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
EMBEDDING_REVISION = os.getenv("EMBEDDING_REVISION", "5617a9f61b028005a4858fdac845db406aefb181" if EMBEDDING_MODEL == "BAAI/bge-m3" else "main")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "1024"))
BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "8"))
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "rag_documents")
PIPELINE_OWNER = "k4-task4-v1"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    temporary = path.with_suffix(path.suffix + ".part")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def _signature() -> dict:
    return {"embedding_provider": EMBEDDING_PROVIDER, "embedding_model": EMBEDDING_MODEL,
            "embedding_revision": EMBEDDING_REVISION,
            "embedding_dim": EMBEDDING_DIM, "normalized": True, "pipeline_owner": PIPELINE_OWNER}


@lru_cache(maxsize=1)
def _embedding_model():
    if EMBEDDING_PROVIDER != "sentence_transformers":
        raise ValueError("Task 4 currently uses sentence_transformers only; no automatic provider fallback.")
    from sentence_transformers import SentenceTransformer
    from huggingface_hub import snapshot_download
    from huggingface_hub.errors import LocalEntryNotFoundError
    # Prefer a complete local snapshot. Download only if it has not been cached.
    kwargs = {"cache_folder": str(MODEL_CACHE), "trust_remote_code": False, "revision": EMBEDDING_REVISION}
    try:
        snapshot = Path(snapshot_download(EMBEDDING_MODEL, revision=EMBEDDING_REVISION,
                                          cache_dir=str(MODEL_CACHE), local_files_only=True))
    except LocalEntryNotFoundError:
        snapshot = None
    if snapshot and any((snapshot / name).is_file() for name in ("model.safetensors", "pytorch_model.bin")):
        model = SentenceTransformer(str(snapshot), local_files_only=True, trust_remote_code=False)
    else:
        model = SentenceTransformer(EMBEDDING_MODEL, **kwargs)
    if model.get_sentence_embedding_dimension() != EMBEDDING_DIM:
        raise ValueError("Model dimension differs from EMBEDDING_DIM; use a matching configuration and collection.")
    return model


def _validate_vectors(vectors: list, count: int) -> None:
    if len(vectors) != count:
        raise ValueError("Embedding count differs from text count")
    for vector in vectors:
        if len(vector) != EMBEDDING_DIM or not all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) for x in vector):
            raise ValueError("Invalid embedding dimension or non-finite values")
        if sum(x * x for x in vector) <= 0:
            raise ValueError("Zero embedding vector")


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Shared document/query encoder; BGE-M3 requires no query prefix."""
    if not texts:
        return []
    if any(not isinstance(text, str) or not text.strip() for text in texts):
        raise ValueError("Embedding input must contain non-empty strings")
    if BATCH_SIZE < 1:
        raise ValueError("EMBEDDING_BATCH_SIZE must be positive")
    model = _embedding_model()
    # Prevent silent truncation of long inputs, particularly future search queries.
    lengths = model.tokenizer(texts, truncation=False, padding=False)["input_ids"]
    if any(len(tokens) > model.max_seq_length for tokens in lengths):
        raise ValueError("Text exceeds embedding model token limit; split it before encoding")
    vectors = model.encode(texts, batch_size=BATCH_SIZE, normalize_embeddings=True,
                           convert_to_numpy=True, show_progress_bar=False).tolist()
    _validate_vectors(vectors, len(texts))
    return vectors


def get_collection():
    """Persistent cosine collection guarded against incompatible embeddings."""
    import chromadb
    from chromadb.config import Settings
    client = chromadb.PersistentClient(path=str(CHROMA_DIR), settings=Settings(anonymized_telemetry=False))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME, embedding_function=None,
        metadata=_signature(), configuration={"hnsw": {"space": "cosine"}},
    )
    if any((collection.metadata or {}).get(key) != value for key, value in _signature().items()):
        raise ValueError("Collection uses different embedding settings; select a new CHROMA_COLLECTION.")
    if collection.configuration["hnsw"]["space"] != "cosine":
        raise ValueError("Collection must use cosine distance")
    return collection


def load_documents() -> list[dict]:
    """Remove front matter from content while preserving citation metadata."""
    import yaml
    documents = []
    for doc_type in ("legal", "news"):
        for path in sorted((STANDARDIZED_DIR / doc_type).glob("*.md")):
            raw = path.read_text(encoding="utf-8-sig")
            match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n(.*)\Z", raw, re.S)
            front, body = ({}, raw) if not match else (yaml.safe_load(match[1]), match[2])
            if not isinstance(front, dict):
                raise ValueError(f"Invalid front matter: {path}")
            metadata = {
                "source": front.get("source", path.name), "title": front.get("title", path.stem),
                "doc_type": doc_type, "url": front.get("url"),
                "standardized_source": path.relative_to(STANDARDIZED_DIR).as_posix(),
            }
            for key in ("language", "date_crawled", "download_url", "source_sha256", "review_status"):
                if front.get(key) is not None:
                    metadata[key] = front[key]
            document = {"id": path.relative_to(STANDARDIZED_DIR).as_posix(),
                        "content": body.strip(), "metadata": metadata}
            validate_document(document)
            documents.append(document)
    if not documents:
        raise ValueError(f"No Markdown documents in {STANDARDIZED_DIR}")
    return documents


def _segments(document: dict):
    """Keep legal chunks within an original PDF page for exact citations."""
    content = document["content"]
    markers = list(re.finditer(r"^## Trang (\d+)\s*$", content, re.M)) if document["metadata"]["doc_type"] == "legal" else []
    if not markers:
        yield content, None
        return
    preamble = content[:markers[0].start()].strip()
    # Preserve real preamble text; Task 3's title-only prefix already lives in metadata.
    if preamble and preamble != f"# {document['metadata']['title']}":
        yield preamble, None
    for index, marker in enumerate(markers):
        end = markers[index + 1].start() if index + 1 < len(markers) else len(content)
        yield content[marker.end():end].strip(), int(marker[1])


def _split(content: str):
    """500-character windows; prefer paragraph, line, sentence, word boundaries."""
    start = 0
    while start < len(content):
        end = min(start + CHUNK_SIZE, len(content))
        if end < len(content):
            for separator in ("\n\n", "\n", ". ", " "):
                split = content.rfind(separator, start + CHUNK_SIZE // 2, end)
                if split >= 0:
                    end = split + len(separator)
                    break
        part = content[start:end].strip()
        if part:
            yield part
        if end == len(content):
            break
        start = max(start + 1, end - CHUNK_OVERLAP)


def chunk_documents(documents: list[dict]) -> list[dict]:
    if not 0 <= CHUNK_OVERLAP < CHUNK_SIZE // 2:
        raise ValueError("Overlap must be non-negative and less than half the chunk size")
    if len({doc["id"] for doc in documents}) != len(documents):
        raise ValueError("Duplicate document IDs")
    chunks = []
    for document in documents:
        validate_document(document)
        index = 0
        for segment, page in _segments(document):
            for text in _split(segment):
                metadata = {**document["metadata"], "document_id": document["id"],
                            "chunk_index": index, "chunking_method": CHUNKING_METHOD}
                if page is not None:
                    metadata["page"] = page
                chunk = {"id": f"{document['id']}::chunk-{index}", "content": text, "metadata": metadata}
                validate_document(chunk, require_chunk=True)
                chunks.append(chunk)
                index += 1
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Resume embedding batches using a content-and-model keyed local cache."""
    if BATCH_SIZE < 1:
        raise ValueError("EMBEDDING_BATCH_SIZE must be positive")
    signature = json.dumps(_signature(), sort_keys=True)
    embedded = []
    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start:start + BATCH_SIZE]
        vectors, pending, cache_paths = {}, [], {}
        for index, chunk in enumerate(batch):
            validate_document(chunk, require_chunk=True)
            key = hashlib.sha256((signature + "\n" + chunk["content"]).encode()).hexdigest()
            path = EMBEDDING_CACHE / f"{key}.json"
            cache_paths[index] = path
            if path.exists():
                vectors[index] = json.loads(path.read_text(encoding="utf-8"))
                _validate_vectors([vectors[index]], 1)
            else:
                pending.append(index)
        if pending:
            fresh = embed_texts([batch[index]["content"] for index in pending])
            _validate_vectors(fresh, len(pending))
            for index, vector in zip(pending, fresh):
                vectors[index] = vector
                _write(cache_paths[index], json.dumps(vector) + "\n")
        embedded.extend({**chunk, "embedding": vectors[index]} for index, chunk in enumerate(batch))
        print(f"Embedded {min(start + BATCH_SIZE, len(chunks))}/{len(chunks)} chunks", flush=True)
    return embedded


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert stable IDs and remove obsolete chunks of the supplied documents."""
    if not chunks:
        raise ValueError("Refusing to index an empty corpus")
    ids = [chunk["id"] for chunk in chunks]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate chunk IDs")
    for chunk in chunks:
        validate_document(chunk, require_chunk=True)
        if not chunk["metadata"].get("document_id"):
            raise ValueError("Missing document_id")
    _validate_vectors([chunk["embedding"] for chunk in chunks], len(chunks))
    collection = get_collection()
    for start in range(0, len(chunks), 100):
        batch = chunks[start:start + 100]
        metadatas = []
        for chunk in batch:
            # Chroma does not accept None; canonical JSONL retains url=None.
            metadata = {key: value for key, value in chunk["metadata"].items() if value is not None}
            metadata.setdefault("url", "")
            metadata["pipeline_owner"] = PIPELINE_OWNER
            metadatas.append(metadata)
        collection.upsert(ids=[c["id"] for c in batch], documents=[c["content"] for c in batch],
                          embeddings=[c["embedding"] for c in batch], metadatas=metadatas)
    wanted = set(ids)
    for doc_id in {c["metadata"]["document_id"] for c in chunks}:
        previous = collection.get(where={"document_id": doc_id}, include=[])["ids"]
        stale = [item for item in previous if item not in wanted]
        if stale:
            collection.delete(ids=stale)


def _save_corpus(chunks: list[dict]) -> None:
    _write(CHUNKS_PATH, "".join(json.dumps(chunk, ensure_ascii=False) + "\n" for chunk in chunks))


def run_pipeline() -> None:
    missing = [name for name in ("chromadb", "sentence_transformers") if importlib.util.find_spec(name) is None]
    if missing:
        raise ModuleNotFoundError(f"Missing Task 4 dependencies: {', '.join(missing)}. See docs/TASK4.md; --prepare works without them.")
    documents = load_documents()
    chunks = chunk_documents(documents)
    print(f"Loaded {len(documents)} documents; prepared {len(chunks)} chunks", flush=True)
    embedded_chunks = embed_chunks(chunks)
    index_to_vectorstore(embedded_chunks)
    collection = get_collection()
    # A full run synchronizes this pipeline's generated corpus, including removed files.
    existing = collection.get(where={"pipeline_owner": PIPELINE_OWNER}, include=[])["ids"]
    wanted = {chunk["id"] for chunk in chunks}
    stale = [item for item in existing if item not in wanted]
    for start in range(0, len(stale), 100):
        collection.delete(ids=stale[start:start + 100])
    if collection.count() != len(chunks):
        raise RuntimeError("Collection count differs from prepared corpus")
    _save_corpus(chunks)
    report = {"status": "indexed", "documents": len(documents), "chunks": len(chunks),
              "collection": COLLECTION_NAME, "distance": "cosine", **_signature(),
              "chunk_size": CHUNK_SIZE, "chunk_overlap": CHUNK_OVERLAP,
              "chunking_method": CHUNKING_METHOD}
    _write(REPORT_PATH, json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"Indexed {len(chunks)} chunks in {CHROMA_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true", help="Export chunks only, without embedding or database writes")
    args = parser.parse_args()
    if args.prepare:
        docs = load_documents()
        chunks = chunk_documents(docs)
        _save_corpus(chunks)
        print(f"Prepared {len(chunks)} chunks from {len(docs)} documents: {CHUNKS_PATH}")
    else:
        run_pipeline()
