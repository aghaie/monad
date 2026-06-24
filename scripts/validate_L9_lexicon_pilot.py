#!/usr/bin/env python3
"""
scripts/validate_L9_lexicon_pilot.py

Validate the L9 pilot: (1) determinism — the build reproduces byte-identical
JSON on a second run; (2) the pre-registered invariant — the aggregate
sense-replication signal is significant (p < 0.05) and the fold factor > 1.

Exit non-zero on any failure.
"""

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BUILD = REPO / "scripts" / "build_L9_lexicon_pilot.py"
OUT = REPO / "generated" / "layers" / "L9_lexicon"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    fails = []

    # ── 1. determinism: rebuild into a temp dir, compare hashes ──
    with tempfile.TemporaryDirectory() as td:
        subprocess.run([sys.executable, str(BUILD), "--out", td, "--quiet"],
                       check=True, cwd=str(REPO))
        for name in ("pilot_dossiers.json", "pilot_stability.json"):
            a, b = OUT / name, Path(td) / name
            if not a.exists():
                fails.append(f"missing committed output {name}")
            elif sha(a) != sha(b):
                fails.append(f"NON-DETERMINISTIC: {name} differs on rebuild")
            else:
                print(f"  ✓ deterministic: {name}")

    # ── 2. pre-registered invariant ──
    s = json.loads((OUT / "pilot_stability.json").read_text(encoding="utf-8"))
    p = s["aggregate_p"]; fold = s["fold_factor"]
    if p < 0.05:
        print(f"  ✓ aggregate replication significant: p={p}")
    else:
        fails.append(f"aggregate p not significant: p={p}")
    if fold and fold > 1.0:
        print(f"  ✓ fold factor > 1: {fold}x")
    else:
        fails.append(f"fold factor not > 1: {fold}")

    # ── 3. honesty guard: every sense must carry a confidence tier ──
    d = json.loads((OUT / "pilot_dossiers.json").read_text(encoding="utf-8"))["dossiers"]
    TIERS = {"صریح", "قوی", "محتمل", "نامشخص"}
    bad = [bw for bw, o in d.items()
           for sense in o["senses"] if sense["confidence"] not in TIERS]
    if bad:
        fails.append(f"senses missing valid confidence tier: {bad[:5]}")
    else:
        print("  ✓ every sense carries a confidence tier")

    print()
    if fails:
        print("VALIDATION FAILED:")
        for f in fails:
            print("   ✗", f)
        sys.exit(1)
    print("L9 pilot validation PASSED "
          f"(p={p}, ~{fold}x; senses tiered; reproducible).")


if __name__ == "__main__":
    main()
