"""مرحلهٔ ۶ — دروازهٔ قطعی. تنها زایندهٔ Knowledge (R1)."""
from engine.predicates import registry


def _tier(result):
    s = result.get("lift", result.get("score", 0)) or 0
    if s >= 3.0:
        return "صریح"
    if s >= 1.8:
        return "قوی"
    return "محتمل"


def run(hypotheses, attacks, unit, adapter):
    verifications = []
    for i, h in enumerate(hypotheses):
        pred = h["prediction"]["predicate"]
        if not registry.known(pred):
            verifications.append({"hypothesis_id": h["hypothesis_id"],
                                  "decision": "UNKNOWN", "confidence_tier": None,
                                  "knowledge_id": None,
                                  "tests": {"error": "unknown predicate"}})
            continue
        res = adapter.execute_predicate(pred, h["prediction"].get("params", {}), unit)
        if res["passed"]:
            verifications.append({
                "hypothesis_id": h["hypothesis_id"], "decision": "ACCEPTED",
                "confidence_tier": _tier(res), "knowledge_id": f"k_{unit['ref']}_{i}",
                "tests": {pred: res}})
        else:
            verifications.append({
                "hypothesis_id": h["hypothesis_id"], "decision": "REJECTED",
                "confidence_tier": None, "knowledge_id": None,
                "tests": {pred: res}})
    return {"verifications": verifications}
