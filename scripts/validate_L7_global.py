#!/usr/bin/env python3
"""validate_L7_global.py — L7 global structure well-formed, the sura-coherence
result beats the permutation null, the crossref map covers the corpus, and the
build is reproducible. Exit 0 = all pass."""

import filecmp
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "generated" / "layers" / "L7_global"
BUILD = REPO / "scripts" / "build_L7_global.py"
CONTENT = ["global_structure.json", "crossref_index.json"]

results = []


def chk(name, ok, detail=""):
    results.append(bool(ok)); print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def main():
    if not all((OUT / f).exists() for f in CONTENT):
        print("L7 outputs missing — run build_L7_global.py first."); return 1
    s = json.loads((OUT / "global_structure.json").read_text(encoding="utf-8"))
    x = json.loads((OUT / "crossref_index.json").read_text(encoding="utf-8"))
    sc = s["sura_coherence"]

    print("Validating L7 — Global structure\n")
    chk("weighted network built", s["weighted_pairs"] > 10000, f'{s["weighted_pairs"]} pairs')
    chk("SURA COHERENCE: intra-sura beats permutation null",
        sc["intra_sura_weight_fraction"] > sc["null_permuted_labels"]["max"],
        f'{sc["intra_sura_weight_fraction"]} vs max {sc["null_permuted_labels"]["max"]}')
    chk("SURA COHERENCE: p <= 0.01", sc["p"] <= 0.01, f'p={sc["p"]}')
    chk("intra-sura concentration >= 2x null mean",
        sc["intra_sura_weight_fraction"] >= 2 * sc["null_permuted_labels"]["mean"])
    chk("crossref index covers the corpus", len(x["index"]) > 5000, f'{len(x["index"])} ayat')
    chk("hubs identified", len(s["hubs_most_connecting_verses"]) >= 10)
    chk("crossref entries have weights + cross_sura flags",
        all("weight" in r and "cross_sura" in r
            for v in list(x["index"].values())[:50] for r in v))

    with tempfile.TemporaryDirectory() as td:
        proc = subprocess.run([sys.executable, str(BUILD), "--out", td, "--quiet"],
                              capture_output=True, text=True)
        identical = (proc.returncode == 0) and all(
            filecmp.cmp(OUT / f, Path(td) / f, shallow=False) for f in CONTENT)
    chk("deterministic re-run (byte-identical outputs)", identical)

    ok = all(results)
    print(f"\n{'ALL PASS' if ok else 'FAILURES PRESENT'} — {sum(results)}/{len(results)}")
    if ok:
        print(f"\n  Suras are coherent network communities: intra-sura connection "
              f"{sc['intra_sura_weight_fraction']} vs {sc['null_permuted_labels']['mean']} null "
              f"(~{sc['intra_sura_weight_fraction']/sc['null_permuted_labels']['mean']:.1f}x), p={sc['p']}.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
