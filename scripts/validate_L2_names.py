#!/usr/bin/env python3
"""
scripts/validate_L2_names.py

Validates Layer L2 (divine names / anchors): well-formed, internally sourced,
honest tiers, the thesis self-prediction beats baseline and random, and the
build is reproducible (byte-identical re-run). Exit 0 = all pass.
"""

import filecmp
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "generated" / "layers" / "L2_names"
BUILD = REPO / "scripts" / "build_L2_names.py"
CONTENT = ["discovered_names.json", "name_signatures.json", "self_prediction.json"]

# A small, unambiguous core that any correct internal discovery MUST place in قوی.
CORE = {"gafuwr", "Ealiym", "r~aHiym", "Hakiym", "samiyE", "baSiyr", "qadiyr"}

results = []


def chk(name, ok, detail=""):
    results.append(bool(ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def load(n):
    return json.loads((OUT / n).read_text(encoding="utf-8"))


def main():
    if not all((OUT / f).exists() for f in CONTENT):
        print("L2 outputs missing — run build_L2_names.py first.")
        return 1

    disc = load("discovered_names.json")
    sig = load("name_signatures.json")
    sp = load("self_prediction.json")

    print("Validating L2 — Divine Names / Anchors\n")

    qawi = {d["lemma_bw"] for d in disc["names_ranked"] if d["tier"].startswith("قوی")}
    chk("candidate pool non-empty", disc["pool_size"] > 0, str(disc["pool_size"]))
    chk("قوی names discovered", len(qawi) >= 10, f"{len(qawi)} names")
    chk("unambiguous core all in قوی", CORE.issubset(qawi),
        f"missing: {sorted(CORE - qawi)}")
    chk("every قوی name has an anchor signature",
        all(d["lemma_bw"] in sig["signatures"] for d in disc["names_ranked"]
            if d["tier"].startswith("قوی")))
    chk("signatures carry top_roots (anchor axes)",
        all(s["top_roots"] for s in sig["signatures"].values()))
    chk("traditional name list NOT used (quarantine honored)",
        "quarantined" in disc["caveat"])

    # The thesis test.
    m1 = sp["model"]["top1_pct"]; m3 = sp["model"]["top3_pct"]
    b1 = sp["baseline"]["top1_pct"]; rf = sp["random_floor_top1_pct"]
    chk("self-prediction reports model/baseline/verdict",
        all(k in sp for k in ("model", "baseline", "verdict")))
    chk("THESIS: model beats random floor", m1 > rf, f"{m1}% vs {rf}%")
    chk("THESIS: model beats baseline (top1)", m1 > b1, f"{m1}% vs {b1}%")
    chk("verdict == model_beats_baseline", sp["verdict"] == "model_beats_baseline",
        sp["verdict"])

    # Reproducibility.
    with tempfile.TemporaryDirectory() as td:
        proc = subprocess.run([sys.executable, str(BUILD), "--out", td, "--quiet"],
                              capture_output=True, text=True)
        identical = (proc.returncode == 0) and all(
            filecmp.cmp(OUT / f, Path(td) / f, shallow=False) for f in CONTENT)
    chk("deterministic re-run (byte-identical outputs)", identical)

    ok = all(results)
    print(f"\n{'ALL PASS' if ok else 'FAILURES PRESENT'} — {sum(results)}/{len(results)}")
    if sp["verdict"] == "model_beats_baseline":
        print(f"\n  THESIS supported: ayah content predicts its sealing name at "
              f"{m1}% top-1 ({m3}% top-3) vs baseline {b1}% / random {rf}%.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
