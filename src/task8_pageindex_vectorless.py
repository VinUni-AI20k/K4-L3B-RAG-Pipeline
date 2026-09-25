"""
Task 8 — PageIndex vectorless fallback.

PageIndex chỉ nhận PDF:
    - legal: upload thẳng PDF gốc trong data/landing/legal/.
    - news: convert Markdown chuẩn hoá sang PDF tạm trong data/_tmp_pdf/.
Document ID được cache trong data/pageindex_doc_ids.json (gitignore, vì ID gắn
với tài khoản PageIndex của từng người) nên chạy lại không upload trùng.

Mọi HTTP call đều có timeout. Hàm search raise lỗi khi thiếu key, chưa upload
hoặc provider lỗi; Task 9 bắt lỗi và giữ hybrid results.

Chạy (upload + chờ xử lý):
    python -m src.task8_pageindex_vectorless
"""

import json
import os
import re
import time
import unicodedata
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
BASE_URL = "https://api.pageindex.ai"

ROOT = Path(__file__).parent.parent
STANDARDIZED_DIR = ROOT / "data" / "standardized"
LANDING_LEGAL_DIR = ROOT / "data" / "landing" / "legal"
TMP_PDF_DIR = ROOT / "data" / "_tmp_pdf"
DOC_IDS_PATH = ROOT / "data" / "pageindex_doc_ids.json"

UPLOAD_TIMEOUT = 120
REQUEST_TIMEOUT = 15
# Tổng thời gian chờ một lần search; UI không được treo lâu hơn mức này.
SEARCH_BUDGET_SECONDS = 45
POLL_INTERVAL_SECONDS = 3

HEADER_FIELD = re.compile(r"^\*\*(Source|Landing file|Crawled):\*\*\s*(.+)$", re.MULTILINE)


def _headers() -> dict:
    if not PAGEINDEX_API_KEY:
        raise RuntimeError("Thiếu PAGEINDEX_API_KEY trong .env")
    return {"api_key": PAGEINDEX_API_KEY}


def _read_markdown_header(path: Path) -> dict:
    """Đọc title và source URL từ header truy vết mà Task 3 ghi vào Markdown."""
    text = path.read_text(encoding="utf-8")
    title_match = re.search(r"^# (.+)$", text, re.MULTILINE)
    fields = dict(HEADER_FIELD.findall(text))
    return {
        "title": title_match.group(1).strip() if title_match else path.stem,
        "url": fields.get("Source"),
        "text": text,
    }


def _to_latin1(text: str) -> str:
    """Font lõi của fpdf chỉ hỗ trợ latin-1; corpus news là tiếng Anh nên chỉ
    cần đổi dấu câu kiểu typographic sang ASCII."""
    replacements = {"‘": "'", "’": "'", "“": '"', "”": '"',
                    "–": "-", "—": "-", "•": "-", "…": "...",
                    " ": " "}
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = unicodedata.normalize("NFKD", text)
    return text.encode("latin-1", "replace").decode("latin-1")


def _markdown_to_pdf(markdown_path: Path) -> Path:
    from fpdf import FPDF

    TMP_PDF_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = TMP_PDF_DIR / f"{markdown_path.stem}.pdf"

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)
    for line in _to_latin1(markdown_path.read_text(encoding="utf-8")).splitlines():
        # new_x/new_y reset con trỏ về đầu dòng sau mỗi multi_cell.
        pdf.multi_cell(0, 5, line or " ", new_x="LMARGIN", new_y="NEXT")
    pdf.output(str(pdf_path))
    return pdf_path


def _load_doc_ids() -> dict:
    if DOC_IDS_PATH.exists():
        return json.loads(DOC_IDS_PATH.read_text(encoding="utf-8"))
    return {}


def _save_doc_ids(doc_ids: dict) -> None:
    DOC_IDS_PATH.write_text(json.dumps(doc_ids, ensure_ascii=False, indent=2), encoding="utf-8")


