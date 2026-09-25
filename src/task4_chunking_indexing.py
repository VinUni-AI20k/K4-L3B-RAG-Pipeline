"""Task 4 — Load, chunk, embed and index standardized Markdown."""

from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

from .contracts import validate_document


load_dotenv()

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 0
CHUNKING_METHOD = "markdown_section_recursive"
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "sentence_transformers").strip().lower()
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3").strip()
EMBEDDING_DIM = 1024
COLLECTION_NAME = "rag_documents"
UPSERT_BATCH_SIZE = 100


def _metadata_value(content: str, label: str) -> str | None:
    match = re.search(rf"^\*\*{re.escape(label)}:\*\*\s*(.*?)\s*$", content, re.MULTILINE)
    if not match:
        return None
    value = match.group(1).strip()
    if value.startswith("<") and value.endswith(">"):
        value = value[1:-1].strip()
    elif value.startswith("`") and value.endswith("`"):
        value = value[1:-1].strip()
    return value or None


def _parse_url(content: str) -> str | None:
    source = _metadata_value(content, "Source")
    if source and urlparse(source).scheme in {"http", "https"}:
        return source
    return None


def load_documents() -> list[dict]:
    """Read all standardized Markdown and recover source metadata."""
    if not STANDARDIZED_DIR.is_dir():
        raise FileNotFoundError(f"Standardized data directory not found: {STANDARDIZED_DIR}")

    documents: list[dict] = []
    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        if not path.is_file() or path.name.startswith("."):
            continue
        content = path.read_text(encoding="utf-8-sig").strip()
        if not content:
            continue

        relative_path = path.relative_to(STANDARDIZED_DIR).as_posix()
        path_parts = Path(relative_path).parts
        folder_type = path_parts[0] if path_parts else ""
        doc_type = _metadata_value(content, "Document type") or (
            "legal" if folder_type == "legal" else "news"
        )
        if doc_type not in {"legal", "news"}:
            doc_type = "legal" if folder_type == "legal" else "news"
        title_match = re.search(r"^#\s+(.+?)\s*$", content, re.MULTILINE)
        title = (title_match.group(1).strip() if title_match else path.stem.replace("_", " "))
        document = {
            "id": relative_path,
            "content": content,
            "metadata": {
                "source": relative_path,
                "title": title,
                "doc_type": doc_type,
                "url": _parse_url(content),
            },
        }
        validate_document(document)
        documents.append(document)
    return documents


def _markdown_sections(content: str) -> list[tuple[list[str], str]]:
    """Group Markdown body text by heading path, excluding copied metadata."""
    sections: list[tuple[list[str], str]] = []
    headings: dict[int, str] = {}
    body_lines: list[str] = []

    def flush() -> None:
        body = "\n".join(body_lines).strip()
        if body:
            sections.append((list(headings[level] for level in sorted(headings)), body))
        body_lines.clear()

    for line in content.splitlines():
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if heading:
            flush()
            level = len(heading.group(1))
            for old_level in [item for item in headings if item >= level]:
                del headings[old_level]
            headings[level] = heading.group(2).strip()
            continue
        if re.match(r"^\*\*(?:Source|Crawled|Document type):\*\*", line.strip(), re.IGNORECASE):
            continue
        if line.strip() == "---":
            continue
        body_lines.append(line)
    flush()
    return sections


def _markdown_blocks(body: str) -> list[str]:
    """Split paragraphs while keeping adjacent Markdown list items together."""
    raw_blocks = [part.strip() for part in re.split(r"\n\s*\n+", body) if part.strip()]
    blocks: list[str] = []
    for block in raw_blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        is_list = bool(lines) and all(
            re.match(r"^(?:[-*+]\s+|\d+[.)]\s+)", line) for line in lines
        )
        if is_list and blocks and all(
            re.match(r"^(?:[-*+]\s+|\d+[.)]\s+)", line)
            for line in blocks[-1].splitlines()
        ):
            blocks[-1] += "\n" + "\n".join(lines)
        else:
            blocks.append("\n".join(lines))
    return blocks


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chunk Markdown by section and paragraph, carrying heading context forward."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    chunks: list[dict] = []
    seen_ids: set[str] = set()
    for document in documents:
        validate_document(document)
        pieces: list[tuple[str, str]] = []
        for section_path, body in _markdown_sections(document["content"]):
            heading_context = " > ".join(section_path) or str(document["metadata"]["title"])
            prefix = f"Section: {heading_context}\n\n"
            body_budget = max(100, CHUNK_SIZE - len(prefix))
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=body_budget,
                chunk_overlap=CHUNK_OVERLAP,
                separators=["\n\n", "\n", ". ", " ", ""],
                strip_whitespace=True,
            )

            fragments: list[str] = []
            for block in _markdown_blocks(body):
                fragments.extend(splitter.split_text(block))

            grouped: list[str] = []
            grouped_length = 0
            for fragment in fragments:
                separator_length = 2 if grouped else 0
                if grouped and grouped_length + separator_length + len(fragment) > body_budget:
                    pieces.append((heading_context, prefix + "\n\n".join(grouped)))
                    grouped = []
                    grouped_length = 0
                    separator_length = 0
                grouped.append(fragment)
                grouped_length += separator_length + len(fragment)
            if grouped:
                pieces.append((heading_context, prefix + "\n\n".join(grouped)))

        for index, (section_path, text) in enumerate(pieces):
            text = text.strip()
            if not text:
                continue
            chunk_id = f"{document['id']}::chunk-{index}"
            if chunk_id in seen_ids:
                raise ValueError(f"Duplicate chunk ID: {chunk_id}")
            seen_ids.add(chunk_id)
            chunk = {
                "id": chunk_id,
                "content": text,
                "metadata": {
                    **document["metadata"],
                    "chunk_index": index,
                    "section_path": section_path,
                },
            }
            validate_document(chunk, require_chunk=True)
            chunks.append(chunk)
    return chunks


