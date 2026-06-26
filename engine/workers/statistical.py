"""Workerِ قطعیِ پیش‌فرض — مشاهده‌ها را از آمارِ خوشه/الگو با قواعدِ ثابت می‌سازد."""
from engine.workers.base import ReasoningWorker, WorkerRequest


class StatisticalWorker(ReasoningWorker):
    name = "StatisticalWorker"

    def reason(self, request: WorkerRequest) -> dict:
        return getattr(self, f"_{request.capability}")(request.input_payload)

    def _observe(self, cpay):
        obs = []
        for c in cpay["clusters"]:
            obs.append({
                "observation_id": f"o_{c['cluster_id']}",
                "type": "description",
                "statement": f"{c['size']} رخداد با امضای {c['signature']}.",
                "cites": [c["cluster_id"]],
            })
        for p in cpay["patterns"][:10]:
            obs.append({
                "observation_id": f"o_{p['pattern_id']}",
                "type": "description",
                "statement": f"هم‌آییِ پایدار با «{p['with']}» (lift={p['lift']}).",
                "cites": [p["pattern_id"]],
            })
        return {"observations": obs}
