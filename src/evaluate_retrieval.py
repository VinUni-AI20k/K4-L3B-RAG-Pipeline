"""Compare retrieval quality across legacy and Markdown-aware chunking.

Run with: python -m src.evaluate_retrieval
The dense model is local and can be selected with RETRIEVAL_EVAL_MODEL.
"""

from __future__ import annotations

import json
import os
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np

from . import task6_lexical_search
from .task4_chunking_indexing import CHUNK_SIZE, chunk_documents, load_documents
from .task7_reranking import rerank_rrf


ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = Path(os.getenv("RETRIEVAL_EVAL_DATASET", ROOT / "group_project" / "evaluation" / "golden_dataset.json"))
REPORT_PATH = Path(os.getenv("RETRIEVAL_EVAL_REPORT", ROOT / "group_project" / "evaluation" / "RETRIEVAL_COMPARISON.md"))
TOP_K = 5
CANDIDATE_K = 10
MODEL_NAME = os.getenv("RETRIEVAL_EVAL_MODEL", "sentence-transformers/all-mpnet-base-v2")
CHALLENGE_LABELS = {
    "bm25_targeted": "BM25-targeted terms",
    "semantic_paraphrase": "Semantic paraphrases",
    "multi_constraint": "Multi-constraint questions",
}
METHODS = ["Sparse (BM25)", "Dense", "Hybrid (RRF)"]


def _normalise(text: str) -> str:
    """Normalize crawler replacement chars, zero-width chars and whitespace."""
    value = unicodedata.normalize("NFKC", text).casefold()
    value = "".join(char for char in value if unicodedata.category(char) != "Cf")
    return re.sub(r"\s+", " ", value).strip()