@lru_cache(maxsize=1)
def _sentence_transformer_model():
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as error:
        raise RuntimeError(
            "sentence-transformers is required for local embeddings; "
            'install project dependencies with: python -m pip install -e ".[dev]"'
        ) from error
    return SentenceTransformer(EMBEDDING_MODEL)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed text with the configured provider; local BGE is the default."""
    if not texts:
        return []
    if any(not isinstance(text, str) or not text.strip() for text in texts):
        raise ValueError("embed_texts only accepts non-empty strings")

    if EMBEDDING_PROVIDER == "sentence_transformers":
        vectors = _sentence_transformer_model().encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return vectors.tolist()

    if EMBEDDING_PROVIDER == "openai":
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("Set OPENAI_API_KEY to use OpenAI embeddings")
        client = OpenAI(api_key=api_key)
        response = client.embeddings.create(model=EMBEDDING_MODEL, input=texts)
        return [item.embedding for item in response.data]

    if EMBEDDING_PROVIDER == "gemini":
        from google import genai

        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("Set GEMINI_API_KEY to use Gemini embeddings")
        client = genai.Client(api_key=api_key)
        vectors: list[list[float]] = []
        for text in texts:
            response = client.models.embed_content(model=EMBEDDING_MODEL, contents=text)
            if not response.embeddings or not response.embeddings[0].values:
                raise RuntimeError("Gemini returned an empty embedding")
            vectors.append(response.embeddings[0].values)
        return vectors

    raise ValueError(
        f"Unsupported EMBEDDING_PROVIDER={EMBEDDING_PROVIDER!r}; "
        "choose sentence_transformers, openai or gemini"
    )


def get_collection():
    """Open the persistent Chroma collection with cosine distance."""
    import chromadb

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def _chroma_metadata(metadata: dict) -> dict:
    """Chroma only accepts scalar metadata values; omit optional null fields."""
    return {key: value for key, value in metadata.items() if value is not None}


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks in bounded batches and remove stale IDs from prior runs."""
    if not chunks:
        raise ValueError("No chunks to index; refusing to clear or alter the collection")
    for chunk in chunks:
        validate_document(chunk, require_chunk=True)
        embedding = chunk.get("embedding")
        if not isinstance(embedding, list) or not embedding:
            raise ValueError(f"Chunk {chunk['id']} has no embedding")

    collection = get_collection()
    ids = [chunk["id"] for chunk in chunks]
    existing_ids = collection.get(include=["metadatas"])["ids"]
    stale_ids = sorted(set(existing_ids) - set(ids))

    for start in range(0, len(chunks), UPSERT_BATCH_SIZE):
        batch = chunks[start : start + UPSERT_BATCH_SIZE]
        collection.upsert(
            ids=[chunk["id"] for chunk in batch],
            documents=[chunk["content"] for chunk in batch],
            embeddings=[chunk["embedding"] for chunk in batch],
            metadatas=[_chroma_metadata(chunk["metadata"]) for chunk in batch],
        )
    if stale_ids:
        collection.delete(ids=stale_ids)


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Embed chunks in batches while preserving each chunk's identity."""
    embedded: list[dict] = []
    for start in range(0, len(chunks), UPSERT_BATCH_SIZE):
        batch = chunks[start : start + UPSERT_BATCH_SIZE]
        vectors = embed_texts([chunk["content"] for chunk in batch])
        if len(vectors) != len(batch):
            raise RuntimeError("Embedding provider returned a different number of vectors")
        for chunk, vector in zip(batch, vectors, strict=True):
            embedded.append({**chunk, "embedding": vector})
    return embedded


def run_pipeline() -> None:
    """Load, chunk, embed and index the current standardized corpus."""
    documents = load_documents()
    if not documents:
        raise ValueError(f"No non-empty Markdown documents found in {STANDARDIZED_DIR}")
    chunks = chunk_documents(documents)
    embedded_chunks = embed_chunks(chunks)
    index_to_vectorstore(embedded_chunks)
    print(f"Indexed {len(embedded_chunks)} chunks from {len(documents)} documents")


if __name__ == "__main__":
    run_pipeline()
