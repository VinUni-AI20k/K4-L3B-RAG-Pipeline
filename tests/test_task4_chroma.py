"""Real Chroma integration with tiny synthetic vectors and a temporary database."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import task4_chunking_indexing as task


@unittest.skipUnless(importlib.util.find_spec("chromadb"), "ChromaDB not installed")
class ChromaIntegrationTests(unittest.TestCase):
    def test_persistence_cosine_upsert_and_configuration_guard(self):
        # Windows Chroma may retain file handles until process exit; retain this
        # tiny fixture in the ignored cache instead of removing an open SQLite DB.
        base = task.ROOT / ".cache" / "test-chroma"
        base.mkdir(parents=True, exist_ok=True)
        directory = Path(tempfile.mkdtemp(dir=base))
        metadata = {"source": "fixture.md", "title": "Fixture", "doc_type": "news", "url": None,
                    "document_id": "news/fixture.md", "chunk_index": 0}
        first = {"id": "news/fixture.md::chunk-0", "content": "First test paragraph",
                 "metadata": metadata, "embedding": [1.0, 0.0]}
        second = {"id": "news/fixture.md::chunk-1", "content": "Second test paragraph",
                  "metadata": {**metadata, "chunk_index": 1}, "embedding": [0.0, 1.0]}
        with patch.object(task, "CHROMA_DIR", directory), patch.object(task, "EMBEDDING_DIM", 2):
            task.index_to_vectorstore([first, second])
            task.index_to_vectorstore([first, second])
            collection = task.get_collection()
            self.assertEqual(collection.count(), 2)
            results = collection.query(query_embeddings=[[1.0, 0.0]], n_results=2,
                                       include=["distances", "metadatas"])
            self.assertEqual(results["ids"][0][0], first["id"])
            self.assertAlmostEqual(results["distances"][0][0], 0.0, places=5)
            self.assertAlmostEqual(results["distances"][0][1], 1.0, places=5)
            self.assertEqual(results["metadatas"][0][0]["url"], "")
            task.index_to_vectorstore([first])
            self.assertEqual(task.get_collection().count(), 1)
            with patch.object(task, "EMBEDDING_MODEL", "other-model"):
                with self.assertRaisesRegex(ValueError, "different embedding"):
                    task.get_collection()


if __name__ == "__main__":
    unittest.main()
