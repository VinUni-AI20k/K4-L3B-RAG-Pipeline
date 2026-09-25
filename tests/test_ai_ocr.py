"""Exercise page rendering and output layout without making API requests."""

import base64
import io
from types import SimpleNamespace

import pytest
from fpdf import FPDF
from PIL import Image

from src import aiOCR


def test_pdf_to_markdown_renders_each_page_and_merges_by_default(tmp_path, monkeypatch, capsys):
    pdf = FPDF()
    for number in (1, 2):
        pdf.add_page()
        pdf.set_font("Helvetica", size=14)
        pdf.cell(text=f"Page {number}")
    source = tmp_path / "source.pdf"
    pdf.output(source)

    requests = []

    class FakeCompletions:
        def create(self, **kwargs):
            requests.append(kwargs)
            image_url = kwargs["messages"][1]["content"][1]["image_url"]["url"]
            assert image_url.startswith("data:image/png;base64,")
            with Image.open(io.BytesIO(base64.b64decode(image_url.split(",", 1)[1]))) as image:
                assert image.format == "PNG"
                assert image.width > 100
            return SimpleNamespace(choices=[SimpleNamespace(
                message=SimpleNamespace(content=f"# Page {len(requests)}")
            )])

    clients = []

    def fake_openai(**kwargs):
        clients.append(kwargs)
        return SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions()))

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.test/v1")
    monkeypatch.setenv("OPENAI_MODEL", "test-vision")
    monkeypatch.setattr(aiOCR, "OpenAI", fake_openai)

    merged = aiOCR.pdf_to_markdown(source)
    assert merged == source.with_suffix(".md")
    assert merged.read_text(encoding="utf-8") == "# Page 1\n\n# Page 2\n"
    assert clients == [{"api_key": "test-key", "base_url": "https://example.test/v1"}]
    assert len(requests) == 2
    assert all(request["model"] == "test-vision" for request in requests)
    assert capsys.readouterr().out.splitlines() == [
        "OCR page 1/2...", "Completed page 1/2",
        "OCR page 2/2...", "Completed page 2/2",
    ]

    requests.clear()
    pages = aiOCR.pdf_to_markdown(source, merge=False)
    assert [path.name for path in pages] == ["page-0001.md", "page-0002.md"]
    assert [path.read_text(encoding="utf-8") for path in pages] == ["# Page 1\n", "# Page 2\n"]
    assert requests == []


def test_page_selection_uses_original_page_numbers(tmp_path, monkeypatch, capsys):
    pdf = FPDF()
    for number in range(1, 5):
        pdf.add_page()
        pdf.set_font("Helvetica", size=14)
        pdf.cell(text=f"Page {number}")
    source = tmp_path / "four-pages.pdf"
    pdf.output(source)

    requested_pages = []

    class FakeCompletions:
        def create(self, **kwargs):
            prompt = kwargs["messages"][1]["content"][0]["text"]
            page_number = int(prompt.split()[2])
            requested_pages.append(page_number)
            return SimpleNamespace(choices=[SimpleNamespace(
                message=SimpleNamespace(content=f"# Page {page_number}")
            )])

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "test-vision")
    monkeypatch.setattr(aiOCR, "OpenAI", lambda **kwargs: SimpleNamespace(
        chat=SimpleNamespace(completions=FakeCompletions())
    ))

    merged = aiOCR.pdf_to_markdown(source, pages="2-3")
    assert merged.read_text(encoding="utf-8") == "# Page 2\n\n# Page 3\n"
    assert requested_pages == [2, 3]
    assert capsys.readouterr().out.splitlines() == [
        "OCR page 2/4...", "Completed page 2/4",
        "OCR page 3/4...", "Completed page 3/4",
    ]

    separate = aiOCR.pdf_to_markdown(source, pages="4", merge=False)
    assert [path.name for path in separate] == ["page-0004.md"]
    assert separate[0].read_text(encoding="utf-8") == "# Page 4\n"
    assert requested_pages == [2, 3, 4]

    for invalid in ("0", "3-2", "4-5", "1,3", "something"):
        with pytest.raises(ValueError, match="pages must"):
            aiOCR.pdf_to_markdown(source, pages=invalid)
    assert requested_pages == [2, 3, 4]


def test_failed_page_preserves_progress_and_rerun_resumes(tmp_path, monkeypatch, capsys):
    pdf = FPDF()
    for number in range(1, 4):
        pdf.add_page()
        pdf.set_font("Helvetica", size=14)
        pdf.cell(text=f"Page {number}")
    source = tmp_path / "interrupted.pdf"
    pdf.output(source)

    requested_pages = []
    fail_page_three = True

    class FakeCompletions:
        def create(self, **kwargs):
            nonlocal fail_page_three
            prompt = kwargs["messages"][1]["content"][0]["text"]
            page_number = int(prompt.split()[2])
            requested_pages.append(page_number)
            content = None if page_number == 3 and fail_page_three else f"# Page {page_number}"
            return SimpleNamespace(choices=[SimpleNamespace(
                message=SimpleNamespace(content=content)
            )])

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "test-vision")
    monkeypatch.setattr(aiOCR, "OpenAI", lambda **kwargs: SimpleNamespace(
        chat=SimpleNamespace(completions=FakeCompletions())
    ))

    with pytest.raises(RuntimeError, match="page 3"):
        aiOCR.pdf_to_markdown(source)
    assert source.with_suffix(".md").read_text(encoding="utf-8") == "# Page 1\n\n# Page 2\n"
    page_dir = tmp_path / "interrupted_pages"
    assert (page_dir / "page-0001.md").read_text(encoding="utf-8") == "# Page 1\n"
    assert (page_dir / "page-0002.md").read_text(encoding="utf-8") == "# Page 2\n"
    assert not (page_dir / "page-0003.md").exists()
    assert requested_pages == [1, 2, 3]

    fail_page_three = False
    merged = aiOCR.pdf_to_markdown(source)
    assert merged.read_text(encoding="utf-8") == "# Page 1\n\n# Page 2\n\n# Page 3\n"
    assert requested_pages == [1, 2, 3, 3]
    assert "Using saved page 1/3" in capsys.readouterr().out
