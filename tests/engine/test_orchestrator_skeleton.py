# tests/engine/test_orchestrator_skeleton.py
from engine import orchestrator, core

def test_run_extract_only(tmp_path):
    res = orchestrator.run("quran-root", "علم", run_root=tmp_path)
    assert res["status"] == "ok"
    art = core.read_artifact(res["run_dir"] + "/01_extract.json")
    assert art["payload"]["unit_stats"]["evidence_count"] == 854
    assert art["unit"]["unit_id"] == 218

def test_run_id_is_reproducible(tmp_path):
    a = orchestrator.run("quran-root", "علم", run_root=tmp_path)
    b = orchestrator.run("quran-root", "علم", run_root=tmp_path)
    assert a["run_id"] == b["run_id"]
