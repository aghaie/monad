# tests/engine/test_e2e.py
"""تستِ end-to-end — معیارِ موفقیتِ v1 (Task 18)."""
from engine import orchestrator


def test_full_pipeline_for_elm():
    res = orchestrator.run_and_score("quran-root", "علم")
    # هر ۹ مرحله
    assert res["stages_done"] == ["extract", "cluster", "observe", "hypothesis",
                                  "attack", "verify", "reduce", "graph", "commit"]
    # دانش ثبت شده
    assert res["committed"]["knowledge"] >= 1
    # RFC تولید شده
    assert res["rfc_id"].startswith("RFC-quran-root-Elm-")
    # بردارِ ۶ بُعدی
    assert set(res["benchmark"]) == {"Recoverability", "Reproducibility",
        "Falsifiability", "Compression", "Coherence", "PredictivePower"}
    # Meta-Protocol ارزیابی شد
    assert "current_stable" in res["metaprotocol"]
