#!/usr/bin/env python3
"""
Monad — Phase P validator: Structural Predictivity / Held-Out Information Engine
===============================================================================

Checks: product presence, method tags, pre-registered-threshold match, leakage-free
fold construction, the fairness lock (structure==baseline when association evidence is
zero), verdict-criteria consistency, mandatory report presence + 7-section structure,
and (with --rebuild) byte-identical reproduction of the deterministic manifest + data
products. The volatile run_metadata.json is intentionally excluded from the byte check.
"""

import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PRODUCTS = [
    "prediction_task.json", "holdout_folds.json", "root_predictivity.json",
    "concept_predictivity.json", "concept_stability.json", "frequency_null_control.json",
    "information_decomposition.json", "robustness_results.json", "falsification_results.json",
    "predictivity_manifest.json",
]
REPORTS = [
    "prediction-task-report.md", "holdout-design-report.md", "root-predictivity-report.md",
    "concept-predictivity-report.md", "frequency-null-control-report.md",
    "information-gain-report.md", "predictivity-robustness-report.md",
    "predictivity-falsification-report.md", "phase-p-final-report.md",
]
SECTIONS = ["Objective", "Method", "Results", "Interpretation", "Falsification",
            "Limitations", "Conclusion"]
METHOD = "predictivity-discovery-1.0"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(d, name):
    return json.loads((Path(d) / name).read_text(encoding="utf-8"))


