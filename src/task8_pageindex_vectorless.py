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

from dotenv import load_dotenv


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"


def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    if not PAGEINDEX_API_KEY:
        print("PAGEINDEX_API_KEY not set. Skipping upload.")
        return

    try:
        import pageindex

        client = pageindex.Client(api_key=PAGEINDEX_API_KEY)
        for path in STANDARDIZED_DIR.rglob("*.md"):
            content = path.read_text(encoding="utf-8")
            print(f"Would upload: {path.name} ({len(content)} chars)")
    except Exception as e:
        print(f"PageIndex upload failed: {e}")


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult."""
    if not PAGEINDEX_API_KEY:
        return []

    try:
        import pageindex

        client = pageindex.Client(api_key=PAGEINDEX_API_KEY)
        # Attempt to query - adapt based on actual SDK
        results = []
        # Parse results into SearchResult format
        return results[:top_k]
    except Exception as e:
        print(f"PageIndex search failed: {e}")
        return []


if __name__ == "__main__":
    upload_documents()
