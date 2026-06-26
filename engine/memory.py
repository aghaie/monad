"""Monad Memory — تاریخِ تلاش‌ها (افزایشی، فقط‌نوشتنی)."""
import json
from pathlib import Path


class Memory:
    def __init__(self, root):
        self.root = Path(root)
        for sub in ("attempts", "rejected", "failed_runs", "abandoned", "discoveries"):
            (self.root / sub).mkdir(parents=True, exist_ok=True)

    def _append(self, sub, event):
        with open(self.root / sub / "events.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def record_attempt(self, run_id, unit, status):
        self._append("attempts", {"run_id": run_id, "unit": unit, "status": status})

    def record_rejected(self, run_id, hyp_id, reason):
        self._append("rejected", {"run_id": run_id, "hypothesis_id": hyp_id,
                                  "reason": reason})

    def record_failed_run(self, run_id, error):
        self._append("failed_runs", {"run_id": run_id, "error": str(error)})

    def record_discovery(self, run_id, knowledge_ids):
        self._append("discoveries", {"run_id": run_id, "knowledge_ids": knowledge_ids})
