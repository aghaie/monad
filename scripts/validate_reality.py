#!/usr/bin/env python3
"""
Monad — Phase R validator: Text → Reality Discovery Engine
==========================================================

Structural-integrity checks on the Phase R outputs and, with --rebuild, a
byte-identical reproduction check (determinism) into a temp directory.
"""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PRODUCTS = [
    "reality_targets.json", "observable_claims.json", "reality_patterns.json",
    "candidate_laws.json", "cross_domain_patterns.json", "falsification_results.json",
    "reality_mapping.json", "law_compression.json", "method_consistency.json",
    "reality_manifest.json",
]
METHOD = "reality-discovery-1.0"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(d, name):
    return json.loads((Path(d) / name).read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="generated/reality")
    ap.add_argument("--db", default="generated/monad.db")
    ap.add_argument("--rebuild", action="store_true")
    args = ap.parse_args()
    out = Path(args.out)
    checks, failed = 0, 0

    def chk(cond, msg):
        nonlocal checks, failed
        checks += 1
        if not cond:
            failed += 1
            print(f"  FAIL: {msg}")

    print(f"Validating Phase R outputs in {out}/ …")

    for name in PRODUCTS:
        chk((out / name).exists(), f"missing product {name}")
    for name in PRODUCTS:
        if (out / name).exists():
            chk(load(out, name).get("method") == METHOD, f"{name}: method tag")

    # reality targets — 10 domains
    tg = load(out, "reality_targets.json")
    chk(len(tg["domains"]) == 10, "targets: 10 domains")
    chk(tg["n_sign_ayahs"] > 0, "targets: sign ayahs positive")

    # observable claims — eschatology excluded, fraction in [0,1]
    cl = load(out, "observable_claims.json")
    chk(cl["n_observable_claims"] > 0, "claims: observable positive")
    chk(cl["n_observable_claims"] + cl["n_excluded_eschatological"] == cl["n_domain_ayahs"],
        "claims: observable + eschatological = domain total")
    chk(0.0 <= cl["observable_fraction"] <= 1.0, "claims: fraction in [0,1]")

    # patterns — lift consistent with P(C|A)/base
    pt = load(out, "reality_patterns.json")
    for p in pt["patterns"]:
        chk(p["cooccurrence_ayahs"] <= p["antecedent_ayahs"], f"{p['id']}: cooc <= antecedent")
        chk(p["lift"] >= 0, f"{p['id']}: lift non-negative")

    # candidate laws — criteria honored
    cd = load(out, "candidate_laws.json")
    crit = cd["criteria"]
    pmeta = {p["id"]: p for p in pt["patterns"]}
    crossd = load(out, "cross_domain_patterns.json")
    cmeta = {c["id"]: c for c in crossd["patterns"]}
    for c in cd["candidates"]:
        p = pmeta[c["id"]]
        nd = cmeta[c["id"]]["n_domains"]
        should = (p["lift"] > crit["min_lift"] and nd >= crit["min_domains"]
                  and p["cooccurrence_ayahs"] >= crit["min_cooccurrence"])
        chk((c["status"] == "CANDIDATE_LAW") == should, f"{c['id']}: candidate criteria consistent")

    # falsification — only candidates tested; survives iff support>counter
    fal = load(out, "falsification_results.json")
    cand_ids = {c["id"] for c in cd["candidates"] if c["status"] == "CANDIDATE_LAW"}
    chk({x["id"] for x in fal["results"]} == cand_ids, "falsification: tests exactly the candidates")
    for x in fal["results"]:
        chk((x["result"] == "SURVIVES") == (x["supporting_ayahs"] > x["counter_example_ayahs"]),
            f"{x['id']}: survive rule")
    chk(set(fal["surviving_laws"]).isdisjoint(set(fal["refuted_laws"])),
        "falsification: survivors and refuted disjoint")

    # mapping — only surviving laws
    mp = load(out, "reality_mapping.json")
    chk({m["id"] for m in mp["mapping"]} == set(fal["surviving_laws"]),
        "mapping: covers exactly surviving laws")

    # compression — reduces, grouped correctly
    cp = load(out, "law_compression.json")
    chk(cp["n_surviving_laws"] == len(fal["surviving_laws"]), "compression: surviving count matches")
    chk(cp["n_meta_laws"] <= cp["n_surviving_laws"], "compression: meta <= surviving")
    subsumed = sorted(s for m in cp["meta_laws"] for s in m["subsumes"])
    chk(subsumed == sorted(fal["surviving_laws"]), "compression: every survivor subsumed once")

    # method consistency — fraction in [0,1], verdict consistent
    mc = load(out, "method_consistency.json")
    chk(0.0 <= mc["law_domain_overlap_with_phaseQ"] <= 1.0, "consistency: overlap in [0,1]")
    chk((mc["consistency"] == "CONSISTENT") == (mc["law_domain_overlap_with_phaseQ"] >= 0.5),
        "consistency: verdict matches threshold")

    # manifest
    man = load(out, "reality_manifest.json")
    chk(man["input_sha256"]["monad.db"] == sha(args.db), "manifest: db hash matches")
    chk("honest_boundary" in man, "manifest: honest boundary stated")
    chk(len(man["prohibitions_observed"]) >= 10, "manifest: prohibitions listed")

    # determinism — byte-identical rebuild
    if args.rebuild:
        print("  --rebuild: regenerating into temp dir for byte-identical check …")
        tmp = Path(tempfile.mkdtemp(prefix="monad_r_"))
        try:
            res = subprocess.run(
                [sys.executable, "scripts/build_reality.py", "--db", args.db, "--out", str(tmp)],
                capture_output=True, text=True)
            chk(res.returncode == 0, f"rebuild exit 0 ({res.stderr[-200:]})")
            for name in PRODUCTS:
                a, b = out / name, tmp / name
                if a.exists() and b.exists():
                    chk(sha(a) == sha(b), f"rebuild byte-identical: {name}")
                else:
                    chk(False, f"rebuild missing: {name}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n  {checks - failed}/{checks} checks pass" + (" — FAILURES" if failed else " — all pass"))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
