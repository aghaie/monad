#!/usr/bin/env python3
"""
scripts/validate_L3_roots.py

Validates Layer L3 (self-grounded root lexicon): well-formed, name-coordinates
are meaningful, masked-root recovery beats baseline and random, reproducible.
Exit 0 = all pass.
"""

import filecmp
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "generated" / "layers" / "L3_roots"
BUILD = REPO / "scripts" / "build_L3_roots.py"
CONTENT = ["root_lexicon.json", "self_prediction.json"]

results = []


def chk(name, ok, detail=""):
    results.append(bool(ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def main():
    if not all((OUT / f).exists() for f in CONTENT):
        print("L3 outputs missing — run build_L3_roots.py first.")
        return 1
    lex = json.loads((OUT / "root_lexicon.json").read_text(encoding="utf-8"))
    sp = json.loads((OUT / "self_prediction.json").read_text(encoding="utf-8"))
    roots = lex["roots"]

    print("Validating L3 — Self-grounded Root Lexicon\n")
    chk("lexicon non-empty", len(roots) > 1000, f"{len(roots)} roots")
    chk("16 anchor names carried", len(lex["anchor_names"]) == 16, str(len(lex["anchor_names"])))
    chk("every root has a tier", all("tier" in v for v in roots.values()))

    # Meaningfulness: the mercy root must anchor on a mercy name; knowledge on علیم.
    rhm = roots.get("rHm", {}).get("name_coordinates", [])
    elm = roots.get("Elm", {}).get("name_coordinates", [])
    chk("rHm (mercy) top name-coordinate is رحیم",
        bool(rhm) and rhm[0]["name_bw"] == "r~aHiym",
        rhm[0]["name_bw"] if rhm else "none")
    chk("Elm (knowledge) top name-coordinate is علیم",
        bool(elm) and elm[0]["name_bw"] == "Ealiym",
        elm[0]["name_bw"] if elm else "none")
    chk("roots carry relational_neighbors",
        any(v["relational_neighbors"] for v in roots.values()))
    chk("name-anchored roots have field_neighbors",
        any(v["field_neighbors"] for v in roots.values()))

    m1 = sp["model"]["top1_pct"]; b1 = sp["baseline"]["top1_pct"]
    rf = sp["random_floor_top1_pct"]; m3 = sp["model"]["top3_pct"]; b3 = sp["baseline"]["top3_pct"]
    chk("self-prediction beats random floor", m1 > rf, f"{m1}% vs {rf}%")
    chk("self-prediction beats baseline (top1)", m1 > b1, f"{m1}% vs {b1}%")
    chk("self-prediction beats baseline (top3)", m3 > b3, f"{m3}% vs {b3}%")
    chk("verdict == model_beats_baseline", sp["verdict"] == "model_beats_baseline", sp["verdict"])

    with tempfile.TemporaryDirectory() as td:
        proc = subprocess.run([sys.executable, str(BUILD), "--out", td, "--quiet"],
                              capture_output=True, text=True)
        identical = (proc.returncode == 0) and all(
            filecmp.cmp(OUT / f, Path(td) / f, shallow=False) for f in CONTENT)
    chk("deterministic re-run (byte-identical outputs)", identical)

    ok = all(results)
    print(f"\n{'ALL PASS' if ok else 'FAILURES PRESENT'} — {sum(results)}/{len(results)}")
    if ok:
        print(f"\n  Masked-root recovery {m1}% top-1 / {m3}% top-3 vs baseline "
              f"{b1}% / {b3}% — the network recovers its own roots from context.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
