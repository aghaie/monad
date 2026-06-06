#!/usr/bin/env python3
"""
Monad — Phase 16 validator: Hub Origin Discovery Engine
=======================================================

Verifies structural integrity, the hub-earns-survival invariant (the hub is
reconstructed/simulated, not protected), statistical completeness, cross-product
consistency, and — with --rebuild — byte-identical reproducibility of
generated/hub_origin/.

Usage:
    python3 scripts/validate_hub_origin.py [--rebuild]
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

OUT = Path("generated/hub_origin")
FILES = [
    "hub_decomposition.json", "hub_reconstruction.json", "hub_necessity.json",
    "hub_uniqueness.json", "hub_simulation.json", "hub_predictability.json",
    "hub_redundancy.json", "hub_falsification.json", "hub_robustness.json",
    "hub_origin_manifest.json",
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
    print("Monad Phase 16 — validating Hub Origin Discovery Engine")

    for f in FILES:
        v.check((OUT / f).exists(), f"missing {f}")
    if v.f:
        print("  aborting")
        sys.exit(1)

    dec = load("hub_decomposition.json")
    rec = load("hub_reconstruction.json")
    nec = load("hub_necessity.json")
    uni = load("hub_uniqueness.json")
    sim = load("hub_simulation.json")
    pred = load("hub_predictability.json")
    red = load("hub_redundancy.json")
    fal = load("hub_falsification.json")
    rob = load("hub_robustness.json")
    man = load("hub_origin_manifest.json")

    for name, obj in [("dec", dec), ("rec", rec), ("nec", nec), ("uni", uni), ("sim", sim),
                      ("pred", pred), ("red", red), ("fal", fal), ("rob", rob), ("man", man)]:
        v.check(obj["method"] == "phase16-hub-origin-1.0", f"{name}.method mismatch")

    # decomposition: frequency predicts dominance; hub rank-1 on key axes
    v.check(abs(dec["hub_activation_share"] - 0.968) < 0.01, "hub share off (expect 0.968)")
    v.check(dec["spearman_marginal_vs"]["degree"] >= 0.9, "frequency does not predict degree")
    v.check(dec["spearman_marginal_vs"]["lexical_frequency"] >= 0.95,
            "frequency not predicted by lexical frequency")
    for axis in ("marginal", "degree", "lexical_frequency"):
        v.check(dec["hub_rank_by_axis"][axis] == 1, f"hub not rank-1 on {axis}")
    v.check("counterfactual_removal" in dec, "counterfactual removal missing")

    # reconstruction: hub is the lexical-frequency rank-1 concept
    v.check(rec["hub_is_lexical_rank1"] is True, "hub is not lexical rank-1 (not reconstructible)")
    v.check(rec["lexical_frequency_rank1"] == "CONCEPT_007", "lexical rank-1 != CONCEPT_007")

    # necessity: Zipf produces a hub, uniform does not
    v.check(nec["root_frequency_distribution"]["heavy_tailed"] is True, "root freq not heavy-tailed")
    v.check(nec["max_concept_share_zipf_roots"] > nec["max_concept_share_uniform_roots"],
            "Zipf does not exceed uniform (necessity not shown)")
    v.check(nec["max_concept_share_uniform_roots"] < 0.5, "uniform produced a strong hub")

    # uniqueness: large gap to next
    v.check(uni["hub_minus_next_gap"] > 0.3, "hub-next gap too small for unique dominance")
    v.check(uni["next_over_hub_ratio"] < 0.6, "next concept too close to hub")

    # simulation: frequency reproduces hub, uniform/topology do not
    v.check(sim["frequency_simulation_max_share"]["mean"] > 0.5, "frequency sim did not make a hub")
    v.check(sim["uniform_simulation_max_share"]["mean"] < sim["frequency_simulation_max_share"]["mean"],
            "uniform sim not weaker than frequency sim")
    v.check(sim["topology_grammar_hub_share_reference"] < 0.1, "topology reference too high")

    # predictability: hub rank-1 from 1%
    v.check(pred["hub_rank1_from_1pct"] is True, "hub not rank-1 from 1%")
    v.check(pred["trajectory"][0]["hub_rank"] == 1, "hub rank != 1 at 1%")

    # falsification: 6 hypotheses; H1 & H5 survive; H2/H3/H4/H6 falsified
    v.check(len(fal["hypotheses"]) == 6, "expected 6 hypotheses")
    surv = set(fal["surviving_hypotheses"])
    v.check("H1" in surv and "H5" in surv, "H1/H5 should survive (frequency-driven)")
    for hid in ("H2", "H3", "H4", "H6"):
        h = next((x for x in fal["hypotheses"] if x["id"] == hid), None)
        v.check(h and "FALSIFIED" in h["result"], f"{hid} should be falsified")
    for h in fal["hypotheses"]:
        v.check(bool(h.get("evidence")), f"{h['id']} lacks evidence")

    # robustness: bootstrap hub top-1
    v.check(rob["bootstrap_runs"] >= 100, "fewer than 100 bootstraps")
    v.check(rob["hub_remains_top1_probability"] >= 0.99, "hub not robustly top-1 under bootstrap")

    # manifest
    t = man["totals"]
    v.check(t["surviving_hypotheses"] == fal["surviving_hypotheses"], "manifest survivor mismatch")
    v.check(t["hub_is_lexical_rank1"] is True, "manifest lexical flag")
    for f in FILES:
        if f in man["output_bytes"]:
            v.check(man["output_bytes"][f] == (OUT / f).stat().st_size,
                    f"manifest output_bytes[{f}] mismatch")

    if args.rebuild:
        print("  --rebuild: hashing, rebuilding, re-hashing …")
        before = {f: hashlib.sha256((OUT / f).read_bytes()).hexdigest() for f in FILES}
        res = subprocess.run([sys.executable, "scripts/build_hub_origin.py"],
                             capture_output=True, text=True)
        v.check(res.returncode == 0, f"rebuild failed: {res.stderr[-400:]}")
        for f in FILES:
            after = hashlib.sha256((OUT / f).read_bytes()).hexdigest()
            v.check(after == before[f], f"{f} not byte-identical after rebuild")

    ok = v.summary()
    print(f"  hub_share={dec['hub_activation_share']} spearman_deg={dec['spearman_marginal_vs']['degree']} "
          f"lexical_rank1={rec['hub_is_lexical_rank1']} freq_sim={sim['frequency_simulation_max_share']['mean']} "
          f"survivors={fal['surviving_hypotheses']}")
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
