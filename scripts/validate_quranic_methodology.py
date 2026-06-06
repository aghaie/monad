#!/usr/bin/env python3
"""
Monad — Phase Q validator: Quranic Methodology Discovery Engine
===============================================================

Checks structural integrity of the Phase Q outputs and, with --rebuild,
verifies byte-identical reproduction (determinism) by rebuilding into a
temp directory and comparing SHA-256 of every product.
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
    "method_vocabulary.json", "imperatives.json", "evidence_model.json",
    "reasoning_patterns.json", "repetition_patterns.json", "story_functions.json",
    "nature_functions.json", "self_descriptions.json", "methodology_model.json",
    "falsification_results.json", "methodology_manifest.json",
]
METHOD = "quranic-methodology-1.0"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(d, name):
    return json.loads((Path(d) / name).read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="generated/quranic_methodology")
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

    print(f"Validating Phase Q outputs in {out}/ …")

    # 1. all products present
    for name in PRODUCTS:
        chk((out / name).exists(), f"missing product {name}")

    # 2. method tag consistency
    for name in PRODUCTS:
        if not (out / name).exists():
            continue
        obj = load(out, name)
        chk(obj.get("method") == METHOD, f"{name}: method tag")

    # 3. method vocabulary structure
    voc = load(out, "method_vocabulary.json")
    chk(set(voc["groups"].keys()) >= {"cognition_reason", "observation_perception",
                                      "evidence_signs", "nature", "story"},
        "method_vocabulary: groups present")
    chk(voc["total_method_tokens"] > 0, "method_vocabulary: token count positive")
    for g, entries in voc["groups"].items():
        for e in entries:
            chk(e["token_count"] >= 0, f"voc {g}/{e['root_arabic']}: token_count")
            chk(e["meccan_ayahs"] + e["medinan_ayahs"] <= e["ayah_count"] + 0,
                f"voc {g}/{e['root_arabic']}: mecc+med <= ayah_count")

    # 4. imperatives
    imp = load(out, "imperatives.json")
    chk(imp["method_imperative_tokens"] > 0, "imperatives: method imperatives positive")
    chk(imp["method_imperative_tokens"] <= imp["total_imperative_tokens_corpus"],
        "imperatives: method <= corpus total")

    # 5. evidence model
    evid = load(out, "evidence_model.json")
    chk(evid["n_sign_ayahs"] > 0, "evidence: sign ayahs positive")
    chk(len(evid["ranked_evidence_types"]) == len(evid["evidence_categories"]),
        "evidence: ranked covers all categories")
    for cat, v in evid["evidence_categories"].items():
        chk(v["sign_ayahs_also_containing"] <= evid["n_sign_ayahs"],
            f"evidence {cat}: shared <= sign ayahs")

    # 6. nature
    nat = load(out, "nature_functions.json")
    chk(0.0 <= nat["fraction"] <= 1.0, "nature: fraction in [0,1]")
    chk(nat["nature_ayahs_with_signs_or_cognition"] <= nat["n_nature_ayahs"],
        "nature: methodological <= total")

    # 7. self descriptions
    selfd = load(out, "self_descriptions.json")
    chk(selfd["n_self_reference_ayahs"] > 0, "self: self-reference ayahs positive")
    chk(len(selfd["ranked_descriptors"]) == len(selfd["descriptors"]),
        "self: ranked covers all descriptors")

    # 8. falsification: H1–H5 falsified, H6 survives
    fal = load(out, "falsification_results.json")
    ids = {h["id"]: h["result"] for h in fal["hypotheses"]}
    for hid in ["H1", "H2", "H3", "H4", "H5"]:
        chk(ids.get(hid) == "FALSIFIED", f"falsification {hid} falsified")
    chk(ids.get("H6") == "SURVIVES", "falsification H6 survives")
    chk(fal["surviving_hypotheses"] == ["H6"], "falsification: only H6 survives")

    # 9. manifest input hash
    man = load(out, "methodology_manifest.json")
    chk("monad.db" in man["input_sha256"], "manifest: db hash present")
    chk(man["input_sha256"]["monad.db"] == sha(args.db), "manifest: db hash matches")
    chk(len(man["prohibitions_observed"]) >= 10, "manifest: prohibitions listed")

    # 10. determinism — byte-identical rebuild
    if args.rebuild:
        print("  --rebuild: regenerating into temp dir for byte-identical check …")
        tmp = Path(tempfile.mkdtemp(prefix="monad_q_"))
        try:
            res = subprocess.run(
                [sys.executable, "scripts/build_quranic_methodology.py",
                 "--db", args.db, "--out", str(tmp)],
                capture_output=True, text=True)
            chk(res.returncode == 0, f"rebuild exit code 0 ({res.stderr[-200:]})")
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
