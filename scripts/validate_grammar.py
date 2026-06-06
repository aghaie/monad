#!/usr/bin/env python3
"""
Monad — Phase 12 validator: Generative Grammar Discovery Engine
==============================================================

Verifies structural integrity, the simulation-confirms-generation invariant
(every generation claim is backed by a simulated metric), statistical
completeness (CIs present), ablation/falsification consistency, and — with
--rebuild — byte-identical reproducibility of generated/grammar/.

Usage:
    python3 scripts/validate_grammar.py [--rebuild]
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

OUT = Path("generated/grammar")
FILES = [
    "rule_candidates.json", "rule_statistics.json", "rule_generation.json",
    "rule_simulation.json", "rule_ablation.json", "rule_falsification.json",
    "rule_robustness.json", "grammar_manifest.json",
]
SUMMARY_KEYS = {"n", "mean", "std", "ci95_low", "ci95_high", "min", "max"}


class V:
    def __init__(self):
        self.p = 0
        self.f = 0

    def check(self, c, m):
        if c:
            self.p += 1
        else:
            self.f += 1
            print(f"  ✗ FAIL: {m}")

    def summary(self):
        print(f"\n  {self.p}/{self.p + self.f} checks passed.")
        return self.f == 0


def load(n):
    return json.loads((OUT / n).read_text("utf-8"))


def is_summary(d):
    return isinstance(d, dict) and SUMMARY_KEYS.issubset(set(d.keys()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true")
    args = ap.parse_args()
    v = V()
    print("Monad Phase 12 — validating Generative Grammar Discovery Engine")

    for f in FILES:
        v.check((OUT / f).exists(), f"missing {f}")
    if v.f:
        print("  aborting: outputs missing")
        sys.exit(1)

    cand = load("rule_candidates.json")
    stat = load("rule_statistics.json")
    gen = load("rule_generation.json")
    sim = load("rule_simulation.json")
    abl = load("rule_ablation.json")
    fal = load("rule_falsification.json")
    rob = load("rule_robustness.json")
    man = load("grammar_manifest.json")

    for name, obj in [("cand", cand), ("stat", stat), ("gen", gen), ("sim", sim),
                      ("abl", abl), ("fal", fal), ("rob", rob), ("man", man)]:
        v.check(obj["method"] == "phase12-grammar-1.0", f"{name}.method mismatch")

    # rules: opaque ids, measured parameters
    v.check(cand["n_rules"] == 3, "expected 3 rules")
    for rid, rec in cand["rules"].items():
        v.check(rid.startswith("RULE_"), f"{rid} not opaque")
        v.check("transformation" in rec and "measured_parameter" in rec,
                f"{rid} missing transformation/measured_parameter")
    v.check(cand["measured_targets"]["N"] == 100, "N != 100")
    v.check(cand["measured_targets"]["M"] == 1059, "M != 1059")
    v.check(cand["measured_targets"]["triad_classes"] == 13, "observed classes != 13")

    # simulation: statistical completeness + the invariant
    v.check(sim["sim_runs"] == 30, "sim_runs != 30")
    for k in ("reciprocity", "transitivity", "hub_share", "n_classes", "triad_cosine", "largest_scc"):
        v.check(is_summary(sim["simulated"][k]), f"sim {k} missing full stats")
    cos = sim["simulated"]["triad_cosine"]
    v.check(0.0 <= cos["mean"] <= 1.0, "triad cosine out of range")
    v.check(cos["mean"] >= 0.8, "triad cosine below 0.8 (local generation should hold)")
    v.check(sim["simulated"]["n_classes"]["mean"] == 13.0, "not all 13 classes reproduced")
    # generation only claimed where simulation confirms
    ga = sim["generation_accuracy"]
    v.check(ga["motif_classes_reproduced"] == 1.0, "motif classes reproduction != 1.0")
    v.check(ga["hub_share_ratio"] < 0.8, "hub ratio claims generation but should be falsified")

    # generation report consistency
    v.check(gen["local_generation"]["verdict"].startswith("GENERATED"),
            "local generation not marked GENERATED")
    v.check(gen["global_generation"]["hub_generated"] is False,
            "hub wrongly marked generated")
    v.check(gen["global_generation"]["consistency_generated"] is False,
            "consistency wrongly marked generated")

    # minimum sets: attachment-only < full; reciprocity is the key addition
    curve = stat["cumulative_curve"]
    v.check(curve[0]["n_rules"] == 1 and curve[-1]["n_rules"] == 3, "curve rule counts off")
    v.check(curve[1]["triad_cosine"]["mean"] >= curve[0]["triad_cosine"]["mean"],
            "adding reciprocity did not help cosine")

    # ablation: importance ranking sorted by cosine drop; most-important consistent
    ranking = abl["importance_ranking"]
    drops = [abl["ablations"][r]["cosine_drop"] for r in ranking]
    v.check(drops == sorted(drops, reverse=True), "ablation ranking not by cosine drop")
    v.check(abl["most_important_rule"] == ranking[0], "most_important_rule mismatch")

    # falsification: motif survives, hub falsified
    results = {t.get("claim", ""): t["result"] for t in fal["tests"]}
    motif_claim = next((t for t in fal["tests"] if "13-class" in t["claim"]), None)
    hub_claim = next((t for t in fal["tests"] if "hub dominance" in t["claim"]), None)
    v.check(motif_claim and motif_claim["result"] == "SURVIVES", "motif claim should survive")
    v.check(hub_claim and "FALSIFIED" in hub_claim["result"], "hub claim should be falsified")
    v.check(fal["n_survived"] >= 1, "no generation claim survived")

    # robustness: parameter stability summaries
    for k in ("reciprocity", "transitivity", "hub_share"):
        v.check(is_summary(rob["parameter_stability"][k]), f"robustness {k} missing stats")

    # manifest
    t = man["totals"]
    v.check(t["n_rules"] == 3, "manifest n_rules")
    v.check(t["local_generation"] == "confirmed", "manifest local generation")
    v.check(t["global_hub_generation"] == "falsified", "manifest hub generation")
    for f in FILES:
        if f in man["output_bytes"]:
            v.check(man["output_bytes"][f] == (OUT / f).stat().st_size,
                    f"manifest output_bytes[{f}] mismatch")

    if args.rebuild:
        print("  --rebuild: hashing, rebuilding, re-hashing …")
        before = {f: hashlib.sha256((OUT / f).read_bytes()).hexdigest() for f in FILES}
        res = subprocess.run([sys.executable, "scripts/build_grammar.py"],
                             capture_output=True, text=True)
        v.check(res.returncode == 0, f"rebuild failed: {res.stderr[-400:]}")
        for f in FILES:
            after = hashlib.sha256((OUT / f).read_bytes()).hexdigest()
            v.check(after == before[f], f"{f} not byte-identical after rebuild")

    ok = v.summary()
    print(f"  rules={cand['n_rules']} triad_cosine={cos['mean']} hub_ratio={ga['hub_share_ratio']} "
          f"most_important={abl['most_important_rule']} survived={fal['n_survived']}")
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
