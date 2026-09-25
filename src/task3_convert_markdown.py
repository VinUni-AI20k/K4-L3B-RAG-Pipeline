"""Task 3 — Chuyển tài liệu gốc sang Markdown."""

import json
import re
from pathlib import Path

LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def convert_legal_docs() -> None:
    from markitdown import MarkItDown

    source_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    converter = MarkItDown()

    for path in sorted(source_dir.iterdir()):
        if path.suffix.lower() not in {".pdf", ".doc", ".docx"}:
            continue

        content = converter.convert(str(path)).text_content.strip()
        if not content:
            raise ValueError(f"Tài liệu không trích xuất được nội dung: {path.name}")

        output = output_dir / f"{path.stem}.md"
        output.write_text(
            f"# {path.stem}\n\n"
            f"**Original file:** {path.name}\n\n"
            f"{content}\n",
            encoding="utf-8",
        )
        print(f"Saved: {output}")


def convert_news_articles() -> None:
    source_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    for path in sorted(source_dir.glob("*.json")):
        article = json.loads(path.read_text(encoding="utf-8"))

        required = ("url", "date_crawled", "content_markdown")
        if not all(str(article.get(key, "")).strip() for key in required):
            raise ValueError(f"Thiếu dữ liệu trong {path.name}")

        raw = article["content_markdown"]

        # Tìm tiêu đề bài viết ngay trước dòng "Cập nhật:".
        published = re.search(r"(?m)^Cập nhật:", raw)
        headings = list(re.finditer(r"(?m)^# (.+)$", raw))

        if not published:
            raise ValueError(f"Không tìm thấy dòng ngày cập nhật: {path.name}")

        before_date = [h for h in headings if h.start() < published.start()]
        if not before_date:
            raise ValueError(f"Không tìm thấy tiêu đề bài viết: {path.name}")

        heading = before_date[-1]
        body = raw[heading.start():]

        # Cắt phần đánh giá, bài liên quan và chân trang.
        ending = re.search(
            r"(?m)^(?:Đánh giá bài viết|Quét mã QR|Xem tiếp|TRANG THÔNG TIN)",
            body,
        )
        if ending:
            body = body[:ending.start()]

        # Bỏ ảnh, nút chia sẻ và thông báo của trình duyệt.
        lines = []
        for line in body.splitlines():
            stripped = line.strip()

            if stripped in {
                "* email",
                "Your browser does not support the audio element.",
            }:
                continue

            if stripped.startswith("![](") or stripped.startswith("[![]("):
                continue

            if any(
                text in stripped.lower()
                for text in (
                    "facebook.com/sharer",
                    "twitter.com/intent/tweet",
                    "instagram.com",
                )
            ):
                continue

            lines.append(line)

        content = "\n".join(lines).strip()
        if len(content) < 200:
            raise ValueError(f"Bài viết sau khi lọc quá ngắn: {path.name}")

        header = (
            f"**Source:** {article['url']}\n\n"
            f"**Crawled:** {article['date_crawled']}\n\n"
            f"---\n\n"
        )

        output = output_dir / f"{path.stem}.md"
        output.write_text(
            header + content + "\n",
            encoding="utf-8",
        )
        print(f"Saved: {output}")


def convert_all() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    convert_legal_docs()
    convert_news_articles()
    print(f"Hoàn tất chuẩn hóa: {OUTPUT_DIR}")


if __name__ == "__main__":
    convert_all()