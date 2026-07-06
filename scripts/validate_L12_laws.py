#!/usr/bin/env python3
"""validate_L12_laws.py — L12 sunan-laws outputs are well-formed and honest:
events come only from substrate-marked conditional constructions, every law's
support equals its evidence list and is recomputable from the events, tier
rules are applied exactly as specified (صریح needs p<=0.005 AND two-half
presence), verified = candidates minus نامشخص, the global law-likeness test
carries a real positive, and the build is byte-identical on re-run.
Exit 0 = all pass."""

import filecmp
import json
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "generated" / "layers" / "L12_laws"
BUILD = REPO / "scripts" / "build_L12_laws.py"
CONTENT = ["events.json", "law_candidates.json", "laws_verified.json",
           "validation.json"]

results = []


def chk(name, ok, detail=""):
    results.append(bool(ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def main():
    if not all((OUT / f).exists() for f in CONTENT):
        print("L12 outputs missing — run build_L12_laws.py first.")
        return 1
    events = json.loads((OUT / "events.json").read_text(encoding="utf-8"))["events"]
    cand = json.loads((OUT / "law_candidates.json").read_text(encoding="utf-8"))["laws"]
    ver = json.loads((OUT / "laws_verified.json").read_text(encoding="utf-8"))["laws"]
    val = json.loads((OUT / "validation.json").read_text(encoding="utf-8"))

    print("Validating L12 — Sunan laws (conditional events)\n")

    chk("events: count matches validation.json",
        len(events) == val["n_events"], f'{len(events)}')
    chk("events: no empty protasis/apodosis",
        all(e["protasis_roots"] and e["apodosis_roots"] for e in events))
    chk("events: rslt strictly after marker",
        all(e["rslt_pos"] > e["marker_pos"] for e in events))

    # recompute pair supports from events
    c = Counter()
    for e in events:
        for a in set(e["protasis_roots"]):
            for b in set(e["apodosis_roots"]):
                c[(a, b)] += 1
    chk("candidates: exactly the pairs with support>=min_support",
        sorted((l["antecedent"], l["consequent"]) for l in cand)
        == sorted(pr for pr, n in c.items() if n >= val["min_support"]))
    chk("candidates: support recomputable from events",
        all(c[(l["antecedent"], l["consequent"])] == l["support"] for l in cand))
    chk("candidates: evidence length == support",
        all(len(l["evidence"]) == l["support"] for l in cand))
    chk("candidates: reverse_support recomputable",
        all(c.get((l["consequent"], l["antecedent"]), 0) == l["reverse_support"]
            for l in cand))
    chk("candidates: halves sum to support",
        all(l["half1_support"] + l["half2_support"] == l["support"] for l in cand))
    chk("candidates: p and q in (0,1]",
        all(0 < l["p"] <= 1 and 0 < l["q"] <= 1 for l in cand))

    def expected_tier(l):
        if l["p"] <= 0.005 and l["two_half_stable"]:
            return "صریح"
        if l["p"] <= 0.01:
            return "قوی"
        if l["p"] <= 0.05:
            return "محتمل"
        return "نامشخص"

    chk("tier rules applied exactly",
        all(l["tier"] == expected_tier(l) for l in cand))
    chk("two_half_stable == (>=2 in each half)",
        all(l["two_half_stable"] == (l["half1_support"] >= 2 and
                                     l["half2_support"] >= 2) for l in cand))
    chk("verified == candidates minus نامشخص",
        [(-l["support"], l["antecedent"], l["consequent"]) for l in ver]
        == [(-l["support"], l["antecedent"], l["consequent"])
            for l in cand if l["tier"] != "نامشخص"])

    g = val["global_test"]
    chk("global: law-likeness beats null (p<=0.01)",
        g["p_n_pairs"] <= 0.01,
        f'{g["observed_n_pairs_at_support"]} pairs vs null mean '
        f'{g["null_n_pairs_mean"]}, p={g["p_n_pairs"]}')
    chk("global: honest negative recorded for raw max-support",
        g["p_max_support"] > 0.05 or g["observed_max_support"] >
        g["null_max_support_max"], f'p={g["p_max_support"]}')

    # byte-identical rebuild
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "L12_laws"
        shutil.copytree(OUT, tmp)
        subprocess.run([sys.executable, str(BUILD)], check=True,
                       capture_output=True)
        same = all(filecmp.cmp(OUT / f, tmp / f, shallow=False) for f in CONTENT)
        chk("byte-identical rebuild", same)

    print(f"\n{sum(results)}/{len(results)} checks passed.")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
