# tests/engine/test_attack.py
from engine.workers import get_worker
from engine.workers.base import WorkerRequest


def test_attack_verdicts_present():
    w = get_worker("statistical")
    hin = {"hypotheses": [
        {"hypothesis_id": "h1", "prediction": {"predicate": "cooccurrence_constraint",
         "params": {"with": "x"}}, "supported_by": ["p0"]}],
        "_patterns": [{"pattern_id": "p0", "with": "x", "lift": 4.0, "null_p": 0.01}]}
    out = w.reason(WorkerRequest("attack", hin, "hypothesis"))
    assert out["attacks"][0]["worker_verdict"] in {"SURVIVES", "WEAKENED", "REFUTED"}
    assert out["attacks"][0]["hypothesis_id"] == "h1"


def test_attack_weakened_on_low_lift():
    """پاترنی با lift پایین باید WEAKENED برگرداند."""
    w = get_worker("statistical")
    hin = {"hypotheses": [
        {"hypothesis_id": "h_low", "prediction": {}, "supported_by": ["p_low"]}],
        "_patterns": [{"pattern_id": "p_low", "with": "y", "lift": 1.0, "null_p": 0.01}]}
    out = w.reason(WorkerRequest("attack", hin, "hypothesis"))
    assert out["attacks"][0]["worker_verdict"] == "WEAKENED"


def test_attack_weakened_on_high_null_p():
    """پاترنی با null_p بالا باید WEAKENED برگرداند."""
    w = get_worker("statistical")
    hin = {"hypotheses": [
        {"hypothesis_id": "h_ns", "prediction": {}, "supported_by": ["p_ns"]}],
        "_patterns": [{"pattern_id": "p_ns", "with": "z", "lift": 3.0, "null_p": 0.10}]}
    out = w.reason(WorkerRequest("attack", hin, "hypothesis"))
    assert out["attacks"][0]["worker_verdict"] == "WEAKENED"


def test_attack_survives_strong_pattern():
    """پاترن قوی (lift≥1.5 و null_p≤0.05) باید SURVIVES برگرداند."""
    w = get_worker("statistical")
    hin = {"hypotheses": [
        {"hypothesis_id": "h_ok", "prediction": {}, "supported_by": ["p_ok"]}],
        "_patterns": [{"pattern_id": "p_ok", "with": "w", "lift": 2.0, "null_p": 0.04}]}
    out = w.reason(WorkerRequest("attack", hin, "hypothesis"))
    assert out["attacks"][0]["worker_verdict"] == "SURVIVES"
    assert out["attacks"][0]["refutations"] == []


def test_attack_one_entry_per_hypothesis():
    """تعداد entries در attacks باید برابر تعداد hypotheses باشد."""
    w = get_worker("statistical")
    hin = {"hypotheses": [
        {"hypothesis_id": "h1", "prediction": {}, "supported_by": []},
        {"hypothesis_id": "h2", "prediction": {}, "supported_by": []},
    ], "_patterns": []}
    out = w.reason(WorkerRequest("attack", hin, "hypothesis"))
    assert len(out["attacks"]) == 2
    assert out["attacks"][0]["hypothesis_id"] == "h1"
    assert out["attacks"][1]["hypothesis_id"] == "h2"


def test_attack_no_supported_by_survives():
    """فرضیه‌ای بدون supported_by باید SURVIVES برگرداند (هیچ پاترنی رد نکرده)."""
    w = get_worker("statistical")
    hin = {"hypotheses": [
        {"hypothesis_id": "h_empty", "prediction": {}, "supported_by": []}],
        "_patterns": []}
    out = w.reason(WorkerRequest("attack", hin, "hypothesis"))
    assert out["attacks"][0]["worker_verdict"] == "SURVIVES"
