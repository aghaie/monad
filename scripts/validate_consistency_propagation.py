#!/usr/bin/env python3
"""
Monad — Phase 15 validator: Consistency Propagation Engine
==========================================================

Verifies structural integrity, the destruction-was-attempted invariant (structural
removals, null shuffles, and data corruption are all run), the not-protected
invariant (every hypothesis carries an explicit result, and the survivor is
backed by the null/corruption evidence), and — with --rebuild — byte-identical
reproducibility of generated/consistency_propagation/.

Usage:
    python3 scripts/validate_consistency_propagation.py [--rebuild]
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

OUT = Path("generated/consistency_propagation")
FILES = [
    "consistency_support.json", "hub_dependence.json", "consistency_core.json",
    "consistency_pathways.json", "motif_contribution.json", "recursive_stability.json",
    "redundancy_contribution.json", "counterfactual_destruction.json",
    "generative_consistency.json", "hypothesis_falsification.json",
    "consistency_propagation_manifest.json",
]


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true")
    args = ap.parse_args()
    v = V()
    print("Monad Phase 15 — validating Consistency Propagation Engine")

    for f in FILES:
        v.check((OUT / f).exists(), f"missing {f}")
    if v.f:
        print("  aborting")
        sys.exit(1)

    sup = load("consistency_support.json")
    hub = load("hub_dependence.json")
    core = load("consistency_core.json")
    path = load("consistency_pathways.json")
    motif = load("motif_contribution.json")
    rec = load("recursive_stability.json")
    red = load("redundancy_contribution.json")
    cf = load("counterfactual_destruction.json")
    gen = load("generative_consistency.json")
    fal = load("hypothesis_falsification.json")
    man = load("consistency_propagation_manifest.json")

    for name, obj in [("sup", sup), ("hub", hub), ("core", core), ("path", path), ("motif", motif),
                      ("rec", rec), ("red", red), ("cf", cf), ("gen", gen), ("fal", fal),
                      ("man", man)]:
        v.check(obj["method"] == "phase15-consistency-propagation-1.0", f"{name}.method mismatch")

    # base consistency
    v.check(sup["base_contradictions"]["total"] == 0, "base contradictions != 0")

    # Phase A: no structure supports consistency; hub mediates necessity
    v.check(sup["max_consistency_support_weight"] == 0, "a structure has positive support weight")
    v.check(sup["n_concepts_with_positive_support"] == 0, "some concept removal increases contradictions")
    v.check(abs(sup["hub_necessity_mediation_share"] - 0.96) < 0.05, "hub mediation share off")

    # Phase B: hub removal does not break consistency
    v.check(hub["contradictions_without_hub"]["total"] == 0, "hub removal created contradictions")
    v.check(hub["consistency_retained"] is True, "consistency not retained without hub")

    # Phase C: no core
    v.check(core["consistency_core_exists"] is False, "a consistency core was claimed")
    v.check(core["minimum_inconsistent_subset_found"] is False, "an inconsistent subset was found")

    # Phase E/F: no motif/SCC maintains consistency
    v.check(motif["max_contradictions_created"] == 0, "a motif removal created contradictions")
    v.check(rec["max_contradictions_created"] == 0, "an SCC removal created contradictions")
    v.check(rec["any_scc_self_negating"] is False, "an SCC is self-negating")

    # Phase H: destruction was actually attempted (three modes), and only corruption works
    v.check(cf["structural_removals_break_consistency"] is False,
            "a structural removal broke consistency (report honestly)")
    v.check(len(cf["structural_removals"]) >= 4, "fewer than 4 structural removals attempted")
    v.check(cf["null_model_runs"] >= 30, "fewer than 30 null runs")
    v.check(cf["null_model_contradictions"]["max"] == 0.0, "null model produced contradictions")
    # corruption curve: contradictions monotone non-decreasing with rate, 0 at rate 0, >0 at rate 1
    cc = cf["corruption_curve"]
    vals = [c["contradictions"] for c in cc]
    v.check(vals == sorted(vals), "corruption curve not monotone")
    v.check(cc[0]["corruption_rate"] == 0.0 and cc[0]["contradictions"] == 0, "corruption at rate 0 != 0")
    v.check(cc[-1]["contradictions"] > 0, "full corruption did not break consistency")

    # Phase I: grammar independence
    v.check(gen["consistency_generable_by_grammar"] is False, "consistency claimed grammar-generable")

    # Phase J: 7 hypotheses, only H7 survives, backed by null/corruption evidence
    v.check(len(fal["hypotheses"]) == 7, "expected 7 hypotheses")
    survived = [h for h in fal["hypotheses"] if h["result"] == "SURVIVES"]
    v.check(len(survived) == 1 and survived[0]["id"] == "H7", "survivor is not exactly H7")
    v.check(fal["surviving_hypotheses"] == ["H7"], "surviving list != [H7]")
    for h in fal["hypotheses"]:
        if h["result"] != "SURVIVES":
            v.check("FALSIFIED" in h["result"], f"{h['id']} not falsified or survived")
        v.check(bool(h.get("evidence")), f"{h['id']} lacks evidence")

    # manifest
    t = man["totals"]
    v.check(t["surviving_hypotheses"] == ["H7"], "manifest survivor mismatch")
    v.check(t["structural_removals_break_consistency"] is False, "manifest removal flag")
    for f in FILES:
        if f in man["output_bytes"]:
            v.check(man["output_bytes"][f] == (OUT / f).stat().st_size,
                    f"manifest output_bytes[{f}] mismatch")

    if args.rebuild:
        print("  --rebuild: hashing, rebuilding, re-hashing …")
        before = {f: hashlib.sha256((OUT / f).read_bytes()).hexdigest() for f in FILES}
        res = subprocess.run([sys.executable, "scripts/build_consistency_propagation.py"],
                             capture_output=True, text=True)
        v.check(res.returncode == 0, f"rebuild failed: {res.stderr[-400:]}")
        for f in FILES:
            after = hashlib.sha256((OUT / f).read_bytes()).hexdigest()
            v.check(after == before[f], f"{f} not byte-identical after rebuild")

    ok = v.summary()
    print(f"  base_contradictions={sup['base_contradictions']['total']} "
          f"hub_mediation={sup['hub_necessity_mediation_share']} "
          f"null_max={cf['null_model_contradictions']['max']} survivor={fal['surviving_hypotheses']}")
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
