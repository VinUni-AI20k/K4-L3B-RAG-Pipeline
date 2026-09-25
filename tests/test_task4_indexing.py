"""Task 4 unit tests: no model downloads, paid APIs or persistent user DB writes."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from src import task4_chunking_indexing as task


def document(item_id="legal/example.md", text="Chính sách du lịch. " * 80):
    return {"id": item_id, "content": text, "metadata": {
        "source": "example.pdf", "title": "Du lịch", "doc_type": "legal", "url": None}}


class MemoryCollection:
    def __init__(self):
        self.items = {}

    def upsert(self, ids, documents, embeddings, metadatas):
        for key, text, vector, metadata in zip(ids, documents, embeddings, metadatas):
            self.items[key] = {"content": text, "embedding": vector, "metadata": metadata}

    def get(self, where, include):
        return {"ids": [key for key, item in self.items.items()
                        if all(item["metadata"].get(k) == v for k, v in where.items())]}

    def delete(self, ids):
        for key in ids:
            del self.items[key]


class IndexTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_front_matter_is_metadata_not_embedding_content(self):
        folder = self.root / "news"
        folder.mkdir()
        (folder / "sample.md").write_text(
            '---\ntitle: "Hội An: ẩm thực"\nurl: "https://example.org/hoi-an"\n'
            'source: "article_05.json"\nlanguage: "en"\n---\n\n# Explore Hoi An\nFood body.', encoding="utf-8")
        with patch.object(task, "STANDARDIZED_DIR", self.root):
            docs = task.load_documents()
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]["metadata"]["url"], "https://example.org/hoi-an")
        self.assertEqual(docs[0]["metadata"]["title"], "Hội An: ẩm thực")
        self.assertNotIn("https://example.org", docs[0]["content"])
        self.assertEqual(docs[0]["id"], "news/sample.md")

    def test_stable_chunks_keep_page_source_and_do_not_mutate(self):
        doc = document(text="# Du lịch\n\n## Trang 1\n" + "A" * 800 + "\n## Trang 2\n" + "B" * 800)
        original = copy.deepcopy(doc)
        chunks = task.chunk_documents([doc])
        self.assertEqual(chunks, task.chunk_documents([doc]))
        self.assertEqual(doc, original)
        self.assertEqual(len({c["id"] for c in chunks}), len(chunks))
        self.assertEqual({c["metadata"]["page"] for c in chunks}, {1, 2})
        for index, chunk in enumerate(chunks):
            self.assertEqual(chunk["metadata"]["chunk_index"], index)
            self.assertLessEqual(len(chunk["content"]), task.CHUNK_SIZE)
            self.assertEqual(chunk["metadata"]["source"], "example.pdf")
            self.assertFalse("A" in chunk["content"] and "B" in chunk["content"])
        self.assertEqual(chunks[0]["content"][-task.CHUNK_OVERLAP:], chunks[1]["content"][:task.CHUNK_OVERLAP])

    def test_duplicate_documents_and_empty_documents_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            task.chunk_documents([document(), document()])
        with self.assertRaises(ValueError):
            task.chunk_documents([document(text=" ")])

    def test_embedding_cache_reuses_vectors_and_keeps_input(self):
        chunks = task.chunk_documents([document()])
        original = copy.deepcopy(chunks)
        calls = []
        def encode(texts):
            calls.extend(texts)
            return [[1.0, 0.0] for _ in texts]
        with patch.object(task, "EMBEDDING_CACHE", self.root / "cache"), \
             patch.object(task, "EMBEDDING_DIM", 2), patch.object(task, "embed_texts", encode):
            first = task.embed_chunks(chunks)
            count = len(calls)
            second = task.embed_chunks(chunks)
        self.assertEqual(first, second)
        self.assertEqual(len(calls), count)
        self.assertEqual(chunks, original)

    def test_upsert_is_idempotent_and_removes_only_changed_document_tail(self):
        collection = MemoryCollection()
        long = task.chunk_documents([document(), document("news/other.md")])
        short = task.chunk_documents([document(text="Short revised policy.")])
        embed = lambda chunks: [{**c, "embedding": [1.0, 0.0]} for c in chunks]
        with patch.object(task, "get_collection", return_value=collection), patch.object(task, "EMBEDDING_DIM", 2):
            task.index_to_vectorstore(embed(long))
            task.index_to_vectorstore(embed(long))
            self.assertEqual(len(collection.items), len(long))
            task.index_to_vectorstore(embed(short))
        self.assertEqual(len(collection.get({"document_id": "legal/example.md"}, [])["ids"]), 1)
        self.assertEqual(len(collection.get({"document_id": "news/other.md"}, [])["ids"]), len(long) // 2)
        self.assertEqual(collection.items[short[0]["id"]]["metadata"]["url"], "")

    def test_invalid_vectors_fail_before_database_access(self):
        chunks = task.chunk_documents([document(text="A short paragraph")])
        with patch.object(task, "get_collection") as get, patch.object(task, "EMBEDDING_DIM", 2):
            for vector in ([1.0], [float("nan"), 1.0], [0.0, 0.0]):
                with self.assertRaises(ValueError):
                    task.index_to_vectorstore([{**chunks[0], "embedding": vector}])
            get.assert_not_called()

    def test_shared_encoder_normalizes_and_rejects_truncation(self):
        calls = []
        model = SimpleNamespace(max_seq_length=10,
            tokenizer=lambda texts, **kwargs: {"input_ids": [[1] * len(t) for t in texts]},
            encode=lambda texts, **kwargs: (calls.append(kwargs) or SimpleNamespace(tolist=lambda: [[1.0, 0.0]])))
        with patch.object(task, "_embedding_model", return_value=model), patch.object(task, "EMBEDDING_DIM", 2):
            self.assertEqual(task.embed_texts(["query"]), [[1.0, 0.0]])
            self.assertTrue(calls[0]["normalize_embeddings"])
            with self.assertRaisesRegex(ValueError, "token limit"):
                task.embed_texts(["long query exceeds limit"])

    def test_collection_model_or_distance_mismatch_rejected(self):
        collection = SimpleNamespace(metadata=task._signature(), configuration={"hnsw": {"space": "cosine"}})
        client = SimpleNamespace(get_or_create_collection=lambda **kwargs: collection)
        modules = {"chromadb": SimpleNamespace(PersistentClient=lambda **kwargs: client),
                   "chromadb.config": SimpleNamespace(Settings=lambda **kwargs: None)}
        with patch.dict("sys.modules", modules):
            self.assertIs(task.get_collection(), collection)
            collection.configuration["hnsw"]["space"] = "l2"
            with self.assertRaisesRegex(ValueError, "cosine"):
                task.get_collection()
            collection.configuration["hnsw"]["space"] = "cosine"
            collection.metadata["embedding_model"] = "other-model"
            with self.assertRaisesRegex(ValueError, "different embedding"):
                task.get_collection()


if __name__ == "__main__":
    unittest.main()
