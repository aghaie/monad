#!/usr/bin/env python3
"""
scripts/validate_concepts.py

Monad Concept Discovery Engine — Validator (Phase 3).

Verifies that generated/concepts/*.json is internally consistent, faithful to the
Phase-1/2 inputs, and deterministically reproducible. Purely structural and
statistical; performs no interpretation and assigns no meaning.

Usage:
    python scripts/validate_concepts.py [--lex DIR] [--concepts DIR] [--rebuild]

Exit code: 0 all checks passed, 1 otherwise.
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
DEFAULT_LEX = REPO_ROOT / "generated" / "lexicon"
DEFAULT_CONCEPTS = REPO_ROOT / "generated" / "concepts"
DEFAULT_DB = REPO_ROOT / "generated" / "monad.db"

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
INFO = "\033[94mINFO\033[0m"

FILES = [
    "concept_candidates.json", "concept_memberships.json", "concept_graph.json",
    "concept_centers.json", "concept_statistics.json",
    "concept_relationships.json", "concept_manifest.json",
]
K_CLIQUE = 4
LEMMA_THR = 0.30


class Validator:
    def __init__(self, lex_dir, c_dir):
        self.lex_dir = Path(lex_dir)
        self.c_dir = Path(c_dir)
        self.failures = 0
        self.data = {}

    def check(self, label, ok, detail=""):
        if not ok:
            self.failures += 1
        print(f"  [{PASS if ok else FAIL}] {label}" + (f"  ({detail})" if detail else ""))
        return ok

    def _load(self, name):
        return json.loads((self.c_dir / name).read_text("utf-8"))

    # ── files ─────────────────────────────────────────────────────────────────

    def check_files(self):
        print("\n── File presence + JSON parse ───────────────────────────────────────")
        for name in FILES:
            if not self.check(f"{name} exists", (self.c_dir / name).exists()):
                continue
            try:
                self.data[name] = self._load(name)
                self.check(f"{name} parses", True)
            except Exception as e:                       # noqa: BLE001
                self.check(f"{name} parses", False, str(e))

    # ── ids + members ─────────────────────────────────────────────────────────

    def check_ids_members(self):
        print("\n── Concept ids + membership integrity ───────────────────────────────")
        cand = self.data["concept_candidates.json"]
        concepts = cand["concepts"]
        n = len(concepts)
        self.check("concept_count matches array", cand["concept_count"] == n)
        ids = [c["concept_id"] for c in concepts]
        self.check("concept ids unique", len(set(ids)) == n)
        expected = [f"CONCEPT_{i+1:03d}" for i in range(n)]
        self.check("concept ids sequential CONCEPT_001..N", ids == expected)
        self.check("all concepts have >= K_CLIQUE roots",
                   all(c["size_roots"] >= K_CLIQUE for c in concepts),
                   f"K_CLIQUE={K_CLIQUE}")

        # referential: roots/lemmas exist in the lexicon
        rp = json.loads((self.lex_dir / "root_profiles.json").read_text("utf-8"))
        lp = json.loads((self.lex_dir / "lemma_profiles.json").read_text("utf-8"))
        root_ids = set(int(k) for k in rp)
        lemma_ids = set(int(k) for k in lp)
        bad_r = bad_l = 0
        for c in concepts:
            for m in c["member_roots"]:
                if m["root_id"] not in root_ids:
                    bad_r += 1
            for m in c["member_lemmas"]:
                if m["lemma_id"] not in lemma_ids:
                    bad_l += 1
        self.check("all member roots exist in lexicon", bad_r == 0, f"{bad_r} bad")
        self.check("all member lemmas exist in lexicon", bad_l == 0, f"{bad_l} bad")

    # ── score ranges ──────────────────────────────────────────────────────────

    def check_ranges(self):
        print("\n── Metric ranges ────────────────────────────────────────────────────")
        concepts = self.data["concept_candidates.json"]["concepts"]
        keys = ["internal_density", "external_separation", "cluster_stability",
                "cohesion_score"]
        bad = 0
        for c in concepts:
            for k in keys:
                if not (0.0 <= c[k] <= 1.0):
                    bad += 1
            for m in c["member_roots"]:
                if not (0.0 <= m["membership_confidence"] <= 1.0):
                    bad += 1
            for m in c["member_lemmas"]:
                if not (LEMMA_THR - 1e-9 <= m["membership_confidence"] <= 1.0):
                    bad += 1
        self.check("all metrics + confidences in valid range", bad == 0, f"{bad} violations")

    # ── memberships consistency ───────────────────────────────────────────────

    def check_memberships(self):
        print("\n── Membership index consistency + multi-membership ──────────────────")
        mem = self.data["concept_memberships.json"]
        concepts = self.data["concept_candidates.json"]["concepts"]
        per_concept = {c["concept_id"]: set(m["root_id"] for m in c["member_roots"])
                       for c in concepts}
        # inverse root index must agree with per-concept lists
        bad = 0
        for rid, lst in mem["root_memberships"].items():
            for entry in lst:
                if int(rid) not in per_concept.get(entry["concept_id"], set()):
                    bad += 1
        self.check("root_memberships inverse index agrees with concepts", bad == 0,
                   f"{bad} mismatches")
        # multi-membership actually present
        multi = sum(1 for lst in mem["root_memberships"].values() if len(lst) > 1)
        self.check("multi-membership roots exist (overlapping clusters)", multi > 0,
                   f"{multi} roots in >1 concept")
        multil = sum(1 for lst in mem["lemma_memberships"].values() if len(lst) > 1)
        self.check("multi-membership lemmas exist", multil > 0,
                   f"{multil} lemmas in >1 concept")

    # ── graph + centrality ────────────────────────────────────────────────────

    def check_graph(self):
        print("\n── Concept graph + centrality ───────────────────────────────────────")
        g = self.data["concept_graph.json"]
        ids = {n["id"] for n in g["nodes"]}
        ncand = self.data["concept_candidates.json"]["concept_count"]
        self.check("graph node_count == concept_count", g["node_count"] == ncand)
        self.check("graph nodes array length matches", len(g["nodes"]) == ncand)
        self.check("edge_count matches edges array", g["edge_count"] == len(g["edges"]))
        dangle = sum(1 for e in g["edges"]
                     if e["source"] not in ids or e["target"] not in ids)
        self.check("all edges reference existing concepts", dangle == 0, f"{dangle} dangling")
        bad_w = sum(1 for e in g["edges"] if not (0.0 <= e["weight"] <= 1.0))
        self.check("all edge weights in [0,1]", bad_w == 0, f"{bad_w}")
        # no duplicate / self edges
        seen = set()
        dup = self_e = 0
        for e in g["edges"]:
            if e["source"] == e["target"]:
                self_e += 1
            key = tuple(sorted((e["source"], e["target"])))
            if key in seen:
                dup += 1
            seen.add(key)
        self.check("no self or duplicate edges", dup == 0 and self_e == 0,
                   f"dup={dup} self={self_e}")
        # centrality present + ranges
        bad_c = 0
        labels = []
        for nd in g["nodes"]:
            if not (0.0 <= nd["eigenvector_centrality"] <= 1.0):
                bad_c += 1
            if nd["betweenness_centrality"] < 0:
                bad_c += 1
            labels.append(nd["meta_community"])
        self.check("eigenvector in [0,1] and betweenness >= 0", bad_c == 0, f"{bad_c}")
        # meta-community labels contiguous 0..M-1
        uniq = sorted(set(labels))
        self.check("meta-community labels contiguous from 0",
                   uniq == list(range(len(uniq))), f"{len(uniq)} communities")

    # ── classifications ───────────────────────────────────────────────────────

    def check_classifications(self):
        print("\n── Discovery classifications ────────────────────────────────────────")
        stat = self.data["concept_statistics.json"]
        ids = {c["concept_id"] for c in self.data["concept_candidates.json"]["concepts"]}
        bad = 0
        for cat, lst in stat["classifications"].items():
            for cid in lst:
                if cid not in ids:
                    bad += 1
        self.check("all classification ids are valid concepts", bad == 0, f"{bad} bad")
        required = {"highly_cohesive", "highly_connected", "bridge_concepts",
                    "isolated_concepts", "highly_stable", "global_concepts",
                    "localized_concepts", "rare_concepts"}
        self.check("all required classifications present",
                   required <= set(stat["classifications"].keys()))

    # ── manifest input fidelity ───────────────────────────────────────────────

    def check_manifest(self):
        print("\n── Manifest input fidelity ──────────────────────────────────────────")
        man = self.data["concept_manifest.json"]

        def h(p):
            return hashlib.sha256(Path(p).read_bytes()).hexdigest()

        ok = True
        for f in ("semantic_neighbors.json", "root_profiles.json",
                  "lemma_profiles.json", "distribution_profiles.json"):
            if man["input_sha256"].get(f) != h(self.lex_dir / f):
                ok = False
        self.check("manifest input hashes match current lexicon", ok)

    # ── deterministic rebuild ─────────────────────────────────────────────────

    def check_rebuild(self, db_path):
        print("\n── Deterministic rebuild ────────────────────────────────────────────")
        tmp = Path(tempfile.mkdtemp(prefix="concepts_rebuild_"))
        try:
            build = REPO_ROOT / "scripts" / "build_concepts.py"
            res = subprocess.run(
                [sys.executable, str(build), "--db", str(db_path),
                 "--lex", str(self.lex_dir), "--out", str(tmp)],
                capture_output=True, text=True)
            if res.returncode != 0:
                self.check("rebuild succeeded", False, res.stderr[-200:])
                return
            mism = 0
            for name in FILES:
                a = hashlib.sha256((self.c_dir / name).read_bytes()).hexdigest()
                b = hashlib.sha256((tmp / name).read_bytes()).hexdigest()
                if a != b:
                    mism += 1
                    print(f"  [{INFO}] differs: {name}")
            self.check("rebuild byte-identical to committed outputs", mism == 0,
                       f"{mism} differ")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def run(self, rebuild, db_path):
        print(f"\nValidating concepts in {self.c_dir} …")
        self.check_files()
        if len(self.data) == len(FILES):
            self.check_ids_members()
            self.check_ranges()
            self.check_memberships()
            self.check_graph()
            self.check_classifications()
            self.check_manifest()
        if rebuild:
            self.check_rebuild(db_path)
        print("\n" + "=" * 72)
        print(f"  RESULT: {PASS if self.failures == 0 else FAIL}"
              + ("" if self.failures == 0 else f" — {self.failures} failed"))
        print("=" * 72 + "\n")
        return self.failures == 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lex", default=str(DEFAULT_LEX))
    ap.add_argument("--concepts", default=str(DEFAULT_CONCEPTS))
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--rebuild", action="store_true")
    args = ap.parse_args()
    ok = Validator(args.lex, args.concepts).run(args.rebuild, args.db)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
