"""Convert a PDF to Markdown by sending one rendered page at a time to a vision model.

Examples:
    python -m src.aiOCR document.pdf
    python -m src.aiOCR document.pdf --no-merge --output document_pages
"""

import argparse
import base64
import hashlib
import io
import json
import os
import re
import tempfile
from pathlib import Path

import pypdfium2 as pdfium
from dotenv import load_dotenv
from openai import OpenAI


OCR_PROMPT = """Transcribe this document page into Markdown.
Preserve the original language, wording, reading order, headings, lists, links,
tables (as Markdown tables where possible), and footnotes. Include visible text
in figures when legible. Do not summarize, translate, invent missing text, or
repeat content. Mark unreadable text as [illegible]. Return only Markdown, with
no code fence or introductory text."""


def _select_pages(pages: str, page_count: int) -> list[int]:
    """Return selected 1-based page numbers, validating against the PDF length."""
    selection = pages.strip().lower()
    if selection == "all":
        return list(range(1, page_count + 1))
    if not re.fullmatch(r"[1-9]\d*(?:-[1-9]\d*)?", selection):
        raise ValueError("pages must be 'all', a page number, or a range like '1-4'")
    start, _, end = selection.partition("-")
    first = int(start)
    last = int(end) if end else first
    if first > last or last > page_count:
        raise ValueError(f"pages must be in ascending order within 1-{page_count}")
    return list(range(first, last + 1))


def _write_text(path: Path, content: str) -> None:
    """Replace a file only after its complete new content has been written."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix=f".{path.name}.", delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary.write(content)
        temporary_path.replace(path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def pdf_to_markdown(
    pdf_path: str | Path,
    output_path: str | Path | None = None,
    merge: bool = True,
    dpi: int = 150,
    pages: str = "all",
) -> Path | list[Path]:
    """OCR selected PDF pages and save one merged file or separate page files.

    When ``merge`` is true, ``output_path`` is a Markdown filename and defaults
    to ``<pdf name>.md``. Otherwise it is a directory and defaults to
    ``<pdf name>_pages`` next to the PDF. Each successful page is saved there
    immediately, including in merge mode. A rerun reuses saved pages when the
    PDF and OCR settings match. The merged file is updated after each page.
    ``pages`` accepts ``all``, ``4``, or ``1-4``. The returned value contains
    the written path(s).
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.is_file() or pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Not a PDF file: {pdf_path}")
    if dpi <= 0:
        raise ValueError("dpi must be positive")

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL")
    if not api_key or not model:
        raise ValueError("Set OPENAI_API_KEY and OPENAI_MODEL in .env")

    client_args = {"api_key": api_key}
    if base_url := os.getenv("OPENAI_BASE_URL"):
        client_args["base_url"] = base_url
    client = OpenAI(**client_args)

    destination = Path(output_path) if output_path is not None else (
        pdf_path.with_suffix(".md") if merge else pdf_path.with_name(f"{pdf_path.stem}_pages")
    )
    if merge and destination.resolve() == pdf_path.resolve():
        raise ValueError("Output path must differ from the input PDF")
    pdf = pdfium.PdfDocument(str(pdf_path))
    try:
        page_count = len(pdf)
        if page_count == 0:
            raise ValueError(f"PDF has no pages: {pdf_path}")
        selected_pages = _select_pages(pages, page_count)
        page_dir = destination.with_name(f"{destination.stem}_pages") if merge else destination
        page_dir.mkdir(parents=True, exist_ok=True)
        state_path = page_dir / ".ocr-state.json"
        pdf_stat = pdf_path.stat()
        identity = {
            "pdf": str(pdf_path.resolve()),
            "pdf_size": pdf_stat.st_size,
            "pdf_mtime_ns": pdf_stat.st_mtime_ns,
            "page_count": page_count,
            "model": model,
            "base_url": base_url or "",
            "dpi": dpi,
            "prompt_sha256": hashlib.sha256(OCR_PROMPT.encode("utf-8")).hexdigest(),
        }
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            state = {}
        if not isinstance(state, dict):
            state = {}
        completed = set(state.get("completed_pages", [])) if state.get("identity") == identity else set()
        if state.get("identity") != identity:
            _write_text(state_path, json.dumps({"identity": identity, "completed_pages": []}, indent=2) + "\n")

        page_markdown: list[tuple[int, str]] = []

        for page_number in selected_pages:
            page_path = page_dir / f"page-{page_number:04d}.md"
            if page_number in completed and page_path.is_file():
                saved_markdown = page_path.read_text(encoding="utf-8").strip()
                if saved_markdown:
                    page_markdown.append((page_number, saved_markdown))
                    if merge:
                        _write_text(destination, "\n\n".join(text for _, text in page_markdown) + "\n")
                    print(f"Using saved page {page_number}/{page_count}", flush=True)
                    continue

            print(f"OCR page {page_number}/{page_count}...", flush=True)
            page = pdf[page_number - 1]
            try:
                bitmap = page.render(scale=dpi / 72)
                try:
                    png = io.BytesIO()
                    bitmap.to_pil().save(png, format="PNG")
                finally:
                    bitmap.close()
            finally:
                page.close()

            image_url = "data:image/png;base64," + base64.b64encode(png.getvalue()).decode("ascii")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": OCR_PROMPT},
                    {"role": "user", "content": [
                        {"type": "text", "text": f"Transcribe page {page_number} of {page_count}."},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ]},
                ],
            )
            markdown = response.choices[0].message.content
            if not isinstance(markdown, str) or not markdown.strip():
                raise RuntimeError(
                    f"OCR returned no text for page {page_number}; "
                    f"completed pages are saved in {page_dir}"
                )
            markdown = markdown.strip()
            _write_text(page_path, markdown + "\n")
            completed.add(page_number)
            _write_text(state_path, json.dumps({
                "identity": identity,
                "completed_pages": sorted(completed),
            }, indent=2) + "\n")
            page_markdown.append((page_number, markdown))
            if merge:
                _write_text(destination, "\n\n".join(text for _, text in page_markdown) + "\n")
            print(f"Completed page {page_number}/{page_count}", flush=True)
    finally:
        pdf.close()

    if merge:
        return destination

    return [page_dir / f"page-{page_number:04d}.md" for page_number, _ in page_markdown]


def main() -> None:
    parser = argparse.ArgumentParser(description="OCR a PDF to Markdown with an OpenAI vision model")
    parser.add_argument("pdf", type=Path, help="Input PDF file")
    parser.add_argument("--output", type=Path, help="Output Markdown file, or directory with --no-merge")
    parser.add_argument("--merge", action=argparse.BooleanOptionalAction, default=True,
                        help="Merge pages into one Markdown file (default: true)")
    parser.add_argument("--dpi", type=int, default=150, help="Page rendering resolution (default: 150)")
    parser.add_argument("--pages", default="all", help="Pages to OCR: all, 4, or 1-4 (default: all)")
    args = parser.parse_args()

    result = pdf_to_markdown(args.pdf, args.output, merge=args.merge, dpi=args.dpi, pages=args.pages)
    if isinstance(result, list):
        for path in result:
            print(path)
    else:
        print(result)


if __name__ == "__main__":
    main()
