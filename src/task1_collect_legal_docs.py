"""Register existing PDFs; optionally download missing files from the manifest."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data/landing/legal"
MANIFEST = ROOT / "data/sources.json"


def setup_directory() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def download_documents(download_missing: bool = False) -> None:
    import requests
    records = []
    for item in json.loads(MANIFEST.read_text(encoding="utf-8-sig")):
        if item["doc_type"] != "legal":
            continue
        path = ROOT / item["local_path"]
        if not path.exists():
            if not download_missing:
                raise FileNotFoundError(f"{path}: use --download-missing or copy the PDF manually")
            response = requests.get(item["url"], timeout=(15, 60))
            response.raise_for_status()
            if not response.content.startswith(b"%PDF-"):
                raise ValueError(f"Not a PDF: {item['url']}")
            path.write_bytes(response.content)
        content = path.read_bytes()
        if path.suffix.lower() == ".pdf" and not content.startswith(b"%PDF-"):
            raise ValueError(f"Invalid PDF: {path}")
        records.append({**item, "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)})
    if len(records) < 3:
        raise ValueError("At least three legal documents are required")
    (ROOT / "data/legal_inventory.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Registered {len(records)} legal documents; originals preserved.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download-missing", action="store_true")
    setup_directory()
    download_documents(parser.parse_args().download_missing)
