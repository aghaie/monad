#!/usr/bin/env python3
"""validate_L6_network.py — the inter-ayah self-interpretation result is
well-formed, the network beats the random null for both all and (strictly) rare
target roots, and the build is reproducible. Exit 0 = all pass."""

import filecmp
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "generated" / "layers" / "L6_network"
BUILD = REPO / "scripts" / "build_L6_network.py"
CONTENT = ["intertextual_test.json", "ayah_network.json"]

results = []


def chk(name, ok, detail=""):
    results.append(bool(ok)); print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def main():
    if not all((OUT / f).exists() for f in CONTENT):
        print("L6 outputs missing — run build_L6_network.py first."); return 1
    t = json.loads((OUT / "intertextual_test.json").read_text(encoding="utf-8"))
    net = json.loads((OUT / "ayah_network.json").read_text(encoding="utf-8"))
    a = t["all_target_roots"]; r = t["rare_target_roots"]

    print("Validating L6 — Inter-ayah Network\n")
    chk("test covers many ayat", t["tested_ayat"] > 3000, f'{t["tested_ayat"]} ayat')
    chk("ALL target roots: network beats random", a["network_hit"] > a["random_null"]["max"],
        f'{a["network_hit"]} vs max {a["random_null"]["max"]}')
    chk("ALL target roots: p <= 0.01", a["p"] <= 0.01, f'p={a["p"]}')
    chk("RARE target roots: network beats random", r["network_hit"] > r["random_null"]["max"],
        f'{r["network_hit"]} vs max {r["random_null"]["max"]}')
    chk("RARE target roots: p <= 0.01", r["p"] <= 0.01, f'p={r["p"]}')
    chk("RARE effect is large (network >= 3x random mean)",
        r["network_hit"] >= 3 * r["random_null"]["mean"],
        f'{r["network_hit"]} vs {r["random_null"]["mean"]}')
    chk("ayah network has connections", len(net["connections"]) > 1000, f'{len(net["connections"])}')
    chk("connections are cross-referenced (each has neighbours)",
        all(c["neighbours"] for c in net["connections"][:50]))

    with tempfile.TemporaryDirectory() as td:
        proc = subprocess.run([sys.executable, str(BUILD), "--out", td, "--quiet"],
                              capture_output=True, text=True)
        identical = (proc.returncode == 0) and all(
            filecmp.cmp(OUT / f, Path(td) / f, shallow=False) for f in CONTENT)
    chk("deterministic re-run (byte-identical outputs)", identical)

    ok = all(results)
    print(f"\n{'ALL PASS' if ok else 'FAILURES PRESENT'} — {sum(results)}/{len(results)}")
    if ok:
        print(f"\n  VERSES EXPLAIN ONE ANOTHER: rare content recovered at "
              f"{r['network_hit']} vs {r['random_null']['mean']} random "
              f"(~{r['network_hit']/r['random_null']['mean']:.0f}x), p={r['p']}.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
