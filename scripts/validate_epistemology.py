#!/usr/bin/env python3
"""
Monad — Phase X validator: Epistemology Discovery Engine
========================================================

Structural-integrity checks on the Phase X outputs and, with --rebuild, a
byte-identical reproduction check (determinism) into a temp directory.
"""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PRODUCTS = [
    "epistemic_actions.json", "knowledge_pathways.json", "ignorance_pathways.json",
    "enablers.json", "obstacles.json", "epistemic_sequence.json",
    "epistemic_compression.json", "falsification_results.json", "robustness_results.json",
    "epistemology_manifest.json",
]
METHOD = "epistemology-discovery-1.0"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(d, name):
    return json.loads((Path(d) / name).read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="generated/epistemology")
    ap.add_argument("--db", default="generated/monad.db")
    ap.add_argument("--rebuild", action="store_true")
    args = ap.parse_args()
    out = Path(args.out)
    checks, failed = 0, 0

    def chk(cond, msg):
        nonlocal checks, failed
        checks += 1
        if not cond:
            failed += 1
            print(f"  FAIL: {msg}")

    print(f"Validating Phase X outputs in {out}/ …")

    for name in PRODUCTS:
        chk((out / name).exists(), f"missing product {name}")
    for name in PRODUCTS:
        if (out / name).exists():
            chk(load(out, name).get("method") == METHOD, f"{name}: method tag")

    # actions inventory
    ai = load(out, "epistemic_actions.json")
    chk(len(ai["actions"]) == 8, "actions: 8 action groups")
    calls = [a["verbal_calls"] for a in ai["actions"]]
    chk(calls == sorted(calls, reverse=True), "actions: sorted by verbal calls")
    chk(ai["dominant_action"] == ai["actions"][0]["action"], "actions: dominant = top")

    # knowledge pathways — directionality in range, edges directional, net outflow sums ~0
    kp = load(out, "knowledge_pathways.json")
    for e in kp["edges"]:
        chk(0.5 <= e["directionality"] <= 1.0, f"kpath edge {e['from']}→{e['to']}: dir in [0.5,1]")
        chk(e["flow"] >= e["reverse"], f"kpath edge {e['from']}→{e['to']}: flow>=reverse")
        chk(e["support"] >= 8, f"kpath edge {e['from']}→{e['to']}: support>=MIN_SUPPORT")
    net_sum = round(sum(x["net_outflow"] for x in kp["net_outflow_ranking"]), 3)
    chk(net_sum == 0.0, f"kpath: net outflow sums to zero ({net_sum})")
    rk = [x["net_outflow"] for x in kp["net_outflow_ranking"]]
    chk(rk == sorted(rk, reverse=True), "kpath: net-outflow ranking sorted")

    # ignorance pathways
    ip = load(out, "ignorance_pathways.json")
    for e in ip["edges"]:
        chk(0.5 <= e["directionality"] <= 1.0, f"ipath edge: dir in [0.5,1]")

    # enablers / obstacles — net forward positive
    en = load(out, "enablers.json")
    for x in en["enablers"]:
        chk(x["flow_into_target"] >= x["reverse"], f"enabler {x['node']}: net forward")
    ob = load(out, "obstacles.json")
    for x in ob["obstacles"]:
        chk(x["flow_into_target"] >= x["reverse"], f"obstacle {x['node']}: net forward")

    # sequence — modes ranked, gradient present
    sq = load(out, "epistemic_sequence.json")
    mf = [m["flow_to_knowledge"] for m in sq["modes_of_knowing"]]
    chk(mf == sorted(mf, reverse=True), "sequence: modes ranked by flow")
    chk(len(sq["pipeline_order"]) == len(kp["net_outflow_ranking"]), "sequence: pipeline covers all nodes")

    # compression — stages partition, forward consistency in [0,1]
    cp = load(out, "epistemic_compression.json")
    allnodes = {n.split(":")[1] for n in kp["net_outflow_ranking"][0]["node"].split() } if False else None
    flat = [n for st in cp["stages"] for n in st["nodes"]]
    chk(len(flat) == len(set(flat)), "compression: stages disjoint")
    chk(len(flat) == len(kp["net_outflow_ranking"]), "compression: stages cover all nodes")
    chk(0.0 <= cp["inter_stage_forward_consistency"] <= 1.0, "compression: consistency in [0,1]")
    chk(cp["compressible"] == (cp["inter_stage_forward_consistency"] >= 0.6),
        "compression: verdict matches threshold")

    # falsification — survive iff dir>=margin
    fl = load(out, "falsification_results.json")
    m = fl["margin"]
    for x in fl["results"]:
        chk((x["result"] == "SURVIVES") == (x["directionality"] >= m), f"falsif {x['from']}→{x['to']}: rule")
    chk(fl["n_survive"] + fl["n_refuted"] == fl["n_edges_tested"], "falsif: counts add up")

    # robustness — stable iff both halves forward
    rb = load(out, "robustness_results.json")
    for x in rb["edges"]:
        chk(x["stable"] == (x["dir_meccan"] >= 0.5 and x["dir_medinan"] >= 0.5),
            f"robust {x['from']}→{x['to']}: stability rule")
    chk(0.0 <= rb["stable_fraction"] <= 1.0, "robust: fraction in [0,1]")

    # manifest
    man = load(out, "epistemology_manifest.json")
    chk(man["input_sha256"]["monad.db"] == sha(args.db), "manifest: db hash matches")
    chk(len(man["prohibitions_observed"]) >= 12, "manifest: prohibitions listed")

    # determinism
    if args.rebuild:
        print("  --rebuild: regenerating into temp dir for byte-identical check …")
        tmp = Path(tempfile.mkdtemp(prefix="monad_x_"))
        try:
            res = subprocess.run(
                [sys.executable, "scripts/build_epistemology.py", "--db", args.db, "--out", str(tmp)],
                capture_output=True, text=True)
            chk(res.returncode == 0, f"rebuild exit 0 ({res.stderr[-200:]})")
            for name in PRODUCTS:
                a, b = out / name, tmp / name
                if a.exists() and b.exists():
                    chk(sha(a) == sha(b), f"rebuild byte-identical: {name}")
                else:
                    chk(False, f"rebuild missing: {name}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n  {checks - failed}/{checks} checks pass" + (" — FAILURES" if failed else " — all pass"))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