def _documents_to_upload() -> list[dict]:
    """Liệt kê tài liệu theo Markdown chuẩn hoá; `source` khớp metadata của chunk."""
    documents = []
    for markdown_path in sorted(STANDARDIZED_DIR.glob("*/*.md")):
        doc_type = markdown_path.parent.name
        header = _read_markdown_header(markdown_path)
        if doc_type == "legal":
            pdf_path = LANDING_LEGAL_DIR / f"{markdown_path.stem}.pdf"
            if not pdf_path.exists():
                print(f"Skip: không thấy PDF gốc cho {markdown_path.name}")
                continue
        else:
            pdf_path = None  # convert lúc upload
        documents.append(
            {
                "source": markdown_path.name,
                "markdown_path": markdown_path,
                "pdf_path": pdf_path,
                "title": header["title"],
                "url": header["url"],
                "doc_type": doc_type,
            }
        )
    return documents


def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    doc_ids = _load_doc_ids()

    for document in _documents_to_upload():
        source = document["source"]
        if source in doc_ids:
            print(f"Skip (cached): {source} -> {doc_ids[source]['doc_id']}")
            continue

        pdf_path = document["pdf_path"] or _markdown_to_pdf(document["markdown_path"])
        try:
            with pdf_path.open("rb") as handle:
                response = requests.post(
                    f"{BASE_URL}/doc/",
                    headers=_headers(),
                    files={"file": (pdf_path.name, handle, "application/pdf")},
                    data={"if_retrieval": True},
                    timeout=UPLOAD_TIMEOUT,
                )
            response.raise_for_status()
            doc_id = response.json()["doc_id"]
        except (requests.RequestException, KeyError, ValueError) as error:
            print(f"Failed: {source} — {error}")
            continue

        doc_ids[source] = {
            "doc_id": doc_id,
            "title": document["title"],
            "url": document["url"],
            "doc_type": document["doc_type"],
        }
        # Lưu sau mỗi file để lỗi giữa chừng không làm mất ID đã upload.
        _save_doc_ids(doc_ids)
        print(f"Uploaded: {source} -> {doc_id}")


def wait_until_ready(timeout_seconds: int = 900) -> None:
    """Chờ PageIndex xử lý xong (tree + retrieval) cho mọi document đã upload."""
    doc_ids = _load_doc_ids()
    pending = {source: info["doc_id"] for source, info in doc_ids.items()}
    deadline = time.monotonic() + timeout_seconds

    while pending and time.monotonic() < deadline:
        for source, doc_id in list(pending.items()):
            try:
                response = requests.get(
                    f"{BASE_URL}/doc/{doc_id}/",
                    headers=_headers(),
                    params={"type": "tree", "summary": False},
                    timeout=REQUEST_TIMEOUT,
                )
                if response.status_code == 200 and response.json().get("retrieval_ready"):
                    print(f"Ready: {source}")
                    del pending[source]
            except requests.RequestException:
                pass
        if pending:
            time.sleep(10)

    if pending:
        print("Chưa xong: " + ", ".join(pending))


def _request(method: str, path: str, deadline: float, **kwargs) -> dict:
    """HTTP call có timeout; gặp 429 thì chờ tới lúc rate limit reset (nếu còn
    trong budget) rồi thử lại. Tài khoản PageIndex giới hạn 120 request/phút."""
    while True:
        response = requests.request(
            method, f"{BASE_URL}{path}", headers=_headers(), timeout=REQUEST_TIMEOUT, **kwargs
        )
        if response.status_code != 429:
            response.raise_for_status()
            return response.json()

        reset_at = response.headers.get("x-ratelimit-reset")
        wait = float(reset_at) - time.time() if reset_at else 5.0
        wait = max(1.0, wait)
        if time.monotonic() + wait >= deadline:
            response.raise_for_status()
        time.sleep(wait)


