"""Tests for engine.metaprotocol — Meta-Protocol registry + Pareto promotion."""
import json
from engine import metaprotocol

V = {"Recoverability": .5, "Reproducibility": 1, "Falsifiability": 1,
     "Compression": .6, "Coherence": 1, "PredictivePower": .5}


def test_first_candidate_becomes_stable(tmp_path):
    reg = tmp_path / "registry.json"
    reg.write_text(json.dumps({"current_stable": None, "versions": {}}), "utf-8")
    out = metaprotocol.evaluate_candidate("0.1.0", V, reg)
    assert out["promoted"] and out["current_stable"] == "0.1.0"


def test_non_dominating_candidate_not_promoted(tmp_path):
    reg = tmp_path / "registry.json"
    reg.write_text(json.dumps({"current_stable": "0.1.0",
        "versions": {"0.1.0": {"score": V, "status": "stable"}}}), "utf-8")
    worse = dict(V); worse["Compression"] = .4
    out = metaprotocol.evaluate_candidate("0.2.0", worse, reg)
    assert out["promoted"] is False and out["current_stable"] == "0.1.0"


def test_reeval_of_current_stable_is_idempotent(tmp_path):
    """Re-evaluating the reigning stable version must NOT demote it to candidate."""
    reg = tmp_path / "registry.json"
    reg.write_text(json.dumps({"current_stable": "0.1.0",
        "versions": {"0.1.0": {"score": V, "status": "stable"}}}), "utf-8")
    out = metaprotocol.evaluate_candidate("0.1.0", V, reg)
    assert out["promoted"] is False
    assert out["current_stable"] == "0.1.0"
    on_disk = json.loads(reg.read_text("utf-8"))
    assert on_disk["versions"]["0.1.0"]["status"] == "stable"
    assert on_disk["current_stable"] == "0.1.0"
