"""تستِ unit برای Store + commit (مرحلهٔ ۹)."""
from engine import store as store_mod
from engine.stages import commit


def test_commit_writes_three_stores_and_dag(tmp_path):
    st = store_mod.Store(tmp_path)
    artifacts = {
        "extract": {"payload": {"evidence": [
            {"evidence_id": "2:31:2:1", "locus": {}, "surface": "ع", "features": {}}]}},
        "verify": {"payload": {"verifications": [
            {"decision": "ACCEPTED", "knowledge_id": "k_Elm_0", "hypothesis_id": "h1",
             "confidence_tier": "قوی", "tests": {}}]}},
        "reduce": {"payload": {"accepted_definition": {"statement": "دانستن",
            "primitives": ["know"]}}},
        "graph": {"payload": {"links": [{"to_unit": "كتب", "relation": "co-defines"}]}},
    }
    out = commit.run(st, {"ref": "Elm", "domain": "quran-root", "unit_id": 218},
                     "rid123", artifacts)
    assert out["committed"]["knowledge"] == 1
    k = st.get_knowledge("k_Elm_0")
    assert "formal_representation" in k and "natural_explanation" in k
    assert st.provenance_complete("k_Elm_0") is True   # P2
    assert (tmp_path / "evidence").exists() and (tmp_path / "ontology").exists()


def test_store_evidence_immutability(tmp_path):
    """P1 — Evidence is never overwritten once written."""
    st = store_mod.Store(tmp_path)
    ev = [{"evidence_id": "1:1:1:1", "locus": {}, "surface": "ب", "features": {"v": 1}}]
    st.put_evidence(ev)
    # Try to overwrite with different data
    ev2 = [{"evidence_id": "1:1:1:1", "locus": {}, "surface": "ب", "features": {"v": 99}}]
    st.put_evidence(ev2)
    import json
    p = tmp_path / "evidence" / "1_1_1_1.json"
    data = json.loads(p.read_text("utf-8"))
    assert data["features"]["v"] == 1  # original preserved


def test_store_dag_dedup(tmp_path):
    """add_dag_nodes deduplicates by id."""
    st = store_mod.Store(tmp_path)
    st.add_dag_nodes([{"id": "k1", "type": "knowledge"}])
    st.add_dag_nodes([{"id": "k1", "type": "knowledge"}, {"id": "k2", "type": "hypothesis"}])
    import json
    dag = json.loads((tmp_path / "provenance" / "graph.json").read_text("utf-8"))
    ids = [n["id"] for n in dag["nodes"]]
    assert ids.count("k1") == 1
    assert "k2" in ids


def test_provenance_incomplete_without_evidence(tmp_path):
    """provenance_complete returns False when no path to evidence exists."""
    st = store_mod.Store(tmp_path)
    st.add_dag_nodes([{"id": "k1", "type": "knowledge"},
                      {"id": "h1", "type": "hypothesis"}])
    st.add_dag_edges([{"from": "k1", "to": "h1", "type": "verifies"}])
    assert st.provenance_complete("k1") is False


def test_append_log(tmp_path):
    """append_log writes JSONL events."""
    st = store_mod.Store(tmp_path)
    st.append_log({"event": "test", "x": 1})
    st.append_log({"event": "test", "x": 2})
    import json
    lines = (tmp_path / "log" / "events.jsonl").read_text("utf-8").strip().split("\n")
    assert len(lines) == 2
    assert json.loads(lines[0])["x"] == 1
    assert json.loads(lines[1])["x"] == 2
