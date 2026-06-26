import json
from pathlib import Path
from engine.workers.base import ReasoningWorker, WorkerRequest


class HumanWorker(ReasoningWorker):
    name = "HumanWorker"

    def __init__(self, fixture_dir):
        self.fixture_dir = Path(fixture_dir)

    def reason(self, request: WorkerRequest) -> dict:
        p = self.fixture_dir / f"{request.capability}.json"
        return json.loads(p.read_text(encoding="utf-8"))
