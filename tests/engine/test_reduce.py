"""تستِ مرحلهٔ ۷ — Reduce: سنجشِ فشرده‌سازی."""
from engine.stages import reduce_measure
from domains.quran_root import adapter


def test_reduce_measures_compression():
    u = adapter.resolve_unit("علم")
    proposed = {"proposed_definition": {"statement": "دانستن/شناخت",
                "primitives": ["know", "perceive"], "relations": []}}
    verifs = [{"decision": "ACCEPTED", "knowledge_id": "k0"},
              {"decision": "REJECTED", "knowledge_id": None}]
    out = reduce_measure.run(proposed, verifs, u, adapter)
    assert out["compression"]["n_primitives"] == 2
    assert 0 <= out["compression"]["coverage"] <= 1
    assert "predicts_heldout" in out["compression"]
    assert "accepted_definition" in out


def test_reduce_gate_pass():
    """coverage >= 0.5 and len(prims) >= 1 → accepted_definition is not UNKNOWN."""
    u = adapter.resolve_unit("علم")
    proposed = {"proposed_definition": {"statement": "X", "primitives": ["p1"], "relations": []}}
    verifs = [{"decision": "ACCEPTED", "knowledge_id": "k0"},
              {"decision": "ACCEPTED", "knowledge_id": "k1"}]
    out = reduce_measure.run(proposed, verifs, u, adapter)
    assert out["accepted_definition"]["statement"] != "UNKNOWN"
    assert "k0" in out["accepted_definition"]["covers_knowledge"]
    assert "k1" in out["accepted_definition"]["covers_knowledge"]


def test_reduce_gate_fail():
    """coverage < 0.5 → accepted_definition = UNKNOWN."""
    u = adapter.resolve_unit("علم")
    proposed = {"proposed_definition": {"statement": "X", "primitives": ["p1"], "relations": []}}
    verifs = [{"decision": "REJECTED", "knowledge_id": None},
              {"decision": "REJECTED", "knowledge_id": None},
              {"decision": "REJECTED", "knowledge_id": None}]
    out = reduce_measure.run(proposed, verifs, u, adapter)
    assert out["accepted_definition"]["statement"] == "UNKNOWN"
    assert out["accepted_definition"]["primitives"] == []


def test_reduce_empty_primitives_gate_fail():
    """len(prims) == 0 → gate fails even if coverage is high."""
    u = adapter.resolve_unit("علم")
    proposed = {"proposed_definition": {"statement": "X", "primitives": [], "relations": []}}
    verifs = [{"decision": "ACCEPTED", "knowledge_id": "k0"}]
    out = reduce_measure.run(proposed, verifs, u, adapter)
    assert out["accepted_definition"]["statement"] == "UNKNOWN"


def test_reduce_mdl_bits():
    """mdl_bits = n_prims * log2(n_prims + 1)."""
    import math
    u = adapter.resolve_unit("علم")
    proposed = {"proposed_definition": {"statement": "X", "primitives": ["a", "b", "c"], "relations": []}}
    verifs = [{"decision": "ACCEPTED", "knowledge_id": "k0"}]
    out = reduce_measure.run(proposed, verifs, u, adapter)
    expected = round(3 * math.log2(3 + 1), 3)
    assert out["compression"]["mdl_bits"] == expected
