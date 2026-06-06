#!/usr/bin/env python3
"""
scripts/validate_compression.py

Monad Dependency Compression Engine — Validator (Phase 5).

Checks that generated/compression/*.json is internally consistent, faithful to
the Phase-4 proposition structure, and deterministically reproducible. Purely
structural; performs no interpretation.

Usage:
    python3 scripts/validate_compression.py [--rebuild]

Exit code: 0 if all checks pass, 1 otherwise.
"""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROPS_DIR = REPO_ROOT / "generated" / "propositions"
COMP_DIR = REPO_ROOT / "generated" / "compression"

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
INFO = "\033[94mINFO\033[0m"

FILES = [
    "foundationality_scores.json",
    "reconstruction_sets.json",
    "dependency_layers.json",
    "irreducible_structures.json",
    "compression_statistics.json",
    "compression_curve.json",
    "hub_removal_analysis.json",
    "compression_manifest.json",
]


class Validator:

    def __init__(self):
        self.failures = 0
        self.data = {}

    def check(self, label, ok, detail=""):
        if not ok:
            self.failures += 1
        print(f"  [{PASS if ok else FAIL}] {label}" + (f"  ({detail})" if detail else ""))
        return ok

    def info(self, label):
        print(f"  [{INFO}] {label}")

    # ── 1. presence + load ────────────────────────────────────────────────────

    def files(self):
        print("\n[1/7] file presence + load")
        for f in FILES:
            self.check(f"file present: {f}", (COMP_DIR / f).is_file())
        for f in FILES:
            try:
                self.data[f] = json.loads((COMP_DIR / f).read_text("utf-8"))
                self.check(f"loads as JSON: {f}", True)
            except Exception as exc:
                self.check(f"loads as JSON: {f}", False, str(exc))

    # ── 2. faithfulness to Phase-4 relation population ────────────────────────

    def _load_relations(self):
        c = json.loads((PROPS_DIR / "proposition_candidates.json").read_text("utf-8"))
        g = json.loads((PROPS_DIR / "proposition_graph.json").read_text("utf-8"))
        concepts = sorted(n["concept_id"] for n in g["nodes"])
        R = c["relations"]
        rels = []
        for t in ("ASSOCIATES_WITH", "CO_OCCURS"):
            for e in R[t]:
                rels.append(frozenset((e["concept_a"], e["concept_b"])))
        for t in ("DEPENDS_ON", "REQUIRES", "PRECEDES", "FOLLOWS", "PREDICTS"):
            for e in R[t]:
                rels.append(frozenset((e["concept_src"], e["concept_tgt"])))
        for e in R["MEDIATES"]:
            rels.append(frozenset((e["concept_a"], e["concept_mediator"], e["concept_d"])))
        for e in R["CONDITIONAL_EMERGES"]:
            rels.append(frozenset((e["concept_a"], e["concept_b"], e["concept_e"])))
        return concepts, rels

    def faithful(self):
        print("\n[2/7] faithfulness to Phase-4 structure")
        concepts, rels = self._load_relations()
        self.relations = rels
        self.concepts = concepts
        f = self.data["foundationality_scores.json"]
        self.check("concept count = 103", f["n_concepts"] == len(concepts) == 103,
                   f"{f['n_concepts']}")
        self.check("relation count = 6832",
                   f["n_relations"] == len(rels) == 6832, f"{f['n_relations']}/{len(rels)}")
        self.check("foundationality scores cover every concept",
                   sorted(s["concept_id"] for s in f["scores"]) == concepts)
        man = self.data["compression_manifest.json"]
        self.check("manifest totals.relations = 6832",
                   man["totals"]["relations"] == 6832)

    # ── 3. foundationality internal consistency ───────────────────────────────

    def foundationality(self):
        print("\n[3/7] foundationality consistency")
        f = self.data["foundationality_scores.json"]
        scores = f["scores"]
        # ranks are a permutation of 1..103
        ranks = sorted(s["rank"] for s in scores)
        self.check("ranks form 1..103", ranks == list(range(1, 104)))
        # composite descending by rank
        by_rank = sorted(scores, key=lambda s: s["rank"])
        comps = [s["composite_score"] for s in by_rank]
        self.check("composite non-increasing with rank",
                   all(a >= b - 1e-9 for a, b in zip(comps, comps[1:])))
        # removal_impact_count equals independent recomputation
        inc = {c: 0 for c in self.concepts}
        for rel in self.relations:
            for m in rel:
                inc[m] += 1
        ok = all(s["removal_impact_count"] == inc[s["concept_id"]] for s in scores)
        self.check("removal_impact_count matches recomputed incidence", ok)
        # order list consistent with ranks
        self.check("foundationality_order matches rank order",
                   f["foundationality_order"] == [s["concept_id"] for s in by_rank])

    # ── 4. reconstruction sets monotone + coverage exact ──────────────────────

    def reconstruction(self):
        print("\n[4/7] reconstruction sets")
        rs = self.data["reconstruction_sets.json"]
        order = rs["greedy_order"]
        self.check("greedy_order is a permutation of 103 concepts",
                   sorted(order) == self.concepts)
        sets = rs["reconstruction_sets"]
        # sizes non-decreasing with target
        sizes = [s["set_size"] for s in sets]
        self.check("set sizes non-decreasing with target",
                   all(a <= b for a, b in zip(sizes, sizes[1:])))
        # verify achieved coverage for each set by recomputation
        all_ok = True
        for s in sets:
            S = set(s["concept_set"])
            cov = sum(1 for rel in self.relations if rel <= S) / len(self.relations)
            if abs(cov - s["achieved_fraction"]) > 1e-6 or cov < s["target_fraction"]:
                all_ok = False
        self.check("achieved coverage recomputes & meets target", all_ok)

    # ── 5. dependency layers + irreducible structures ────────────────────────

    def layers_irreducible(self):
        print("\n[5/7] dependency layers + irreducible structures")
        dl = self.data["dependency_layers.json"]
        # every concept appears exactly once across layers ∪ unlayered
        seen = list(dl["unlayered_concepts"]["concepts"])
        for L in dl["layers"]:
            seen += L["concepts"]
        self.check("layers ∪ unlayered partition all 103 concepts",
                   sorted(seen) == self.concepts, f"{len(seen)}")
        # level 0 exists
        self.check("level 0 present (structural sinks)",
                   any(L["level"] == 0 for L in dl["layers"]))
        irr = self.data["irreducible_structures.json"]
        # SCC members are disjoint and size>=2
        comps = irr["dependency_irreducible"]["components"]
        members = [c for comp in comps for c in comp["concepts"]]
        self.check("dependency SCC members disjoint",
                   len(members) == len(set(members)))
        self.check("all dependency SCCs size >= 2",
                   all(comp["size"] >= 2 for comp in comps))
        self.check("dependency SCC count matches",
                   irr["dependency_irreducible"]["count"] == len(comps))

    # ── 6. hub removal + curve sanity ─────────────────────────────────────────

    def hub_and_curve(self):
        print("\n[6/7] hub removal + compression curve")
        h = self.data["hub_removal_analysis.json"]
        self.check("removed hub = CONCEPT_007", h["removed_hub"] == "CONCEPT_007")
        self.check("hub removal verdict in {collapse,reorganize,partial_reorganize}",
                   h["verdict"]["classification"] in
                   {"collapse", "reorganize", "partial_reorganize"})
        # retention recomputed
        S = set(self.concepts) - {"CONCEPT_007"}
        keep = sum(1 for rel in self.relations if rel <= S) / len(self.relations)
        self.check("hub-removal proposition retention recomputes",
                   abs(keep - h["structure_retention"]["proposition_retention"]) < 1e-6,
                   f"{keep:.6f}")
        cur = self.data["compression_curve.json"]
        gc = cur["greedy_coverage_curve"]
        self.check("greedy curve runs k=0..103", gc[0]["k"] == 0 and gc[-1]["k"] == 103)
        self.check("greedy curve ends at fraction 1.0", abs(gc[-1]["fraction"] - 1.0) < 1e-9)
        fracs = [p["fraction"] for p in gc]
        self.check("greedy curve monotone non-decreasing",
                   all(a <= b + 1e-9 for a, b in zip(fracs, fracs[1:])))

    # ── 7. byte-identical rebuild ──────────────────────────────────────────────

    def rebuild(self):
        print("\n[7/7] byte-identical rebuild (--rebuild)")
        before = {f: (COMP_DIR / f).read_bytes() for f in FILES if (COMP_DIR / f).exists()}
        res = subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / "build_compression.py")],
                             capture_output=True, text=True)
        self.check("builder exits 0", res.returncode == 0, res.stderr[-200:] if res.returncode else "")
        for f in FILES:
            after = (COMP_DIR / f).read_bytes()
            self.check(f"byte-identical: {f}", before.get(f) == after)

    def run(self, do_rebuild):
        self.files()
        self.faithful()
        self.foundationality()
        self.reconstruction()
        self.layers_irreducible()
        self.hub_and_curve()
        if do_rebuild:
            self.rebuild()
        print(f"\n{'='*50}")
        if self.failures == 0:
            print(f"  ALL CHECKS PASS")
        else:
            print(f"  {self.failures} CHECK(S) FAILED")
        print(f"{'='*50}")
        return self.failures == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true")
    args = ap.parse_args()
    print("Monad Dependency Compression Engine — Validator (Phase 5)")
    ok = Validator().run(args.rebuild)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
