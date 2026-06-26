import json
import pytest
from engine.workers.claude import ClaudeWorker
from engine.workers.base import WorkerRequest


def test_claude_reads_prepared_response(tmp_path):
    d = tmp_path / "_claude"
    d.mkdir()
    (d / "observe.json").write_text(json.dumps({"observations": []}), "utf-8")
    w = ClaudeWorker(response_dir=d)
    assert w.reason(WorkerRequest("observe", {}, "cluster")) == {"observations": []}


def test_claude_without_response_raises():
    w = ClaudeWorker(response_dir=None)
    with pytest.raises(NotImplementedError):
        w.reason(WorkerRequest("observe", {}, "cluster"))
