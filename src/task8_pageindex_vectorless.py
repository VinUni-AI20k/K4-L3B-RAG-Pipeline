"""
Task 8 — PageIndex Vectorless RAG.

Đăng ký tài khoản tại: https://pageindex.ai/ (hoặc https://dash.pageindex.ai/)
Lấy API key (tiền tố pix_...) và cấu hình vào file .env:
    PAGEINDEX_API_KEY=pix_xxxxxxxxxxxx

PageIndex cho phép RAG mà không cần vector database — sử dụng tree structure & semantic
parsing trực tiếp trên tài liệu. Được dùng làm fallback khi hybrid search không đạt threshold.
"""

import os
import re
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
LANDING_LEGAL_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"
DOCS_MAP_FILE = Path(__file__).parent.parent / "data" / "pageindex_docs.json"


def upload_documents() -> list[str]:
    """
    Upload các tài liệu PDF trong data/landing/legal/ lên PageIndex Cloud.
    Lưu danh sách doc_id vào data/pageindex_docs.json để tái sử dụng.
    """
    if not PAGEINDEX_API_KEY or PAGEINDEX_API_KEY.startswith("pix_mock"):
        print("⚠ Chưa có PAGEINDEX_API_KEY thật từ https://pageindex.ai/. Bỏ qua upload.")
        return []

    from pageindex.client import PageIndexClient
    client = PageIndexClient(api_key=PAGEINDEX_API_KEY)

    doc_ids = []
    if LANDING_LEGAL_DIR.exists():
        for pdf_file in LANDING_LEGAL_DIR.glob("*.pdf"):
            print(f"Uploading {pdf_file.name} to PageIndex...")
            try:
                resp = client.submit_document(file_path=str(pdf_file))
                doc_id = resp.get("doc_id") or resp.get("id")
                if doc_id:
                    doc_ids.append(doc_id)
                    print(f"  ✓ Uploaded thành công: {pdf_file.name} -> doc_id: {doc_id}")
            except Exception as e:
                print(f"  ❌ Lỗi upload {pdf_file.name}: {e}")

    if doc_ids:
        DOCS_MAP_FILE.write_text(json.dumps(doc_ids, indent=2), encoding="utf-8")
        print(f"✓ Đã lưu {len(doc_ids)} doc_id vào {DOCS_MAP_FILE}")

    return doc_ids


