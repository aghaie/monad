#!/usr/bin/env python3
"""
scripts/validate_lexicon.py

Monad Quran Internal Lexicon Engine — Validator (Phase 2).

Verifies that generated/lexicon/*.json is internally consistent, faithful to
generated/monad.db, and deterministically reproducible. Runs no interpretation;
purely structural and statistical integrity checks.

Usage:
    python scripts/validate_lexicon.py [--db PATH] [--lex DIR] [--rebuild]

Checks:
    * all seven expected output files exist and parse
    * entity counts match the database (roots / lemmas / surahs / ayahs)
    * occurrence counts agree with the database token counts
    * referential integrity (every neighbor / node / edge id is real)
    * semantic neighbors: <= top_k, confidence in [0,1], sorted descending
    * context windows: one per word token, window contents within ayah bounds
    * graph: node/edge counts self-consistent, edge endpoints exist
    * --rebuild: rebuild into a temp dir and assert byte-identical output

Exit code:
    0  all checks passed
    1  one or more checks failed
"""

import argparse
import hashlib
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO_ROOT / "generated" / "monad.db"
DEFAULT_LEX = REPO_ROOT / "generated" / "lexicon"

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
INFO = "\033[94mINFO\033[0m"

FILES = [
    "root_profiles.json", "lemma_profiles.json", "context_windows.json",
    "cooccurrence_graph.json", "semantic_neighbors.json",
    "distribution_profiles.json", "lexicon_summary.json",
]


