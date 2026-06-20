#!/usr/bin/env python3
"""
scripts/build_L7_global.py

Monad v2 — Layer L7: Global structure of the self-interpreting network.

Builds on the validated inter-ayah network (L6). Two products:

  1. crossref_index.json — for every ayah, the verses across the Quran that most
     explain it (rare-root, idf-weighted shared content): the computational
     "Quran-by-Quran" cross-reference map, and the network HUBS (the most
     connecting verses).

  2. A falsifiable STRUCTURAL claim: are SURAS coherent communities of this
     network? Test intra-sura vs inter-sura connection weight against a
     sura-label permutation null. If intra-sura connection concentrates beyond
     chance, suras are real thematic units of the self-interpreting network.

Edges use rare roots only (df in [3,40]) so connections reflect specific shared
content, not ubiquitous function words.

Source: generated/monad.db. Deterministic (seeded), offline, no external semantics.
"""

import argparse
import json
import math
import random
import sqlite3
import statistics
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DB_DEFAULT = REPO / "generated" / "monad.db"
OUT_DEFAULT = REPO / "generated" / "layers" / "L7_global"
ALLAH = "{ll~ah"
DF_LO, DF_HI = 3, 40
N_NULL = 200
SEED = 11
TOPREF = 5


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=str(DB_DEFAULT))
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    db = Path(args.db); out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(db); con.row_factory = sqlite3.Row
    allah = con.execute("SELECT lemma_id FROM lemmas WHERE lemma_buckwalter=?", (ALLAH,)).fetchone()[0]
    rows = con.execute("SELECT surah_number s,ayah_number a,pos,segment_type st,lemma_id,root_id "
                       "FROM morphology ORDER BY surah_number,ayah_number").fetchall()
    con.close()

    by = defaultdict(list)
    for r in rows:
        by[(r["s"], r["a"])].append(r)
    ayah_roots = {}
    for key, toks in by.items():
        rs = {t["root_id"] for t in toks if t["st"] == "STEM" and t["pos"] in ("N", "ADJ", "V")
              and t["root_id"] is not None and t["lemma_id"] != allah}
        ayah_roots[key] = rs
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

    # weighted edges via shared rare roots
    pair_w = defaultdict(float)
    nbr = defaultdict(Counter)
    for r in rare:
        wv = idf(r)
        ays = inv[r]
        for a, b in combinations(ays, 2):
            pair_w[(a, b)] += wv
            nbr[a][b] += wv
            nbr[b][a] += wv

    # ── sura coherence test ──
    sura_of = {k: k[0] for k in keys}
    pairs = list(pair_w.items())
    total_w = sum(w for _, w in pairs)
    def intra_frac(label):
        intra = sum(w for (a, b), w in pairs if label[a] == label[b])
        return intra / total_w if total_w else 0.0
    real_intra = intra_frac(sura_of)
    rnd = random.Random(SEED)
    labels = [sura_of[k] for k in keys]
    null = []
    for _ in range(N_NULL):
        perm = labels[:]; rnd.shuffle(perm)
        lab = {k: perm[i] for i, k in enumerate(keys)}
        null.append(intra_frac(lab))
    p_intra = (sum(1 for x in null if x >= real_intra) + 1) / (N_NULL + 1)

    # ── crossref index + hubs ──
    total_weight = {k: sum(nbr[k].values()) for k in keys}
    crossref = {}
    for k in keys:
        refs = nbr[k].most_common(TOPREF)
        crossref[f"{k[0]}:{k[1]}"] = [{"ayah": f"{b[0]}:{b[1]}", "weight": round(w, 3),
                                       "cross_sura": b[0] != k[0]} for b, w in refs]
    hubs = sorted(keys, key=lambda k: -total_weight[k])[:30]
    hub_list = [{"ayah": f"{k[0]}:{k[1]}", "total_connection_weight": round(total_weight[k], 2),
                 "n_connections": len(nbr[k])} for k in hubs]

    degs = sorted((len(nbr[k]) for k in keys), reverse=True)

    structure = {
        "method": "L7-global-1.0", "seed": SEED, "edge_roots_df_band": [DF_LO, DF_HI],
        "ayat": N, "weighted_pairs": len(pairs),
        "sura_coherence": {
            "question": "do connections concentrate within suras beyond chance?",
            "intra_sura_weight_fraction": round(real_intra, 4),
            "null_permuted_labels": {"mean": round(statistics.mean(null), 4),
                                     "sd": round(statistics.pstdev(null), 4),
                                     "max": round(max(null), 4)},
            "p": round(p_intra, 4),
            "verdict": "suras are coherent communities" if real_intra > max(null) else "no advantage",
        },
        "degree_distribution": {"max": degs[0], "median": degs[len(degs) // 2],
                                "mean": round(statistics.mean(degs), 1)},
        "hubs_most_connecting_verses": hub_list,
    }
    (out / "global_structure.json").write_text(json.dumps(structure, ensure_ascii=False, indent=1),
                                               encoding="utf-8")
    (out / "crossref_index.json").write_text(
        json.dumps({"method": "L7-global-1.0",
                    "note": "for each ayah, the verses that most explain it (rare-root idf-weighted)",
                    "index": crossref}, ensure_ascii=False, indent=1), encoding="utf-8")

    if not args.quiet:
        sc = structure["sura_coherence"]
        print("L7 — Global structure of the self-interpreting network\n")
        print(f"  ayat: {N}   weighted pairs: {len(pairs)}   "
              f"degree: max={degs[0]} median={degs[len(degs)//2]}")
        print(f"  SURA COHERENCE: intra-sura weight = {sc['intra_sura_weight_fraction']}  "
              f"null = {sc['null_permuted_labels']['mean']}±{sc['null_permuted_labels']['sd']} "
              f"(max {sc['null_permuted_labels']['max']})  p={sc['p']}  → {sc['verdict']}")
        print("\n  Most-connecting verses (hubs):")
        for h in hub_list[:6]:
            print(f"    {h['ayah']:>8}   weight={h['total_connection_weight']}  conns={h['n_connections']}")
        ex = next((a for a in ("2:255", "112:1", "1:2") if a in crossref), keys and f"{keys[0][0]}:{keys[0][1]}")
        print(f"\n  Example — verses that explain {ex}:")
        for r in crossref.get(ex, [])[:5]:
            tag = "cross-sura" if r["cross_sura"] else "same-sura"
            print(f"    {r['ayah']:>8}  (w={r['weight']}, {tag})")


if __name__ == "__main__":
    main()