def _retrieve_all(doc_ids: dict, query: str) -> tuple[dict[str, list[dict]], list[str]]:
    """Submit query cho mọi document, rồi poll theo vòng chỉ những cái chưa xong.

    Retrieval của PageIndex là bất đồng bộ và theo từng document. Poll theo vòng
    (thay vì mỗi document một vòng lặp riêng) giữ số request mỗi lần search ở
    mức ~8 submit + vài vòng poll, dưới rate limit của tài khoản.
    """
    deadline = time.monotonic() + SEARCH_BUDGET_SECONDS
    pending: dict[str, str] = {}
    nodes_by_source: dict[str, list[dict]] = {}
    errors: list[str] = []

    for source, info in doc_ids.items():
        try:
            body = _request(
                "POST", "/retrieval/", deadline,
                json={"doc_id": info["doc_id"], "query": query, "thinking": False},
            )
            pending[source] = body["retrieval_id"]
        except (requests.RequestException, KeyError, ValueError) as error:
            errors.append(f"{source}: {error}")

    while pending and time.monotonic() < deadline:
        time.sleep(POLL_INTERVAL_SECONDS)
        for source, retrieval_id in list(pending.items()):
            try:
                body = _request("GET", f"/retrieval/{retrieval_id}/", deadline)
            except (requests.RequestException, ValueError) as error:
                errors.append(f"{source}: {error}")
                del pending[source]
                continue
            status = body.get("status")
            if status == "completed":
                nodes_by_source[source] = body.get("retrieved_nodes") or []
                del pending[source]
            elif status == "failed":
                errors.append(f"{source}: retrieval failed")
                del pending[source]

    errors += [f"{source}: quá {SEARCH_BUDGET_SECONDS}s" for source in pending]
    return nodes_by_source, errors


def _node_to_result(node: dict, source: str, info: dict) -> dict | None:
    """Đổi một retrieved node thành SearchResult (score gán sau theo rank).

    Response thật có dạng:
        {"id": "0000", "title": "...",
         "relevant_contents": [[{"section_title": ..., "relevant_content": ...}]]}
    """
    passages = [
        passage
        for group in node.get("relevant_contents") or []
        for passage in (group if isinstance(group, list) else [group])
        if isinstance(passage, dict) and (passage.get("relevant_content") or "").strip()
    ]
    if not passages:
        return None

    node_id = str(node.get("id", "0"))
    section = passages[0].get("section_title") or node.get("title") or info["title"]
    return {
        "id": f"pageindex::{source}::{node_id}",
        "content": "\n\n".join(passage["relevant_content"].strip() for passage in passages),
        "score": 0.0,
        "metadata": {
            "source": source,
            "title": info["title"],
            "doc_type": info["doc_type"],
            "url": info["url"],
            "chunk_index": int(node_id) if node_id.isdigit() else 0,
            "section": section,
        },
        "retrieval_method": "pageindex",
    }


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult."""
    if not query or not query.strip() or top_k <= 0:
        return []

    doc_ids = _load_doc_ids()
    if not doc_ids:
        raise RuntimeError(
            "Chưa có document nào trên PageIndex; chạy python -m src.task8_pageindex_vectorless"
        )

    nodes_by_source, errors = _retrieve_all(doc_ids, query)
    if not nodes_by_source:
        raise RuntimeError("PageIndex lỗi ở mọi document: " + "; ".join(errors))

    # Giữ thứ tự document ổn định theo cache để kết quả lặp lại được.
    per_document = [
        [
            result
            for result in (_node_to_result(node, source, doc_ids[source]) for node in nodes_by_source[source])
            if result
        ]
        for source in doc_ids
        if source in nodes_by_source
    ]

    # PageIndex không trả score. Xen kẽ theo rank trong từng document (rank 1 của
    # mọi document trước, rồi rank 2...) và gán score giảm dần theo vị trí.
    merged: list[dict] = []
    for rank in range(max((len(results) for results in per_document), default=0)):
        for results in per_document:
            if rank < len(results):
                merged.append(results[rank])

    merged = merged[:top_k]
    for position, result in enumerate(merged):
        result["score"] = 1.0 / (position + 1)
    return merged


if __name__ == "__main__":
    upload_documents()
    wait_until_ready()

    for result in pageindex_search("What are the phases of the cutover stage?", top_k=3):
        print(f"[{result['score']:.3f}] {result['metadata']['title']} — {result['metadata']['section']}")
        print(f"        {result['content'][:160]}...")
