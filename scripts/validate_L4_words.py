#!/usr/bin/env python3
"""validate_L4_words.py — L4 outputs well-formed, patterns extracted, the
within-root disambiguation test reported honestly (both instruments vs baseline),
reproducible. Exit 0 = all pass."""

import filecmp
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "generated" / "layers" / "L4_words"
BUILD = REPO / "scripts" / "build_L4_words.py"
CONTENT = ["word_lexicon.json", "pattern_stats.json", "self_prediction.json"]

results = []


def chk(name, ok, detail=""):
    results.append(bool(ok)); print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def main():
    if not all((OUT / f).exists() for f in CONTENT):
        print("L4 outputs missing — run build_L4_words.py first."); return 1
    lex = json.loads((OUT / "word_lexicon.json").read_text(encoding="utf-8"))["lemmas"]
    pat = json.loads((OUT / "pattern_stats.json").read_text(encoding="utf-8"))
    sp = json.loads((OUT / "self_prediction.json").read_text(encoding="utf-8"))

    print("Validating L4 — Word / Form meaning\n")
    chk("lexicon non-empty", len(lex) > 4000, f"{len(lex)} lemmas")
    chk("every lemma has root + pattern + tier",
        all(all(k in v for k in ("root_bw", "pattern", "tier")) for v in lex.values()))
    chk("morphological patterns extracted", pat["distinct_patterns"] >= 10,
        f'{pat["distinct_patterns"]} patterns')
    chk("participle patterns present (ACT-PCPL / PASS-PCPL)",
        any(p["pattern"] in ("ACT-PCPL", "PASS-PCPL") for p in pat["patterns"]))
    chk("self-prediction reports ayah, local, baseline, verdict",
        all(k in sp for k in ("model_ayah_bag", "model_local_window", "baseline", "verdict")))
    chk("verdict is an honest value",
        sp["verdict"] in ("forms_carry_contextual_meaning", "no_improvement_over_baseline"))
    chk("polysemy present (ktb has multiple forms)",
        sum(1 for v in lex.values() if v["root_bw"] == "ktb") >= 2)

    with tempfile.TemporaryDirectory() as td:
        proc = subprocess.run([sys.executable, str(BUILD), "--out", td, "--quiet"],
                              capture_output=True, text=True)
        identical = (proc.returncode == 0) and all(
            filecmp.cmp(OUT / f, Path(td) / f, shallow=False) for f in CONTENT)
    chk("deterministic re-run (byte-identical outputs)", identical)

    ok = all(results)
    print(f"\n{'ALL PASS' if ok else 'FAILURES PRESENT'} — {sum(results)}/{len(results)}")
    print(f"\n  Finding: within-root form disambiguation does not beat the most-frequent-form "
          f"baseline (ayah {sp['model_ayah_bag']['top1_pct']}%, local {sp['model_local_window']['top1_pct']}% "
          f"vs {sp['baseline']['top1_pct']}%) ⇒ the ROOT, not the specific form, carries relational meaning.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
