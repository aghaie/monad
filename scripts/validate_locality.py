#!/usr/bin/env python3
"""
Monad — Phase 14 validator: Structural Locality & Distribution Engine
====================================================================

Verifies structural integrity, the regions-from-structure-only invariant (regions
are clusters of fingerprints, members are surah numbers, no names/labels),
statistical completeness, cross-product consistency, and — with --rebuild —
byte-identical reproducibility of generated/locality/.

Usage:
    python3 scripts/validate_locality.py [--rebuild]
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

OUT = Path("generated/locality")
FILES = [
    "density_maps.json", "structural_fingerprints.json", "region_candidates.json",
    "region_similarity.json", "specialization_analysis.json", "ablation_analysis.json",
    "redundancy_analysis.json", "inequality_metrics.json", "locality_analysis.json",
    "falsification_results.json", "robustness_results.json", "locality_manifest.json",
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
    print("Monad Phase 14 — validating Structural Locality & Distribution Engine")

    for f in FILES:
        v.check((OUT / f).exists(), f"missing {f}")
    if v.f:
        print("  aborting")
        sys.exit(1)

    dens = load("density_maps.json")
    fp = load("structural_fingerprints.json")
    reg = load("region_candidates.json")
    sim = load("region_similarity.json")
    spec = load("specialization_analysis.json")
    abl = load("ablation_analysis.json")
    red = load("redundancy_analysis.json")
    ineq = load("inequality_metrics.json")
    loc = load("locality_analysis.json")
    fal = load("falsification_results.json")
    rob = load("robustness_results.json")
    man = load("locality_manifest.json")

    for name, obj in [("dens", dens), ("fp", fp), ("reg", reg), ("sim", sim), ("spec", spec),
                      ("abl", abl), ("red", red), ("ineq", ineq), ("loc", loc), ("fal", fal),
                      ("rob", rob), ("man", man)]:
        v.check(obj["method"] == "phase14-locality-1.0", f"{name}.method mismatch")

    # density: 114 surahs
    v.check(len(dens["surah_density_map"]) == 114, "density map != 114 surahs")
    v.check(dens["concentration"]["n_surahs"] == 114, "concentration n_surahs != 114")
    c50 = dens["concentration"]["50pct_carried_by_surahs"]
    c80 = dens["concentration"]["80pct_carried_by_surahs"]
    v.check(0 < c50 < c80 <= 114, "concentration counts incoherent")

    # fingerprints: raw + discriminative summaries; homogeneity reported
    v.check("raw_similarity_summary" in fp and "discriminative_similarity_summary" in fp,
            "fingerprints missing similarity summaries")
    v.check(fp["raw_similarity_summary"]["mean"] > fp["discriminative_similarity_summary"]["mean"],
            "raw homogeneity should exceed discriminative similarity")

    # regions: members are surah numbers (integers), cohesion/separation in range
    surahs_seen = set()
    for rid, rdata in reg["regions"].items():
        v.check(rid.startswith("REGION_"), f"{rid} not opaque region id")
        v.check(all(isinstance(s, int) for s in rdata["surahs"]),
                f"{rid} member not a surah number (label imported?)")
        surahs_seen |= set(rdata["surahs"])
        v.check(0.0 <= rdata["cohesion"] <= 1.0, f"{rid} cohesion range")
        v.check(0.0 <= rdata["separation"] <= 1.0, f"{rid} separation range")
        v.check(rdata["n_surahs"] == len(rdata["surahs"]), f"{rid} size mismatch")
    v.check(len(surahs_seen) == 114, "regions do not partition all 114 surahs")
    v.check(reg["n_regions"] == len(reg["regions"]), "n_regions mismatch")

    # ablation: hub/consistency robustness flags consistent with per-region data
    breaks_hub = any(not abl["regions"][k].get("hub_still_rank1", True) for k in abl["regions"])
    breaks_cons = any(abl["regions"][k].get("consistency_overlap_after", 0) > 0 for k in abl["regions"])
    v.check(abl["any_removal_breaks_hub"] == breaks_hub, "hub-break flag mismatch")
    v.check(abl["any_removal_breaks_consistency"] == breaks_cons, "consistency-break flag mismatch")

    # inequality: gini in range; density gini < activations gini (length-effect finding)
    ga = ineq["metrics"]["activations"]["gini"]
    gd = ineq["metrics"]["activation_density"]["gini"]
    v.check(0.0 <= ga <= 1.0 and 0.0 <= gd <= 1.0, "gini out of range")
    v.check(gd < ga, "per-ayah density gini should be lower than totals gini")

    # locality: window recovery — hub & consistency recover fully even at small windows
    for w, d in loc["windows"].items():
        v.check(0.0 <= d["hub_rank1_probability"] <= 1.0, f"{w} hub prob range")
        v.check(0.0 <= d["consistency_recovery"] <= 1.0, f"{w} consistency range")
    v.check(loc["windows"]["10pct"]["hub_rank1_probability"] == 1.0,
            "hub not fully local at 10% window")
    v.check(loc["windows"]["10pct"]["consistency_recovery"] == 1.0,
            "consistency not fully local at 10% window")

    # falsification: 5 tests, uniform-distribution falsified
    v.check(len(fal["tests"]) == 5, "falsification != 5 tests")
    uni = next((t for t in fal["tests"] if "uniformly distributed" in t["claim"]), None)
    v.check(uni and uni["result"] == "FALSIFIED", "uniform-distribution should be falsified")

    # robustness: gini bootstrap + threshold sweep present
    v.check("gini_bootstrap" in rob and "mean" in rob["gini_bootstrap"], "gini bootstrap missing")
    v.check(len(rob["similarity_threshold_sweep"]) >= 3, "threshold sweep too short")

    # manifest
    tt = man["totals"]
    v.check(tt["n_surahs"] == 114, "manifest n_surahs")
    v.check(tt["any_ablation_breaks_hub"] == abl["any_removal_breaks_hub"], "manifest hub flag")
    for f in FILES:
        if f in man["output_bytes"]:
            v.check(man["output_bytes"][f] == (OUT / f).stat().st_size,
                    f"manifest output_bytes[{f}] mismatch")

    if args.rebuild:
        print("  --rebuild: hashing, rebuilding, re-hashing …")
        before = {f: hashlib.sha256((OUT / f).read_bytes()).hexdigest() for f in FILES}
        res = subprocess.run([sys.executable, "scripts/build_locality.py"],
                             capture_output=True, text=True)
        v.check(res.returncode == 0, f"rebuild failed: {res.stderr[-400:]}")
        for f in FILES:
            after = hashlib.sha256((OUT / f).read_bytes()).hexdigest()
            v.check(after == before[f], f"{f} not byte-identical after rebuild")

    ok = v.summary()
    print(f"  n_regions={reg['n_regions']} gini_act={ga} gini_density={gd} "
          f"hub_local={loc['windows']['10pct']['hub_rank1_probability']} "
          f"breaks_hub={abl['any_removal_breaks_hub']}")
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
