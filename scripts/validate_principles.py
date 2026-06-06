#!/usr/bin/env python3
"""
Monad — Phase 8 validator: Foundational Principle Discovery Engine
=================================================================

Verifies structural integrity, partition consistency, coverage arithmetic, the
emerge-not-invent invariant (every principle member is a discovered concept; the
partition covers all 103), and — with --rebuild — byte-identical reproducibility
of generated/principles/.

Usage:
    python3 scripts/validate_principles.py [--rebuild]
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

OUT = Path("generated/principles")
FILES = [
    "principle_candidates.json", "principle_coverage.json", "principle_removal.json",
    "principle_reconstruction.json", "principle_hierarchy.json",
    "principle_dependencies.json", "irreducible_principles.json",
    "principle_falsification.json", "principle_manifest.json",
]


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true")
    args = ap.parse_args()
    v = V()
    print("Monad Phase 8 — validating Foundational Principle Discovery Engine")

    for f in FILES:
        v.check((OUT / f).exists(), f"missing output {f}")
    if v.f:
        print("  aborting: outputs missing")
        sys.exit(1)

    cand = load("principle_candidates.json")
    cov = load("principle_coverage.json")
    rem = load("principle_removal.json")
    rec = load("principle_reconstruction.json")
    hier = load("principle_hierarchy.json")
    dep = load("principle_dependencies.json")
    irr = load("irreducible_principles.json")
    fal = load("principle_falsification.json")
    man = load("principle_manifest.json")

    for name, obj in [("cand", cand), ("cov", cov), ("rem", rem), ("rec", rec),
                      ("hier", hier), ("dep", dep), ("irr", irr), ("fal", fal),
                      ("man", man)]:
        v.check(obj["method"] == "phase8-principles-1.0", f"{name}.method mismatch")

    pids = sorted(cand["principles"].keys())
    n_principles = len(pids)
    v.check(n_principles == cand["n_principles"], "n_principles mismatch")

    # partition: members are concepts, disjoint, cover exactly 103
    all_members = []
    for pid in pids:
        all_members += cand["principles"][pid]["member_concepts"]
    v.check(len(all_members) == 103, f"members cover {len(all_members)} != 103 concepts")
    v.check(len(set(all_members)) == 103, "members not disjoint / not 103 unique")
    v.check(all(c.startswith("CONCEPT_") for c in all_members),
            "a principle member is not a discovered concept (invented?)")

    # size consistency across products
    for pid in pids:
        sz = cand["principles"][pid]["size"]
        v.check(sz == len(cand["principles"][pid]["member_concepts"]), f"{pid} size mismatch")
        v.check(cov["principles"][pid]["size"] == sz, f"{pid} coverage size mismatch")
        v.check(rem["principles"][pid]["size"] == sz, f"{pid} removal size mismatch")
        v.check(fal["principles"][pid]["size"] == sz, f"{pid} falsification size mismatch")

    # coverage arithmetic
    n_rel = cov["n_relations"]
    v.check(n_rel == 6832, f"n_relations {n_rel} != 6832")
    v.check(cov["global_intra_principle_relations"] + cov["global_inter_principle_relations"] == n_rel,
            "intra+inter != n_relations")
    # internal <= incident for every principle
    for pid in pids:
        p = cov["principles"][pid]
        v.check(p["relations_internal"] <= p["relations_incident"],
                f"{pid} internal > incident")
        v.check(0.0 <= p["concept_coverage"] <= 1.0, f"{pid} concept_coverage range")
        # retention consistency with falsification
        f = fal["principles"][pid]
        v.check(f["survives"] == (f["internal_relation_retention"] >= fal["constant_survive_retention"]),
                f"{pid} survives/retention inconsistent")
        v.check(abs(f["boundary_leakage"] + f["internal_relation_retention"] - 1.0) < 1e-6,
                f"{pid} leakage+retention != 1")

    # falsification totals
    surv = sum(1 for pid in pids if fal["principles"][pid]["survives"])
    v.check(surv == fal["n_survive"], "falsification survive count mismatch")
    v.check(fal["n_survive"] + fal["n_fail"] == n_principles, "survive+fail != n_principles")

    # reconstruction monotonic curves + ceilings
    for key in ("incidence_greedy_order", "internal_greedy_order"):
        fr = [o["cumulative_fraction"] for o in rec[key]]
        v.check(fr == sorted(fr), f"{key} not monotonic")
        v.check(all(rec[key][i]["set_size"] == i + 1 for i in range(len(rec[key]))),
                f"{key} set_size not sequential")
    v.check(abs(rec["internal_coverage_ceiling"] - cov["global_intra_fraction"]) < 1e-6,
            "internal ceiling != global intra fraction")
    # internal minimum sets above ceiling must be unreachable
    for s in rec["internal_minimum_sets"]:
        if s["target_fraction"] > rec["internal_coverage_ceiling"] + 1e-9:
            v.check(s["reachable"] is False, f"internal target {s['target_fraction']} wrongly reachable")

    # hierarchy: cyclic clusters are SCCs of size>=2; layers cover components
    for c in hier["cyclic_principle_clusters"]:
        v.check(len(c) >= 2, "cyclic cluster size < 2")
    v.check(hier["n_layers"] == len(hier["layers"]), "n_layers mismatch")
    # irreducible largest size consistency
    if irr["irreducible_principle_clusters"]:
        v.check(irr["largest_irreducible_size"] ==
                max(c["size"] for c in irr["irreducible_principle_clusters"]),
                "largest irreducible size mismatch")
    v.check(abs(irr["irreducible_explanatory_residue_fraction"] -
                cov["global_inter_fraction"]) < 1e-6,
            "residue fraction != inter fraction")

    # manifest totals
    t = man["totals"]
    v.check(t["n_principles"] == n_principles, "manifest n_principles")
    v.check(t["falsification_survive"] == fal["n_survive"], "manifest survive mismatch")
    for f in FILES:
        if f in man["output_bytes"]:
            v.check(man["output_bytes"][f] == (OUT / f).stat().st_size,
                    f"manifest output_bytes[{f}] mismatch")

    if args.rebuild:
        print("  --rebuild: hashing, rebuilding, re-hashing …")
        before = {f: hashlib.sha256((OUT / f).read_bytes()).hexdigest() for f in FILES}
        res = subprocess.run([sys.executable, "scripts/build_principles.py"],
                             capture_output=True, text=True)
        v.check(res.returncode == 0, f"rebuild failed: {res.stderr[-400:]}")
        for f in FILES:
            after = hashlib.sha256((OUT / f).read_bytes()).hexdigest()
            v.check(after == before[f], f"{f} not byte-identical after rebuild")

    ok = v.summary()
    print(f"  principles={n_principles} modularity={cand['modularity']} "
          f"intra={cov['global_intra_fraction']} survive={fal['n_survive']}/{n_principles}")
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
