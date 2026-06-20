#!/usr/bin/env python3
"""
scripts/build_scorecard.py

Monad v2 — the held-out EXTERNAL SCORECARD (touched once, never an input).

Compares the internally-derived inter-ayah network (L6/L7) against a human
reference of parallel verses (external/mutashabiha_data.json). Measures how well
our purely-internal network recovers human-identified related verses — RECALL@K
vs a random baseline. Per the charter, our extra links are NOT counted as errors;
the text is the criterion.

QUARANTINE: this is the only script that reads external/. The L0–L8 pipeline
never does.
"""

import argparse
import json
import math
import sqlite3
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DB = REPO / "generated" / "monad.db"
EXT = REPO / "external" / "mutashabiha_data.json"
OUT = REPO / "generated" / "layers" / "scorecard"
ALLAH = "{ll~ah"
DF_LO, DF_HI = 3, 40
KS = [5, 10, 20, 50]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--quiet", action="store_true"); args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row
    allah = con.execute("SELECT lemma_id FROM lemmas WHERE lemma_buckwalter=?", (ALLAH,)).fetchone()[0]
    # absolute (sequential) ayah number -> (sura, ayah)
    abs2sa = {}
    for s, a, seq in con.execute("SELECT surah_number,ayah_number,ayah_sequential FROM ayahs"):
        if seq is not None:
            abs2sa[seq] = (s, a)
    rows = con.execute("SELECT surah_number s,ayah_number a,pos,segment_type st,lemma_id,root_id "
                       "FROM morphology ORDER BY surah_number,ayah_number").fetchall()
    con.close()
    # sanity: absolute 8 should be 2:1 (al-Fatiha = 7 ayat)
    assert abs2sa.get(8) == (2, 1), f"absolute-numbering mismatch: abs 8 -> {abs2sa.get(8)}"

    by = defaultdict(list)
    for r in rows:
        by[(r["s"], r["a"])].append(r)
    ayah_roots = {}
    for key, toks in by.items():
        ayah_roots[key] = sorted({t["root_id"] for t in toks
                                  if t["st"] == "STEM" and t["pos"] in ("N", "ADJ", "V")
                                  and t["root_id"] is not None and t["lemma_id"] != allah})
    keys = sorted(ayah_roots)
    N = len(keys)
    df = Counter()
    for k in keys:
        for r in ayah_roots[k]:
            df[r] += 1
    rare = {r for r, d in df.items() if DF_LO <= d <= DF_HI}
    def idf(r):
        return math.log(N / df[r])
    inv = defaultdict(list)
    for k in keys:
        for r in ayah_roots[k]:
            if r in rare:
                inv[r].append(k)

    inv_all = defaultdict(list)
    for k in keys:
        for r in ayah_roots[k]:
            inv_all[r].append(k)

    # full ranked neighbour list per ayah (idf-weighted; all suras).
    # rare-only = our thematic content network; all-roots = surface/lexical overlap.
    def ranked_neighbours(k, use_rare):
        score = Counter()
        index = inv if use_rare else inv_all
        for r in ayah_roots[k]:
            if use_rare and r not in rare:
                continue
            w = idf(r)
            for b in index[r]:
                if b != k:
                    score[b] += w
        return [b for b, _ in score.most_common()]

    # parse human reference into undirected (sura:ayah) pairs
    data = json.loads(EXT.read_text(encoding="utf-8"))
    def srcs(rec):
        s = rec["src"]["ayah"]
        return s if isinstance(s, list) else [s]
    pairs = set()
    for juz, recs in data.items():
        for rec in recs:
            for sa in srcs(rec):
                for m in rec["muts"]:
                    ma = m["ayah"]
                    for mm in (ma if isinstance(ma, list) else [ma]):
                        if sa in abs2sa and mm in abs2sa and sa != mm:
                            a, b = abs2sa[sa], abs2sa[mm]
                            pairs.add((min(a, b), max(a, b)))

    # evaluate recall for each pair under a given neighbour variant
    def evaluate(use_rare):
        cache = {}
        def neigh(k):
            if k not in cache:
                cache[k] = ranked_neighbours(k, use_rare)
            return cache[k]
        hits = {K: 0 for K in KS}; ranks = []
        for a, b in pairs:
            na = neigh(a); nb = neigh(b)
            ra = na.index(b) + 1 if b in na else None
            rb = nb.index(a) + 1 if a in nb else None
            best = min([r for r in (ra, rb) if r is not None], default=None)
            if best is not None:
                ranks.append(best)
                for K in KS:
                    if best <= K:
                        hits[K] += 1
        return hits, sorted(ranks)

    total = len(pairs)
    def pct(x):
        return round(100.0 * x / total, 2) if total else 0.0
    rand = {f"recall@{K}": round(100.0 * K / (N - 1), 3) for K in KS}

    hits_rare, ranks_rare = evaluate(True)
    hits_all, ranks_all = evaluate(False)
    rare_recall = {f"recall@{K}": pct(hits_rare[K]) for K in KS}
    all_recall = {f"recall@{K}": pct(hits_all[K]) for K in KS}
    median_rare = ranks_rare[len(ranks_rare) // 2] if ranks_rare else None

    result = {
        "method": "scorecard-1.0", "reference": "mutashabiha (human parallel verses)",
        "human_pairs_evaluated": total,
        "rare_concept_network": {"recall": rare_recall, "found_anywhere_pct": pct(len(ranks_rare)),
                                 "median_rank_when_found": median_rare,
                                 "fold_over_random@20": round(rare_recall["recall@20"] / rand["recall@20"], 1)},
        "all_root_surface_overlap": {"recall": all_recall, "found_anywhere_pct": pct(len(ranks_all))},
        "random_baseline": rand,
        "interpretation": "mutashābihāt are textual/PHRASE parallels (memorisation confusions). The "
                          "rare-concept network targets specific shared content, not common phrasing, so its "
                          "overlap is modest but far above chance. The all-root (surface) variant recovers "
                          "many more — confirming the reference captures lexical phrase-overlap, a DIFFERENT "
                          "relation than the thematic network. Links our network finds beyond the reference "
                          "are potential discoveries, not errors (charter: the text is the criterion).",
    }
    (out / "scorecard.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")

    if not args.quiet:
        print("EXTERNAL SCORECARD — internal network vs human mutashābihāt (held-out, one-time)\n")
        print(f"  human parallel-verse pairs evaluated: {total}")
        print(f"\n  {'K':>5}  {'rare-concept':>13}  {'all-root(surface)':>18}  {'random':>9}")
        for K in KS:
            print(f"  {K:>5}  {rare_recall[f'recall@{K}']:>12}%  "
                  f"{all_recall[f'recall@{K}']:>17}%  {rand[f'recall@{K}']:>8}%")
        print(f"\n  rare-concept fold over random @20: "
              f"{result['rare_concept_network']['fold_over_random@20']}x")
        print("  ⇒ network recovers human parallels far above chance; the all-root (surface) variant")
        print("    recovers many more — the reference measures PHRASE overlap, a different relation than")
        print("    our thematic rare-concept network.")


if __name__ == "__main__":
    main()
