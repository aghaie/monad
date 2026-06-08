#!/usr/bin/env python3
"""Monad — Phase Φ validator: Counterfactual Quran Discovery."""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PRODUCTS = [
    "constraint_inventory.json", "generator_levels.json", "alternative_space.json",
    "selection_pressure.json", "ayah_counterfactuals.json", "global_counterfactuals.json",
    "choice_residual.json", "selection_classification.json", "counterfactual_manifest.json",
]
REPORTS = [
    "constraint-inventory-report.md", "alternative-space-report.md", "selection-pressure-report.md",
    "rare-choice-report.md", "local-counterfactual-report.md", "global-counterfactual-report.md",
    "choice-residual-report.md", "selection-classification-report.md", "phase-phi-final-report.md",
]
METHOD = "counterfactual-discovery-1.0"
TYPES = ["TYPE_A_unconstrained_freedom", "TYPE_B_weakly_constrained_selection",
         "TYPE_C_strongly_constrained_selection", "TYPE_D_near_unique_selection", "TYPE_E_unknown"]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(d, n):
    return json.loads((Path(d) / n).read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="generated/counterfactual")
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

    print(f"Validating Phase Φ in {out}/ …")
    for n in PRODUCTS:
        chk((out / n).exists(), f"missing {n}")
    for n in PRODUCTS:
        if (out / n).exists():
            chk(load(out, n).get("method") == METHOD, f"{n}: method tag")

    sp = load(out, "alternative_space.json")
    chk(sp["log2_alternatives_frequency"] > 0, "alternative space positive")
    chk(sp["log2_alternatives_uniform"] > sp["log2_alternatives_frequency"],
        "uniform space > frequency space (frequency constrains)")
    chk(sp["H_choice_bits_per_draw"] < sp["H_uniform_bits_per_draw"], "H_choice < H_uniform")

    rare = load(out, "ayah_counterfactuals.json")
    chk(0.0 <= rare["structural_statistic_percentile"] <= 1.0, "typicality percentile in [0,1]")
    chk("TYPICAL" in rare["lexical_typicality"], "lexical typicality reported")

    cls = load(out, "selection_classification.json")
    chk(cls["classification"] in TYPES, "classification in allowed set")
    v = cls["verdict"]
    chk(v["Q4_constraints_explain_lexical_choices"] in ("YES", "NO", "PARTIAL"), "Q4 in set")
    chk(v["Q6_classification"] == cls["classification"], "Q6 == classification")
    # consistency: weakly-constrained iff residual fraction > 0.6
    cr = load(out, "choice_residual.json")
    rf = cr["fraction_of_uniform_choice_remaining"]
    if rf > 0.6:
        chk(cls["classification"] == "TYPE_B_weakly_constrained_selection",
            "verdict logic: residual>0.6 ⇒ weakly constrained")

    man = load(out, "counterfactual_manifest.json")
    chk(man["input_sha256"]["monad.db"] == sha(args.db), "manifest db hash")
    chk(any("never evaluate" in p.lower() for p in man["prohibitions_observed"]),
        "prohibitions: never-evaluate-truth/theology present")

    for n in REPORTS:
        chk((docs / n).exists(), f"missing report {n}")

    if args.rebuild:
        print("  --rebuild …")
        tmp = Path(tempfile.mkdtemp(prefix="monad_cf_"))
        res = subprocess.run([sys.executable, "scripts/build_counterfactual.py",
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