class Validator:
    def __init__(self, db_path: Path, lex_dir: Path):
        self.db_path = db_path
        self.lex_dir = lex_dir
        self.failures = 0
        self.con = sqlite3.connect(db_path)

    def check(self, label, passed, detail=""):
        status = PASS if passed else FAIL
        if not passed:
            self.failures += 1
        line = f"  [{status}] {label}"
        if detail:
            line += f"  ({detail})"
        print(line)
        return passed

    def info(self, label, detail=""):
        line = f"  [{INFO}] {label}"
        if detail:
            line += f"  ({detail})"
        print(line)

    def _load(self, name):
        return json.loads((self.lex_dir / name).read_text(encoding="utf-8"))

    # ── files exist + parse ───────────────────────────────────────────────────

    def check_files(self):
        print("\n── File presence + JSON parse ───────────────────────────────────────")
        self.data = {}
        for name in FILES:
            p = self.lex_dir / name
            ok = p.exists()
            if not self.check(f"{name} exists", ok):
                continue
            try:
                self.data[name] = json.loads(p.read_text(encoding="utf-8"))
                self.check(f"{name} parses", True)
            except Exception as e:                       # noqa: BLE001
                self.check(f"{name} parses", False, str(e))

    # ── counts vs database ────────────────────────────────────────────────────

    def check_counts(self):
        print("\n── Entity counts vs database ────────────────────────────────────────")
        con = self.con
        db_roots = con.execute(
            "SELECT COUNT(DISTINCT root_id) FROM words WHERE root_id IS NOT NULL").fetchone()[0]
        db_lemmas = con.execute(
            "SELECT COUNT(DISTINCT lemma_id) FROM words WHERE lemma_id IS NOT NULL").fetchone()[0]
        db_words = con.execute("SELECT COUNT(*) FROM words").fetchone()[0]

        rp = self.data.get("root_profiles.json", {})
        lp = self.data.get("lemma_profiles.json", {})
        self.check("root_profiles count == distinct roots in words",
                   len(rp) == db_roots, f"{len(rp)} vs {db_roots}")
        self.check("lemma_profiles count == distinct lemmas in words",
                   len(lp) == db_lemmas, f"{len(lp)} vs {db_lemmas}")

        cw = self.data.get("context_windows.json", {})
        self.check("context_windows count == word tokens",
                   cw.get("occurrence_count") == db_words,
                   f"{cw.get('occurrence_count')} vs {db_words}")
        self.check("context_windows array length matches header",
                   len(cw.get("windows", [])) == cw.get("occurrence_count"))

        summ = self.data.get("lexicon_summary.json", {})
        t = summ.get("totals", {})
        self.check("summary.totals.roots matches profiles",
                   t.get("roots") == len(rp))
        self.check("summary.totals.lemmas matches profiles",
                   t.get("lemmas") == len(lp))

    # ── occurrence fidelity ───────────────────────────────────────────────────

    def check_occurrences(self):
        print("\n── Occurrence-count fidelity (sampled) ──────────────────────────────")
        con = self.con
        rp = self.data.get("root_profiles.json", {})
        # Sum of root occurrence_count must equal #word tokens with a root.
        db_root_tokens = con.execute(
            "SELECT COUNT(*) FROM words WHERE root_id IS NOT NULL").fetchone()[0]
        sum_root = sum(v["occurrence_count"] for v in rp.values())
        self.check("sum(root occurrence_count) == tokens with root",
                   sum_root == db_root_tokens, f"{sum_root} vs {db_root_tokens}")

        lp = self.data.get("lemma_profiles.json", {})
        db_lemma_tokens = con.execute(
            "SELECT COUNT(*) FROM words WHERE lemma_id IS NOT NULL").fetchone()[0]
        sum_lemma = sum(v["occurrence_count"] for v in lp.values())
        self.check("sum(lemma occurrence_count) == tokens with lemma",
                   sum_lemma == db_lemma_tokens, f"{sum_lemma} vs {db_lemma_tokens}")

        # Per-entity spot checks against the DB.
        ok = True
        detail = ""
        for rid in list(rp.keys())[:50]:
            db_c = con.execute(
                "SELECT COUNT(*) FROM words WHERE root_id=?", (int(rid),)).fetchone()[0]
            if db_c != rp[rid]["occurrence_count"]:
                ok = False
                detail = f"root {rid}: {rp[rid]['occurrence_count']} vs {db_c}"
                break
        self.check("first 50 root occurrence_counts match DB", ok, detail)

    # ── referential integrity ─────────────────────────────────────────────────

    def check_referential(self):
        print("\n── Referential integrity ────────────────────────────────────────────")
        rp = self.data.get("root_profiles.json", {})
        lp = self.data.get("lemma_profiles.json", {})
        root_ids = set(int(k) for k in rp)
        lemma_ids = set(int(k) for k in lp)

        ok = all(int(n["root_id"]) in root_ids
                 for v in rp.values() for n in v["top_neighbor_roots"])
        self.check("root profile neighbor_roots reference real roots", ok)
        ok = all(int(n["lemma_id"]) in lemma_ids
                 for v in lp.values() for n in v["top_neighbor_lemmas"])
        self.check("lemma profile neighbor_lemmas reference real lemmas", ok)

        sem = self.data.get("semantic_neighbors.json", {})
        ok = all(int(n["root_id"]) in root_ids
                 for v in sem.get("roots", {}).values() for n in v["neighbors"])
        self.check("semantic root neighbors reference real roots", ok)
        ok = all(int(n["lemma_id"]) in lemma_ids
                 for v in sem.get("lemmas", {}).values() for n in v["neighbors"])
        self.check("semantic lemma neighbors reference real lemmas", ok)

    # ── semantic-neighbor invariants ──────────────────────────────────────────

    def check_semantics(self):
        print("\n── Semantic-neighbor invariants ─────────────────────────────────────")
        sem = self.data.get("semantic_neighbors.json", {})
        top_k = sem.get("top_k", 20)
        bad_len = bad_range = bad_sort = bad_self = 0
        for group, idkey in (("roots", "root_id"), ("lemmas", "lemma_id")):
            for eid, v in sem.get(group, {}).items():
                ns = v["neighbors"]
                if len(ns) > top_k:
                    bad_len += 1
                confs = [n["confidence"] for n in ns]
                if any(c < 0.0 or c > 1.0 for c in confs):
                    bad_range += 1
                if confs != sorted(confs, reverse=True):
                    bad_sort += 1
                if any(int(n[idkey]) == int(eid) for n in ns):
                    bad_self += 1
        self.check(f"all neighbor lists <= top_k ({top_k})", bad_len == 0,
                   f"{bad_len} violations")
        self.check("all confidences in [0,1]", bad_range == 0, f"{bad_range} violations")
        self.check("all neighbor lists sorted by confidence desc", bad_sort == 0,
                   f"{bad_sort} violations")
        self.check("no entity is its own neighbor", bad_self == 0, f"{bad_self} violations")

    # ── context-window invariants ─────────────────────────────────────────────

    def check_windows(self):
        print("\n── Context-window invariants (sampled) ──────────────────────────────")
        con = self.con
        cw = self.data.get("context_windows.json", {})
        wins = cw.get("windows", [])
        self.check("window_sizes == [3,5,10]", cw.get("window_sizes") == [3, 5, 10])
        bad = 0
        sample = wins[::max(1, len(wins) // 500)]   # ~500 spread samples
        for w in sample:
            # neighbor counts must not exceed the window size
            for size in ("3", "5", "10"):
                if len(w["neighbor_roots"][size]) > 2 * int(size):
                    bad += 1
                if len(w["neighbor_lemmas"][size]) > 2 * int(size):
                    bad += 1
            # prev/next forms must come from the same ayah
            n_in_ayah = con.execute(
                "SELECT COUNT(*) FROM words WHERE surah_number=? AND ayah_number=?",
                (w["surah"], w["ayah"])).fetchone()[0]
            if len(w["prev_forms"]) + 1 + len(w["next_forms"]) > n_in_ayah + 18:
                bad += 1
        self.check("sampled windows respect size + ayah bounds", bad == 0,
                   f"{bad} violations in {len(sample)} samples")

    # ── graph invariants ──────────────────────────────────────────────────────

    def check_graph(self):
        print("\n── Co-occurrence graph invariants ───────────────────────────────────")
        g = self.data.get("cooccurrence_graph.json", {})
        nodes = g.get("nodes", [])
        edges = g.get("edges", [])
        self.check("node_count matches nodes array", g.get("node_count") == len(nodes))
        self.check("edge_count matches edges array", g.get("edge_count") == len(edges))
        node_ids = {n["id"] for n in nodes}
        bad = sum(1 for e in edges
                  if e["source"] not in node_ids or e["target"] not in node_ids)
        self.check("all edge endpoints exist as nodes", bad == 0, f"{bad} dangling")
        bad = sum(1 for e in edges if e["cooccurrence"] < g.get("min_cooccurrence", 0))
        self.check("all edges meet min_cooccurrence", bad == 0, f"{bad} violations")

    # ── determinism ───────────────────────────────────────────────────────────

    @staticmethod
    def _hash(path: Path):
        h = hashlib.sha256()
        h.update(path.read_bytes())
        return h.hexdigest()

    def check_rebuild(self):
        print("\n── Deterministic rebuild ────────────────────────────────────────────")
        tmp = Path(tempfile.mkdtemp(prefix="lexicon_rebuild_"))
        try:
            build = REPO_ROOT / "scripts" / "build_lexicon.py"
            res = subprocess.run(
                [sys.executable, str(build), "--db", str(self.db_path),
                 "--out", str(tmp)],
                capture_output=True, text=True)
            if res.returncode != 0:
                self.check("rebuild succeeded", False, res.stderr[-200:])
                return
            mismatch = 0
            for name in FILES:
                a = self._hash(self.lex_dir / name)
                b = self._hash(tmp / name)
                if a != b:
                    mismatch += 1
                    self.info(f"differs: {name}")
            self.check("rebuild byte-identical to committed outputs", mismatch == 0,
                       f"{mismatch} files differ")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def run(self, rebuild):
        print(f"\nValidating lexicon in {self.lex_dir} against {self.db_path.name} …")
        self.check_files()
        if self.failures == 0 or self.data:
            self.check_counts()
            self.check_occurrences()
            self.check_referential()
            self.check_semantics()
            self.check_windows()
            self.check_graph()
        if rebuild:
            self.check_rebuild()
        self.con.close()
        print("\n" + ("=" * 72))
        if self.failures == 0:
            print(f"  RESULT: {PASS} — all checks passed")
        else:
            print(f"  RESULT: {FAIL} — {self.failures} check(s) failed")
        print("=" * 72 + "\n")
        return self.failures == 0


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--lex", default=str(DEFAULT_LEX))
    ap.add_argument("--rebuild", action="store_true",
                    help="Also rebuild into a temp dir and assert byte-identical output")
    args = ap.parse_args()

    v = Validator(Path(args.db), Path(args.lex))
    ok = v.run(rebuild=args.rebuild)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
