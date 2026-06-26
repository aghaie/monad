"""تستِ مرحلهٔ ۸ — Graph."""
from engine.stages import graph


def test_graph_links_and_coherence():
    patterns = [{"with": "كتب", "with_root_id": 5, "lift": 4.0},
                {"with": "ايه", "with_root_id": 9, "lift": 2.5}]
    out = graph.run({"accepted_definition": {"primitives": ["know"]}},
                    patterns, {"ref": "Elm"})
    assert out["links"] and out["links"][0]["relation"] == "co-defines"
    assert out["network_coherence"]["passed"] is True
    assert "score" in out["predictive_check"]


def test_graph_top5_limit():
    patterns = [{"with": f"r{i}", "with_root_id": i, "lift": float(10 - i)}
                for i in range(10)]
    out = graph.run({}, patterns, {"ref": "test"})
    assert len(out["links"]) == 5
    # sorted by lift descending
    weights = [l["weight"] for l in out["links"]]
    assert weights == sorted(weights, reverse=True)


def test_graph_empty_patterns():
    out = graph.run({}, [], {"ref": "empty"})
    assert out["links"] == []
    assert out["network_coherence"]["passed"] is True
    assert out["predictive_check"]["score"] == 0.0


def test_graph_predictive_check_score():
    patterns = [{"with": "a", "with_root_id": 1, "lift": 2.0},
                {"with": "b", "with_root_id": 2, "lift": 1.0}]
    out = graph.run({}, patterns, {"ref": "x"})
    # only "a" has lift > 1.5 → hits=1, score=0.5
    assert out["predictive_check"]["hits"] == 1
    assert out["predictive_check"]["score"] == 0.5
