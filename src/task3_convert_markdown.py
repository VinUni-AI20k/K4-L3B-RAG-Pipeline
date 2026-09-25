"""
Task 3 — Chuẩn hóa dữ liệu sang Markdown.

Mỗi file Markdown đầu ra có header truy vết về nguồn:
    # <title>
    **Source:** <URL công khai>
    **Landing file:** <legal|news>/<tên file gốc>
    (news có thêm **Crawled:**)
    ---
    <nội dung>

Header giữ cùng format cho legal và news để Task 4 đọc metadata thống nhất.
Tên file output = stem của file landing, nên chạy lại chỉ ghi đè, không tạo
bản sao; Markdown không còn file landing tương ứng sẽ bị xoá để output luôn
khớp landing.

Chạy:
    python -m src.task3_convert_markdown
"""

import json
import re
from collections import Counter
from pathlib import Path

from markitdown import MarkItDown

from src.task1_collect_legal_docs import SOURCES as LEGAL_SOURCES


LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"

LEGAL_EXTENSIONS = {".pdf", ".doc", ".docx"}

# Ngưỡng acceptance test (tests/test_acceptance.py) là 200 ký tự.
MIN_CONTENT_CHARS = 200


def _header(title: str, source: str, landing_file: str, crawled: str | None = None) -> str:
    lines = [
        f"# {title}",
        "",
        f"**Source:** {source}",
        "",
        f"**Landing file:** {landing_file}",
        "",
    ]
    if crawled:
        lines += [f"**Crawled:** {crawled}", ""]
    lines += ["---", "", ""]
    return "\n".join(lines)


def _title_from_filename(stem: str) -> str:
    """aws-large-migration-foundation-playbook -> AWS Large Migration Foundation Playbook."""
    words = stem.replace("_", "-").split("-")
    return " ".join(word.upper() if word.lower() == "aws" else word.capitalize() for word in words)


# Dòng mục lục của PDF: "Introduction ........ 1".
TOC_LINE = re.compile(r"\.{5,}\s*\d+\s*$")

# Header chạy của PDF chỉ bị coi là nhiễu khi lặp ít nhất ngần này lần,
# để không xoá nhầm dòng nội dung trùng tiêu đề.
MIN_RUNNING_HEADER_REPEATS = 5


def _clean_pdf_text(content: str) -> tuple[str, str | None]:
    """Bỏ mục lục và header lặp mỗi trang; trả về (nội dung, tiêu đề PDF).

    Tiêu đề là dòng không rỗng đầu tiên. Header chạy là dòng kết thúc bằng
    tiêu đề đó và lặp nhiều lần, ví dụ
    "AWS Prescriptive Guidance Migration playbook for AWS large migrations".
    Không xoá mọi dòng lặp vì có dòng lặp là nội dung thật
    ("This task consists of the following steps:").
    """
    lines = content.splitlines()
    title = next((line.strip() for line in lines if line.strip()), None)
    if not title:
        return content, None

    counts = Counter(line.strip() for line in lines)
    running_headers = {
        line for line, count in counts.items()
        if count >= MIN_RUNNING_HEADER_REPEATS and line != title and line.endswith(title)
    }

    kept = [
        line for line in lines
        if line.strip() not in running_headers and not TOC_LINE.search(line)
    ]
    cleaned = re.sub(r"\n{3,}", "\n\n", "\n".join(kept)).strip()
    return cleaned, title


def _write_outputs(output_dir: Path, outputs: dict[str, str]) -> None:
    """Ghi các file Markdown và xoá Markdown mồ côi trong output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)

    for name, text in outputs.items():
        (output_dir / name).write_text(text, encoding="utf-8")

    for stale in output_dir.glob("*.md"):
        if stale.name not in outputs:
            stale.unlink()
            print(f"Removed stale: {stale.relative_to(OUTPUT_DIR)}")


def convert_legal_docs() -> None:
    """Convert PDF/DOC/DOCX trong landing/legal sang standardized/legal."""
    legal_dir = LANDING_DIR / "legal"
    converter = MarkItDown()
    outputs: dict[str, str] = {}

    for path in sorted(legal_dir.iterdir()):
        if path.name.startswith(".") or path.suffix.lower() not in LEGAL_EXTENSIONS:
            continue

        try:
            content = converter.convert(str(path)).text_content.strip()
        except Exception as error:
            print(f"Failed: legal/{path.name} — {error}")
            continue

        pdf_title = None
        if path.suffix.lower() == ".pdf":
            content, pdf_title = _clean_pdf_text(content)

        if len(content) < MIN_CONTENT_CHARS:
            print(
                f"Failed: legal/{path.name} — chỉ {len(content)} ký tự, "
                "có thể là PDF scan không có lớp text"
            )
            continue

        header = _header(
            title=pdf_title or _title_from_filename(path.stem),
            source=LEGAL_SOURCES.get(path.name, "unknown"),
            landing_file=f"legal/{path.name}",
        )
        outputs[f"{path.stem}.md"] = header + content + "\n"
        print(f"Converted: legal/{path.name} — {len(content):,} chars")

    _write_outputs(OUTPUT_DIR / "legal", outputs)


def convert_news_articles() -> None:
    """Convert JSON trong landing/news sang standardized/news."""
    news_dir = LANDING_DIR / "news"
    outputs: dict[str, str] = {}

    for path in sorted(news_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            content = data["content_markdown"].strip()
            header = _header(
                title=data["title"].strip(),
                source=data["url"].strip(),
                landing_file=f"news/{path.name}",
                crawled=data["date_crawled"],
            )
        except (json.JSONDecodeError, KeyError, AttributeError) as error:
            print(f"Failed: news/{path.name} — JSON thiếu hoặc sai field: {error}")
            continue

        if len(content) < MIN_CONTENT_CHARS:
            print(f"Failed: news/{path.name} — chỉ {len(content)} ký tự")
            continue

        outputs[f"{path.stem}.md"] = header + content + "\n"
        print(f"Converted: news/{path.name} — {len(content):,} chars")

    _write_outputs(OUTPUT_DIR / "news", outputs)


def convert_all() -> None:
    """Convert toàn bộ dữ liệu landing."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"Saved Markdown to: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()
