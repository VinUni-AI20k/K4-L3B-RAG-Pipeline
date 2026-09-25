import json
from pathlib import Path
from types import SimpleNamespace
import sys

import pytest

from src import task3_convert_markdown as task3


@pytest.fixture
def corpus(tmp_path, monkeypatch):
    landing = tmp_path / "landing"
    for kind in ("legal", "news"):
        (landing / kind).mkdir(parents=True)
    monkeypatch.setattr(task3, "LANDING_DIR", landing)
    monkeypatch.setattr(task3, "OUTPUT_DIR", tmp_path / "standardized")
    return landing


def write_article(corpus, content, **overrides):
    data = dict(title='Tướng: "A"', url="https://example.org/wiki/A", date_crawled="2026-09-25", content_markdown=content)
    data.update(overrides)
    path = corpus / "news" / "article_01.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_html_preserves_sources_tables_and_rerun_is_unchanged(corpus):
    (corpus / "legal" / "policy.html").write_text('<html><h1>Quy định</h1><nav>MENU</nav><article><h2>Xử phạt</h2><table><tr><td>Hành vi</td><td>Khóa</td></tr><tr><td>Hack</td><td>30 ngày</td></tr></table><a href="/details">Chi tiết</a><script>NOISE</script></article><footer>FOOTER</footer></html>', encoding="utf-8")
    (corpus / "legal" / "sources.json").write_text(json.dumps({"policy.html": {"url": "https://example.org/policy", "date_crawled": "2026-09-25"}}))
    task3.convert_all()
    path = task3.OUTPUT_DIR / "legal" / "policy.md"
    before = path.read_bytes(), path.stat().st_mtime_ns
    text = path.read_text()
    assert all(noise not in text for noise in ("MENU", "FOOTER", "NOISE"))
    assert "| Hack | 30 ngày |" in text
    assert "https://example.org/details" in text
    assert 'source: "legal/policy.html"' in text
    task3.convert_all()
    assert before == (path.read_bytes(), path.stat().st_mtime_ns)
    assert len(list(task3.OUTPUT_DIR.rglob("*.md"))) == 1


def test_metadata_roundtrip_and_changed_source_updates_existing_file(corpus):
    source = write_article(corpus, "Nội dung ban đầu")
    task3.convert_news_articles()
    target = task3.OUTPUT_DIR / "news" / "article_01.md"
    header = target.read_text().split("---\n")[1]
    metadata = {k: json.loads(v) for k, v in (line.split(": ", 1) for line in header.splitlines())}
    assert metadata["title"] == 'Tướng: "A"'
    assert metadata["id"] == "news/article_01.md"
    write_article(corpus, "Nội dung cập nhật", title="Tướng khác")
    task3.convert_news_articles()
    assert "Nội dung ban đầu" not in target.read_text()
    assert "# Tướng khác" in target.read_text()
    assert source.exists()
    assert len(list(task3.OUTPUT_DIR.rglob("*.md"))) == 1


@pytest.mark.parametrize("content", ["", " \n ", "Stub\n\n*This article is a [stub](https://example.org).*", "## Heading rỗng"])
def test_empty_content_rejected_without_output(corpus, content):
    write_article(corpus, content)
    with pytest.raises(ValueError):
        task3.convert_news_articles()
    assert not list(task3.OUTPUT_DIR.rglob("*.md"))


@pytest.mark.parametrize("key", ["title", "url", "date_crawled", "content_markdown"])
def test_invalid_metadata_does_not_overwrite_previous_output(corpus, key):
    write_article(corpus, "Nội dung hợp lệ")
    task3.convert_news_articles()
    target = task3.OUTPUT_DIR / "news" / "article_01.md"
    before = target.read_bytes()
    write_article(corpus, "Mới", **{key: None})
    with pytest.raises(ValueError, match=key):
        task3.convert_news_articles()
    assert target.read_bytes() == before


