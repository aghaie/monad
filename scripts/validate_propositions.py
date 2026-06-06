#!/usr/bin/env python3
"""
scripts/validate_propositions.py

Monad Proposition Discovery Engine — Validator (Phase 4).

Checks that generated/propositions/*.json is internally consistent, faithful to
the Phase-1/2/3 inputs, threshold-compliant, and deterministically reproducible.
Purely structural and statistical; performs no interpretation.

Usage:
    python3 scripts/validate_propositions.py [--db PATH] [--lex DIR]
                                              [--concepts DIR] [--props DIR]
                                              [--rebuild]

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
DEFAULT_DB = REPO_ROOT / "generated" / "monad.db"
DEFAULT_LEX = REPO_ROOT / "generated" / "lexicon"
DEFAULT_CONCEPTS = REPO_ROOT / "generated" / "concepts"
DEFAULT_PROPS = REPO_ROOT / "generated" / "propositions"

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
INFO = "\033[94mINFO\033[0m"

FILES = [
    "proposition_candidates.json",
    "proposition_graph.json",
    "dependency_candidates.json",
    "implication_candidates.json",
    "conditional_patterns.json",
    "bridge_patterns.json",
    "proposition_manifest.json",
]

# constants used in threshold-compliance checks (mirror builder)
SUPPORT_MIN = 5
NPMI_MIN = 0.20
DEPENDS_LIFT_MIN = 2.0
DEPENDS_CONF_MIN = 0.30
REQUIRES_CONF_MIN = 0.90
ORDER_ASYM_MIN = 0.30
ORDER_SUPPORT_MIN = 10
PREDICT_LIFT_MIN = 1.5
PREDICT_CONF_MIN = 0.20
PREDICT_SUPPORT_MIN = 5
MED_CONF_MIN = 0.70
MED_ISO_MIN = 0.50
MED_SUPPORT_MIN = 5
SYNERGY_MIN = 0.15
SYNERGY_SUPPORT_MIN = 5


class Validator:

    def __init__(self, db, lex_dir, c_dir, p_dir):
        self.db = Path(db)
        self.lex_dir = Path(lex_dir)
        self.c_dir = Path(c_dir)
        self.p_dir = Path(p_dir)
        self.failures = 0
        self.data = {}

    def check(self, label, ok, detail=""):
        if not ok:
            self.failures += 1
        print(f"  [{PASS if ok else FAIL}] {label}"
              + (f"  ({detail})" if detail else ""))
        return ok

    def info(self, label):
        print(f"  [{INFO}] {label}")

    def _load(self, name):
        return json.loads((self.p_dir / name).read_text("utf-8"))

    # ── 1. File presence + load ──────────────────────────────────────────────

    def files(self):
        print("\n[1/6] file presence + load")
        for f in FILES:
            self.check(f"file present: {f}", (self.p_dir / f).is_file())
        for f in FILES:
            try:
                self.data[f] = self._load(f)
                self.check(f"loads as JSON: {f}", True)
            except Exception as exc:
                self.check(f"loads as JSON: {f}", False, str(exc))

    # ── 2. Schema + top-level keys ──────────────────────────────────────────

    def schema(self):
        print("\n[2/6] schema + top-level keys")
        cands = self.data["proposition_candidates.json"]
        for k in ("method", "n_concepts", "n_active_ayahs", "relations",
                  "statistics", "classifications"):
            self.check(f"proposition_candidates.{k}", k in cands)
        rel_types = ("ASSOCIATES_WITH", "CO_OCCURS", "DEPENDS_ON", "REQUIRES",
                     "PRECEDES", "FOLLOWS", "PREDICTS", "MEDIATES",
                     "CONDITIONAL_EMERGES")
        for t in rel_types:
            self.check(f"relations.{t} present", t in cands["relations"])

        graph = self.data["proposition_graph.json"]
        for k in ("method", "directed", "node_count", "edge_count",
                  "edge_attributes", "nodes", "edges", "bridges"):
            self.check(f"proposition_graph.{k}", k in graph)

        dep = self.data["dependency_candidates.json"]
        for k in ("method", "constants", "depends_on", "requires",
                  "hierarchical_chains"):
            self.check(f"dependency_candidates.{k}", k in dep)

        imp = self.data["implication_candidates.json"]
        for k in ("method", "constants", "predicts_by_window"):
            self.check(f"implication_candidates.{k}", k in imp)

        cond = self.data["conditional_patterns.json"]
        for k in ("method", "constants", "conditional_emerges"):
            self.check(f"conditional_patterns.{k}", k in cond)

        br = self.data["bridge_patterns.json"]
        for k in ("method", "constants", "mediates", "bridges",
                  "bridge_betweenness"):
            self.check(f"bridge_patterns.{k}", k in br)

        mani = self.data["proposition_manifest.json"]
        for k in ("method", "constants", "input_sha256", "totals",
                  "prohibitions_observed", "output_bytes"):
            self.check(f"proposition_manifest.{k}", k in mani)

    # ── 3. Concept-id referential integrity ─────────────────────────────────

    def referential(self):
        print("\n[3/6] referential integrity (concept ids subset of Phase-3)")
        memberships = json.loads(
            (self.c_dir / "concept_memberships.json").read_text("utf-8"))
        phase3_ids = set(memberships["concepts"].keys())

        graph = self.data["proposition_graph.json"]
        node_ids = {n["concept_id"] for n in graph["nodes"]}
        self.check("graph nodes == Phase-3 concepts",
                   node_ids == phase3_ids,
                   detail=f"|nodes|={len(node_ids)} |phase3|={len(phase3_ids)}")

        # all edges reference known nodes
        bad_edges = sum(1 for e in graph["edges"]
                         if e["src"] not in phase3_ids
                         or e["tgt"] not in phase3_ids)
        self.check("all graph edges reference known nodes", bad_edges == 0,
                   detail=f"bad={bad_edges}")

        # candidate concept ids
        bad_rel = 0
        rels = self.data["proposition_candidates.json"]["relations"]
        for rt in ("ASSOCIATES_WITH", "CO_OCCURS"):
            for e in rels[rt]:
                if e["concept_a"] not in phase3_ids or e["concept_b"] not in phase3_ids:
                    bad_rel += 1
        for rt in ("DEPENDS_ON", "REQUIRES", "PRECEDES", "FOLLOWS", "PREDICTS"):
            for e in rels[rt]:
                if e["concept_src"] not in phase3_ids or e["concept_tgt"] not in phase3_ids:
                    bad_rel += 1
        for e in rels["MEDIATES"]:
            if (e["concept_mediator"] not in phase3_ids
                    or e["concept_a"] not in phase3_ids
                    or e["concept_d"] not in phase3_ids):
                bad_rel += 1
        for e in rels["CONDITIONAL_EMERGES"]:
            if (e["concept_a"] not in phase3_ids
                    or e["concept_b"] not in phase3_ids
                    or e["concept_e"] not in phase3_ids):
                bad_rel += 1
        self.check("all relation entries reference known concept ids",
                   bad_rel == 0, detail=f"bad={bad_rel}")

    # ── 4. Threshold compliance ─────────────────────────────────────────────

    def thresholds(self):
        print("\n[4/6] threshold compliance")
        rels = self.data["proposition_candidates.json"]["relations"]

        bad = sum(1 for e in rels["ASSOCIATES_WITH"]
                   if e["npmi"] < NPMI_MIN - 1e-9
                   or e["support_count"] < SUPPORT_MIN)
        self.check("ASSOCIATES_WITH thresholds", bad == 0, f"bad={bad}")

        bad = sum(1 for e in rels["CO_OCCURS"] if e["support_count"] < SUPPORT_MIN)
        self.check("CO_OCCURS support floor", bad == 0, f"bad={bad}")

        bad = sum(1 for e in rels["DEPENDS_ON"]
                   if e["p_src_given_tgt"] < DEPENDS_CONF_MIN - 1e-9
                   or e["lift"] < DEPENDS_LIFT_MIN - 1e-9
                   or e["support_count"] < SUPPORT_MIN)
        self.check("DEPENDS_ON thresholds", bad == 0, f"bad={bad}")

        bad = sum(1 for e in rels["REQUIRES"]
                   if e["p_tgt_given_src"] < REQUIRES_CONF_MIN - 1e-9
                   or e["support_count"] < SUPPORT_MIN)
        self.check("REQUIRES thresholds", bad == 0, f"bad={bad}")

        bad = sum(1 for e in rels["PRECEDES"]
                   if e["asymmetry"] < ORDER_ASYM_MIN - 1e-9
                   or e["support_count"] < ORDER_SUPPORT_MIN)
        self.check("PRECEDES thresholds", bad == 0, f"bad={bad}")

        bad = sum(1 for e in rels["FOLLOWS"]
                   if e["asymmetry"] < ORDER_ASYM_MIN - 1e-9
                   or e["support_count"] < ORDER_SUPPORT_MIN)
        self.check("FOLLOWS thresholds", bad == 0, f"bad={bad}")

        bad = sum(1 for e in rels["PREDICTS"]
                   if e["p_tgt_given_src"] < PREDICT_CONF_MIN - 1e-9
                   or e["lift"] < PREDICT_LIFT_MIN - 1e-9
                   or e["support_count"] < PREDICT_SUPPORT_MIN)
        self.check("PREDICTS thresholds", bad == 0, f"bad={bad}")

        bad = sum(1 for e in rels["MEDIATES"]
                   if e["p_mediator_given_a_and_d"] < MED_CONF_MIN - 1e-9
                   or e["isolation"] < MED_ISO_MIN - 1e-9
                   or e["support_count_with_mediator"] < MED_SUPPORT_MIN)
        self.check("MEDIATES thresholds", bad == 0, f"bad={bad}")

        bad = sum(1 for e in rels["CONDITIONAL_EMERGES"]
                   if e["synergy"] < SYNERGY_MIN - 1e-9
                   or e["support_count"] < SYNERGY_SUPPORT_MIN)
        self.check("CONDITIONAL_EMERGES thresholds", bad == 0, f"bad={bad}")

        # totals match manifest
        mani_totals = self.data["proposition_manifest.json"]["totals"]
        actual = {f"edges_{k}": len(v) for k, v in rels.items()}
        for k in ("ASSOCIATES_WITH", "CO_OCCURS", "DEPENDS_ON", "REQUIRES",
                  "PRECEDES", "FOLLOWS", "PREDICTS", "MEDIATES",
                  "CONDITIONAL_EMERGES"):
            ek = f"edges_{k}"
            self.check(f"manifest totals match {ek}",
                       mani_totals.get(ek) == actual[ek],
                       f"manifest={mani_totals.get(ek)} actual={actual[ek]}")

        # graph edge count
        self.check("manifest.graph_edges matches proposition_graph",
                   mani_totals["graph_edges"]
                   == self.data["proposition_graph.json"]["edge_count"])

        # implication windows totals
        imp = self.data["implication_candidates.json"]["predicts_by_window"]
        total_w = sum(len(v) for v in imp.values())
        self.check("implication windows total = PREDICTS count",
                   total_w == len(rels["PREDICTS"]),
                   f"windows={total_w} flat={len(rels['PREDICTS'])}")

    # ── 5. Input SHA-256 fidelity ───────────────────────────────────────────

    def inputs(self):
        print("\n[5/6] input SHA-256 fidelity")
        mani = self.data["proposition_manifest.json"]
        expected = mani["input_sha256"]

        def sha(p):
            h = hashlib.sha256()
            h.update(Path(p).read_bytes())
            return h.hexdigest()

        actual = {
            "monad.db": sha(self.db),
            "root_profiles.json": sha(self.lex_dir / "root_profiles.json"),
            "lemma_profiles.json": sha(self.lex_dir / "lemma_profiles.json"),
            "distribution_profiles.json":
                sha(self.lex_dir / "distribution_profiles.json"),
            "semantic_neighbors.json":
                sha(self.lex_dir / "semantic_neighbors.json"),
            "concept_memberships.json":
                sha(self.c_dir / "concept_memberships.json"),
            "concept_candidates.json":
                sha(self.c_dir / "concept_candidates.json"),
            "concept_graph.json": sha(self.c_dir / "concept_graph.json"),
            "concept_manifest.json": sha(self.c_dir / "concept_manifest.json"),
        }
        for k, v in actual.items():
            self.check(f"input {k} sha256 matches manifest",
                       expected.get(k) == v,
                       detail=("differ" if expected.get(k) != v else ""))

    # ── 6. Byte-identical rebuild ───────────────────────────────────────────

    def rebuild(self):
        print("\n[6/6] byte-identical rebuild (--rebuild)")
        tmp = Path(tempfile.mkdtemp(prefix="monad_prop_rebuild_"))
        try:
            subprocess.run(
                ["python3", str(REPO_ROOT / "scripts" / "build_propositions.py"),
                 "--db", str(self.db),
                 "--lex", str(self.lex_dir),
                 "--concepts", str(self.c_dir),
                 "--out", str(tmp)],
                check=True,
                stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            for f in FILES:
                a = (self.p_dir / f).read_bytes()
                b = (tmp / f).read_bytes()
                self.check(f"byte-identical: {f}", a == b,
                           detail=f"old={len(a)}b new={len(b)}b"
                                  if a != b else "")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    # ── Run ──────────────────────────────────────────────────────────────────

    def run(self, do_rebuild):
        print(f"\nValidating {self.p_dir} …")
        self.files()
        if self.failures > 0:
            print(f"\nEarly exit: {self.failures} structural failures.\n")
            return 1
        self.schema()
        self.referential()
        self.thresholds()
        self.inputs()
        if do_rebuild:
            self.rebuild()
        print()
        if self.failures == 0:
            print(f"[{PASS}] all checks passed.\n")
            return 0
        print(f"[{FAIL}] {self.failures} failure(s).\n")
        return 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--lex", default=str(DEFAULT_LEX))
    ap.add_argument("--concepts", default=str(DEFAULT_CONCEPTS))
    ap.add_argument("--props", default=str(DEFAULT_PROPS))
    ap.add_argument("--rebuild", action="store_true")
    args = ap.parse_args()
    v = Validator(args.db, args.lex, args.concepts, args.props)
    sys.exit(v.run(args.rebuild))


if __name__ == "__main__":
    main()
