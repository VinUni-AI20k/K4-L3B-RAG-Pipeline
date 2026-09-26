"""
Task 1 — Thu thập tài liệu chính sách/quy định.

Hướng dẫn:
    1. Chọn chủ đề của nhóm.
    2. Tìm tối thiểu 3 tài liệu PDF/DOCX từ nguồn công khai.
    3. Lưu file gốc vào data/landing/legal/.
    4. Đặt tên không dấu và thể hiện đúng nội dung.

Ví dụ tài liệu: học phí, học bổng, ký túc xá, quy trình đăng ký.
Nếu website chặn crawler, hãy chọn nguồn công khai khác; không vượt WAF.
"""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"
SOURCES = (
    ("09.signed.pdf", "luat_du_lich_09_2017_qh14.pdf", "190290", "2017/07", "Luật Du lịch 09/2017/QH14"),
    ("168.signed.pdf", "nghi_dinh_168_2017_nd_cp_huong_dan_luat_du_lich.pdf", "193059", "2018/03", "Nghị định 168/2017/NĐ-CP hướng dẫn Luật Du lịch"),
    ("109.signed.pdf", "nghi_dinh_109_2017_nd_cp_bao_ve_quan_ly_di_san.pdf", "191224", "2017/09", "Nghị định 109/2017/NĐ-CP bảo vệ và quản lý di sản thế giới"),
)


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def download_documents(local_dirs: tuple[Path, ...] = ()) -> None:
    """Thu thập bản gốc; ưu tiên file có sẵn, tải nguồn công khai nếu thiếu.

    Chỉ dùng thư viện chuẩn, không phụ thuộc môi trường RAG đang cài đặt.
    Không OCR ở bước landing.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = DATA_DIR / "sources.json"
    previous = {}
    if manifest_path.exists():
        previous = {
            item["filename"]: item
            for item in json.loads(manifest_path.read_text(encoding="utf-8"))["documents"]
        }
    documents = []
    for original, filename, docid, folder, title in SOURCES:
        target = DATA_DIR / filename
        url = f"https://datafiles.chinhphu.vn/cpp/files/vbpq/{folder}/{original}"
        old = previous.get(filename, {})
        if target.exists():
            content = target.read_bytes()
            acquired_from = old.get("acquired_from", "existing landing file")
        else:
            local = next((d / original for d in local_dirs if (d / original).is_file()), None)
            if local is not None:
                content = local.read_bytes()
                acquired_from = str(local.resolve())
            else:
                # HTTP failures propagate; do not bypass access controls/WAF.
                with urlopen(url, timeout=60) as response:
                    content = response.read()
                acquired_from = url
        signature = b"%PDF-"
        if not content.startswith(signature):
            raise ValueError(f"Invalid document (possibly an HTML error page): {filename}")
        digest = hashlib.sha256(content).hexdigest()
        if old.get("sha256") and old["sha256"] != digest:
            raise ValueError(f"Checksum changed; inspect before collecting again: {filename}")
        if not target.exists():
            temporary = target.with_suffix(target.suffix + ".part")
            temporary.write_bytes(content)
            temporary.replace(target)
        documents.append({
            "filename": filename, "original_filename": original, "title": title,
            "source_url": f"https://vanban.chinhphu.vn/default.aspx?docid={docid}&pageid=27160",
            "download_url": url, "acquired_from": acquired_from,
            "collected_at": old.get("collected_at", datetime.now(timezone.utc).isoformat()),
            "sha256": digest, "size_bytes": len(content),
            "counts_toward_pdf_docx_minimum": target.suffix == ".pdf",
        })
        print(f"Ready: {filename} ({len(content)} bytes)")
    manifest = {"topic": "Du lịch và bảo tồn di sản văn hóa Việt Nam", "documents": documents}
    temporary = manifest_path.with_suffix(".json.part")
    temporary.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(manifest_path)
    print("Collected 3 original PDFs.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local-dir", type=Path, action="append", default=[],
                        help="Folder containing originals; repeat for multiple folders.")
    args = parser.parse_args()
    setup_directory()
    download_documents(tuple(args.local_dir))