def _local_structural_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Tìm kiếm dựa trên cấu trúc đề mục (headings & sections) của Markdown documents.
    Phục vụ như cơ chế vectorless fallback nội bộ khi chưa có hoặc lỗi kết nối PageIndex API.
    """
    results = []
    if not STANDARDIZED_DIR.exists():
        return results

    query_tokens = set(re.findall(r"\w+", query.lower()))

    # Quét qua tất cả file markdown và trích xuất các section theo heading (#, ##, ###)
    sections = []
    for md_file in STANDARDIZED_DIR.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        raw_sections = re.split(r"\n(?=#{1,3}\s)", content)
        
        for sec in raw_sections:
            sec_clean = sec.strip()
            if not sec_clean:
                continue
            
            lines = sec_clean.split("\n")
            title = lines[0].replace("#", "").strip()
            
            sections.append({
                "source": md_file.name,
                "title": title,
                "content": sec_clean,
            })

    # Chấm điểm độ khớp từ khoá với tiêu đề và nội dung section
    scored_sections = []
    for sec in sections:
        sec_tokens = set(re.findall(r"\w+", sec["content"].lower()))
        title_tokens = set(re.findall(r"\w+", sec["title"].lower()))
        
        # Tiêu đề khớp được trọng số cao hơn
        title_matches = len(query_tokens.intersection(title_tokens))
        body_matches = len(query_tokens.intersection(sec_tokens))
        score = (title_matches * 2.0 + body_matches * 1.0) / max(1, len(query_tokens))
        
        if score > 0:
            scored_sections.append((score, sec))

    scored_sections.sort(key=lambda x: x[0], reverse=True)

    fallback_items = scored_sections[:top_k] if scored_sections else [(0.5, s) for s in sections[:top_k]]

    for rank, (score, sec) in enumerate(fallback_items, 1):
        doc_type = "legal" if "legal" in str(sec["source"]).lower() else "news"
        results.append({
            "id": f"{Path(sec['source']).stem}-{rank-1}",
            "content": sec["content"],
            "score": round(float(score if score > 0 else 0.5 / rank), 4),
            "metadata": {
                "source": sec["source"],
                "title": sec["title"],
                "doc_type": doc_type,
                "url": None,
                "chunk_index": rank - 1,
            },
            "retrieval_method": "pageindex",
            "source": "pageindex",
        })

    return results[:top_k]


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Vectorless retrieval sử dụng PageIndex Cloud API (hoặc local structural index fallback).

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of SearchResult dictionaries:
        {
            'id': str,
            'content': str,
            'score': float,
            'metadata': dict,
            'retrieval_method': 'pageindex'
        }
    """
    # 1. Thử gọi PageIndex Cloud API nếu có API key thật
    if PAGEINDEX_API_KEY and not PAGEINDEX_API_KEY.startswith("pix_mock"):
        try:
            from pageindex.client import PageIndexClient
            client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
            
            # Lấy danh sách doc_id đã upload
            doc_ids = []
            if DOCS_MAP_FILE.exists():
                doc_ids = json.loads(DOCS_MAP_FILE.read_text(encoding="utf-8"))
            if not doc_ids:
                # Nếu chưa upload, tự động upload
                doc_ids = upload_documents()

            if doc_ids:
                all_results = []
                idx_counter = 0
                for doc_id in doc_ids[:2]:  # Query các doc chính
                    resp = client.submit_query(doc_id=doc_id, query=query)
                    retrieval_id = resp.get("retrieval_id") or resp.get("id")
                    
                    if retrieval_id:
                        # Poll chờ retrieval hoàn thành
                        for _ in range(10):
                            if client.is_retrieval_ready(retrieval_id):
                                break
                            time.sleep(1)

                        retrieval = client.get_retrieval(retrieval_id)
                        for node in retrieval.get("retrieved_nodes", []):
                            for group in node.get("relevant_contents", []):
                                for item in group:
                                    content_text = item.get("relevant_content", "")
                                    if not content_text:
                                        continue
                                    idx_counter += 1
                                    sec_title = item.get("section_title", "General")
                                    all_results.append({
                                        "id": f"pageindex-{doc_id}-{idx_counter}",
                                        "content": content_text,
                                        "score": 0.85,
                                        "metadata": {
                                            "source": f"{doc_id}.pdf",
                                            "title": sec_title,
                                            "doc_type": "legal",
                                            "url": None,
                                            "chunk_index": idx_counter,
                                        },
                                        "retrieval_method": "pageindex",
                                        "source": "pageindex",
                                    })
                if all_results:
                    return all_results[:top_k]
        except Exception as e:
            print(f"Lưu ý: Không thể truy vấn PageIndex Cloud ({e}). Tự động kích hoạt Local Structural Fallback.")

    # 2. Local structural search (mô phỏng cây cấu trúc không dùng vector)
    return _local_structural_search(query, top_k=top_k)


if __name__ == "__main__":
    print("=" * 60)
    print("Task 8: PageIndex Vectorless Search")
    print(f"API Key: {'Đã cấu hình' if PAGEINDEX_API_KEY and not PAGEINDEX_API_KEY.startswith('pix_mock') else 'Chưa có key (dùng Local Fallback)'}")
    print("=" * 60)

    results = pageindex_search("chính sách bảo hành và đổi trả", top_k=3)
    for r in results:
        print(f"[{r['score']:.4f}][{r['source']}] {r['content'][:100]}...")
