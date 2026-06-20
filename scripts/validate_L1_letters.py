#!/usr/bin/env python3
"""
scripts/validate_L1_letters.py

Validates Layer L1 outputs: well-formed, consistent with the L0 substrate,
honest about abstentions, and reproducible (deterministic byte-identical re-run).
Exit code 0 = all pass, 1 = any failure.
"""

import filecmp
import json
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "generated" / "layers" / "L1_letters"
DB = REPO / "generated" / "monad.db"
BUILD = REPO / "scripts" / "build_L1_letters.py"

CONTENT_FILES = ["letter_inventory.json", "root_morphophonology.json",
                 "muqattaat.json", "self_prediction.json"]

results = []


def chk(name, ok, detail=""):
    results.append(bool(ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def load(n):
    return json.loads((OUT / n).read_text(encoding="utf-8"))


def main():
    if not all((OUT / f).exists() for f in CONTENT_FILES):
        print("L1 outputs missing — run build_L1_letters.py first.")
        return 1

    inv = load("letter_inventory.json")
    mor = load("root_morphophonology.json")
    muq = load("muqattaat.json")
    sp = load("self_prediction.json")

    con = sqlite3.connect(DB)
    n_roots = con.execute(
        "SELECT COUNT(*) FROM roots WHERE root_buckwalter IS NOT NULL AND root_buckwalter!=''"
    ).fetchone()[0]
    n_inl_suras = con.execute(
        "SELECT COUNT(DISTINCT surah_number) FROM morphology WHERE tag='INL' OR pos='INL'"
    ).fetchone()[0]
    con.close()

    print("Validating L1 — Letters / Phonology\n")

    chk("alphabet size == 28", inv["alphabet_size"] == 28, str(inv["alphabet_size"]))
    chk("no nonstandard symbols", inv["nonstandard_symbols"] == [],
        str(inv["nonstandard_symbols"]))
    chk("roots count matches substrate", mor["total_roots"] == n_roots,
        f'{mor["total_roots"]} vs {n_roots}')
    chk("length distribution sums to roots",
        sum(mor["length_distribution"].values()) == n_roots)
    chk("OCP R1=R2 ratio == 0 (categorical avoidance)",
        mor["radical_identity_OCP"]["R1=R2"]["ratio_obs_over_exp"] == 0.0)
    chk("OCP R2=R3 preferred (ratio > 1)",
        mor["radical_identity_OCP"]["R2=R3"]["ratio_obs_over_exp"] > 1.0)
    chk("hamzated count ABSTAINS (no false zero)",
        mor["classes"]["hamzated_mahmuz"]["status"] == "UNKNOWN")
    chk("muqattaʿat sura count matches substrate",
        muq["suras_with_muqattaat"] == n_inl_suras,
        f'{muq["suras_with_muqattaat"]} vs {n_inl_suras}')
    chk("self-prediction reports model, baseline, verdict",
        all(k in sp for k in ("model", "baseline", "verdict")))
    chk("self-prediction verdict is an honest value",
        sp["verdict"].startswith(("model_beats_baseline", "equal_to_baseline",
                                  "no_improvement_over_baseline")))

    # Reproducibility: rebuild into a temp dir, require byte-identical outputs.
    with tempfile.TemporaryDirectory() as td:
        proc = subprocess.run([sys.executable, str(BUILD), "--out", td],
                              capture_output=True, text=True)
        rebuilt = (proc.returncode == 0)
        identical = rebuilt and all(
            filecmp.cmp(OUT / f, Path(td) / f, shallow=False) for f in CONTENT_FILES
        )
    chk("deterministic re-run (byte-identical outputs)", identical)

    ok = all(results)
    print(f"\n{'ALL PASS' if ok else 'FAILURES PRESENT'} — {sum(results)}/{len(results)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
