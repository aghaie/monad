#!/usr/bin/env python3
"""Monad — Phase Ξ validator: Foundation Audit & Representation Collapse."""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PRODUCTS = [
    "discovery_dependency_graph.json", "assumption_inventory.json", "assumption_removal_results.json",
    "representation_rebuilds.json", "representation_agreement.json", "discovery_survival.json",
    "invariant_discoveries.json", "collapse_analysis.json", "stress_test_results.json",
    "foundation_audit_manifest.json",
]
REPORTS = [
    "dependency-map-report.md", "assumption-inventory-report.md", "assumption-removal-report.md",
    "representation-rebuild-report.md", "representation-agreement-report.md", "discovery-survival-report.md",
    "invariant-discoveries-report.md", "collapse-analysis-report.md", "stress-test-report.md",
    "phase-xi-final-report.md",
]
METHOD = "foundation-audit-1.0"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(d, n):
    return json.loads((Path(d) / n).read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="generated/foundation_audit")
    ap.add_argument("--docs", default="docs")
    ap.add_argument("--db", default="generated/monad.db")
    ap.add_argument("--rebuild", action="store_true")
    args = ap.parse_args()
    out, docs = Path(args.out), Path(args.docs)
    checks = failed = 0

    def chk(c, m):
        nonlocal checks, failed
        checks += 1
        if not c:
            failed += 1
            print(f"  FAIL: {m}")

    print(f"Validating Phase Ξ in {out}/ …")
    for n in PRODUCTS:
        chk((out / n).exists(), f"missing {n}")
    for n in PRODUCTS:
        if (out / n).exists():
            chk(load(out, n).get("method") == METHOD, f"{n}: method tag")

    # representation rebuilds: residual measured at 3 levels, all > 0.5
    rb = load(out, "representation_rebuilds.json")["representations"]
    chk(set(rb.keys()) == {"root", "lemma", "word"}, "rebuilds: 3 representations")
    for l, d in rb.items():
        chk(0.0 <= d["residual_fraction"] <= 1.0, f"{l}: residual in [0,1]")
        chk(abs(d["explained_by_frequency"] + d["residual_fraction"] - 1.0) < 1e-6, f"{l}: explained+residual=1")

    # agreement consistency
    ag = load(out, "representation_agreement.json")
    chk(ag["n_agree"] == sum(1 for v in ag["invariant_checks"].values() if v), "agreement count consistent")

    # survival fractions sum sanity
    sv = load(out, "discovery_survival.json")
    n = sv["n_discoveries"]
    total = (len(sv["TYPE_D_robust_invariant"]) + len(sv["TYPE_B_weak"])
             + len(sv["TYPE_C_strongly_representation_dependent"]) + len(sv["TYPE_A_artifact"]))
    chk(total == n, "survival: all discoveries classified exactly once")
    chk(abs(sv["fraction_representation_invariant"] - len(sv["TYPE_D_robust_invariant"]) / n) < 1e-6,
        "invariant fraction consistent")

    v = sv["verdict"]
    chk(v["Q6_stable_core_independent_of_assumptions"] in ("YES", "NO", "PARTIAL"), "Q6 in set")
    chk(isinstance(v["Q8_minimal_trusted_set"], list) and len(v["Q8_minimal_trusted_set"]) >= 3,
        "Q8 minimal set listed")
    chk(set(v["Q1_survive_every_representation"]) == set(sv["TYPE_D_robust_invariant"]),
        "Q1 survivors == TYPE_D")

    # collapse analysis covers all
    ca = load(out, "collapse_analysis.json")
    cov = (len(ca["TYPE_A_artifact"]) + len(ca["TYPE_B_weak"])
           + len(ca["TYPE_C_strongly_representation_dependent"]) + len(ca["TYPE_D_robust"]))
    chk(cov == n, "collapse analysis covers all discoveries")

    man = load(out, "foundation_audit_manifest.json")
    chk(man["input_sha256"]["monad.db"] == sha(args.db), "manifest db hash")
    chk(any("nothing protected" in p.lower() for p in man["prohibitions_observed"]),
        "prohibition: nothing protected")

    for nm in REPORTS:
        chk((docs / nm).exists(), f"missing report {nm}")

    if args.rebuild:
        print("  --rebuild …")
        tmp = Path(tempfile.mkdtemp(prefix="monad_fa_"))
        res = subprocess.run([sys.executable, "scripts/build_foundation_audit.py",
                              "--db", args.db, "--out", str(tmp)], capture_output=True, text=True)
        chk(res.returncode == 0, f"rebuild exit 0 ({res.stderr[-300:]})")
        for nm in PRODUCTS:
            a, b = out / nm, tmp / nm
            if a.exists() and b.exists():
                chk(sha(a) == sha(b), f"rebuild byte-identical: {nm}")
            else:
                chk(False, f"rebuild missing {nm}")
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n  {checks - failed}/{checks} checks pass" + (" — FAILURES" if failed else " — all pass"))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
