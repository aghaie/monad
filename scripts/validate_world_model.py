#!/usr/bin/env python3
"""
Monad — Phase Ω validator: World Model Discovery Engine
=======================================================

Verifies structural integrity, the model-must-emerge-or-fail invariant (the
structural model is reported AND the semantic non-emergence is reported honestly,
not forced), opacity (concepts/anchors are evidence, never glossed), cross-product
consistency, and — with --rebuild — byte-identical reproducibility of
generated/world_model/.

Usage:
    python3 scripts/validate_world_model.py [--rebuild]
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

OUT = Path("generated/world_model")
FILES = [
    "entity_model.json", "state_model.json", "transformation_model.json", "causal_model.json",
    "feedback_model.json", "agency_model.json", "knowledge_model.json", "society_model.json",
    "history_model.json", "world_model.json", "compression_analysis.json",
    "falsification_results.json", "robustness_results.json", "world_model_manifest.json",
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
    print("Monad Phase Ω — validating World Model Discovery Engine")

    for f in FILES:
        v.check((OUT / f).exists(), f"missing {f}")
    if v.f:
        print("  aborting")
        sys.exit(1)

    ent = load("entity_model.json")
    state = load("state_model.json")
    trans = load("transformation_model.json")
    causal = load("causal_model.json")
    fb = load("feedback_model.json")
    agency = load("agency_model.json")
    know = load("knowledge_model.json")
    soc = load("society_model.json")
    hist = load("history_model.json")
    wm = load("world_model.json")
    comp = load("compression_analysis.json")
    fal = load("falsification_results.json")
    rob = load("robustness_results.json")
    man = load("world_model_manifest.json")

    for name, obj in [("ent", ent), ("state", state), ("trans", trans), ("causal", causal),
                      ("fb", fb), ("agency", agency), ("know", know), ("soc", soc), ("hist", hist),
                      ("wm", wm), ("comp", comp), ("fal", fal), ("rob", rob), ("man", man)]:
        v.check(obj["method"] == "omega-world-model-1.0", f"{name}.method mismatch")

    # entity / transformation / state classification
    v.check(ent["n_entities"] == 83, f"entity count {ent['n_entities']} != 83")
    v.check(trans["n_transformations"] == 20, f"transformation count != 20")
    v.check(state["n_grammatical_states"] == 0, "state class should be 0 (does not emerge)")
    v.check(ent["n_entities"] + trans["n_transformations"] + state["n_grammatical_states"] == 103,
            "role classes do not sum to 103")
    # opacity: entities listed with anchors but concept ids opaque
    for e in ent["recurring_entities"]:
        v.check(e["concept_id"].startswith("CONCEPT_"), "entity not an opaque concept id")

    # transition graph
    v.check(trans["n_transition_edges"] == 720, f"transition edges {trans['n_transition_edges']} != 720")
    v.check(causal["caveat"].startswith("these are consistent"), "causal caveat missing")

    # feedback
    v.check(fb["largest_transition_scc"] >= 2, "no feedback core")

    # world model: structural emerges, semantic does not
    v.check(wm["semantic_world_model"]["emerges"] is False,
            "semantic world model wrongly claimed to emerge")
    v.check("structural_world_model" in wm and wm["structural_world_model"]["components"],
            "structural world model missing")

    # knowledge / society / history honestly fail to emerge
    for m, name in [(know, "knowledge"), (soc, "society"), (hist, "history")]:
        v.check("FAILS TO EMERGE" in m["emergence"], f"{name} should report non-emergence")

    # falsification: 4 structural survive, semantic components fail
    v.check(fal["n_structural_components_survive"] == 4, "expected 4 surviving structural components")
    v.check(fal["n_semantic_components_fail"] >= 4, "expected >=4 semantic non-emergences")
    survives = [t for t in fal["tests"] if t["result"].startswith("SURVIVES")]
    v.check(len(survives) == 4, "survivor count mismatch")
    targets_fail = {t["target"] for t in fal["tests"] if "EMERGE" in t["result"]}
    for need in ("knowledge model", "society model", "history model", "semantic world model"):
        v.check(need in targets_fail, f"{need} not reported as failing to emerge")

    # robustness: entity ~83, state stably 0
    v.check(abs(rob["entity_count"]["mean"] - 83) < 3, "entity count not bootstrap-stable")
    v.check(rob["state_count_stable_zero"] is True, "state count not stably zero")

    # manifest
    t = man["totals"]
    v.check(t["structural_world_model_emerges"] is True, "manifest structural flag")
    v.check(t["semantic_world_model_emerges"] is False, "manifest semantic flag")
    for f in FILES:
        if f in man["output_bytes"]:
            v.check(man["output_bytes"][f] == (OUT / f).stat().st_size,
                    f"manifest output_bytes[{f}] mismatch")

    if args.rebuild:
        print("  --rebuild: hashing, rebuilding, re-hashing …")
        before = {f: hashlib.sha256((OUT / f).read_bytes()).hexdigest() for f in FILES}
        res = subprocess.run([sys.executable, "scripts/build_world_model.py"],
                             capture_output=True, text=True)
        v.check(res.returncode == 0, f"rebuild failed: {res.stderr[-400:]}")
        for f in FILES:
            after = hashlib.sha256((OUT / f).read_bytes()).hexdigest()
            v.check(after == before[f], f"{f} not byte-identical after rebuild")

    ok = v.summary()
    print(f"  entities={ent['n_entities']} transformations={trans['n_transformations']} states=0 "
          f"structural_emerges=True semantic_emerges={wm['semantic_world_model']['emerges']}")
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
