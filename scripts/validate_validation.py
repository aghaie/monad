#!/usr/bin/env python3
"""
Monad — Phase 11 validator: Discovery Stability & Robustness Engine
==================================================================

Verifies structural integrity, statistical-completeness (means / medians / std /
CIs are present, not just point estimates), the no-protection invariant (every
survivor classification carries evidence and a probability/summary), and — with
--rebuild — byte-identical reproducibility of generated/validation/.

Usage:
    python3 scripts/validate_validation.py [--rebuild]
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

OUT = Path("generated/validation")
FILES = [
    "threshold_sweeps.json", "bootstrap_results.json", "subsampling_results.json",
    "noise_results.json", "hub_validation.json", "motif_validation.json",
    "consistency_validation.json", "reproducibility_audit.json",
    "survivor_analysis.json", "validation_manifest.json",
]
SUMMARY_KEYS = {"n", "mean", "median", "std", "ci95_low", "ci95_high", "min", "max"}


class V:
    def __init__(self):
        self.p = 0
        self.f = 0

    def check(self, cond, msg):
        if cond:
            self.p += 1
        else:
            self.f += 1
            print(f"  ✗ FAIL: {msg}")

    def summary(self):
        print(f"\n  {self.p}/{self.p + self.f} checks passed.")
        return self.f == 0


def load(name):
    return json.loads((OUT / name).read_text("utf-8"))


def is_summary(d):
    return isinstance(d, dict) and SUMMARY_KEYS.issubset(set(d.keys()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true")
    args = ap.parse_args()
    v = V()
    print("Monad Phase 11 — validating Discovery Stability & Robustness Engine")

    for f in FILES:
        v.check((OUT / f).exists(), f"missing output {f}")
    if v.f:
        print("  aborting: outputs missing")
        sys.exit(1)

    ts = load("threshold_sweeps.json")
    boot = load("bootstrap_results.json")
    sub = load("subsampling_results.json")
    noise = load("noise_results.json")
    hub = load("hub_validation.json")
    motif = load("motif_validation.json")
    consist = load("consistency_validation.json")
    repro = load("reproducibility_audit.json")
    surv = load("survivor_analysis.json")
    man = load("validation_manifest.json")

    for name, obj in [("ts", ts), ("boot", boot), ("sub", sub), ("noise", noise),
                      ("hub", hub), ("motif", motif), ("consist", consist),
                      ("repro", repro), ("surv", surv), ("man", man)]:
        v.check(obj["method"] == "phase11-validation-1.0", f"{name}.method mismatch")

    # statistical completeness: bootstrap summaries carry full stats
    v.check(boot["runs"] == 1000, "bootstrap runs != 1000")
    for k in ("hub_share", "top5_concept_jaccard", "top10_concept_jaccard", "active_concept_count"):
        v.check(is_summary(boot[k]), f"bootstrap {k} missing full statistics")
        v.check(boot[k]["n"] == 1000, f"bootstrap {k} n != 1000")
    # subsampling: 5 levels x 100, full summaries
    v.check(len(sub["levels"]) == 5, "subsampling != 5 levels")
    for lk, lv in sub["levels"].items():
        v.check(lv["repeats"] == 100, f"{lk} repeats != 100")
        v.check(is_summary(lv["hub_share"]), f"{lk} hub_share missing stats")
        v.check(0.0 <= lv["hub_remains_top1_probability"] <= 1.0, f"{lk} top1 prob range")

    # hub validation — the headline robustness claim
    v.check(hub["challenged"] == "CONCEPT_007", "hub not CONCEPT_007")
    v.check(hub["remains_top1_marginal_probability_overall"] == 1.0,
            "hub does not always remain top-1 (report honestly if changed)")
    v.check(hub["min_observed_share_across_all_perturbations"] > 0.5,
            "hub min share collapsed below 0.5")
    v.check(len(hub["bootstrap_share_ci95"]) == 2, "hub CI malformed")

    # motif validation — vocabulary stability
    v.check(motif["canonical"]["triad_classes"] == 13, "canonical triad classes != 13")
    for reg in noise["regimes"].values():
        for lvl in reg.values():
            v.check(is_summary(lvl["n_triad_classes"]), "noise n_triad_classes missing stats")
            v.check(is_summary(lvl["largest_scc_size"]), "noise scc missing stats")

    # consistency validation
    v.check(consist["surviving_contradictions_under_all_regimes"] == 0,
            "a contradiction appeared under some regime (report honestly)")
    v.check(consist["max_exclusion_positive_overlap"] == 0,
            "exclusion/positive overlap appeared under threshold sweep")

    # reproducibility
    v.check(repro["all_byte_identical"] is True, "not all rebuilt engines byte-identical")
    v.check(repro["n_engines_rebuilt"] >= 5, "fewer than 5 engines rebuilt")
    for name, a in repro["audits"].items():
        if a["rebuilt_ok"]:
            v.check(a["byte_identical"] is True, f"{name} not byte-identical: {a['mismatched_files']}")

    # survivor analysis — no-protection invariant
    scale = ["SURVIVES STRONGLY", "SURVIVES MODERATELY", "SURVIVES WEAKLY", "FAILS"]
    v.check(len(surv["survivors"]) >= 8, "fewer than 8 discoveries classified")
    for k, s in surv["survivors"].items():
        v.check(s["classification"] in scale, f"{k} bad classification")
        v.check("evidence" in s and s["evidence"], f"{k} classification without evidence")
    tally_sum = sum(surv["tally"].values())
    v.check(tally_sum == len(surv["survivors"]), "tally does not sum to survivor count")
    # consistency between survivor verdicts and the measured probabilities
    v.check(surv["survivors"]["CONCEPT_007_dominance"]["classification"] == "SURVIVES STRONGLY",
            "hub not classified STRONGLY despite prob 1.0")

    # manifest
    t = man["totals"]
    v.check(t["hub_remains_top1_overall"] == hub["remains_top1_marginal_probability_overall"],
            "manifest hub mismatch")
    v.check(t["all_byte_identical"] == repro["all_byte_identical"], "manifest repro mismatch")
    for f in FILES:
        if f in man["output_bytes"]:
            v.check(man["output_bytes"][f] == (OUT / f).stat().st_size,
                    f"manifest output_bytes[{f}] mismatch")

    if args.rebuild:
        print("  --rebuild: hashing, rebuilding, re-hashing (runs nested engine rebuilds) …")
        before = {f: hashlib.sha256((OUT / f).read_bytes()).hexdigest() for f in FILES}
        res = subprocess.run([sys.executable, "scripts/build_validation.py"],
                             capture_output=True, text=True)
        v.check(res.returncode == 0, f"rebuild failed: {res.stderr[-400:]}")
        for f in FILES:
            after = hashlib.sha256((OUT / f).read_bytes()).hexdigest()
            v.check(after == before[f], f"{f} not byte-identical after rebuild")

    ok = v.summary()
    print(f"  hub_top1={hub['remains_top1_marginal_probability_overall']} "
          f"contradictions_all_regimes={consist['surviving_contradictions_under_all_regimes']} "
          f"reproducible={repro['all_byte_identical']} tally={surv['tally']}")
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
