"""تستِ RFC Generator — Publication Layer + P2 provenance gate."""
from engine import store as store_mod
from engine.stages import commit
from rfc import generator


def _populated_store(tmp_path):
    st = store_mod.Store(tmp_path)
    arts = {"extract": {"payload": {"evidence": [
              {"evidence_id": "2:31:2:1", "locus": {}, "surface": "ع", "features": {}}]}},
            "verify": {"payload": {"verifications": [
              {"decision": "ACCEPTED", "knowledge_id": "k_Elm_0", "hypothesis_id": "h1",
               "confidence_tier": "قوی", "tests": {}}]}},
            "reduce": {"payload": {"accepted_definition": {"statement": "دانستن",
               "primitives": ["know"]}}},
            "graph": {"payload": {"links": []}}}
    commit.run(st, {"ref": "Elm", "domain": "quran-root", "unit_id": 218}, "rid", arts)
    return st


def test_rfc_generated_with_seven_fields(tmp_path):
    st = _populated_store(tmp_path)
    rfc = generator.generate(st, {"ref": "Elm", "domain": "quran-root", "unit_id": 218},
                             "rid", "0.1.0", out_root=tmp_path / "rfc")
    assert set(rfc["fields"]) == {"evidence", "reasoning", "confidence", "scope",
                                  "limitations", "relationships", "history"}
    assert rfc["knowledge"][0]["formal_representation"]
    assert (tmp_path / "rfc" / "quran-root" / "Elm").exists()


def test_rfc_id_format(tmp_path):
    st = _populated_store(tmp_path)
    rfc = generator.generate(st, {"ref": "Elm", "domain": "quran-root", "unit_id": 218},
                             "rid", "0.1.0", out_root=tmp_path / "rfc")
    assert rfc["rfc_id"] == "RFC-quran-root-Elm-v0.1.0-rid"


def test_rfc_files_written(tmp_path):
    st = _populated_store(tmp_path)
    rfc = generator.generate(st, {"ref": "Elm", "domain": "quran-root", "unit_id": 218},
                             "rid", "0.1.0", out_root=tmp_path / "rfc")
    rfc_dir = tmp_path / "rfc" / "quran-root" / "Elm"
    assert (rfc_dir / f"{rfc['rfc_id']}.json").exists()
    assert (rfc_dir / f"{rfc['rfc_id']}.md").exists()


def test_p2_gate_raises_on_incomplete_provenance(tmp_path):
    """P2 gate: اگر knowledge بدون provenance باشد، ProvenanceError پرتاب می‌شود."""
    import json
    st = store_mod.Store(tmp_path)
    # دستی یک knowledge بدون provenance DAG می‌نویسیم
    obj = {
        "knowledge_id": "k_orphan_0",
        "unit": {"ref": "X", "domain": "quran-root", "unit_id": 999},
        "run_id": "test",
        "status": "ACCEPTED",
        "formal_representation": {
            "definition_primitives": [],
            "relations": [],
            "verified_by": [{}],
            "scope": {"unit": "X"},
            "confidence_tier": "محتمل"},
        "natural_explanation": "test",
        "provenance_nodes": [],
        "relations_to_knowledge": []}
    st.put_knowledge(obj)
    # بدون افزودن به DAG — provenance_complete باید False برگرداند
    try:
        generator.generate(st, {"ref": "X", "domain": "quran-root", "unit_id": 999},
                           "rid", "0.1.0", out_root=tmp_path / "rfc")
        assert False, "باید ProvenanceError پرتاب می‌شد"
    except generator.ProvenanceError:
        pass
