"""Offline checks for conversion boundaries, metadata and safe reruns."""

import hashlib
import json
import tempfile
import unittest
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch

from src import task3_convert_markdown as converter


class ConversionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.landing = self.root / "landing"
        self.output = self.root / "standardized"
        (self.landing / "news").mkdir(parents=True)
        (self.landing / "legal").mkdir()
        for name, value in (("LANDING_DIR", self.landing), ("OUTPUT_DIR", self.output)):
            patcher = patch.object(converter, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def news(self, body="Nội dung có dấu và [nguồn](https://example.org/a)."):
        data = {"url": "https://example.org/a", "title": "Tiêu đề: có dấu",
                "date_crawled": "2026-09-25T00:00:00+00:00", "content_markdown": body}
        path = self.landing / "news" / "article_01.json"
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return path, data

    def test_news_preserves_metadata_and_content_and_rerun(self):
        source, data = self.news()
        original = source.read_bytes()
        converter.convert_news_articles()
        output = self.output / "news" / "article_01.md"
        text = output.read_text(encoding="utf-8")
        header = text.split("---\n")[1]
        metadata = {line.split(": ", 1)[0]: json.loads(line.split(": ", 1)[1]) for line in header.splitlines()}
        self.assertEqual(metadata["url"], data["url"])
        self.assertEqual(metadata["date_crawled"], data["date_crawled"])
        self.assertEqual(metadata["source_sha256"], hashlib.sha256(original).hexdigest())
        self.assertIn(data["content_markdown"], text)
        before = output.stat().st_mtime_ns
        converter.convert_news_articles()
        self.assertEqual(output.stat().st_mtime_ns, before)
        self.assertEqual(source.read_bytes(), original)
        self.assertEqual(len(list(self.output.rglob("*.md"))), 1)

    def test_empty_news_does_not_replace_good_output(self):
        self.news()
        converter.convert_news_articles()
        output = self.output / "news" / "article_01.md"
        before = output.read_bytes()
        self.news("   ")
        with self.assertRaises(ValueError):
            converter.convert_news_articles()
        self.assertEqual(output.read_bytes(), before)

    def test_empty_body_rejected_before_metadata_can_mask_it(self):
        with self.assertRaises(ValueError):
            converter.markdown_document({"title": "Title"}, "\n\t")

    def test_pdf_docx_same_stem_rejected(self):
        for suffix in ("pdf", "docx"):
            (self.landing / "legal" / f"same.{suffix}").touch()
        with self.assertRaisesRegex(ValueError, "colliding"):
            converter.convert_legal_docs()

    def test_source_hash_mismatch_rejected(self):
        legal = self.landing / "legal"
        (legal / "sample.pdf").write_bytes(b"changed")
        (legal / "sources.json").write_text(json.dumps({"documents": [
            {"filename": "sample.pdf", "sha256": "wrong"}]}), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "checksum"):
            converter.convert_legal_docs()

    def test_vietnamese_headings_and_unicode(self):
        result = converter.legal_headings("Chương I\nĐiều 1. Phạm vi\n1. Nội dung\n")
        self.assertIn("## Chương I", result)
        self.assertIn("### Điều 1. Phạm vi", result)
        self.assertIn("\n1. Nội dung", result)
        self.assertEqual(converter.normalize("Vie\u0323\u0302t"), "Việt")

    def test_ocr_page_cache_and_model_change(self):
        model_dir = self.root / "tessdata"
        model_dir.mkdir()
        model = model_dir / "vie.traineddata"
        model.write_bytes(b"model-v1")
        calls = []

        class Page:
            rect = SimpleNamespace(get_area=lambda: 100)

            def get_image_info(self):
                return [{"bbox": (0, 0, 9, 9)}]

            def get_text(self, *, sort, textpage=None):
                return "Ký bởi: Cổng Thông tin điện tử Chính phủ. Cơ quan: Văn phòng Chính phủ."

            def get_textpage_ocr(self, **kwargs):
                calls.append(kwargs)
                return SimpleNamespace(extractDICT=lambda: {"blocks": [{"lines": [{"spans": [
                    {"text": "Điều 1. Văn bản tiếng Việt sau khi nhận diện từ ảnh scan."}
                ]}]}]})

        class Document(list):
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        fake = SimpleNamespace(VersionBind="test", open=lambda path: Document([Page(), Page()]),
                               Rect=lambda bbox: SimpleNamespace(get_area=lambda: 81))
        with patch.dict("sys.modules", {"pymupdf": fake}), \
                patch.object(converter, "TESSDATA_DIR", model_dir), \
                patch.object(converter, "CACHE_DIR", self.root / "cache"):
            first, metadata = converter.pdf_text(Path("sample.pdf"), "digest")
            second, _ = converter.pdf_text(Path("sample.pdf"), "digest")
            self.assertEqual(first, second)
            self.assertEqual(len(calls), 2)
            self.assertEqual(metadata["ocr_pages"], [1, 2])
            self.assertIn("## Trang 2", first)
            model.write_bytes(b"model-v2")
            converter.pdf_text(Path("sample.pdf"), "digest")
            self.assertEqual(len(calls), 4)

    def test_ocr_preserves_word_boundaries(self):
        textpage = SimpleNamespace(extractDICT=lambda: {"blocks": [{"lines": [{"spans": [
            {"text": "về"}, {"text": "tài"}, {"text": " "}, {"text": "nguyên"}
        ]}]}]})
        self.assertEqual(converter.ocr_text(textpage), "về tài nguyên")


if __name__ == "__main__":
    unittest.main()
