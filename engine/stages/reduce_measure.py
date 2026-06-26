"""مرحلهٔ ۷ — تعریفِ کمینه: Worker پیشنهاد می‌دهد، کد می‌سنجد."""
import math


def run(proposed, verifications, unit, adapter):
    pdef = proposed["proposed_definition"]
    prims = pdef.get("primitives", [])
    accepted = [v for v in verifications if v.get("decision") == "ACCEPTED"]
    coverage = round(len(accepted) / len(verifications), 4) if verifications else 0.0
    mdl_bits = round(len(prims) * math.log2(max(len(prims), 1) + 1), 3)
    heldout = adapter.execute_predicate("masked_recovery", {}, unit)
    gate = coverage >= 0.5 and len(prims) >= 1
    return {
        "proposed_definition": pdef,
        "compression": {
            "n_primitives": len(prims),
            "coverage": coverage,
            "mdl_bits": mdl_bits,
            "predicts_heldout": {
                "score": heldout["score"],
                "passed": heldout["passed"],
            },
        },
        "accepted_definition": (
            {
                "statement": pdef.get("statement", ""),
                "primitives": prims,
                "covers_knowledge": [v["knowledge_id"] for v in accepted],
            }
            if gate
            else {"statement": "UNKNOWN", "primitives": [], "covers_knowledge": []}
        ),
    }
