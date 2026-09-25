"""Offline checks for Person 1's corpus, provenance and golden evidence."""
import hashlib
import json
from pathlib import Path

import pytest

from src.contracts import validate_document
from src.task2_crawl_news import extract_article, validate_article
from src.task3_convert_markdown import convert_all

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8-sig"))


def test_manifest_has_unique_ids_and_separate_audiences():
    items = read("data/sources.json")
    assert len(items) == len({x["id"] for x in items}) == 8
    legal = [x for x in items if x["doc_type"] == "legal"]
    assert {x["audience"] for x in legal} == {
        "dai_hoc_chinh_quy", "lien_thong_cao_dang", "lien_thong_dai_hoc"}
    assert all(x["admission_year"] == 2026 for x in items)
    assert all((ROOT / x["local_path"]).is_file() for x in items)


def test_article_extraction_excludes_navigation_and_keeps_table():
    html = '''<nav>UNRELATED MENU</nav><div class="title-news"><h1>Admissions</h1></div>
    <div id="post-content"><div><p>''' + "Admissions evidence. " * 20 + '''</p>
    <table><tr><th>Exam</th><th>Score</th></tr><tr><td>IELTS</td><td>6.5</td></tr></table>
    </div><div class="tags">UNRELATED TAGS</div></div><footer>UNRELATED FOOTER</footer>'''
    title, content, _ = extract_article(html)
    assert title == "Admissions"
    assert "UNRELATED" not in content
    assert "| IELTS | 6.5 |" in content


def test_error_page_and_placeholder_are_rejected():
    with pytest.raises(ValueError):
        extract_article("<h1>Access denied</h1><p>Try later</p>")
    with pytest.raises(ValueError, match="Unverified"):
        validate_article({"url": "https://example.org", "title": "x",
                          "date_crawled": "2026-09-25", "content_markdown": "Placeholder"})


def test_articles_have_real_raw_html_provenance():
    for item in read("data/sources.json"):
        if item["doc_type"] != "news":
            continue
        article = read(item["local_path"])
        validate_article(article)
        raw = (ROOT / article["raw_html_path"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == article["raw_sha256"]
        title, body, _ = extract_article(raw.decode("utf-8"))
        assert title == article["title"]
        assert body == article["content_markdown"]


def test_all_pdf_pages_are_accounted_for():
    expected = {"neu2026_undergraduate": 11, "neu2026_college_transfer": 7, "neu2026_second_degree": 4}
    for item in read("data/sources.json"):
        if item["doc_type"] != "legal":
            continue
        cache = read(f"data/ocr/{item['id']}.json")
        assert hashlib.sha256((ROOT / item["local_path"]).read_bytes()).hexdigest() == cache["sha256"]
        assert [p["page"] for p in cache["pages"]] == list(range(1, expected[item["id"]] + 1))
        assert all(len(p["text"]) >= 80 for p in cache["pages"])


def test_standardized_documents_match_contract_and_manifest():
    for item in read("data/sources.json"):
        doc = read(f"data/standardized/{item['doc_type']}/{item['id']}.json")
        validate_document(doc)
        assert doc["metadata"]["url"] == item["url"]
        assert doc["metadata"]["audience"] == item["audience"]


def test_conversion_is_repeatable_without_network_or_ocr(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Existing OCR cache must make conversion offline")
    monkeypatch.setattr("src.task3_convert_markdown.ocr_page", forbidden)
    paths = sorted((ROOT / "data/standardized").glob("*/*"))
    before = {str(p): p.read_bytes() for p in paths if p.is_file()}
    convert_all()
    after = {str(p): p.read_bytes() for p in sorted((ROOT / "data/standardized").glob("*/*")) if p.is_file()}
    assert before == after


def test_every_golden_evidence_is_exactly_in_its_source():
    dataset = read("group_project/evaluation/golden_dataset.json")
    assert len(dataset) >= 15
    sources = {x["id"]: x for x in read("data/sources.json")}
    for case in dataset:
        assert case["expected_answer"].strip()
        assert case["expected_context"] == "\n\n".join(e["quote"] for e in case["evidence"])
        for evidence in case["evidence"]:
            source = sources[evidence["source_id"]]
            doc = read(f"data/standardized/{source['doc_type']}/{source['id']}.json")
            assert evidence["quote"] in doc["content"]
            assert evidence["url"] == source["url"]
    assert {x["split"] for x in dataset} == {"evaluation"}
    assert {x["split"] for x in read("group_project/evaluation/fallback_dataset.json")} == {"calibration"}


def test_reviewed_certificate_table_preserves_numeric_values():
    doc = read("data/standardized/legal/neu2026_undergraduate.json")
    assert "| 6.5 | 79 - 93 | 890/170/170 | 9.0 |" in doc["content"]
    assert doc["metadata"]["visually_reviewed_pages"] == [1, 4, 5, 6, 7]


def test_reviewed_program_tables_reconcile_with_published_total():
    rows = []
    for page in (4, 5, 6, 7):
        content = (ROOT / f"data/reviewed/neu2026_undergraduate/page_{page:02d}.md").read_text(encoding="utf-8")
        for line in content.splitlines():
            columns = [x.strip() for x in line.strip("|").split("|")]
            if len(columns) == 6 and columns[0].isdigit():
                rows.append(columns)
    assert sum(int(row[-1]) for row in rows) == 8780
    assert {int(row[0]) for row in rows} == set(range(1, 89))
