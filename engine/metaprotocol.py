"""Meta-Protocol — نسخه‌بندی و ارتقای پروتکل با غلبهٔ پارتو."""
import json
from pathlib import Path
from engine.benchmark.score import pareto_dominates


def evaluate_candidate(candidate_version, score_vec, registry_path):
    """ارزیابی نامزد نسخه و ارتقا بر اساس غلبهٔ پارتو.

    Args:
        candidate_version: رشتهٔ نسخه (مثلاً "0.1.0")
        score_vec: دیکشنری شش‌بُعدی امتیاز
        registry_path: مسیر فایل registry.json

    Returns:
        dict با کلیدهای "promoted" (bool) و "current_stable" (str|None)
    """
    reg = json.loads(Path(registry_path).read_text("utf-8"))
    cur = reg.get("current_stable")
    promoted = False
    if cur is None:
        promoted = True
    else:
        promoted = pareto_dominates(score_vec, reg["versions"][cur]["score"])
    reg["versions"][candidate_version] = {
        "score": score_vec, "status": "stable" if promoted else "candidate"}
    if promoted:
        if cur and cur in reg["versions"]:
            reg["versions"][cur]["status"] = "superseded"
        reg["current_stable"] = candidate_version
    Path(registry_path).write_text(json.dumps(reg, ensure_ascii=False, indent=2), "utf-8")
    return {"promoted": promoted, "current_stable": reg["current_stable"]}
