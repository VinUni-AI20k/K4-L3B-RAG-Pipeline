"""Export current Task 4 chunks as a readable Markdown inspection file.

Run with: python -m src.export_chunks
"""

from __future__ import annotations

from pathlib import Path

from .task4_chunking_indexing import CHUNK_OVERLAP, CHUNK_SIZE, CHUNKING_METHOD, chunk_documents, load_documents


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT / "group_project" / "evaluation" / "CHUNKING_PREVIEW.md"


def export_chunks() -> Path:
    documents = load_documents()
    chunks = chunk_documents(documents)
    lines = [
        "# Chunking preview",
        "",
        f"- Documents: {len(documents)}",
        f"- Chunks: {len(chunks)}",
        f"- Strategy: `{CHUNKING_METHOD}`",
        f"- Target size: {CHUNK_SIZE} characters; overlap: {CHUNK_OVERLAP}",
        "",
        "Use the document and section headings below to inspect whether each chunk retains enough context and avoids mixing unrelated content.",
        "",
    ]

    previous_document = None
    for chunk in chunks:
        document_id = chunk["metadata"]["source"]
        if document_id != previous_document:
            lines.extend([f"## `{document_id}`", ""])
            previous_document = document_id

        section_path = chunk["metadata"].get("section_path", "")
        lines.extend([
            f"### Chunk {chunk['metadata']['chunk_index']} — {len(chunk['content'])} characters",
            "",
            f"- ID: `{chunk['id']}`",
            f"- Section: {section_path or '(document introduction)'}",
            "",
            "```text",
            chunk["content"].replace("```", "` ` `"),
            "```",
            "",
        ])

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return OUTPUT_PATH


if __name__ == "__main__":
    path = export_chunks()
    print(f"Saved {path}")
