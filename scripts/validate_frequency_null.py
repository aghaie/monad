#!/usr/bin/env python3
"""
Monad — Phase 17 validator: Frequency Null Model Engine
=======================================================

Verifies structural integrity, the no-protection invariant (every discovery is
compared to a frequency null with explicit z-score / structure-fraction, and both
survivals and failures are reported), statistical completeness, cross-product
consistency, and — with --rebuild — byte-identical reproducibility of
generated/frequency_null/.

Usage:
    python3 scripts/validate_frequency_null.py [--rebuild]
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

OUT = Path("generated/frequency_null")
FILES = [
    "null_corpora.json", "concept_survival.json", "proposition_survival.json",
    "motif_survival.json", "consistency_survival.json", "identity_survival.json",
    "scc_survival.json", "grammar_survival.json", "information_decomposition.json",
    "survivor_analysis.json", "frequency_falsification.json", "robustness.json",
    "frequency_null_manifest.json",
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
    print("Monad Phase 17 — validating Frequency Null Model Engine")

    for f in FILES:
        v.check((OUT / f).exists(), f"missing {f}")
    if v.f:
        print("  aborting")
        sys.exit(1)

    nullc = load("null_corpora.json")
    conc = load("concept_survival.json")
    prop = load("proposition_survival.json")
    motif = load("motif_survival.json")
    cons = load("consistency_survival.json")
    ident = load("identity_survival.json")
    scc = load("scc_survival.json")
    gram = load("grammar_survival.json")
    dec = load("information_decomposition.json")
    surv = load("survivor_analysis.json")
    fal = load("frequency_falsification.json")
    rob = load("robustness.json")
    man = load("frequency_null_manifest.json")

    for name, obj in [("nullc", nullc), ("conc", conc), ("prop", prop), ("motif", motif),
                      ("cons", cons), ("ident", ident), ("scc", scc), ("gram", gram),
                      ("dec", dec), ("surv", surv), ("fal", fal), ("rob", rob), ("man", man)]:
        v.check(obj["method"] == "phase17-frequency-null-1.0", f"{name}.method mismatch")

    # null counts
    v.check(nullc["n_concept_nulls"] == 1000, "concept nulls != 1000")
    v.check(nullc["n_root_nulls"] == 200, "root nulls != 200")
    v.check("co-occurrence" in nullc["destroyed"], "null does not destroy co-occurrence")

    # concept survival: significantly exceeds null (z > 2)
    v.check(conc["zscore"] is not None and conc["zscore"] > 2, "concept clustering does not exceed null")
    v.check(conc["ratio_obs_over_null"] > 1.0, "concept cohesion ratio <= 1")

    # proposition survival: strong associations exceed null
    sa = prop["strong_associations"]
    v.check(sa["zscore"] is not None and sa["zscore"] > 2, "strong associations do not exceed null")
    v.check(prop["edges"]["ratio_obs_over_null"] > 2, "edges ratio <= 2")

    # motif survival: at least one class significant; structure_fraction present
    v.check(motif["n_surviving"] >= 1, "no motif class survives")
    for mid, m in motif["motifs"].items():
        v.check("zscore" in m and "structure_fraction" in m, f"{mid} missing z/structure")

    # consistency: does NOT exceed null (null also consistent) — honest deflation
    v.check(cons["consistency_exceeds_null"] is False, "consistency claimed to exceed null")
    v.check(cons["null_contradictions"]["max"] == 0.0, "null produced contradictions")

    # identity: frequency-explained fraction in [0,1]
    v.check(0.0 <= ident["frequency_explained_fraction"] <= 1.0, "identity fraction range")

    # scc: exceeds null
    v.check(scc["largest_scc"]["ratio_obs_over_null"] > 1.5, "SCC does not exceed null")

    # decomposition: 10 discoveries, structure% in range, mean reported
    v.check(len(dec["discoveries"]) == 10, "decomposition != 10 discoveries")
    for k, d in dec["discoveries"].items():
        v.check(0.0 <= d["structure_pct"] <= 100.0, f"{k} structure_pct range")
        v.check(abs(d["structure_pct"] + d["frequency_pct"] - 100.0) < 1e-3, f"{k} pct sum != 100")
    v.check(0.0 <= dec["mean_structure_pct"] <= 100.0, "mean structure pct range")

    # survivor analysis: categories valid, tally sums to 10
    cats = {"FREQUENCY ONLY", "MOSTLY FREQUENCY", "MIXED", "MOSTLY STRUCTURE", "STRUCTURE ONLY"}
    for k, s in surv["discoveries"].items():
        v.check(s["category"] in cats, f"{k} bad category")
    v.check(sum(surv["tally"].values()) == 10, "tally != 10")
    v.check(surv["strongest_surviving_discovery"] == surv["survival_ranking"][0],
            "strongest survivor mismatch")

    # falsification: 7 hypotheses; H1/H2/H3/H7 survive; H4 falsified (consistency)
    v.check(len(fal["hypotheses"]) == 7, "expected 7 hypotheses")
    sset = set(fal["surviving_hypotheses"])
    for hid in ("H1", "H2", "H3", "H7"):
        v.check(hid in sset, f"{hid} should survive")
    h4 = next((h for h in fal["hypotheses"] if h["id"] == "H4"), None)
    v.check(h4 and "FALSIFIED" in h4["result"], "H4 (consistency) should be falsified")
    for h in fal["hypotheses"]:
        v.check(bool(h.get("evidence")), f"{h['id']} lacks evidence")

    # manifest
    t = man["totals"]
    v.check(t["surviving_hypotheses"] == fal["surviving_hypotheses"], "manifest survivor mismatch")
    v.check(0 <= t["mean_structure_pct"] <= 100, "manifest structure pct")
    for f in FILES:
        if f in man["output_bytes"]:
            v.check(man["output_bytes"][f] == (OUT / f).stat().st_size,
                    f"manifest output_bytes[{f}] mismatch")

    if args.rebuild:
        print("  --rebuild: hashing, rebuilding, re-hashing …")
        before = {f: hashlib.sha256((OUT / f).read_bytes()).hexdigest() for f in FILES}
        res = subprocess.run([sys.executable, "scripts/build_frequency_null.py"],
                             capture_output=True, text=True)
        v.check(res.returncode == 0, f"rebuild failed: {res.stderr[-400:]}")
        for f in FILES:
            after = hashlib.sha256((OUT / f).read_bytes()).hexdigest()
            v.check(after == before[f], f"{f} not byte-identical after rebuild")

    ok = v.summary()
    print(f"  structure={dec['mean_structure_pct']}% frequency={dec['mean_frequency_pct']}% "
          f"strongest={surv['strongest_surviving_discovery']} survivors={fal['surviving_hypotheses']}")
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
