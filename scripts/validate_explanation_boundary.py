#!/usr/bin/env python3
"""Monad — Phase Ω(B) validator: Explanation Boundary Discovery."""

import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PRODUCTS = [
    "discovery_inventory.json", "explanatory_power.json", "redundancy.json",
    "maximum_model.json", "residual_structure.json", "residual_characterization.json",
    "null_attack.json", "explanation_frontier.json", "future_knowledge.json",
    "explanation_manifest.json",
]
REPORTS = [
    "discovery-inventory-report.md", "explanatory-power-report.md",
    "explanation-redundancy-report.md", "residual-structure-report.md",
    "residual-characterization-report.md", "null-attack-report.md",
    "explanation-frontier-report.md", "future-knowledge-report.md",
    "phase-explanation-boundary-final-report.md",
]
METHOD = "explanation-boundary-1.0"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(d, n):
    return json.loads((Path(d) / n).read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="generated/explanation_boundary")
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

    print(f"Validating Phase Ω(B) in {out}/ …")
    for n in PRODUCTS:
        chk((out / n).exists(), f"missing {n}")
    for n in PRODUCTS:
        if (out / n).exists():
            chk(load(out, n).get("method") == METHOD, f"{n}: method tag")

    ep = load(out, "explanatory_power.json")["budget"]
    chk(0.0 <= ep["explained_by_frequency"] <= 1.0, "explained fraction in [0,1]")
    # consistency: explained + residual_after_frequency == 1
    chk(abs(ep["explained_by_frequency"] + ep["residual_fraction_after_frequency"] - 1.0) < 1e-6,
        "explained + residual(freq) == 1")
    # uniform NLL = log2(V) sanity
    import math
    chk(abs(ep["nll_uniform_bits"] - math.log2(1642)) < 0.01, "uniform NLL = log2(vocab)")

    fr = load(out, "explanation_frontier.json")
    v = fr["verdict"]
    chk(abs(v["Q1_explained_fraction"] + v["Q2_unexplained_fraction"] - 1.0) < 1e-6,
        "Q1 + Q2 == 1")
    chk(v["Q3_residual_stronger_than_nulls"] in ("YES", "NO", "PARTIAL"), "Q3 in set")
    chk(v["Q4_frontier_saturated"] in ("YES", "NO"), "Q4 in set")
    na = load(out, "null_attack.json")
    chk(v["Q3_residual_stronger_than_nulls"] == ("PARTIAL" if na["residual_structure_survives_null"] else "NO"),
        "Q3 consistent with null attack")
    fut = load(out, "future_knowledge.json")
    chk(v["Q4_frontier_saturated"] == ("YES" if fut["generalizable_gain_from_better_models"] == 0.0 else "NO"),
        "Q4 consistent with future-knowledge")

    man = load(out, "explanation_manifest.json")
    chk(man["input_sha256"]["monad.db"] == sha(args.db), "manifest db hash")
    chk(man["totals"]["unexplained_fraction"] == v["Q2_unexplained_fraction"], "manifest/verdict agree")
    chk(len(man["prohibitions_observed"]) >= 8, "prohibitions listed (incl 'we do not know')")

    for n in REPORTS:
        chk((docs / n).exists(), f"missing report {n}")

    if args.rebuild:
        print("  --rebuild …")
        tmp = Path(tempfile.mkdtemp(prefix="monad_eb_"))
        res = subprocess.run([sys.executable, "scripts/build_explanation_boundary.py",
                              "--db", args.db, "--out", str(tmp)], capture_output=True, text=True)
        chk(res.returncode == 0, f"rebuild exit 0 ({res.stderr[-300:]})")
        for n in PRODUCTS:
            a, b = out / n, tmp / n
            if a.exists() and b.exists():
                chk(sha(a) == sha(b), f"rebuild byte-identical: {n}")
            else:
                chk(False, f"rebuild missing {n}")
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n  {checks - failed}/{checks} checks pass" + (" — FAILURES" if failed else " — all pass"))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
