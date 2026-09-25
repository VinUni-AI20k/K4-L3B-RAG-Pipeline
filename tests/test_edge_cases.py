import asyncio
import io
import zipfile

import pytest


DOCX_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
MC_NS = "http://schemas.openxmlformats.org/markup-compatibility/2006"


def _make_docx(document_xml: str, entry_name: str = "word/document.xml") -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(entry_name, document_xml)
    return buffer.getvalue()


def test_docx_to_text_reads_backslash_zip_entry(tmp_path):
    from src.task3_convert_markdown import _docx_to_text

    xml = f"""<w:document xmlns:w="{DOCX_NS}">
      <w:body><w:p><w:r><w:t>Hello backslash</w:t></w:r></w:p></w:body>
    </w:document>"""
    path = tmp_path / "sample.docx"
    path.write_bytes(_make_docx(xml, entry_name="word\\document.xml"))

    assert _docx_to_text(path).strip() == "Hello backslash"


def test_docx_to_text_does_not_duplicate_textbox_alternate_content(tmp_path):
    """AlternateContent stores a modern w:drawing textbox in mc:Choice and a
    legacy VML fallback in mc:Fallback, both wrapping an equivalent
    w:txbxContent paragraph. Extraction must keep exactly one copy, and must
    not also swallow the nested textbox text into the host paragraph's own
    text (which previously produced up to 5x duplication).
    """
    from src.task3_convert_markdown import _docx_to_text

    xml = f"""<w:document xmlns:w="{DOCX_NS}" xmlns:mc="{MC_NS}">
      <w:body>
        <w:p>
          <w:r><w:t>Host paragraph text</w:t></w:r>
          <w:r>
            <mc:AlternateContent>
              <mc:Choice Requires="wps">
                <w:drawing>
                  <wps:txbxContent xmlns:wps="urn:fake">
                    <w:p><w:r><w:t>Textbox line</w:t></w:r></w:p>
                  </wps:txbxContent>
                </w:drawing>
              </mc:Choice>
              <mc:Fallback>
                <w:pict>
                  <v:textbox xmlns:v="urn:fake2">
                    <w:txbxContent>
                      <w:p><w:r><w:t>Textbox line</w:t></w:r></w:p>
                    </w:txbxContent>
                  </v:textbox>
                </w:pict>
              </mc:Fallback>
            </mc:AlternateContent>
          </w:r>
        </w:p>
      </w:body>
    </w:document>"""
    path = tmp_path / "textbox.docx"
    path.write_bytes(_make_docx(xml))

    text = _docx_to_text(path)
    assert text.count("Textbox line") == 1
    assert "Host paragraph text" in text
    # The host paragraph's own text must not have swallowed the textbox's.
    host_line = next(line for line in text.split("\n\n") if "Host paragraph" in line)
    assert "Textbox" not in host_line


def test_docx_to_text_converts_tabs_and_breaks_to_whitespace(tmp_path):
    from src.task3_convert_markdown import _docx_to_text

    xml = f"""<w:document xmlns:w="{DOCX_NS}">
      <w:body>
        <w:p>
          <w:r><w:t>Truoc</w:t><w:tab/><w:t>Sau</w:t><w:br/><w:t>Dong moi</w:t></w:r>
        </w:p>
      </w:body>
    </w:document>"""
    path = tmp_path / "tabs.docx"
    path.write_bytes(_make_docx(xml))

    text = _docx_to_text(path)
    assert "Truoc\tSau" in text
    assert "Sau\nDong moi" in text
    assert "TruocSau" not in text


def test_should_convert_reconverts_when_source_is_newer_than_target(tmp_path):
    import os
    import time

    from src.task3_convert_markdown import _should_convert

    source = tmp_path / "source.docx"
    target = tmp_path / "target.md"
    source.write_bytes(b"v1")
    target.write_text("x" * 300)

    # Target already exists and is non-trivial in size: previously this
    # alone caused a permanent skip, even after the source was re-crawled
    # or re-downloaded with new content.
    assert _should_convert(source, target) is False

    time.sleep(0.01)
    os.utime(source, None)  # bump source mtime past target's
    assert _should_convert(source, target) is True


def test_is_valid_docx_rejects_non_zip_content(tmp_path):
    from src.task1_collect_legal_docs import _is_valid_docx

    garbage = tmp_path / "garbage.docx"
    garbage.write_bytes(b"<html>expired token</html>")
    assert _is_valid_docx(garbage) is False

    real = tmp_path / "real.docx"
    real.write_bytes(_make_docx(f'<w:document xmlns:w="{DOCX_NS}"/>'))
    assert _is_valid_docx(real) is True

    missing = tmp_path / "missing.docx"
    assert _is_valid_docx(missing) is False


def test_download_documents_does_not_keep_a_bad_download(monkeypatch, tmp_path):
    """A download that returns HTML (e.g. an expired signed URL) or a
    truncated file must not be accepted as a valid landed document, and
    must not leave a partial file behind that a future run's skip-if-exists
    check would treat as already downloaded.
    """
    import subprocess

    import src.task1_collect_legal_docs as task1

    monkeypatch.setattr(task1, "DATA_DIR", tmp_path)
    monkeypatch.setattr(task1, "SOURCES", {"bad.docx": "https://example.com/bad.docx"})

    def fake_run(cmd, check):
        # Simulate curl "succeeding" (exit 0) while the server actually
        # returned an HTML error page instead of the real document.
        out_path = cmd[cmd.index("-o") + 1]
        with open(out_path, "wb") as f:
            f.write(b"<html>token expired</html>")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(ValueError):
        task1.download_documents()

    assert not (tmp_path / "bad.docx").exists()
    assert not (tmp_path / "bad.docx.part").exists()


def test_crawl_article_raises_when_crawl_reports_failure(monkeypatch):
    import crawl4ai

    import src.task2_crawl_news as task2

    class FakeResult:
        success = False
        status_code = 403
        error_message = "blocked"
        markdown = "Forbidden - please enable JavaScript"
        metadata = {"title": "Forbidden"}

    class FakeCrawler:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def arun(self, url):
            return FakeResult()

    # crawl_article does `from crawl4ai import AsyncWebCrawler` inside the
    # function body, so patching the module attribute is picked up at call
    # time without needing to patch the task2 module itself.
    monkeypatch.setattr(crawl4ai, "AsyncWebCrawler", FakeCrawler)

    with pytest.raises(ValueError):
        asyncio.run(task2.crawl_article("https://example.com/blocked"))
