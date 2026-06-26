"""ClaudeWorker — اتصالِ مدل از طریقِ Skill-0001. در v1 از پاسخِ آماده می‌خواند."""
import json
from pathlib import Path
from engine.workers.base import ReasoningWorker, WorkerRequest


class ClaudeWorker(ReasoningWorker):
    name = "ClaudeWorker"

    def __init__(self, response_dir=None):
        self.response_dir = Path(response_dir) if response_dir else None

    def reason(self, request: WorkerRequest) -> dict:
        if self.response_dir and (self.response_dir / f"{request.capability}.json").exists():
            return json.loads(
                (self.response_dir / f"{request.capability}.json").read_text("utf-8"))
        raise NotImplementedError(
            "ClaudeWorker در مسیرِ خودکار نیاز به Skill-0001 دارد؛ "
            "از --worker statistical برای اجرای بی‌دخالت استفاده کن.")
