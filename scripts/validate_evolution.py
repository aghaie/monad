#!/usr/bin/env python3
"""
Monad — Phase 13 validator: Revelation Evolution Engine
=======================================================

Verifies structural integrity, the no-leakage invariant (snapshot ayah counts are
monotone non-decreasing and bounded by the total; the final snapshot sees all
ayahs), that revelation-order traditions are documented + hashed and analysed
separately, cross-product consistency, and — with --rebuild — byte-identical
reproducibility of generated/evolution/.

Usage:
    python3 scripts/validate_evolution.py [--rebuild]
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

OUT = Path("generated/evolution")
FILES = [
    "snapshot_statistics.json", "hub_evolution.json", "motif_evolution.json",
    "consistency_evolution.json", "scc_evolution.json", "identity_evolution.json",
    "predictability_analysis.json", "phase_transitions.json", "evolution_manifest.json",
]
TRADS = ["TRADITION_CANONICAL", "TRADITION_MECCAN_MEDINAN"]


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
    print("Monad Phase 13 — validating Revelation Evolution Engine")

    for f in FILES:
        v.check((OUT / f).exists(), f"missing {f}")
    if v.f:
        print("  aborting")
        sys.exit(1)

    snap = load("snapshot_statistics.json")
    hub = load("hub_evolution.json")
    motif = load("motif_evolution.json")
    consist = load("consistency_evolution.json")
    scc = load("scc_evolution.json")
    ident = load("identity_evolution.json")
    pred = load("predictability_analysis.json")
    pt = load("phase_transitions.json")
    man = load("evolution_manifest.json")

    for name, obj in [("snap", snap), ("hub", hub), ("motif", motif), ("consist", consist),
                      ("scc", scc), ("ident", ident), ("pred", pred), ("pt", pt), ("man", man)]:
        v.check(obj["method"] == "phase13-evolution-1.0", f"{name}.method mismatch")

    # traditions documented + hashed + separate
    v.check(set(snap["traditions"].keys()) == set(TRADS), "tradition set mismatch")
    for t in TRADS:
        v.check(len(snap["traditions"][t]["order_sha256"]) == 64, f"{t} order not hashed")
        v.check(t in man["revelation_order_traditions"], f"{t} not in manifest")
    v.check(snap["traditions"][TRADS[0]]["order_sha256"] != snap["traditions"][TRADS[1]]["order_sha256"],
            "two traditions share a hash (silently merged?)")
    v.check("control" in snap, "control order not documented")

    total = snap["total_ayahs"]
    v.check(total == 6101, f"total ayahs {total} != 6101")

    # NO-LEAKAGE invariant: snapshot ayah counts monotone non-decreasing, bounded, final = total
    for t in list(snap["snapshots"].keys()):
        series = snap["snapshots"][t]
        v.check(len(series) == 12, f"{t} != 12 snapshots")
        counts = [s["n_ayahs"] for s in series]
        v.check(counts == sorted(counts), f"{t} ayah counts not monotone (leakage?)")
        v.check(all(c <= total for c in counts), f"{t} snapshot exceeds total ayahs")
        v.check(counts[-1] == total, f"{t} final snapshot does not see all ayahs")
        # consistency overlap must be 0 at every snapshot
        for s in series:
            v.check(s["exclusion_positive_overlap"] >= 0, f"{t} negative overlap")

    # hub evolution: rank-1 from start across traditions; field present
    for t in TRADS:
        v.check(hub["traditions"][t]["rank1_from_start"] is True,
                f"{t}: hub not rank-1 from start (report honestly if changed)")
        v.check(hub["traditions"][t]["first_rank1_threshold"] is not None, f"{t} no rank1 threshold")

    # consistency: never inconsistent in any order
    for t in list(consist["traditions"].keys()):
        v.check(consist["traditions"][t]["ever_inconsistent"] is False,
                f"{t}: an inconsistency appeared (report honestly)")
        v.check(consist["traditions"][t]["max_overlap"] == 0, f"{t}: nonzero overlap")

    # predictability ranges + monotone-ish presence
    for t in TRADS:
        traj = pred["traditions"][t]["trajectory"]
        v.check(len(traj) == 12, f"{t} predictability length")
        for x in traj:
            v.check(0.0 <= x["composite_predictability"] <= 1.0, f"{t} composite out of range")
        v.check(traj[-1]["composite_predictability"] == 1.0, f"{t} final predictability != 1.0")

    # robustness + falsification (folded into phase_transitions)
    rob = pt["robustness"]
    fal = pt["falsification"]
    v.check("hub present from start" in rob["temporally_robust_findings"],
            "hub-from-start not in robust findings")
    v.check("consistency holds throughout" in rob["temporally_robust_findings"],
            "consistency not in robust findings")
    hub_test = next((x for x in fal["tests"] if "hub emergence" in x["claim"]), None)
    v.check(hub_test and hub_test["result"] == "FALSIFIED",
            "hub-order-artifact claim should be falsified (holds under control)")
    chrono = next((x for x in fal["tests"] if "historical chronology" in x["claim"]), None)
    v.check(chrono and "LIMITATION" in chrono["result"], "chronology limitation not acknowledged")

    # manifest
    tt = man["totals"]
    v.check(tt["hub_rank1_from_start_all"] is True, "manifest hub flag")
    v.check(tt["consistency_robust"] is True, "manifest consistency flag")
    for f in FILES:
        if f in man["output_bytes"]:
            v.check(man["output_bytes"][f] == (OUT / f).stat().st_size,
                    f"manifest output_bytes[{f}] mismatch")

    if args.rebuild:
        print("  --rebuild: hashing, rebuilding, re-hashing …")
        before = {f: hashlib.sha256((OUT / f).read_bytes()).hexdigest() for f in FILES}
        res = subprocess.run([sys.executable, "scripts/build_evolution.py"],
                             capture_output=True, text=True)
        v.check(res.returncode == 0, f"rebuild failed: {res.stderr[-400:]}")
        for f in FILES:
            after = hashlib.sha256((OUT / f).read_bytes()).hexdigest()
            v.check(after == before[f], f"{f} not byte-identical after rebuild")

    ok = v.summary()
    print(f"  hub_rank1_from_start={tt['hub_rank1_from_start_all']} "
          f"consistency_robust={tt['consistency_robust']} "
          f"motif_stab={tt['motif_stabilization_canonical']} "
          f"pred@10pct={tt['predictability_at_10pct_canonical']}")
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
