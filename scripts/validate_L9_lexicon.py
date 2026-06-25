#!/usr/bin/env python3
"""
scripts/validate_L9_lexicon.py

Validate the FULL L9 lexicon:
  1. determinism — byte-identical rebuild of all three JSON outputs;
  2. coverage — every content root has a dossier with a stable neighbourhood
     and a confidence tier; every one of the 6,236 ayahs has a dossier;
  3. honesty — every emitted sense lives under a non-نامشخص tier, and roots
     tiered نامشخص emit zero senses (no unsupported sense claims).

Exit non-zero on any failure.
"""

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BUILD = REPO / "scripts" / "build_L9_lexicon.py"
GLOSS = REPO / "scripts" / "build_L9_glosses.py"
OUT = REPO / "generated" / "layers" / "L9_lexicon"
TIERS = {"صریح", "قوی", "محتمل", "نامشخص"}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    fails = []
    names = ("root_dossiers.json", "ayah_dossiers.json", "lexicon_summary.json")

    with tempfile.TemporaryDirectory() as td:
        subprocess.run([sys.executable, str(BUILD), "--out", td, "--quiet"],
                       check=True, cwd=str(REPO))
        for name in names:
            a, b = OUT / name, Path(td) / name
            if not a.exists():
                fails.append(f"missing committed output {name}")
            elif sha(a) != sha(b):
                fails.append(f"NON-DETERMINISTIC: {name} differs on rebuild")
            else:
                print(f"  ✓ deterministic: {name}")

    roots = json.loads((OUT / "root_dossiers.json").read_text(encoding="utf-8"))["dossiers"]
    ayahs = json.loads((OUT / "ayah_dossiers.json").read_text(encoding="utf-8"))["index"]
    summ = json.loads((OUT / "lexicon_summary.json").read_text(encoding="utf-8"))

    if len(ayahs) == 6236:
        print(f"  ✓ every ayah has a dossier: {len(ayahs)}")
    else:
        fails.append(f"ayah coverage {len(ayahs)} != 6236")

    no_nb = [bw for bw, o in roots.items() if not o["neighbourhood"] and o["n_ayahs"] >= 3]
    if no_nb:
        fails.append(f"{len(no_nb)} well-attested roots have empty neighbourhood, e.g. {no_nb[:5]}")
    else:
        print(f"  ✓ every well-attested root has a stable neighbourhood ({len(roots)} roots)")

    bad_tier = [bw for bw, o in roots.items() if o["confidence"] not in TIERS]
    if bad_tier:
        fails.append(f"invalid confidence tier: {bad_tier[:5]}")
    else:
        print("  ✓ every root carries a valid confidence tier")

    # honesty: نامشخص roots must emit NO senses; resolved roots' senses tiered
    leak = [bw for bw, o in roots.items() if o["confidence"] == "نامشخص" and o["senses"]]
    if leak:
        fails.append(f"نامشخص roots emitting senses (unsupported claims): {leak[:5]}")
    else:
        print("  ✓ no sense claims under نامشخص (abstention honoured)")

    # ── gloss layer: deterministic, covers every kept facet ──
    with tempfile.TemporaryDirectory() as td:
        for name in ("root_dossiers.json", "ayah_dossiers.json", "lexicon_summary.json"):
            (Path(td) / name).write_bytes((OUT / name).read_bytes())
        subprocess.run([sys.executable, str(GLOSS), "--out", td, "--quiet"],
                       check=True, cwd=str(REPO))
        if (OUT / "glosses.json").exists() and sha(OUT / "glosses.json") == sha(Path(td) / "glosses.json"):
            print("  ✓ deterministic: glosses.json")
        else:
            fails.append("glosses.json missing or non-deterministic")
    gl = json.loads((OUT / "glosses.json").read_text(encoding="utf-8"))
    total_senses = sum(len(o["senses"]) for o in roots.values())
    if gl["n_facets"] == total_senses and gl["n_unresolved"] == 0:
        print(f"  ✓ every kept facet glossed: {gl['n_glossed']}/{gl['n_facets']} "
              f"({gl['n_sense']} معنا, {gl['n_frame']} بافت)")
    else:
        fails.append(f"gloss coverage gap: {gl['n_glossed']}/{gl['n_facets']}, "
                     f"unresolved={gl['n_unresolved']}, dossier senses={total_senses}")

    resolved = summ["roots_with_resolved_senses"]
    print(f"\n  tiers: {summ['tier_counts']}")
    print(f"  roots with resolved senses: {resolved}")
    print(f"  ayahs with explaining verses: {summ['ayahs_with_explaining_verses']}")

    print()
    if fails:
        print("VALIDATION FAILED:")
        for f in fails:
            print("   ✗", f)
        sys.exit(1)
    print("L9 full lexicon validation PASSED (reproducible; full coverage; "
          "senses honestly tiered).")


if __name__ == "__main__":
    main()
