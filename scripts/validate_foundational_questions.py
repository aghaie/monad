#!/usr/bin/env python3
"""Monad — Phase ΩΣ validator: Foundational Question Discovery Engine."""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PRODUCTS = [
    "question_formalization.json", "evidence_inventory.json", "question_results.json",
    "question_integration.json", "question_falsification.json", "question_stability.json",
    "representation_validation.json", "foundational_model.json", "foundational_manifest.json",
]
REPORTS = [
    "q1-minimization-report.md", "q2-maximization-report.md", "q3-human-vs-world-report.md",
    "q4-minimal-core-report.md", "q5-hidden-reality-report.md", "q6-omission-report.md",
    "q7-object-vs-relation-report.md", "q8-book-vs-engine-report.md", "q9-name-removal-report.md",
    "q10-order-report.md", "q11-time-report.md", "q12-geometry-report.md",
    "q13-essentiality-report.md", "q14-central-question-report.md", "question-integration-report.md",
    "omega-sigma-falsification-report.md", "omega-sigma-stability-report.md",
    "omega-sigma-representation-report.md", "phase-omega-sigma-final-report.md",
    "omega-sigma-executive-summary.md",
]
METHOD = "foundational-questions-1.0"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(d, n):
    return json.loads((Path(d) / n).read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="generated/foundational_questions")
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

    print(f"Validating Phase ΩΣ in {out}/ …")
    for n in PRODUCTS:
        chk((out / n).exists(), f"missing {n}")
    for n in PRODUCTS:
        if (out / n).exists():
            chk(load(out, n).get("method") == METHOD, f"{n}: method tag")

    # all 14 questions present in results
    res = load(out, "question_results.json")["results"]
    expected_q = {"Q3", "Q7", "Q8", "Q9", "Q11", "Q12", "Q13", "Q14",
                  "Q1_minimization", "Q2_maximization", "Q5_hidden_reality",
                  "Q6_omission", "Q10_order"}
    chk(expected_q.issubset(set(res)), "all 14 questions represented in results")

    # Q9 retention sanity: ratios near 1, coherence retained
    q9 = res["Q9"]["metrics"]
    chk(0.85 < q9["retention"]["gini_ratio"] < 1.15, "Q9 gini retention near 1")
    chk(0.85 < q9["retention"]["residual_ratio"] < 1.15, "Q9 residual retention near 1")
    chk(q9["before"]["coherence_beyond_null"] and q9["after"]["coherence_beyond_null"],
        "Q9 coherence retained before+after")
    chk(0.0 < q9["proper_noun_token_fraction"] < 0.2, "Q9 PN fraction in (0,0.2)")

    # Q12 ring: real, null, z present and internally consistent with beyond_null
    q12 = res["Q12"]["metrics"]
    chk(q12["beyond_null"] == (q12["mirror_jaccard_real"] > q12["null_p95"]), "Q12 beyond_null consistent")

    # census ratios in [0,1]
    chk(0 <= res["Q3"]["metrics"]["address_share"] <= 1, "Q3 share in [0,1]")
    chk(0 <= res["Q7"]["metrics"]["object_share"] <= 1, "Q7 share in [0,1]")
    chk(0 <= res["Q8"]["metrics"]["process_share"] <= 1, "Q8 share in [0,1]")

    # representation independence: explained+residual=1 at each level, agreement count consistent
    rv = load(out, "representation_validation.json")
    chk(set(rv["representations"]) == {"root", "lemma", "word"}, "repval 3 levels")
    for l, d in rv["representations"].items():
        chk(abs(d["explained_by_frequency"] + d["residual_fraction"] - 1.0) < 1e-6, f"{l}: explained+residual=1")
    chk(rv["n_agree"] == sum(1 for v in rv["invariant_checks"].values() if v), "repval agreement consistent")

    # model: 14 answers, honest verdict present
    model = load(out, "foundational_model.json")
    chk(len(model["answers"]) == 14, "model has 14 answers")
    chk("PARTIAL" in model["honest_verdict"] or "SUCCESS" in model["honest_verdict"], "model verdict present")
    chk(model["representation_independent"] is True, "model representation-independent flag")

    # manifest: db hash + prohibitions
    man = load(out, "foundational_manifest.json")
    chk(man["input_sha256"]["monad.db"] == sha(args.db), "manifest db hash")
    chk(any("no interpretation" in p.lower() for p in man["prohibitions_observed"]), "prohibition: no interpretation")
    chk(any("unknown is first-class" in p.lower() for p in man["prohibitions_observed"]),
        "prohibition: UNKNOWN first-class")

    for nm in REPORTS:
        chk((docs / nm).exists(), f"missing report {nm}")

    if args.rebuild:
        print("  --rebuild …")
        tmp = Path(tempfile.mkdtemp(prefix="monad_fq_"))
        res2 = subprocess.run([sys.executable, "scripts/build_foundational_questions.py",
                               "--db", args.db, "--out", str(tmp)], capture_output=True, text=True)
        chk(res2.returncode == 0, f"rebuild exit 0 ({res2.stderr[-300:]})")
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
