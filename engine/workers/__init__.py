# (خالی — package marker)
from engine.workers.statistical import StatisticalWorker


def get_worker(name, **kw):
    if name in ("statistical", "StatisticalWorker"):
        return StatisticalWorker()
    if name in ("human", "HumanWorker"):
        from engine.workers.human import HumanWorker
        return HumanWorker(kw["fixture_dir"])
    if name in ("claude", "ClaudeWorker"):
        from engine.workers.claude import ClaudeWorker
        return ClaudeWorker()
    raise ValueError(f"unknown worker: {name}")
