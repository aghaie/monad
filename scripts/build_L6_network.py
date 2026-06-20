#!/usr/bin/env python3
"""
scripts/build_L6_network.py

Monad v2 — Layer L6: the Inter-ayah Network — the heart of the thesis
("the network of connections between all verses interprets itself").

The decisive, leakage-controlled test:
  Split each ayah's content roots into KEY and TARGET halves (deterministic).
  Find the ayah's top-K neighbours using ONLY the KEY roots (cross-sura, to rule
  out local proximity). Then ask: do those neighbours contain the TARGET roots
  (which were NOT used to find them) more than K RANDOM ayat do?

If yes — knowing half of a verse lets the network find other verses that supply
the other half — then verses genuinely explain one another, beyond frequency.
Reported for all target roots and, more strictly, for RARE target roots.

Source: generated/monad.db.  Deterministic (seeded), offline, no external semantics.
"""

import argparse
import json
import math
import random
import sqlite3
import statistics
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DB_DEFAULT = REPO / "generated" / "monad.db"
OUT_DEFAULT = REPO / "generated" / "layers" / "L6_network"
ALLAH = "{ll~ah"
K = 10                 # neighbours
RARE_DF = 20           # a target root is "rare" if it occurs in <= RARE_DF ayat
N_NULL = 200
SEED = 7


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
    root_bw = {r: b for r, b in con.execute("SELECT root_id,root_buckwalter FROM roots")}
    rows = con.execute("SELECT surah_number s,ayah_number a,pos,segment_type st,lemma_id,root_id "
                       "FROM morphology ORDER BY surah_number,ayah_number").fetchall()
    con.close()

    by = defaultdict(list)
    for r in rows:
        by[(r["s"], r["a"])].append(r)
    ayah_roots = {}
    for key, toks in by.items():
        rs = sorted({t["root_id"] for t in toks
                     if t["st"] == "STEM" and t["pos"] in ("N", "ADJ", "V")
                     and t["root_id"] is not None and t["lemma_id"] != allah})
        ayah_roots[key] = rs
    keys = [k for k in sorted(ayah_roots) if len(ayah_roots[k]) >= 4]
    N = len(ayah_roots)

    df = Counter()
    for k in ayah_roots:
        for r in ayah_roots[k]:
            df[r] += 1
    def w(r):
        return math.log(N / df[r]) if df[r] else 0.0

    # inverted index root -> ayat
    inv = defaultdict(list)
    for k in ayah_roots:
        for r in ayah_roots[k]:
            inv[r].append(k)

    # deterministic key/target split (by index parity over sorted roots)
    def split(k):
        rs = ayah_roots[k]
        key = [r for i, r in enumerate(rs) if i % 2 == 0]
        tgt = [r for i, r in enumerate(rs) if i % 2 == 1]
        return key, tgt

    def neighbours(k, key, cross_sura=True):
        score = Counter()
        ks = k[0]
        for r in key:
            for b in inv[r]:
                if b == k:
                    continue
                if cross_sura and b[0] == ks:
                    continue
                score[b] += w(r)
        return [b for b, _ in score.most_common(K)]

    def pool_roots(ayat):
        p = set()
        for b in ayat:
            p.update(ayah_roots[b])
        return p

    def hit(tgt, pool):
        if not tgt:
            return None, None
        allh = sum(1 for r in tgt if r in pool) / len(tgt)
        rare = [r for r in tgt if df[r] <= RARE_DF]
        rareh = (sum(1 for r in rare if r in pool) / len(rare)) if rare else None
        return allh, rareh

    rnd = random.Random(SEED)

    # REAL (network neighbours, cross-sura)
    all_hits = []; rare_hits = []; network = []
    for k in keys:
        key, tgt = split(k)
        nb = neighbours(k, key, cross_sura=True)
        if not nb:
            continue
        a, r = hit(tgt, pool_roots(nb))
        if a is not None:
            all_hits.append(a)
        if r is not None:
            rare_hits.append(r)
        if len(network) < 6000:
            network.append({"ayah": f"{k[0]}:{k[1]}",
                            "neighbours": [f"{b[0]}:{b[1]}" for b in nb[:3]]})
    real_all = statistics.mean(all_hits)
    real_rare = statistics.mean(rare_hits)

    # NULL (K random ayat), N_NULL configs
    def null_means():
        ah = []; rh = []
        pool_keys = keys
        for k in keys:
            _, tgt = split(k)
            rnd_ayat = rnd.sample(pool_keys, K)
            a, r = hit(tgt, pool_roots(rnd_ayat))
            if a is not None:
                ah.append(a)
            if r is not None:
                rh.append(r)
        return statistics.mean(ah), statistics.mean(rh)
    null_all = []; null_rare = []
    for _ in range(N_NULL):
        a, r = null_means()
        null_all.append(a); null_rare.append(r)

    def pval(real, null):
        return (sum(1 for x in null if x >= real) + 1) / (len(null) + 1)
    def stat(xs):
        return {"mean": round(statistics.mean(xs), 4), "sd": round(statistics.pstdev(xs), 4),
                "max": round(max(xs), 4)}

    result = {
        "method": "L6-network-1.0", "seed": SEED, "K": K, "rare_df_max": RARE_DF,
        "tested_ayat": len(all_hits),
        "all_target_roots": {"network_hit": round(real_all, 4), "random_null": stat(null_all),
                             "p": round(pval(real_all, null_all), 4),
                             "verdict": "network beats random" if real_all > max(null_all) else "no advantage"},
        "rare_target_roots": {"network_hit": round(real_rare, 4), "random_null": stat(null_rare),
                              "p": round(pval(real_rare, null_rare), 4),
                              "verdict": "network beats random" if real_rare > max(null_rare) else "no advantage"},
        "reading": "network_hit > random ⇒ verses found via half a verse supply the other half ⇒ "
                   "verses explain one another beyond frequency. The RARE-target result is the strict test.",
    }
    (out / "intertextual_test.json").write_text(json.dumps(result, ensure_ascii=False, indent=1),
                                                encoding="utf-8")
    (out / "ayah_network.json").write_text(
        json.dumps({"method": "L6-network-1.0", "note": "top cross-sura neighbours by rare-root overlap",
                    "connections": network}, ensure_ascii=False, indent=1), encoding="utf-8")

    if not args.quiet:
        ra = result["all_target_roots"]; rr = result["rare_target_roots"]
        print("L6 — Inter-ayah Network (the heart of the thesis)\n")
        print(f"  tested ayat: {len(all_hits)}   (split key/target, cross-sura neighbours, K={K})")
        print(f"  ALL target roots:  network={ra['network_hit']}  "
              f"random={ra['random_null']['mean']}±{ra['random_null']['sd']} "
              f"(max {ra['random_null']['max']})  p={ra['p']}  → {ra['verdict']}")
        print(f"  RARE target roots: network={rr['network_hit']}  "
              f"random={rr['random_null']['mean']}±{rr['random_null']['sd']} "
              f"(max {rr['random_null']['max']})  p={rr['p']}  → {rr['verdict']}")
        print("\n  (RARE-target result is the strict, decisive test.)")


if __name__ == "__main__":
    main()
