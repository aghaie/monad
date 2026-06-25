#!/usr/bin/env python3
"""validate_L11b_controls.py — the control-corpus comparison is well-formed,
reproduces byte-identically, and the honest orderings hold: classical poetry is
MORE rhyme-cohesive than the Quran, Bible prose is near chance, and the Quran is
the most length-free. The scorecard must keep 'superhuman' out of scope."""

import filecmp
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "generated" / "layers" / "L11_style"
BUILD = REPO / "scripts" / "build_L11b_controls.py"
F = "control_comparison.json"

results = []


def chk(name, ok, detail=""):
    results.append(bool(ok)); print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def main():
    if not (OUT / F).exists():
        print("L11b output missing — run build_L11b_controls.py first."); return 1
    r = json.loads((OUT / F).read_text(encoding="utf-8"))
    c = r["corpora"]
    qr = c["quran"]["rhyme"]["rhyme_cohesion"]
    pr = c["poetry_classical"]["rhyme"]["rhyme_cohesion"]
    br = c["bible_arabic"]["rhyme"]["rhyme_cohesion"]

    print("Validating L11b — control-corpus comparison\n")
    chk("all three corpora present & non-trivial",
        all(c[k]["verse_units"] > 1000 for k in ("quran", "poetry_classical", "bible_arabic")))
    chk("poetry is MORE rhyme-cohesive than the Quran (humans rhyme stricter)",
        pr > qr, f"poetry {pr} > quran {qr}")
    chk("Bible prose rhyme is near chance (well below Quran)",
        br < qr and c["bible_arabic"]["rhyme"]["fold_over_chance"] < 1.3, f"bible {br}")
    chk("Quran is the most length-free (highest CV)",
        c["quran"]["length_freedom_cv"] > c["poetry_classical"]["length_freedom_cv"],
        f'quran {c["quran"]["length_freedom_cv"]} vs poetry {c["poetry_classical"]["length_freedom_cv"]}')
    chk("poetry is metrically rigid (low length CV)",
        c["poetry_classical"]["length_freedom_cv"] < 0.15)
    chk("each rhyme test beats its own null (p<=0.01)",
        all(c[k]["rhyme"]["p"] <= 0.01 for k in c))
    chk("Quran does NOT exceed ALL controls by 2 SD on rhyme (honest negative vs prompt's bar)",
        r["quran_placement"]["sd_below_poetry"] < 2.0,
        f'only {r["quran_placement"]["sd_below_poetry"]} SD below poetry')
    chk("scorecard keeps 'superhuman' out of scope (UNKNOWN)",
        "UNKNOWN" in r["note"] or "UNKNOWN" in r["quran_placement"]["verdict"])

    with tempfile.TemporaryDirectory() as td:
        proc = subprocess.run([sys.executable, str(BUILD), "--out", td, "--quiet"],
                              capture_output=True, text=True)
        identical = (proc.returncode == 0) and filecmp.cmp(OUT / F, Path(td) / F, shallow=False)
    chk("deterministic re-run (byte-identical)", identical, "" if identical else proc.stderr[-300:])

    ok = all(results)
    print(f"\n{'ALL PASS' if ok else 'FAILURES PRESENT'} — {sum(results)}/{len(results)}")
    if ok:
        print(f"\n  Rhyme: poetry {pr} > Quran {qr} > Bible {br}. Quran is rhymed prose (saj'): "
              f"more rhyme than prose, more length-freedom than poetry. Humans rhyme stricter — "
              f"rhyme is no proof of superhuman origin (that stays UNKNOWN).")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
