#!/usr/bin/env python3
"""
Monad — Phase 10 validator: Contradiction & Consistency Discovery Engine
=======================================================================

Verifies structural integrity, the high-burden-of-proof invariant (every
surviving contradiction carries explicit structural evidence; no candidate is
asserted without surviving an explicit disproof attempt), cross-product
consistency, the reconstructed-matrix anchor (6101 active ayahs = Phase 4/6), and
— with --rebuild — byte-identical reproducibility of generated/consistency/.

Usage:
    python3 scripts/validate_consistency.py [--rebuild]
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

OUT = Path("generated/consistency")
FILES = [
    "consistency_model.json", "proposition_conflicts.json", "dependency_conflicts.json",
    "identity_conflicts.json", "motif_conflicts.json", "recursive_consistency.json",
    "consistency_scores.json", "contradiction_candidates.json", "consistency_manifest.json",
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
    print("Monad Phase 10 — validating Contradiction & Consistency Discovery Engine")

    for f in FILES:
        v.check((OUT / f).exists(), f"missing output {f}")
    if v.f:
        print("  aborting: outputs missing")
        sys.exit(1)

    model = load("consistency_model.json")
    prop = load("proposition_conflicts.json")
    dep = load("dependency_conflicts.json")
    ident = load("identity_conflicts.json")
    motif = load("motif_conflicts.json")
    rec = load("recursive_consistency.json")
    scores = load("consistency_scores.json")
    cand = load("contradiction_candidates.json")
    man = load("consistency_manifest.json")

    for name, obj in [("model", model), ("prop", prop), ("dep", dep), ("ident", ident),
                      ("motif", motif), ("rec", rec), ("scores", scores), ("cand", cand),
                      ("man", man)]:
        v.check(obj["method"] == "phase10-consistency-1.0", f"{name}.method mismatch")

    # reconstructed matrix anchor
    v.check(model["matrix_summary"]["active_ayahs"] == 6101,
            f"active ayahs {model['matrix_summary']['active_ayahs']} != 6101 (Phase 4/6 anchor)")

    # model documents all obligation classes and contradiction rules
    for k in ("NECESSITY", "STRICT_ORDER", "EXCLUSION", "TENDENCY"):
        v.check(k in model["obligation_classes"], f"model missing obligation class {k}")
    v.check(len(model["contradiction_rules"]) >= 6, "fewer than 6 contradiction rules documented")

    # candidates: arithmetic + the central invariant
    v.check(cand["n_candidates"] == cand["n_survived"] + cand["n_falsified"],
            "candidate arithmetic mismatch")
    v.check(len(cand["all_candidates"]) == cand["n_candidates"], "all_candidates length mismatch")
    v.check(len(cand["surviving_contradictions"]) == cand["n_survived"],
            "surviving list length mismatch")
    # every candidate is either genuine (then in survivors) or falsified with an explicit disproof
    for c in cand["all_candidates"]:
        if c["genuine_after_test"]:
            v.check(c["confidence"] >= 1.0 - 1e-9, "genuine candidate without full confidence")
        else:
            v.check(c.get("falsification"), "falsified candidate lacks explicit disproof")
            v.check(c["confidence"] == 0.0, "falsified candidate has nonzero confidence")
    # candidates sorted by confidence desc
    confs = [c["confidence"] for c in cand["all_candidates"]]
    v.check(confs == sorted(confs, reverse=True), "candidates not confidence-sorted")
    # survivors must match every per-phase genuine count
    v.check(cand["n_survived"] ==
            prop["n_necessity_conflicts"] + dep["n_necessity_exclusion_conflicts"] +
            dep["n_self_negating"] + motif["n_strict_order_cycles"] +
            ident["n_genuine_inversions"] + rec["n_self_negating"],
            "survivor count != sum of per-phase genuine contradictions")

    # per-phase: genuine counts must equal what survives (no hidden assertions)
    v.check(prop["n_necessity_conflicts"] == len(prop["necessity_conflict_candidates"]),
            "proposition necessity count mismatch")
    v.check(dep["n_necessity_exclusion_conflicts"] == 0 or
            len(dep["necessity_exclusion_conflicts"]) == dep["n_necessity_exclusion_conflicts"],
            "dependency C1 count mismatch")
    # motif: strict + weak = all order cycles
    v.check(motif["n_strict_order_cycles"] == len(motif["strict_order_cycles"]),
            "strict cycle count mismatch")
    v.check(motif["n_weak_order_cycles"] == len(motif["weak_order_cycles"]),
            "weak cycle count mismatch")
    # every weak order cycle must indeed be weak (min asymmetry < strict threshold)
    strict_asym = model["constants"]["STRICT_ASYM"]
    for c in motif["weak_order_cycles"]:
        v.check(c["min_asymmetry"] < strict_asym, "a weak cycle has strict asymmetry")
    for c in motif["strict_order_cycles"]:
        v.check(c["min_asymmetry"] >= strict_asym, "a strict cycle is not strict")

    # recursive: every self_negating must have an internal exclusion (else mislabeled)
    for s in rec["dependency_sccs"]:
        if s["classification"] == "self_negating":
            v.check(s["internal_exclusion_pairs"] > 0, "self_negating SCC without exclusion")
        else:
            v.check(s["internal_exclusion_pairs"] == 0, "self_supporting SCC with exclusion")

    # scores: 103 concepts, ranges
    v.check(len(scores["concepts"]) == 103, "consistency scores != 103 concepts")
    v.check(0.0 <= scores["global_consistency_index"] <= 1.0, "global index out of range")
    for cid, s in scores["concepts"].items():
        for k in ("consistency_score", "stability_score", "coherence_score"):
            v.check(0.0 <= s[k] <= 1.0 + 1e-9, f"{cid} {k} out of range")
        v.check(s["in_surviving_contradiction"] is False or cand["n_survived"] > 0,
                f"{cid} flagged in contradiction but none survive")

    # manifest
    t = man["totals"]
    v.check(t["n_surviving_contradictions"] == cand["n_survived"], "manifest survivors mismatch")
    v.check(t["internally_coherent"] == (cand["n_survived"] == 0), "manifest coherence flag")
    for f in FILES:
        if f in man["output_bytes"]:
            v.check(man["output_bytes"][f] == (OUT / f).stat().st_size,
                    f"manifest output_bytes[{f}] mismatch")

    if args.rebuild:
        print("  --rebuild: hashing, rebuilding, re-hashing …")
        before = {f: hashlib.sha256((OUT / f).read_bytes()).hexdigest() for f in FILES}
        res = subprocess.run([sys.executable, "scripts/build_consistency.py"],
                             capture_output=True, text=True)
        v.check(res.returncode == 0, f"rebuild failed: {res.stderr[-400:]}")
        for f in FILES:
            after = hashlib.sha256((OUT / f).read_bytes()).hexdigest()
            v.check(after == before[f], f"{f} not byte-identical after rebuild")

    ok = v.summary()
    print(f"  candidates={cand['n_candidates']} survived={cand['n_survived']} "
          f"global_consistency={scores['global_consistency_index']} "
          f"coherent={man['totals']['internally_coherent']}")
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