def test_cleaning_retains_nested_gems_and_nonempty_sections():
    text = '''## Hướng dẫn

### [Phù hiệu](/wiki/Phu_hieu)

Có thể dùng nhánh phụ 2.

### [Bảng ngọc](/wiki/Ngoc)

### [Phép bổ trợ](/wiki/Phep)

## Trang phục

### Thiết kế cũ

## Bảng ngọc

### Bộ ngọc 1

- **Ngọc đỏ:** Đỏ III TLCM
  - Số lượng: 10x TLCM

### Bộ ngọc 2

- **Ngọc lục:** Lục III GHC
  - Số lượng: 10x GHC
'''
    cleaned = task3.clean_markdown(text, "https://example.org/a")
    assert "### [Phù hiệu](https://example.org/wiki/Phu_hieu)" in cleaned
    assert "Có thể dùng nhánh phụ 2." in cleaned
    assert "### [Bảng ngọc]" not in cleaned
    assert "Trang phục" not in cleaned and "Thiết kế cũ" not in cleaned
    assert "### Bộ ngọc 1" in cleaned and "### Bộ ngọc 2" in cleaned
    assert "  - Số lượng: 10x GHC" in cleaned
    assert task3.clean_markdown(cleaned, "https://example.org/a") == cleaned


def test_noise_removal_retains_real_tables_and_citations():
    text = '''Stub

*This article is a [stub](/stub).* 

## Xem thêm

|  |
| --- |
| **[Tướng](/vi/wiki/Th%E1%BB%83_lo%E1%BA%A1i:Tướng "Thể loại:Tướng")** | |
|  | |

1. [↑](#cite_ref-1) [Nguồn](https://example.org)

## Kỹ năng

| Chiêu | Sát thương |
| --- | --- |
| A | 200 |
'''
    cleaned = task3.clean_markdown(text)
    assert "stub" not in cleaned.lower()
    assert "Thể loại:Tướng" not in cleaned
    assert "[↑](#cite_ref-1)" in cleaned
    assert "| A | 200 |" in cleaned


def test_fenced_code_and_markdown_hard_breaks_are_preserved():
    code = '```python\n# heading inside code\n\n\n  x = 2  \n```'
    cleaned = task3.clean_markdown("Dòng 1  \nDòng 2\n\n" + code)
    assert code in cleaned
    assert "Dòng 1  \nDòng 2" in cleaned


def test_duplicate_stems_rejected_before_writes(corpus):
    for suffix in ("html", "pdf"):
        (corpus / "legal" / f"policy.{suffix}").write_text("content")
    with pytest.raises(ValueError, match="Duplicate"):
        task3.convert_legal_docs()
    assert not list(task3.OUTPUT_DIR.rglob("*.md"))


@pytest.mark.parametrize("suffix", ["pdf", "docx"])
def test_binary_document_converter_dispatch(corpus, monkeypatch, suffix):
    source = corpus / "legal" / f"policy.{suffix}"
    source.write_bytes(b"fixture")

    class FakeConverter:
        def convert(self, path):
            assert Path(path) == source
            return SimpleNamespace(title="Policy", text_content="## Rule\n\nKeep this rule.")

    monkeypatch.setitem(sys.modules, "markitdown", SimpleNamespace(MarkItDown=FakeConverter))
    task3.convert_legal_docs()
    assert "Keep this rule." in (task3.OUTPUT_DIR / "legal" / "policy.md").read_text()


def test_current_corpus_preserves_every_recovered_build_and_table(tmp_path, monkeypatch):
    # Regression against the colleague's improved Task 2 corpus, offline.
    monkeypatch.setattr(task3, "OUTPUT_DIR", tmp_path / "standardized")
    task3.convert_all()
    assert len(list(task3.OUTPUT_DIR.rglob("*.md"))) == 11
    for source in (task3.LANDING_DIR / "news").glob("*.json"):
        data = json.loads(source.read_text())
        output = (task3.OUTPUT_DIR / "news" / f"{source.stem}.md").read_text()
        content = data["content_markdown"]
        for heading in ("## Phù hiệu", "## Bảng ngọc", "## Phép bổ trợ", "### Bộ ngọc 1", "### Bộ ngọc 2"):
            if heading in content:
                assert heading in output
        for line in content.splitlines():
            if line.lstrip().startswith(("- **", "- Số lượng:")) or (line.startswith("|") and "Sát thương" in line):
                assert line in output
    before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in task3.OUTPUT_DIR.rglob("*.md")}
    task3.convert_all()
    assert before == {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in task3.OUTPUT_DIR.rglob("*.md")}
