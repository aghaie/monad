"""تستِ Benchmark شش‌بُعدی + قاعدهٔ پارتو."""
from engine.benchmark import score


def test_pareto_rule():
    a = {"Recoverability": .5, "Reproducibility": 1, "Falsifiability": .8,
         "Compression": .5, "Coherence": 1, "PredictivePower": .6}
    b = dict(a); b["Recoverability"] = .4
    assert score.pareto_dominates(a, b) is True
    assert score.pareto_dominates(b, a) is False
    assert score.pareto_dominates(a, a) is False  # برابر → غلبه نیست


def test_score_keys_present(tmp_path):
    # یک run کاملِ from-scratch
    from engine import orchestrator
    res = orchestrator.run("quran-root", "علم", run_root=tmp_path)
    from domains.quran_root import adapter
    import json
    from pathlib import Path
    redteam_path = Path(__file__).resolve().parents[2] / "engine" / "benchmark" / "redteam" / "Elm.json"
    redteam = json.loads(redteam_path.read_text("utf-8"))
    vec = score.score_run(res["run_dir"], adapter,
                          adapter.resolve_unit("علم"), redteam=redteam)
    assert set(vec) == {"Recoverability", "Reproducibility", "Falsifiability",
                        "Compression", "Coherence", "PredictivePower"}
    assert all(0 <= v <= 1 for v in vec.values())
