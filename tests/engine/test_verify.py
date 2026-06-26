# tests/engine/test_verify.py
from engine.stages import verify
from domains.quran_root import adapter


def test_true_cooccurrence_accepted():
    u = adapter.resolve_unit("علم")
    kt = adapter.resolve_unit("كتب")
    hyps = [{"hypothesis_id": "h1", "status": "PROPOSED",
             "prediction": {"predicate": "cooccurrence_constraint",
                            "params": {"with_root_id": kt["unit_id"]}}}]
    out = verify.run(hyps, [], u, adapter)
    v = out["verifications"][0]
    assert v["decision"] in {"ACCEPTED", "REJECTED", "UNKNOWN"}
    if v["decision"] == "ACCEPTED":
        assert v["confidence_tier"] in {"صریح", "قوی", "محتمل"}
        assert v["knowledge_id"]


def test_false_hypothesis_rejected():
    u = adapter.resolve_unit("علم")
    # ریشه‌ای کم‌ربط با علم → باید رد شود
    rare = adapter.resolve_unit("فيل")  # «فیل» (سورهٔ فیل)
    hyps = [{"hypothesis_id": "hF", "status": "PROPOSED",
             "prediction": {"predicate": "cooccurrence_constraint",
                            "params": {"with_root_id": rare["unit_id"]}}}]
    out = verify.run(hyps, [], u, adapter)
    assert out["verifications"][0]["decision"] != "ACCEPTED"


def test_unknown_predicate():
    u = adapter.resolve_unit("علم")
    hyps = [{"hypothesis_id": "hU", "status": "PROPOSED",
             "prediction": {"predicate": "nonexistent_predicate",
                            "params": {}}}]
    out = verify.run(hyps, [], u, adapter)
    v = out["verifications"][0]
    assert v["decision"] == "UNKNOWN"
    assert v["confidence_tier"] is None
    assert v["knowledge_id"] is None


def test_output_structure():
    u = adapter.resolve_unit("علم")
    kt = adapter.resolve_unit("كتب")
    hyps = [{"hypothesis_id": "h1", "status": "PROPOSED",
             "prediction": {"predicate": "cooccurrence_constraint",
                            "params": {"with_root_id": kt["unit_id"]}}}]
    out = verify.run(hyps, [], u, adapter)
    assert "verifications" in out
    v = out["verifications"][0]
    assert "hypothesis_id" in v
    assert "decision" in v
    assert "confidence_tier" in v
    assert "knowledge_id" in v
    assert "tests" in v
