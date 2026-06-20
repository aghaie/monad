#!/usr/bin/env python3
"""
Phase F1 — The "consistent" leg of the author's CFS claim.

Claim component: "the Quran is internally CONSISTENT."
We do NOT take this on faith; we read it off the repo's validated consistency layer
(Phase-10) and semantics layer (L8), which were built by self-prediction and leakage
control. F1 aggregates those validated outputs into a graded verdict + one fresh
confirmation (the surviving-contradiction rate vs the number of relations tested).
"""
import json

C  = json.load(open("generated/consistency/consistency_scores.json"))
PC = json.load(open("generated/consistency/proposition_conflicts.json"))
SC = json.load(open("generated/semantics/semantic_consistency.json"))
CM = json.load(open("generated/compression/compression_statistics.json"))

n_concepts = CM["n_concepts"]
n_relations = CM["n_relations"]
gci = C["global_consistency_index"]
mean_stab = C["mean_stability"]
necessity_conflicts = PC["n_necessity_conflicts"]
tendency_falsified = PC["n_tendency_candidates_falsified"]
n_stable, n_total = SC["n_stable"], SC["n_concepts"]
mean_drift = SC["drift_distribution"]["mean"]

# fresh confirmation: surviving genuine contradictions per 1000 relations tested
contradiction_rate = necessity_conflicts / (n_relations/1000.0)

# graded verdict
checks = {
  "global_consistency_index>=0.9": gci >= 0.9,
  "zero_genuine_proposition_contradictions": necessity_conflicts == 0,
  "majority_concepts_semantically_stable": n_stable/n_total >= 0.8,
}
passed = sum(checks.values())

res = {
  "leg": "consistent",
  "evidence": {
    "global_consistency_index": gci,
    "mean_stability": mean_stab,
    "n_relations_tested": n_relations,
    "genuine_proposition_contradictions_surviving": necessity_conflicts,
    "tendency_candidates_falsified": tendency_falsified,
    "surviving_contradictions_per_1000_relations": round(contradiction_rate, 4),
    "concepts_semantically_stable": f"{n_stable}/{n_total}",
    "mean_cross_half_neighbour_cosine": round(mean_drift, 3),
  },
  "checks": checks,
  "checks_passed": f"{passed}/{len(checks)}",
  "verdict": ("SUPPORTED — the Quran's relational/semantic network is internally "
              "consistent to a high degree (0 surviving genuine contradictions across "
              f"{n_relations} relations; consistency index {gci:.2f}).")
             if passed == len(checks) else "PARTIAL / NOT SUPPORTED",
}
json.dump(res, open("generated/book-quran-audit/f1_consistency.json","w"),
          ensure_ascii=False, indent=2)
print(json.dumps(res, ensure_ascii=False, indent=2))
