from copy import deepcopy

import pytest

from src.contracts import validate_search_results
from src.task7_reranking import rerank_rrf


def result(item_id, score=0.9, method="dense"):
    return {
        "id": item_id,
        "content": f"Content for {item_id}",
        "score": score,
        "metadata": {
            "source": "admissions.md",
            "title": "Admissions",
            "doc_type": "legal",
            "url": None,
            "chunk_index": 0,
        },
        "retrieval_method": method,
    }


def test_fusion_uses_ranks_and_preserves_inputs():
    lists = [
        [result("a", 0.9), result("b", 0.8)],
        [result("b", 100, "bm25"), result("c", 50, "bm25")],
    ]
    original = deepcopy(lists)

    fused = rerank_rrf(lists, top_k=3)

    validate_search_results(fused, top_k=3, expected_method="hybrid")
    assert [item["id"] for item in fused] == ["b", "a", "c"]
    assert [item["score"] for item in fused] == pytest.approx(
        [1 / 62 + 1 / 61, 1 / 61, 1 / 62]
    )
    assert fused[0]["metadata"] == original[0][1]["metadata"]
    assert lists == original
    fused[0]["score"] = 0
    assert lists == original


def test_duplicate_id_contributes_only_first_original_rank_per_list():
    first = result("a")
    duplicate = result("a", 100, "bm25")
    duplicate["content"] = "Duplicate content"
    fused = rerank_rrf([[first, duplicate, result("b")], [duplicate]])

    assert [item["id"] for item in fused] == ["a", "b"]
    assert fused[0]["score"] == pytest.approx(2 / 61)
    assert fused[1]["score"] == pytest.approx(1 / 63)
    assert fused[0]["content"] == first["content"]


@pytest.mark.parametrize("lists", [[], [[]], [[], []]])
def test_empty_lists(lists):
    assert rerank_rrf(lists) == []


@pytest.mark.parametrize("top_k", [0, -1])
def test_non_positive_top_k(top_k):
    assert rerank_rrf([[result("a")]], top_k=top_k) == []


def test_top_k_and_ties_follow_first_seen_order():
    lists = [[result("b")], [], [result("a")], [result("c")]]
    assert [item["id"] for item in rerank_rrf(lists, top_k=2)] == ["b", "a"]
    assert len(rerank_rrf(lists, top_k=100)) == 3


@pytest.mark.parametrize("k", [0, 10])
def test_custom_k(k):
    fused = rerank_rrf([[result("a"), result("b")]], k=k)
    assert [item["score"] for item in fused] == pytest.approx(
        [1 / (k + 1), 1 / (k + 2)]
    )


def test_negative_k_is_rejected():
    with pytest.raises(ValueError, match="k must be non-negative"):
        rerank_rrf([[result("a")]], k=-1)
