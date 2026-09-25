"""Utilities for showing two real vectorization methods in the Streamlit demo."""

from functools import lru_cache
from pathlib import Path

import numpy as np

from .task4_chunking_indexing import chunk_documents, load_documents
from .task5_semantic_search import semantic_search


@lru_cache(maxsize=1)
def _corpus() -> tuple[dict, ...]:
    return tuple(chunk_documents(load_documents()))


@lru_cache(maxsize=2)
def _sentence_model(model_name: str):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def _model_results(query: str, model_name: str, top_k: int) -> list[dict]:
    if model_name == "BAAI/bge-m3" and not _has_local_bge_model():
        raise RuntimeError("BGE-M3 model is not fully available in the local cache")
    chunks = list(_corpus())
    model = _sentence_model(model_name)
    vectors = model.encode(
        [chunk["content"] for chunk in chunks], normalize_embeddings=True
    )
    query_vector = model.encode([query], normalize_embeddings=True)[0]
    scores = np.asarray(vectors) @ np.asarray(query_vector)
    ranked = np.argsort(-scores)[:top_k]
    return [_as_result(chunks[index], float(scores[index]), model_name) for index in ranked]


def _has_local_bge_model() -> bool:
    cache_root = Path.home() / ".cache" / "huggingface" / "hub" / "models--BAAI--bge-m3"
    return any(
        path.is_file() and path.stat().st_size > 1_000_000
        for path in cache_root.glob("snapshots/*/model.safetensors")
    )


def _tfidf_results(query: str, top_k: int) -> list[dict]:
    from sklearn.feature_extraction.text import TfidfVectorizer

    chunks = list(_corpus())
    vectorizer = TfidfVectorizer(strip_accents="unicode", lowercase=True)
    matrix = vectorizer.fit_transform(chunk["content"] for chunk in chunks)
    query_vector = vectorizer.transform([query])
    scores = (matrix @ query_vector.T).toarray().ravel()
    ranked = np.argsort(-scores)[:top_k]
    return [_as_result(chunks[index], float(scores[index]), "TF-IDF") for index in ranked]


def _as_result(chunk: dict, score: float, model_name: str) -> dict:
    return {
        **chunk,
        "score": score,
        "retrieval_method": model_name,
    }


def compare_embeddings(query: str, top_k: int = 3) -> dict:
    """Return MiniLM results and BGE-M3 results, with an explicit local fallback."""
    if not query.strip() or top_k <= 0:
        return {"MiniLM": [], "BGE-M3": [], "BGE-M3_status": "empty query"}

    result = {"MiniLM": semantic_search(query, top_k=top_k), "BGE-M3_status": "ready"}
    try:
        result["BGE-M3"] = _model_results(query, "BAAI/bge-m3", top_k)
    except Exception as exc:
        result["BGE-M3"] = _tfidf_results(query, top_k)
        result["BGE-M3_status"] = f"unavailable; showing TF-IDF fallback ({type(exc).__name__})"
    return result