def _legacy_chunks(documents: list[dict]) -> list[dict]:
    """Recreate Task 4's former 500-character recursive strategy."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks: list[dict] = []
    for document in documents:
        for index, content in enumerate(splitter.split_text(document["content"])):
            chunks.append({
                "id": f"{document['id']}::chunk-{index}",
                "content": content,
                "metadata": {**document["metadata"], "chunk_index": index},
            })
    return chunks


def _top_dense(query_vector: np.ndarray, corpus_vectors: np.ndarray, chunks: list[dict]) -> list[dict]:
    scores = corpus_vectors @ query_vector
    indices = sorted(range(len(chunks)), key=lambda index: (-float(scores[index]), chunks[index]["id"]))
    return [
        {**chunks[index], "score": float(scores[index]), "retrieval_method": "dense"}
        for index in indices[:CANDIDATE_K]
    ]


def _metric(ranking: list[dict], relevant: set[str], k: int) -> tuple[float, float]:
    hit = float(any(item["id"] in relevant for item in ranking[:k]))
    reciprocal_rank = 0.0
    for rank, item in enumerate(ranking[:k], start=1):
        if item["id"] in relevant:
            reciprocal_rank = 1.0 / rank
            break
    return hit, reciprocal_rank


def _relevant_ids(query: dict, chunks: list[dict]) -> set[str]:
    anchors = [_normalise(span) for span in query.get("gold_evidence_spans", [])]
    if not anchors:
        raise ValueError(f"{query['id']} has no gold_evidence_spans")
    relevant = {
        chunk["id"] for chunk in chunks
        if any(anchor in _normalise(chunk["content"]) for anchor in anchors)
    }
    if not relevant:
        raise ValueError(
            f"{query['id']} has no evidence-matching chunk; refine its gold_evidence_spans "
            "or preserve the evidence within a single chunk"
        )
    return relevant


def _run_chunker(label: str, chunks: list[dict], queries: list[dict], query_vectors: np.ndarray, model) -> dict:
    task6_lexical_search.CORPUS = chunks
    corpus_vectors = model.encode(
        [item["content"] for item in chunks],
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    rankings: dict[str, dict[str, list[dict]]] = {}
    relevant_by_query = {query["id"]: _relevant_ids(query, chunks) for query in queries}
    for query, query_vector in zip(queries, query_vectors, strict=True):
        dense = _top_dense(query_vector, corpus_vectors, chunks)
        sparse = task6_lexical_search.lexical_search(query["question"], top_k=CANDIDATE_K)
        hybrid = rerank_rrf([dense, sparse], top_k=TOP_K, k=60)
        rankings[query["id"]] = {
            "Sparse (BM25)": sparse[:TOP_K],
            "Dense": dense[:TOP_K],
            "Hybrid (RRF)": hybrid,
        }
    return {"label": label, "chunks": chunks, "rankings": rankings, "relevant": relevant_by_query}


def _aggregate(result: dict, queries: list[dict]) -> dict[str, dict[str, float]]:
    metrics: dict[str, dict[str, float]] = {}
    for method in METHODS:
        values = {f"hit@{k}": [] for k in (1, 3, 5)}
        values["MRR@5"] = []
        for query in queries:
            relevant = result["relevant"][query["id"]]
            ranking = result["rankings"][query["id"]][method]
            for k in (1, 3, 5):
                values[f"hit@{k}"].append(_metric(ranking, relevant, k)[0])
            values["MRR@5"].append(_metric(ranking, relevant, TOP_K)[1])
        metrics[method] = {name: sum(items) / len(items) for name, items in values.items()}
    return metrics


def _compact(chunk_id: str) -> str:
    document, chunk_number = chunk_id.split("::chunk-")
    return f"{Path(document).stem}::chunk-{chunk_number}"


def _write_report(queries: list[dict], results: list[dict], docs: list[dict]) -> str:
    metrics = {result["label"]: _aggregate(result, queries) for result in results}
    old, new = results
    old_lengths = [len(chunk["content"]) for chunk in old["chunks"]]
    new_lengths = [len(chunk["content"]) for chunk in new["chunks"]]
    old_median = sorted(old_lengths)[len(old_lengths) // 2]
    new_median = sorted(new_lengths)[len(new_lengths) // 2]
    lines = [
        f"# Chunking and retrieval comparison: {len(queries)} IELTS Writing questions",
        "",
        "## Corpus analysis and chunking choice",
        "",
        f"- Corpus: {len(docs)} standardized IELTS Writing Markdown pages. The pages use nested headings, paragraphs, and lists; the longest article contains long criterion explanations and examples.",
        f"- Legacy: recursive character splitting, 500 characters with 50-character overlap; {len(old['chunks'])} chunks.",
        f"- Updated: Markdown heading-path-aware recursive splitting, {CHUNK_SIZE} characters maximum including a repeated `Section:` breadcrumb, zero overlap, and paragraph/list grouping; {len(new['chunks'])} chunks.",
        f"- Chunk content length: legacy average {sum(old_lengths) / len(old_lengths):.0f} / median {old_median} characters; updated average {sum(new_lengths) / len(new_lengths):.0f} / median {new_median} characters.",
        "- Reason: heading context prevents chunks from becoming detached from the IELTS criterion/task they describe. Paragraph/list grouping keeps self-contained guidance together. Zero overlap avoids indexing repeated content; document sections already carry context.",
        "- Gold relevance is determined from exact evidence spans in the corpus, normalized for crawler replacement/zero-width characters and whitespace. This makes labels independent of chunk IDs and permits a fair comparison across boundaries.",
        f"- Query language: {'Vietnamese; this measures cross-language retrieval against English source evidence.' if all(item.get('language') == 'vi' for item in queries) else 'English; questions match the language of the source corpus.'}",
        f"- Dense: `{MODEL_NAME}` Sentence Transformers embeddings with normalized cosine vectors. Sparse: the project's BM25 implementation. Hybrid: RRF (`k=60`) from each method's top {CANDIDATE_K}, output top {TOP_K}.",
        "- Metrics are macro averages across the same 30 queries. Hit@k means a chunk containing a complete accepted evidence span appears in the first k. This evaluates chunk match, not generated answer correctness or citation quality.",
        "",
        "## Aggregate chunk-match results",
        "",
        "| Chunker | Method | Hit@1 | Hit@3 | Hit@5 | MRR@5 |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for result in results:
        for method in METHODS:
            m = metrics[result["label"]][method]
            lines.append(
                f"| {result['label']} | {method} | {m['hit@1']:.3f} | {m['hit@3']:.3f} | "
                f"{m['hit@5']:.3f} | {m['MRR@5']:.3f} |"
            )
    lines.extend(["", "## Change by retrieval method", "", "| Method | Δ Hit@1 | Δ Hit@3 | Δ Hit@5 | Δ MRR@5 |", "|---|---:|---:|---:|---:|"])
    for method in METHODS:
        before, after = metrics[old["label"]][method], metrics[new["label"]][method]
        lines.append("| " + method + " | " + " | ".join(
            f"{after[key] - before[key]:+.3f}" for key in ("hit@1", "hit@3", "hit@5", "MRR@5")
        ) + " |")

    sparse_delta = metrics[new["label"]]["Sparse (BM25)"]["hit@5"] - metrics[old["label"]]["Sparse (BM25)"]["hit@5"]
    dense_delta = metrics[new["label"]]["Dense"]["hit@5"] - metrics[old["label"]]["Dense"]["hit@5"]
    hybrid_delta = metrics[new["label"]]["Hybrid (RRF)"]["hit@5"] - metrics[old["label"]]["Hybrid (RRF)"]["hit@5"]
    lines.extend([
        "",
        "## Reading the result",
        "",
        f"Updated versus legacy Hit@5: BM25 {sparse_delta:+.3f}, dense {dense_delta:+.3f}, hybrid {hybrid_delta:+.3f}. These measured results describe this dataset and embedder only; they do not guarantee that hybrid ranks first for every query. For Vietnamese questions against English source chunks, evaluate a bilingual embedder and query translation as separate configurations before selecting production behavior.",
    ])

    lines.extend(["", "## Scores by question challenge", "", "| Challenge | Chunker | Method | Hit@1 | Hit@5 | MRR@5 |", "|---|---|---|---:|---:|---:|"])
    for challenge, label in CHALLENGE_LABELS.items():
        subset = [query for query in queries if query["challenge_type"] == challenge]
        if not subset:
            continue
        for result in results:
            for method in METHODS:
                rows = [(_metric(result["rankings"][q["id"]][method], result["relevant"][q["id"]], 1)[0],
                         _metric(result["rankings"][q["id"]][method], result["relevant"][q["id"]], TOP_K)[0],
                         _metric(result["rankings"][q["id"]][method], result["relevant"][q["id"]], TOP_K)[1]) for q in subset]
                means = [sum(row[index] for row in rows) / len(rows) for index in range(3)]
                lines.append(f"| {label} | {result['label']} | {method} | {means[0]:.3f} | {means[1]:.3f} | {means[2]:.3f} |")

    lines.extend(["", "## Per-question chunk match", "", "‘✓’ marks a chunk that contains a complete gold evidence span.", ""])
    for query in queries:
        lines.extend([f"### {query['id']} — {CHALLENGE_LABELS[query['challenge_type']]}", "", f"> {query['question']}", ""])
        for result in results:
            lines.append(f"**{result['label']}**")
            lines.append("")
            lines.append("| Method | Hit@5 | Top-5 chunks |")
            lines.append("|---|---:|---|")
            relevant = result["relevant"][query["id"]]
            for method in METHODS:
                ranking = result["rankings"][query["id"]][method]
                found = any(item["id"] in relevant for item in ranking[:TOP_K])
                formatted = ", ".join(
                    f"{rank}. `{_compact(item['id'])}` ({item['score']:.4f}){' ✓' if item['id'] in relevant else ''}"
                    for rank, item in enumerate(ranking[:TOP_K], start=1)
                ) or "(no lexical matches)"
                lines.append(f"| {method} | {'Yes' if found else 'No'} | {formatted} |")
            lines.append("")
        lines.extend([f"Evidence: {query['evidence']}", ""])
    lines.extend([
        "## Limits",
        "",
        "The corpus currently has five IELTS pages and does not include all eight planned sources. The benchmark's dense model is `all-mpnet-base-v2`, while production Task 4 defaults to `BAAI/bge-m3`; use the same benchmark with BGE-M3 before treating dense/hybrid numbers as production estimates. Retrieval scores are not comparable across methods; only ranked evidence matches are compared.",
        "",
    ])
    return "\n".join(lines)


def run() -> str:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    queries = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    query_ids = [item.get("id") for item in queries]
    if len(query_ids) != len(set(query_ids)):
        raise ValueError("Golden dataset query IDs must be unique")
    for query in queries:
        if query.get("scope") != "Ask IELTS Writing":
            raise ValueError(f"{query['id']} is outside the single Ask IELTS Writing scope")
        if query.get("challenge_type") not in CHALLENGE_LABELS:
            raise ValueError(f"{query['id']} has an invalid challenge_type")
    docs = load_documents()
    chunkers = [
        ("Legacy recursive 500/50", _legacy_chunks(docs)),
        (f"Markdown section-aware {CHUNK_SIZE}/0", chunk_documents(docs)),
    ]
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(MODEL_NAME)
    query_vectors = model.encode(
        [item["question"] for item in queries],
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    results = [_run_chunker(label, chunks, queries, query_vectors, model) for label, chunks in chunkers]
    report = _write_report(queries, results, docs)
    REPORT_PATH.write_text(report, encoding="utf-8")
    return report


if __name__ == "__main__":
    print(run())
