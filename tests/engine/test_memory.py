"""تستِ Memory — تاریخِ افزایشی."""
from engine.memory import Memory
import json


def test_memory_records(tmp_path):
    m = Memory(tmp_path)
    m.record_attempt("r1", {"ref": "Elm"}, "ok")
    m.record_rejected("r1", "hF", "low lift")
    m.record_discovery("r1", ["k_Elm_0"])
    rej = (tmp_path / "rejected" / "events.jsonl").read_text("utf-8").strip()
    assert "hF" in rej
    att = (tmp_path / "attempts" / "events.jsonl").read_text("utf-8").strip()
    assert json.loads(att)["status"] == "ok"


def test_memory_subdirs_created(tmp_path):
    m = Memory(tmp_path)
    for sub in ("attempts", "rejected", "failed_runs", "abandoned", "discoveries"):
        assert (tmp_path / sub).is_dir()


def test_memory_failed_run(tmp_path):
    m = Memory(tmp_path)
    m.record_failed_run("r2", ValueError("boom"))
    line = (tmp_path / "failed_runs" / "events.jsonl").read_text("utf-8").strip()
    ev = json.loads(line)
    assert ev["run_id"] == "r2"
    assert "boom" in ev["error"]


def test_memory_discovery(tmp_path):
    m = Memory(tmp_path)
    m.record_discovery("r3", ["k_a", "k_b"])
    line = (tmp_path / "discoveries" / "events.jsonl").read_text("utf-8").strip()
    ev = json.loads(line)
    assert ev["knowledge_ids"] == ["k_a", "k_b"]


def test_memory_append_multiple(tmp_path):
    m = Memory(tmp_path)
    m.record_attempt("r1", {"ref": "A"}, "ok")
    m.record_attempt("r2", {"ref": "B"}, "ok")
    lines = (tmp_path / "attempts" / "events.jsonl").read_text("utf-8").strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["run_id"] == "r1"
    assert json.loads(lines[1])["run_id"] == "r2"
