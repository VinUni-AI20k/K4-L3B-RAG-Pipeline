"""Thu thập văn bản chính thức cho chatbot Du lịch Việt Nam."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data" / "landing" / "legal"
MANIFEST_PATH = DATA_DIR / "legal_sources.json"

# URL tệp đều thuộc datafiles.chinhphu.vn và được liên kết từ trang văn bản
# tương ứng trên vanban.chinhphu.vn/chinhphu.vn.
DOCUMENT_SOURCES = [
    {
        "filename": "luat-du-lich-09-2017-qh14.pdf",
        "title": "Luật Du lịch",
        "document_number": "09/2017/QH14",
        "issuer": "Quốc hội",
        "issued_date": "2017-06-19",
        "effective_date": "2018-01-01",
        "status": "Còn hiệu lực",
        "version_note": "Bản gốc; trạng thái được kiểm tra trên CSDL quốc gia về VBPL.",
        "source_page": "https://vanban.chinhphu.vn/default.aspx?docid=190290&pageid=27160",
        "full_text_url": "https://vbpl.moj.gov.vn/TW/Pages/vbpq-toanvan.aspx?ItemID=129350",
        "download_url": "https://congbaocdn.chinhphu.vn/CongBaoCP/CongBao/2017/7/24237/18441-1-515-516.pdf",
    },
    {
        "filename": "nghi-dinh-168-2017-nd-cp.pdf",
        "title": "Quy định chi tiết một số điều của Luật Du lịch",
        "document_number": "168/2017/NĐ-CP",
        "issuer": "Chính phủ",
        "issued_date": "2017-12-31",
        "effective_date": "2018-01-01",
        "status": "Còn hiệu lực",
        "version_note": "Bản gốc; khi áp dụng cần đối chiếu các văn bản sửa đổi liên quan.",
        "source_page": "https://vanban.chinhphu.vn/?docid=193059&pageid=27160",
        "full_text_url": "https://vbpl.moj.gov.vn/TW/Pages/vbpq-toanvan.aspx?ItemID=130762",
        "download_url": "https://congbaocdn.chinhphu.vn/CongBaoCP/VanBan/2017/12/26028/21615-1-2018429-430168-2017-nd-cp.pdf",
    },
    {
        "filename": "nghi-dinh-45-2019-nd-cp.pdf",
        "title": "Quy định xử phạt vi phạm hành chính trong lĩnh vực du lịch",
        "document_number": "45/2019/NĐ-CP",
        "issuer": "Chính phủ",
        "issued_date": "2019-05-21",
        "effective_date": "2019-08-01",
        "status": "Hết hiệu lực một phần",
        "version_note": "Đã được sửa đổi; phải đọc cùng Nghị định 129/2021/NĐ-CP và 348/2025/NĐ-CP.",
        "source_page": "https://chinhphu.vn/default.aspx?docid=197075&pageid=27160",
        "full_text_url": "https://vbpl.moj.gov.vn/TW/Pages/vbpq-toanvan.aspx?ItemID=135401",
        "download_url": "https://congbaocdn.chinhphu.vn/CongBaoCP/VanBan/2019/5/29007/26837-1-2019459-46045-2019-nd-cp.pdf",
    },
    {
        "filename": "nghi-dinh-348-2025-nd-cp.pdf",
        "title": "Sửa đổi Nghị định 45/2019/NĐ-CP về xử phạt trong lĩnh vực du lịch",
        "document_number": "348/2025/NĐ-CP",
        "issuer": "Chính phủ",
        "issued_date": "2025-12-30",
        "effective_date": "2026-02-15",
        "status": "Còn hiệu lực",
        "version_note": "Văn bản sửa đổi mới được thu thập để cập nhật Nghị định 45/2019/NĐ-CP.",
        "source_page": "https://vanban.chinhphu.vn/?docid=216361&pageid=27160",
        "full_text_url": "https://vbpl.moj.gov.vn/TW/Pages/vbpq-toanvan.aspx?ItemID=185625",
        "download_url": "https://congbao.cdnchinhphu.vn/180507251028987904/2026/1/15/348signed-1768467126187726941896.pdf",
    },
]


def setup_directory() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _download(url: str, destination: Path) -> None:
    request = Request(url, headers={"User-Agent": "K4-RAG-Lab/1.0"})
    with urlopen(request, timeout=60) as response:
        content = response.read()
    if len(content) <= 1024 or not content.startswith(b"%PDF"):
        raise ValueError(f"Tệp tải về không phải PDF hợp lệ: {url}")
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_bytes(content)
    temporary.replace(destination)


def download_documents() -> None:
    """Tải văn bản và ghi manifest để truy vết nguồn/phiên bản."""
    setup_directory()
    collected_at = datetime.now(timezone.utc).isoformat()
    previous_items = []
    if MANIFEST_PATH.exists():
        previous_items = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    previous_by_filename = {item["filename"]: item for item in previous_items}
    manifest = []
    for source in DOCUMENT_SOURCES:
        destination = DATA_DIR / source["filename"]
        previous = previous_by_filename.get(source["filename"], {})
        source_changed = previous.get("download_url") != source["download_url"]
        if not destination.exists() or destination.stat().st_size <= 1024 or source_changed:
            _download(source["download_url"], destination)
            print(f"Downloaded: {destination}")
        else:
            print(f"Verified existing: {destination}")
        manifest.append({**source, "collected_at": collected_at, "size_bytes": destination.stat().st_size})

    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Saved manifest: {MANIFEST_PATH}")


if __name__ == "__main__":
    download_documents()
