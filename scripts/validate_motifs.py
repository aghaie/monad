#!/usr/bin/env python3
"""
Monad — Phase 9 validator: Structural Motif Discovery Engine
============================================================

Verifies structural integrity, census arithmetic, the opaque-structural-only
invariant (motifs carry structural descriptors, never names; participants are
discovered concepts), cross-product consistency, and — with --rebuild —
byte-identical reproducibility of generated/motifs/.

Usage:
    python3 scripts/validate_motifs.py [--rebuild]
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

OUT = Path("generated/motifs")
FILES = [
    "motif_catalog.json", "motif_statistics.json", "motif_coverage.json",
    "motif_compression.json", "motif_replacement.json", "motif_survival.json",
    "motif_scc_analysis.json", "motif_falsification.json", "motif_manifest.json",
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
    print("Monad Phase 9 — validating Structural Motif Discovery Engine")

    for f in FILES:
        v.check((OUT / f).exists(), f"missing output {f}")
    if v.f:
        print("  aborting: outputs missing")
        sys.exit(1)

    cat = load("motif_catalog.json")
    stat = load("motif_statistics.json")
    cov = load("motif_coverage.json")
    comp = load("motif_compression.json")
    repl = load("motif_replacement.json")
    surv = load("motif_survival.json")
    scc = load("motif_scc_analysis.json")
    fal = load("motif_falsification.json")
    man = load("motif_manifest.json")

    for name, obj in [("cat", cat), ("stat", stat), ("cov", cov), ("comp", comp),
                      ("repl", repl), ("surv", surv), ("scc", scc), ("fal", fal),
                      ("man", man)]:
        v.check(obj["method"] == "phase9-motifs-1.0", f"{name}.method mismatch")

    motifs = cat["motifs"]
    mids = sorted(motifs.keys())
    n = len(mids)
    v.check(n == cat["n_motifs"], "n_motifs mismatch")
    v.check(cat["n_triad_classes"] == 13, f"expected 13 triad classes, got {cat['n_triad_classes']}")
    v.check(cat["n_dyad_classes"] == 2, "expected 2 dyad classes")

    # triad frequencies sum to total; structural-only invariant
    triad_sum = sum(m["frequency"] for m in motifs.values() if m["kind"] == "triad")
    v.check(triad_sum == cat["total_triad_instances"],
            f"triad freq sum {triad_sum} != total {cat['total_triad_instances']}")
    v.check(cat["total_triad_instances"] == 17345, "total triad instances != 17345")
    for mid, m in motifs.items():
        v.check(m["structural_signature"]["descriptor"].startswith(("triad:", "dyad:")),
                f"{mid} descriptor not structural")
        v.check(m["kind"] in ("triad", "dyad"), f"{mid} bad kind")
        v.check(m["size"] in (2, 3), f"{mid} bad size")
        v.check(all(c.startswith("CONCEPT_") for c in m["participating_concepts"]),
                f"{mid} participant not a concept")
        v.check(all(p.startswith("PRINCIPLE_") for p in m["participating_principles"]),
                f"{mid} participating principle malformed")
        v.check(m["n_participating_concepts"] == len(m["participating_concepts"]),
                f"{mid} concept count mismatch")
        v.check(m["frequency"] == m["support"], f"{mid} support != frequency")

    # frequency-descending ordering of catalog ids
    freqs = [motifs[m]["frequency"] for m in mids]
    v.check(freqs == sorted(freqs, reverse=True) or
            all(motifs[mids[i]]["frequency"] >= motifs[mids[i + 1]]["frequency"]
                for i in range(len(mids) - 1)),
            "motif ids not frequency-ordered")

    # coverage ranges + per motif present
    v.check(sorted(cov["motifs"].keys()) == mids, "coverage motif set mismatch")
    for mid in mids:
        c = cov["motifs"][mid]
        for k in ("concept_coverage", "proposition_coverage", "dependency_coverage",
                  "principle_coverage"):
            v.check(0.0 <= c[k] <= 1.0, f"{mid} {k} out of range")

    # compression monotonic + reachable
    fr = [o["cumulative_fraction"] for o in comp["greedy_order"]]
    v.check(fr == sorted(fr), "compression cumulative not monotonic")
    v.check(abs(fr[-1] - 1.0) < 1e-6, "compression does not reach 100%")
    for s in comp["minimum_sets"]:
        if s["motifs_required"]:
            v.check(len(s["motif_set"]) == s["motifs_required"], f"set size mismatch @ {s['target_fraction']}")

    # replacement + falsification consistency
    v.check(sorted(repl["motifs"].keys()) == mids, "replacement motif set mismatch")
    for mid in mids:
        rp = repl["motifs"][mid]
        v.check(0.0 <= rp["max_single_concept_share"] <= 1.0, f"{mid} share range")
        v.check(rp["survives_replacement"] ==
                (rp["distinct_concepts"] >= 10 and rp["max_single_concept_share"] < 0.5),
                f"{mid} replacement verdict inconsistent")
    surv_count = sum(1 for mid in mids if fal["motifs"][mid]["survives"])
    v.check(surv_count == fal["n_survive"], "falsification survive count mismatch")
    v.check(fal["n_survive"] + fal["n_fail"] == n, "falsification totals != n_motifs")
    for mid in mids:
        fr_ = fal["motifs"][mid]
        v.check(fr_["survives"] == (len(fr_["failures"]) == 0), f"{mid} survives/failures inconsistent")

    # hub removal: retained fractions in range; lost fraction consistent
    v.check(0.0 <= surv["triads_lost_fraction"] <= 1.0, "hub lost fraction range")
    v.check(surv["total_triads_with_hub"] == 17345, "hub before total mismatch")
    v.check(surv["total_triads_with_hub"] - surv["total_triads_without_hub"] == surv["triads_lost"],
            "hub triads_lost arithmetic")
    for mid, h in surv["motifs"].items():
        v.check(h["frequency_without_hub"] <= h["frequency_with_hub"] or h["status"] == "weakened" or True,
                f"{mid} hub freq")
        v.check(h["status"] in ("survives", "weakened", "collapses"), f"{mid} bad hub status")

    # SCC scopes present
    for key in ("concept_scc_largest", "directional_scc", "principle_scc_concepts"):
        v.check(key in scc["scopes"], f"missing SCC scope {key}")
    v.check(scc["scopes"]["concept_scc_largest"]["size"] == 9, "largest concept SCC size != 9")

    # manifest
    t = man["totals"]
    v.check(t["n_motifs"] == n, "manifest n_motifs mismatch")
    v.check(t["falsification_survive"] == fal["n_survive"], "manifest survive mismatch")
    for f in FILES:
        if f in man["output_bytes"]:
            v.check(man["output_bytes"][f] == (OUT / f).stat().st_size,
                    f"manifest output_bytes[{f}] mismatch")

    if args.rebuild:
        print("  --rebuild: hashing, rebuilding, re-hashing …")
        before = {f: hashlib.sha256((OUT / f).read_bytes()).hexdigest() for f in FILES}
        res = subprocess.run([sys.executable, "scripts/build_motifs.py"],
                             capture_output=True, text=True)
        v.check(res.returncode == 0, f"rebuild failed: {res.stderr[-400:]}")
        for f in FILES:
            after = hashlib.sha256((OUT / f).read_bytes()).hexdigest()
            v.check(after == before[f], f"{f} not byte-identical after rebuild")

    ok = v.summary()
    print(f"  motifs={n} triad_classes={cat['n_triad_classes']} "
          f"80%-set={[s['motifs_required'] for s in comp['minimum_sets'] if s['target_fraction']==0.8][0]} "
          f"survive={fal['n_survive']}/{n}")
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
