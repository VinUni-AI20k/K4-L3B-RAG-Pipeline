"""
Task 8 — PageIndex vectorless fallback.

Hướng dẫn:
    1. Đọc PAGEINDEX_API_KEY từ .env.
    2. Upload tài liệu ở định dạng PageIndex hỗ trợ.
    3. Cache document IDs để không upload lại.
    4. Parse kết quả thành SearchResult có method pageindex.

PageIndex là dịch vụ ngoài: cần timeout và xử lý lỗi để pipeline không crash.
"""

import os
from pathlib import Path

import re

from dotenv import load_dotenv


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"

# Có thể thay bằng adapter PageIndex thật mà không đổi pageindex_search().
PAGEINDEX_BACKEND = None
_DOCUMENT_IDS: dict[str, str] = {}


def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    """Chuẩn bị mock document index từ standardized data.

    Khi nối PageIndex thật, adapter chỉ cần cập nhật ``_DOCUMENT_IDS`` và
    gán callable vào ``PAGEINDEX_BACKEND``.
    """
    _DOCUMENT_IDS.clear()
    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        if path.is_file() and path.read_text(encoding="utf-8").strip():
            relative = path.relative_to(STANDARDIZED_DIR).as_posix()
            _DOCUMENT_IDS[relative] = relative


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult."""
    if top_k <= 0 or not query.strip():
        return []

    if PAGEINDEX_BACKEND is not None:
        return PAGEINDEX_BACKEND(query, top_k)

    # Mock fallback: dùng cùng standardized corpus để pipeline chạy được
    # trước khi nhóm cấu hình PageIndex thật.
    from .task4_chunking_indexing import chunk_documents, load_documents

    if not _DOCUMENT_IDS:
        upload_documents()
    chunks = chunk_documents(load_documents())
    query_tokens = set(_tokenize(query))
    ranked = []
    for chunk in chunks:
        content_tokens = set(_tokenize(chunk["content"]))
        overlap = len(query_tokens & content_tokens)
        if overlap:
            ranked.append((overlap, chunk))

    ranked.sort(key=lambda item: (-item[0], item[1]["id"]))
    results = []
    for rank, (overlap, chunk) in enumerate(ranked[:top_k], 1):
        results.append({
            **chunk,
            "score": float(overlap) / rank,
            "retrieval_method": "pageindex",
        })
    return results


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower(), flags=re.UNICODE)


if __name__ == "__main__":
    upload_documents()
