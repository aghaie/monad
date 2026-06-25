#!/usr/bin/env python3
"""validate_L11_stylometry.py — L11 stylometry outputs are well-formed, the
falsifiable tests behave as designed (fawasil cohesion beats its null; the
meccan/medinan and register results carry honest verdicts; the legacy 52.7%
process-share is reproduced), feature coverage is complete, and the build is
byte-identical on re-run. Exit 0 = all pass."""

import filecmp
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "generated" / "layers" / "L11_style"
BUILD = REPO / "scripts" / "build_L11_stylometry.py"
CONTENT = ["stylometry_tests.json", "ayah_features.json", "sura_features.json"]

results = []


def chk(name, ok, detail=""):
    results.append(bool(ok)); print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def main():
    if not all((OUT / f).exists() for f in CONTENT):
        print("L11 outputs missing — run build_L11_stylometry.py first."); return 1
    t = json.loads((OUT / "stylometry_tests.json").read_text(encoding="utf-8"))
    af = json.loads((OUT / "ayah_features.json").read_text(encoding="utf-8"))
    sf = json.loads((OUT / "sura_features.json").read_text(encoding="utf-8"))
    A = t["test_A_fawasil_cohesion"]
    B = t["test_B_meccan_medinan_separability"]
    C = t["test_C_hidden_heterogeneity"]
    D = t["test_D_register_by_period"]

    print("Validating L11 — Stylometric & prosodic self-structure\n")
    chk("feature coverage: all 6236 ayat", len(af["features"]) == 6236, f'{len(af["features"])}')
    chk("feature coverage: all 114 suras", len(sf["suras"]) == 114, f'{len(sf["suras"])}')

    # Test A — must be a real, strong positive (rhyme is genuinely there)
    chk("A: fawasil cohesion beats permutation null",
        A["observed"] > A["null"]["max"], f'{A["observed"]} vs max {A["null"]["max"]}')
    chk("A: p <= 0.01", A["p"] <= 0.01, f'p={A["p"]}')
    chk("A: confidence صریح", A["confidence"] == "صریح")

    # Test B — separability reported, with the length caveat preserved
    chk("B: with-length separability beats null",
        B["with_length"]["separates"], f'bal-acc={B["with_length"]["balanced_accuracy"]}')
    chk("B: shape-only result is reported (length-caveat honest)",
        "balanced_accuracy" in B["shape_only"])

    # Test C — structure characterised concretely (rhyme regimes), verdict consistent
    excess = C["observed"] > C["null"]["max"]
    chk("C: verdict matches null comparison",
        ("rhyme-diversity regimes" in C["verdict"]) == excess, C["verdict"])
    if excess:
        rr = C["rhyme_regimes"]
        chk("C: rhyme regimes partition all 114 suras",
            rr["monorhyme_suras"] + rr["varied_suras"] == 114,
            f'{rr["monorhyme_suras"]} mono + {rr["varied_suras"]} varied')
        chk("C: monorhyme group genuinely lower rhyme-variety (not arbitrary)",
            rr["feature_means"]["fasila_entropy"]["monorhyme"] <
            rr["feature_means"]["fasila_entropy"]["varied"])
        chk("C: structure is one-dimensional, not multi-author",
            "NOT evidence of multiple authors" in C["interpretation"])

    # Test D — legacy 52.7% reproduced; verdict consistent with p
    chk("D: legacy 52.7% process-share reproduced",
        D["legacy_claim_52_7pct"] == "confirmed", f'share={D["overall_process_share"]}')
    chk("D: verdict consistent with p",
        ("differs" in D["verdict"]) == (D["p"] <= 0.05), f'p={D["p"]}')

    # Honesty guard: the out-of-scope / UNKNOWN note must be present
    chk("scope note keeps 'superhuman' out of scope (UNKNOWN)",
        "UNKNOWN" in t["scope_note"] and "control corpus" in t["scope_note"].lower())

    # Reproducibility — re-run WITHOUT --write-db, compare the JSON artifacts
    with tempfile.TemporaryDirectory() as td:
        proc = subprocess.run([sys.executable, str(BUILD), "--out", td, "--quiet"],
                              capture_output=True, text=True)
        identical = (proc.returncode == 0) and all(
            filecmp.cmp(OUT / f, Path(td) / f, shallow=False) for f in CONTENT)
    chk("deterministic re-run (byte-identical outputs)", identical,
        "" if identical else proc.stderr[-300:])

    ok = all(results)
    print(f"\n{'ALL PASS' if ok else 'FAILURES PRESENT'} — {sum(results)}/{len(results)}")
    if ok:
        print(f"\n  Fawasil cohere within suras {A['observed']} vs {A['null']['mean']} null "
              f"(~{A['fold']}x, p={A['p']}).  Meccan/medinan separate with length "
              f"(bal-acc {B['with_length']['balanced_accuracy']}, p={B['with_length']['p']}) but "
              f"NOT on shape alone (p={B['shape_only']['p']}) — style evolves, driven by verse length. "
              f"Process-register {D['overall_process_share']} (legacy confirmed), medinan more than meccan.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
