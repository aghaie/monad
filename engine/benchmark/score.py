"""Benchmark شش‌بُعدی + قاعدهٔ پارتو."""
import json
import tempfile
from pathlib import Path

DIMS = ["Recoverability", "Reproducibility", "Falsifiability",
        "Compression", "Coherence", "PredictivePower"]


def _art(run_dir, idx, name):
    return json.loads((Path(run_dir) / f"0{idx}_{name}.json").read_text("utf-8"))


def score_run(run_dir, adapter, unit, redteam=None, n_repro=2):
    reduce_p = _art(run_dir, 7, "reduce")["payload"]
    graph_p = _art(run_dir, 8, "graph")["payload"]
    verify_p = _art(run_dir, 6, "verify")["payload"]

    # Recoverability — از خروجیِ compression
    recover = float(reduce_p["compression"]["predicts_heldout"]["score"])
    recover = max(0.0, min(1.0, recover))

    # Reproducibility — اجرای مجدد و Jaccardِ knowledge_idهای ACCEPTED
    from engine import orchestrator
    base = {v["knowledge_id"] for v in verify_p["verifications"]
            if v["decision"] == "ACCEPTED"}
    agree = 1.0
    if base:
        with tempfile.TemporaryDirectory() as td:
            r2 = orchestrator.run(unit["domain"], unit["display"], run_root=td)
            v2 = _art(r2["run_dir"], 6, "verify")["payload"]
            s2 = {v["knowledge_id"] for v in v2["verifications"]
                  if v["decision"] == "ACCEPTED"}
            inter = len(base & s2)
            uni = len(base | s2)
            agree = inter / uni if uni else 1.0

    # Falsifiability — نسبتِ red-team که REJECTED شد
    rt = redteam or {"false_hypotheses": []}
    fp = 0
    for h in rt["false_hypotheses"]:
        params = dict(h["prediction"]["params"])
        if params.get("with_root_id") is None and params.get("with_arabic"):
            params["with_root_id"] = adapter.resolve_unit(params["with_arabic"])["unit_id"]
        res = adapter.execute_predicate(h["prediction"]["predicate"], params, unit)
        if not res["passed"]:
            fp += 1
    fals = fp / len(rt["false_hypotheses"]) if rt["false_hypotheses"] else 1.0

    # Compression — coverage
    comp = float(reduce_p["compression"]["coverage"])

    # Coherence — گذشتن از network_coherence
    coher = 1.0 if graph_p["network_coherence"]["passed"] else 0.0

    # PredictivePower — امتیازِ predictive_check
    pred = float(graph_p["predictive_check"]["score"])

    return {
        "Recoverability": round(recover, 4),
        "Reproducibility": round(agree, 4),
        "Falsifiability": round(fals, 4),
        "Compression": round(comp, 4),
        "Coherence": round(coher, 4),
        "PredictivePower": round(pred, 4),
    }


def pareto_dominates(a, b) -> bool:
    """a بر b غلبه می‌کند اگر در همهٔ ابعاد a≥b و در حداقل یک بُعد a>b."""
    ge = all(a[d] >= b[d] for d in DIMS)
    gt = any(a[d] > b[d] for d in DIMS)
    return ge and gt
