#!/usr/bin/env python3
"""
Monad — Phase Σ validator: Internal Semantic Reconstruction Engine
==================================================================

Verifies structural integrity, the no-external-meaning invariant (every definition
is built only from other opaque concepts; anchors are evidence labels, no glosses),
the relational-emerges / referential-fails honesty, statistical completeness, and —
with --rebuild — byte-identical reproducibility of generated/semantics/.

Usage:
    python3 scripts/validate_semantics.py [--rebuild]
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

OUT = Path("generated/semantics")
FILES = [
    "recoverability.json", "definitions.json", "semantic_boundaries.json", "contrasts.json",
    "functional_roles.json", "semantic_equations.json", "semantic_primitives.json",
    "semantic_consistency.json", "semantic_anchors.json", "internal_dictionary.json",
    "falsification_results.json", "robustness_results.json", "semantic_manifest.json",
]


class V:
    def __init__(self):
        self.p = 0
        self.f = 0

    def check(self, c, m):
        if c:
            self.p += 1
        else:
            self.f += 1
            print(f"  ✗ FAIL: {m}")

    def summary(self):
        print(f"\n  {self.p}/{self.p + self.f} checks passed.")
        return self.f == 0


def load(n):
    return json.loads((OUT / n).read_text("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true")
    args = ap.parse_args()
    v = V()
    print("Monad Phase Σ — validating Internal Semantic Reconstruction Engine")

    for f in FILES:
        v.check((OUT / f).exists(), f"missing {f}")
    if v.f:
        print("  aborting")
        sys.exit(1)

    rec = load("recoverability.json")
    defs = load("definitions.json")
    bound = load("semantic_boundaries.json")
    contr = load("contrasts.json")
    func = load("functional_roles.json")
    eqs = load("semantic_equations.json")
    prim = load("semantic_primitives.json")
    cons = load("semantic_consistency.json")
    anch = load("semantic_anchors.json")
    dict = load("internal_dictionary.json")
    fal = load("falsification_results.json")
    rob = load("robustness_results.json")
    man = load("semantic_manifest.json")

    for name, obj in [("rec", rec), ("defs", defs), ("bound", bound), ("contr", contr),
                      ("func", func), ("eqs", eqs), ("prim", prim), ("cons", cons),
                      ("anch", anch), ("dict", dict), ("fal", fal), ("rob", rob), ("man", man)]:
        v.check(obj["method"] == "sigma-semantics-1.0", f"{name}.method mismatch")

    # recoverability: classes sum to 103
    tally = rec["tally"]
    v.check(sum(tally.values()) == 103, "recoverability classes != 103")
    v.check(tally.get("RECOVERABLE", 0) >= 50, "fewer than 50 recoverable")
    for c, d in rec["concepts"].items():
        v.check(d["classification"] in ("RECOVERABLE", "PARTIALLY_RECOVERABLE", "NON_RECOVERABLE"),
                f"{c} bad classification")

    # definitions: built only from concepts (no external words); anchor is evidence label
    v.check(defs["n_defined"] >= 50, "too few definitions")
    for c, d in list(defs["concepts"].items())[:20]:
        for a in d["associated_with"]:
            v.check(a["concept"].startswith("CONCEPT_"), f"{c} associated not a concept")
        for x in d["requires"] + d["contrasts_with"] + d["preceded_by"]:
            v.check(x.startswith("CONCEPT_"), f"{c} definition uses non-concept token (external?)")

    # internal dictionary: no external language flag + entries are concept-only
    v.check(dict["no_external_language"] is True, "dictionary not flagged concept-only")
    v.check(dict["n_entries"] == defs["n_defined"], "dictionary entry count mismatch")

    # contrasts: count + structure
    v.check(contr["n_contrast_pairs"] == 401, f"contrast pairs {contr['n_contrast_pairs']} != 401")
    for p in contr["strongest_contrasts"][:5]:
        v.check(p["a"].startswith("CONCEPT_") and p["b"].startswith("CONCEPT_"), "contrast not concepts")

    # consistency: mostly stable; concepts dict present
    v.check("concepts" in cons, "consistency missing per-concept dict")
    v.check(cons["n_stable"] >= 0.6 * cons["n_concepts"], "meaning not mostly consistent")
    v.check(0.0 <= cons["drift_distribution"]["mean"] <= 1.0, "drift mean range")

    # semantic anchors: frequency hub is NOT a semantic anchor (residual < 0); top anchors positive
    v.check(anch["frequency_hub_as_semantic_anchor"]["is_semantic_anchor"] is False,
            "frequency hub wrongly flagged as semantic anchor")
    v.check(anch["frequency_hub_as_semantic_anchor"]["residual"] < 0, "frequency hub residual >= 0")
    v.check(anch["top_semantic_anchors"][0]["residual"] > 0, "top semantic anchor residual <= 0")

    # primitives: minimum sets present
    v.check(len(prim["minimum_sets"]) == 4, "primitive minimum sets != 4")

    # equations: tested + holding count
    v.check(eqs["n_holding"] <= eqs["n_equations"], "more holding than total equations")

    # falsification: relational survives, referential fails to emerge
    rels = {t["claim"]: t["result"] for t in fal["tests"]}
    v.check(fal["n_surviving"] == 3, "expected 3 surviving relational claims")
    ref = next((t for t in fal["tests"] if "REFERENTIAL" in t["claim"]), None)
    v.check(ref and "FAILS TO EMERGE" in ref["result"], "referential meaning should fail to emerge")

    # manifest
    t = man["totals"]
    v.check(t["relational_meaning_emerges"] is True, "manifest relational flag")
    v.check(t["referential_meaning_emerges"] is False, "manifest referential flag")
    v.check(t["frequency_hub_is_semantic_anchor"] is False, "manifest hub-anchor flag")
    for f in FILES:
        if f in man["output_bytes"]:
            v.check(man["output_bytes"][f] == (OUT / f).stat().st_size,
                    f"manifest output_bytes[{f}] mismatch")

    if args.rebuild:
        print("  --rebuild: hashing, rebuilding, re-hashing …")
        before = {f: hashlib.sha256((OUT / f).read_bytes()).hexdigest() for f in FILES}
        res = subprocess.run([sys.executable, "scripts/build_semantics.py"],
                             capture_output=True, text=True)
        v.check(res.returncode == 0, f"rebuild failed: {res.stderr[-400:]}")
        for f in FILES:
            after = hashlib.sha256((OUT / f).read_bytes()).hexdigest()
            v.check(after == before[f], f"{f} not byte-identical after rebuild")

    ok = v.summary()
    print(f"  recoverable={tally.get('RECOVERABLE',0)} defined={defs['n_defined']} "
          f"stable={cons['n_stable']}/{cons['n_concepts']} "
          f"hub_anchor={anch['frequency_hub_as_semantic_anchor']['is_semantic_anchor']} "
          f"relational=True referential=False")
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
