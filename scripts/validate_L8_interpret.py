#!/usr/bin/env python3
"""validate_L8_interpret.py — the stability result holds (concept definitions
replicate across independent halves far above the mismatched null), the
self-tafsir demonstrations are well-formed, and the build is reproducible.
Exit 0 = all pass."""

import filecmp
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "generated" / "layers" / "L8_interpret"
BUILD = REPO / "scripts" / "build_L8_interpret.py"
CONTENT = ["stability.json", "self_tafsir_demo.json"]

results = []


def chk(name, ok, detail=""):
    results.append(bool(ok)); print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def main():
    if not all((OUT / f).exists() for f in CONTENT):
        print("L8 outputs missing — run build_L8_interpret.py first."); return 1
    st = json.loads((OUT / "stability.json").read_text(encoding="utf-8"))
    demo = json.loads((OUT / "self_tafsir_demo.json").read_text(encoding="utf-8"))["demonstrations"]

    print("Validating L8 — Self-interpretation capstone\n")
    chk("stability tested enough roots", st["tested_roots"] >= 200, f'{st["tested_roots"]} roots')
    chk("STABILITY: real replication beats mismatched null",
        st["real_mean_jaccard"] > st["null_max"], f'{st["real_mean_jaccard"]} vs max {st["null_max"]}')
    chk("STABILITY: p <= 0.01", st["p"] <= 0.01, f'p={st["p"]}')
    chk("STABILITY: replication >= 3x null", st["fold_factor"] >= 3, f'{st["fold_factor"]}x')
    chk("self-tafsir produced demonstrations", len(demo) >= 4, f'{len(demo)} verses')
    linked = [v for v, ls in demo.items() if ls and ls[0].get("shared_concepts")]
    chk("demonstrations carry shared concept-roots", len(linked) >= 3, f'{len(linked)} with concepts')
    chk("links are cross-sura by construction",
        all(ls[0]["ayah"].split(":")[0] != v.split(":")[0] for v, ls in demo.items() if ls))

    with tempfile.TemporaryDirectory() as td:
        proc = subprocess.run([sys.executable, str(BUILD), "--out", td, "--quiet"],
                              capture_output=True, text=True)
        identical = (proc.returncode == 0) and all(
            filecmp.cmp(OUT / f, Path(td) / f, shallow=False) for f in CONTENT)
    chk("deterministic re-run (byte-identical outputs)", identical)

    ok = all(results)
    print(f"\n{'ALL PASS' if ok else 'FAILURES PRESENT'} — {sum(results)}/{len(results)}")
    if ok:
        print(f"\n  Self-derived concept definitions replicate across independent halves "
              f"{st['real_mean_jaccard']} vs {st['mismatched_null_mean']} null "
              f"(~{st['fold_factor']}x), p={st['p']} — the meanings are reliable.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
