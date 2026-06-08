#!/usr/bin/env python3
"""Monad — Phase Δ validator: Quranic Decision Architecture Discovery."""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PRODUCTS = [
    "decision_events.json", "decision_triggers.json", "information_usage.json",
    "uncertainty_architecture.json", "conflict_resolution.json", "priority_architecture.json",
    "outcome_evaluation.json", "decision_loops.json", "agent_architecture.json",
    "decision_falsification.json", "decision_stability.json", "decision_manifest.json",
]
REPORTS = [
    "decision-events-report.md", "decision-triggers-report.md", "information-usage-report.md",
    "uncertainty-report.md", "conflict-resolution-report.md", "priority-report.md",
    "outcome-evaluation-report.md", "decision-loops-report.md", "agent-architecture-report.md",
    "decision-falsification-report.md", "decision-stability-report.md", "phase-delta-final-report.md",
]
METHOD = "decision-architecture-1.0"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(d, n):
    return json.loads((Path(d) / n).read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="generated/decision_architecture")
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

    print(f"Validating Phase Δ in {out}/ …")
    for n in PRODUCTS:
        chk((out / n).exists(), f"missing {n}")
    for n in PRODUCTS:
        if (out / n).exists():
            chk(load(out, n).get("method") == METHOD, f"{n}: method tag")

    import importlib.util
    spec = importlib.util.spec_from_file_location("bd", "scripts/build_decision_architecture.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    fal = load(out, "decision_falsification.json")
    chk(fal["n_exist"] == sum(1 for e in fal["results"] if e["exists_beyond_frequency"]),
        "falsification exist count consistent")
    for e in fal["results"]:
        for k in ["exists_beyond_frequency", "directional_beyond_order", "real_support", "real_dir"]:
            chk(k in e, f"falsification edge missing {k}")

    stab = load(out, "decision_stability.json")
    for x in stab["results"]:
        chk(x["stable"] == (x["boot_ci_lo"] > 0.5 and min(x["subsample_persistence"].values()) >= 0.9),
            f"stability rule for {x['edge']}")

    v = load(out, "agent_architecture.json")["verdict"]
    chk(v["Q1_coherent_architecture"] in ("YES", "NO", "PARTIAL"), "Q1 in set")
    chk(v["Q8_survives_falsification"] in ("YES", "NO", "PARTIAL"), "Q8 in set")
    # verdict logic: NO if exist_fraction < NO_EXIST_FRAC
    if v["exist_fraction"] < mod.NO_EXIST_FRAC:
        chk(v["Q1_coherent_architecture"] == "NO", "verdict logic: low existence ⇒ NO")
    chk(isinstance(v["Q2_robust_components_surviving"], int), "Q2 integer")
    chk("comparison" in v and all(k in v["comparison"] for k in ["X", "Z", "R", "P"]),
        "verdict cross-references X/Z/R/P")

    man = load(out, "decision_manifest.json")
    chk(man["input_sha256"]["monad.db"] == sha(args.db), "manifest db hash")
    chk(man["totals"]["coherent_architecture"] == v["Q1_coherent_architecture"], "manifest/verdict agree")
    chk(any("imposed" in p.lower() for p in man["prohibitions_observed"]), "no-framework-imposed prohibition")

    for n in REPORTS:
        chk((docs / n).exists(), f"missing report {n}")

    if args.rebuild:
        print("  --rebuild …")
        tmp = Path(tempfile.mkdtemp(prefix="monad_da_"))
        res = subprocess.run([sys.executable, "scripts/build_decision_architecture.py",
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
