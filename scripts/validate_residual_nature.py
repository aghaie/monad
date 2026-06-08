#!/usr/bin/env python3
"""Monad — Phase Ψ validator: Residual Nature Discovery."""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PRODUCTS = [
    "residual_decomposition.json", "long_range_results.json", "referentiality_results.json",
    "combinatorial_results.json", "reconstruction_results.json", "representation_results.json",
    "compression_boundary.json", "null_assault.json", "residual_taxonomy.json",
    "residual_nature_manifest.json",
]
REPORTS = [
    "residual-decomposition-report.md", "long-range-report.md", "referentiality-report.md",
    "combinatorial-report.md", "reconstruction-report.md", "representation-sensitivity-report.md",
    "compression-boundary-report.md", "residual-taxonomy-report.md",
    "residual-null-assault-report.md", "phase-psi-final-report.md",
]
METHOD = "residual-nature-1.0"
TYPES = ["TYPE_001_random", "TYPE_002_lexical", "TYPE_003_referential", "TYPE_004_structural",
         "TYPE_005_higher_order", "TYPE_006_mixed", "TYPE_007_unknown"]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(d, n):
    return json.loads((Path(d) / n).read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="generated/residual_nature")
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

    print(f"Validating Phase Ψ in {out}/ …")
    for n in PRODUCTS:
        chk((out / n).exists(), f"missing {n}")
    for n in PRODUCTS:
        if (out / n).exists():
            chk(load(out, n).get("method") == METHOD, f"{n}: method tag")

    dec = load(out, "residual_decomposition.json")["budget"]
    chk(0.0 <= dec["residual_fraction_of_uniform"] <= 1.0, "residual fraction in [0,1]")
    chk(abs(dec["of_residual_explained_by_surah_topical"] + dec["of_residual_irreducible_lexical"] - 1.0) < 1e-6,
        "residual fractions sum to 1")
    chk(dec["of_residual_explained_by_surah_topical"] >= 0.0, "topical fraction non-negative (clamped)")

    lr = load(out, "long_range_results.json")
    chk(len(lr["recurrence_profile"]) >= 7, "long-range profile has all distances")

    rec = load(out, "reconstruction_results.json")
    chk(rec["recoverable_out_of_sample"] is False, "reconstruction: not recoverable out-of-sample (Phase P)")

    rep = load(out, "representation_results.json")
    chk(set(rep["levels"].keys()) == {"root", "lemma", "word"}, "representation: 3 levels")

    tax = load(out, "residual_taxonomy.json")
    chk(tax["taxonomy"] in TYPES, "taxonomy in allowed set")
    v = tax["verdict"]
    comp = v["Q1_residual_composition"]
    chk(abs(comp["surah_topical_discourse_frequency"] + comp["irreducible_lexical_specificity"]
            + comp["structural_generalizable"] + comp["higher_order"] + comp["long_range"] - 1.0) < 1e-6,
        "Q1 composition sums to 1")
    chk(v["Q3_long_range_exists"] in ("YES", "NO", "PARTIAL"), "Q3 in set")
    chk(v["Q6_remains_unexplained_after_attacks"] in ("YES", "NO"), "Q6 in set")
    na = load(out, "null_assault.json")
    chk(isinstance(na["surah_topical_survives_null"], bool), "null assault boolean")

    man = load(out, "residual_nature_manifest.json")
    chk(man["input_sha256"]["monad.db"] == sha(args.db), "manifest db hash")
    chk(any("we do not know" in p.lower() for p in man["prohibitions_observed"]), "'we do not know' principle present")

    for n in REPORTS:
        chk((docs / n).exists(), f"missing report {n}")

    if args.rebuild:
        print("  --rebuild …")
        tmp = Path(tempfile.mkdtemp(prefix="monad_psi_"))
        res = subprocess.run([sys.executable, "scripts/build_residual_nature.py",
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
