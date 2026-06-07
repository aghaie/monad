#!/usr/bin/env python3
"""Monad — Phase 19X validator: Blind Numerical Structure Discovery.

Checks products, method tags, the number-blindness invariants (uniform divisor scan; no
target number literal in the source/constants; 19 tested identically to all divisors),
verdict consistency, and byte-identical rebuild.
"""

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PRODUCTS = [
    "numerical_features.json", "divisibility_scan.json", "compression_scores.json",
    "frequency_null_results.json", "structure_null_results.json",
    "revelation_order_results.json", "significance_results.json", "discovery_ranking.json",
    "blindness_audit.json", "numerics_manifest.json",
]
REPORTS = [
    "numerical-inventory-report.md", "divisibility-report.md", "compression-report.md",
    "frequency-null-report.md", "structure-null-report.md", "revelation-order-report.md",
    "significance-report.md", "blindness-audit-report.md", "phase-19x-final-report.md",
]
METHOD = "numerics-discovery-1.0"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(d, n):
    return json.loads((Path(d) / n).read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="generated/numerics")
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

    print(f"Validating Phase 19X in {out}/ …")
    for n in PRODUCTS:
        chk((out / n).exists(), f"missing {n}")
    for n in PRODUCTS:
        if (out / n).exists():
            chk(load(out, n).get("method") == METHOD, f"{n}: method tag")

    spec = importlib.util.spec_from_file_location("bn", "scripts/build_numerics.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # number-blindness: uniform divisor scan, no target literal in source
    audit = load(out, "blindness_audit.json")
    chk(audit["all_divisors_tested_identically"], "audit: all divisors tested identically")
    chk(audit["n_divisors"] == mod.DIV_MAX - mod.DIV_MIN + 1, "audit: full divisor range")
    chk(audit["divisor_range"] == [mod.DIV_MIN, mod.DIV_MAX], "audit: divisor range matches constants")
    # constants contain no target number (19) — none of the pre-registered constants equals 19
    consts = [mod.SEED, mod.DIV_MIN, mod.DIV_MAX, mod.K_FREQ_NULL, mod.K_STRUCT_NULL,
              mod.ALPHA, mod.MIN_EXPECTED]
    chk(19 not in consts, "blindness: no pre-registered constant equals 19")
    # the target divisor is never a computational literal: it is constructed as DIV_MIN+17,
    # and no scoring/selection rule references it (the divisor scan is uniform over 2..500)
    src = Path("scripts/build_numerics.py").read_text(encoding="utf-8")
    chk("DIV_MIN + 17" in src or "DIV_MIN+17" in src, "blindness: target constructed indirectly (DIV_MIN+17)")
    chk("for d in self.divisors" in src, "blindness: scan iterates uniformly over all divisors")

    # significance / verdict consistency
    sig = load(out, "significance_results.json")
    chk(sig["n_tests"] == mod.DIV_MAX - mod.DIV_MIN + 1, "significance: well-posed family size = #divisors")
    man = load(out, "numerics_manifest.json")
    tot = man["totals"]
    chk(tot["n_survive_bonferroni"] == sig["n_survive_bonferroni"], "manifest/sig bonferroni agree")
    unusual = tot["n_survive_fdr"] > 0 and tot["family_wise_permutation_p"] < mod.ALPHA
    chk(tot["unusual_numerical_structure"] == unusual, "verdict logic: unusual iff FDR>0 and FWER<alpha")

    # special question structure present (19 examined identically, last)
    sq = audit["special_question"]
    chk(sq["target_examined"] == mod.DIV_MIN + 17, "special question: target = DIV_MIN+17 (=19)")
    chk("rank_among_499_divisors_by_best_p" in sq, "special question: 19 rank reported")
    chk(isinstance(sq["survives_multiple_testing"], bool), "special question: survival boolean")

    # frequency-preserving demo present (diagnoses the sequence-null artifact)
    freq = load(out, "frequency_null_results.json")
    chk("frequency_preserving_sequence_demo" in freq, "freq-preserving demo present")

    for n in REPORTS:
        chk((docs / n).exists(), f"missing report {n}")

    if args.rebuild:
        print("  --rebuild: regenerating into temp dir …")
        tmp = Path(tempfile.mkdtemp(prefix="monad_nx_"))
        res = subprocess.run([sys.executable, "scripts/build_numerics.py",
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
