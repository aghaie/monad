#!/usr/bin/env python3
"""Monad — Phase Z validator: Quran Self-Method Discovery (falsification study).

Structural-integrity checks + verdict/threshold consistency + byte-identical rebuild.
"""

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
    "methodology_graph.json", "methodology_chains.json", "methodology_prerequisites.json",
    "methodology_obstacles.json", "methodology_outcomes.json", "methodology_cycles.json",
    "methodology_falsification.json", "methodology_stability.json", "methodology_manifest.json",
]
REPORTS = [
    "methodology-discovery-report.md", "methodology-chain-report.md",
    "methodology-obstacle-report.md", "methodology-outcome-report.md",
    "methodology-cycle-report.md", "methodology-stability-report.md",
    "self-methodology-falsification-report.md", "phase-z-final-report.md",
]
METHOD = "self-methodology-1.0"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(d, n):
    return json.loads((Path(d) / n).read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="generated/self_methodology")
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

    print(f"Validating Phase Z in {out}/ …")

    for n in PRODUCTS:
        chk((out / n).exists(), f"missing {n}")
    for n in PRODUCTS:
        if (out / n).exists():
            chk(load(out, n).get("method") == METHOD, f"{n}: method tag")

    bp = importlib.util.spec_from_file_location("bz", "scripts/build_self_methodology.py")
    mod = importlib.util.module_from_spec(bp)
    bp.loader.exec_module(mod)

    # verdict consistency with pre-registered thresholds
    fal = load(out, "methodology_falsification.json")
    v = fal["verdict"]
    chk(v["verdict"] in ("YES", "NO", "PARTIAL"), "verdict in {YES,NO,PARTIAL}")
    ef = v["existence_survivor_fraction"]
    df = v["directionality_survivor_fraction"]
    bb = v["largest_connected_backbone_nodes"]
    if ef < mod.NO_EXIST_FRAC:
        chk(v["verdict"] == "NO", "verdict logic: low existence ⇒ NO")
    elif df >= mod.YES_DIR_FRAC and bb >= mod.YES_BACKBONE_NODES:
        chk(v["verdict"] == "YES", "verdict logic: high directionality+backbone ⇒ YES")
    else:
        chk(v["verdict"] == "PARTIAL", "verdict logic: otherwise ⇒ PARTIAL")
    man = load(out, "methodology_manifest.json")
    chk(man["verdict"] == v["verdict"], "manifest verdict == falsification verdict")
    chk(man["input_sha256"]["monad.db"] == sha(args.db), "manifest db hash matches")

    # falsification structure: every candidate edge has the full null battery
    for e in fal["results"]:
        for k in ["exists_beyond_frequency", "directional_beyond_order", "length_stable",
                  "real_support", "real_dir", "freq_null_support_p95", "order_null_dir_p95",
                  "word_order_null_dir_p95", "ayah_order_null_dir_p95"]:
            chk(k in e, f"falsification edge missing {k}")
    chk(fal["edges_existing_beyond_frequency"] ==
        sum(1 for e in fal["results"] if e["exists_beyond_frequency"]),
        "existence count consistent")

    # stability structure: bootstrap CI + subsample persistence present
    st = load(out, "methodology_stability.json")
    for x in st["results"]:
        chk("boot_ci_lo" in x and "subsample_persistence" in x, "stability fields present")
        chk(x["stable"] == (x["dir_ci_excludes_0.5"] and min(x["subsample_persistence"].values()) >= 0.9),
            f"stability rule for {x['edge']}")
    chk(len(st["threshold_sweep"]) == len(mod.THRESH_SUPPORT) * len(mod.THRESH_DIR),
        "threshold sweep complete")

    # comparison to Q/X/P present in verdict
    cmp = v.get("comparison", {})
    for k in ["Q_claim", "X_claim", "P_result", "Z_test"]:
        chk(k in cmp, f"verdict comparison missing {k}")

    # reports present
    for n in REPORTS:
        chk((docs / n).exists(), f"missing report {n}")

    # determinism
    if args.rebuild:
        print("  --rebuild: regenerating into temp dir …")
        tmp = Path(tempfile.mkdtemp(prefix="monad_z_"))
        res = subprocess.run([sys.executable, "scripts/build_self_methodology.py",
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