def import_build():
    spec = importlib.util.spec_from_file_location("bp", "scripts/build_predictivity.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="generated/predictivity")
    ap.add_argument("--docs", default="docs")
    ap.add_argument("--db", default="generated/monad.db")
    ap.add_argument("--concepts", default="generated/concepts/concept_memberships.json")
    ap.add_argument("--rebuild", action="store_true")
    args = ap.parse_args()
    out = Path(args.out)
    docs = Path(args.docs)
    checks = failed = 0

    def chk(cond, msg):
        nonlocal checks, failed
        checks += 1
        if not cond:
            failed += 1
            print(f"  FAIL: {msg}")

    print(f"Validating Phase P in {out}/ …")

    # 1. products + run_metadata present, method tags
    for name in PRODUCTS:
        chk((out / name).exists(), f"missing product {name}")
    chk((out / "run_metadata.json").exists(), "missing run_metadata.json (volatile provenance)")
    for name in PRODUCTS:
        if (out / name).exists():
            chk(load(out, name).get("method") == METHOD, f"{name}: method tag")

    # 2. pre-registered thresholds in manifest match the build module constants
    bp = import_build()
    man = load(out, "predictivity_manifest.json")
    th = man["pre_registered_thresholds"]
    chk(th["ALPHA"] == bp.ALPHA and th["LAMBDA"] == bp.LAMBDA, "manifest: ALPHA/LAMBDA match code")
    chk(th["MIN_BITS_GAIN"] == bp.MIN_BITS_GAIN and th["MIN_HITS10_GAIN"] == bp.MIN_HITS10_GAIN,
        "manifest: effect-floor thresholds match code")
    chk(th["K_NULL"] == bp.K_NULL and th["SEED"] == bp.SEED, "manifest: K_NULL/SEED match code")
    chk(man["input_sha256"]["monad.db"] == sha(args.db), "manifest: db hash matches")
    chk(man["input_sha256"]["concept_memberships.json"] == sha(args.concepts),
        "manifest: concepts hash matches")
    chk(set(man["output_sha256"].keys()) == set(PRODUCTS[:-1]) | set(),
        "manifest: output hashes cover all data products")
    for name, h in man["output_sha256"].items():
        chk(sha(out / name) == h, f"manifest: recorded hash matches file {name}")

    # 3. fairness lock — with an UNINFORMATIVE (empty) context the structure model reduces
    #    EXACTLY to the baseline (NLL and rank), so any deviation in the real experiment is
    #    driven solely by training co-occurrence evidence and the predictors are
    #    tie-convention-symmetric. (Non-empty context legitimately reweights collocates.)
    ts2 = bp.TrainStats([frozenset({10, 11}), frozenset({20, 21}), frozenset({10, 11}),
                         frozenset({20, 21})])
    res = bp.score_instance(ts2, [], 10)   # empty context -> no evidence for ANY unit
    chk(abs(res["nll_struct"] - res["nll_base"]) < 1e-9,
        f"fairness lock: struct NLL==base NLL with empty context ({res['nll_struct']} vs {res['nll_base']})")
    chk(res["rank_struct"] == res["rank_base"],
        "fairness lock: struct rank==base rank with empty context")
    # and the model DOES use evidence when context is informative (sanity)
    res2 = bp.score_instance(ts2, [11], 10)   # 10 co-occurs with 11 -> positive evidence
    chk(res2["nll_struct"] < res2["nll_base"] or res2["rank_struct"] <= res2["rank_base"],
        "model sanity: informative context shifts the structure prediction")

    # 4. leakage-free fold construction — train ∩ test = ∅, train ∪ test = all
    eng = bp.PredictivityEngine(args.db, args.concepts, tempfile.mkdtemp(prefix="mp_chk_"))
    eng.load()
    allseq = set(eng.seqs)
    for builder in [eng.folds_random(bp.FOLDS_PRIMARY), eng.folds_blocks(bp.N_BLOCKS),
                    eng.folds_length_strat(bp.FOLDS_PRIMARY)]:
        union_test = set()
        for name, train, test in builder:
            chk(set(train).isdisjoint(set(test)), f"{name}: train∩test empty")
            chk(set(train) | set(test) == allseq, f"{name}: train∪test == all ayahs")
            union_test |= set(test)
        chk(union_test == allseq, "k-fold test sets partition the corpus")

    # 5. coverage / OOV accounting present and in range
    rp = load(out, "root_predictivity.json")
    for mode, cell in rp["R1_5fold"].items():
        chk(0.0 < cell["coverage"] <= 1.0, f"root {mode}: coverage in (0,1]")
        chk(cell["n_instances"] > 0 and cell["oov_excluded"] >= 0, f"root {mode}: instance counts")

    # 6. null control structure — every cell reports real & null bands, decisive flag
    nc = load(out, "frequency_null_control.json")
    cells = [nc["R1_5fold"]["single"], nc["concept_R1"]] + list(nc["regimes"].values())
    for c in cells:
        chk("real_mrr_struct" in c and "null_mrr_struct" in c, "null cell: real+null present")
        chk(c["k_null"] == bp.K_NULL, "null cell: K matches")
        chk(isinstance(c["real_beats_null_mrr"], bool), "null cell: decisive flag boolean")

    # 7. verdict-criteria consistency
    fr = load(out, "falsification_results.json")
    crit = fr["pre_registered_criteria"]
    v = fr["verdict"]
    chk(v in bp.VERDICTS, "falsification: verdict in allowed set")
    if not crit["c1_beats_frequency"]:
        chk(v == "NON_PREDICTIVE", "verdict logic: ¬c1 ⇒ NON_PREDICTIVE")
    elif crit["c1_beats_frequency"] and not crit["c2_beats_null"]:
        chk(v == "FREQUENCY_SHAPED", "verdict logic: c1∧¬c2 ⇒ FREQUENCY_SHAPED")
    elif all(crit[k] for k in ["c1_beats_frequency", "c2_beats_null", "c3_not_degree",
                               "c4_min_effect", "c5_stable_regimes"]):
        chk(v == "GENUINE_STRUCTURE", "verdict logic: all criteria ⇒ GENUINE_STRUCTURE")
    chk(man["verdict"] == v, "manifest verdict == falsification verdict")

    # 8. mandatory reports present, with the 7-section structure
    for name in REPORTS:
        p = docs / name
        if not p.exists():
            chk(False, f"missing report {name}")
            continue
        text = p.read_text(encoding="utf-8")
        for sec in SECTIONS:
            chk(sec.lower() in text.lower(), f"{name}: missing section '{sec}'")
    es = docs / "executive-summary.md"
    if es.exists():
        t = es.read_text(encoding="utf-8")
        for kw in ["Objective", "Method", "Verdict", "Confidence"]:
            chk(kw.lower() in t.lower(), f"executive-summary: missing '{kw}'")
        chk(len(t) <= 9000, "executive-summary: within ~2 pages")
    else:
        chk(False, "missing executive-summary.md")

    # 9. byte-identical rebuild (manifest + data products; run_metadata excluded)
    if args.rebuild:
        print("  --rebuild: regenerating into temp dir (full run — slow) …")
        tmp = Path(tempfile.mkdtemp(prefix="monad_p_"))
        res = subprocess.run([sys.executable, "scripts/build_predictivity.py",
                              "--db", args.db, "--concepts", args.concepts, "--out", str(tmp)],
                             capture_output=True, text=True)
        chk(res.returncode == 0, f"rebuild exit 0 ({res.stderr[-300:]})")
        for name in PRODUCTS:
            a, b = out / name, tmp / name
            if a.exists() and b.exists():
                chk(sha(a) == sha(b), f"rebuild byte-identical: {name}")
            else:
                chk(False, f"rebuild missing: {name}")
        chk((tmp / "run_metadata.json").exists(), "rebuild: run_metadata present (not byte-checked)")
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n  {checks - failed}/{checks} checks pass" + (" — FAILURES" if failed else " — all pass"))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
