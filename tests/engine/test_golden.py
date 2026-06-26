import json
from pathlib import Path
from engine import orchestrator, core

GOLDEN = Path(__file__).resolve().parents[1] / "golden"

def _strip(env):
    env = dict(env); env.pop("produced_at", None); return env

def _check(stage_index, stage, tmp_path):
    res = orchestrator.run("quran-root", "علم", run_root=tmp_path)
    got = _strip(core.read_artifact(f"{res['run_dir']}/0{stage_index}_{stage}.json"))
    gold = json.loads((GOLDEN / f"0{stage_index}_{stage}.json").read_text("utf-8"))
    assert got == _strip(gold), f"golden drift in stage {stage}"

def test_golden_extract(tmp_path):
    _check(1, "extract", tmp_path)

def test_golden_cluster(tmp_path):
    _check(2, "cluster", tmp_path)

def test_golden_observe(tmp_path):
    _check(3, "observe", tmp_path)

def test_golden_hypothesis(tmp_path):
    _check(4, "hypothesis", tmp_path)
