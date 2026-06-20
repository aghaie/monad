#!/usr/bin/env python3
"""
scripts/build_L8_interpret.py

Monad v2 — Layer L8: Self-interpretation capstone.

Turns the validated self-interpreting network into two things:

  1. STABILITY test (the capstone falsification): are the self-derived concept
     definitions RELIABLE? Split the corpus into two independent halves; for each
     well-attested root, compute its top co-root associates in each half; measure
     how well they agree (Jaccard) vs the agreement between MISMATCHED roots. If a
     root's meaning-neighbourhood replicates across independent halves far above
     the mismatched baseline, the self-derived meanings are stable, not noise.

  2. SELF-TAFSIR demonstration: for notable verses, the verses across the Quran
     that explain them and the shared concept-roots that link them — the Quran
     interpreting itself, end to end.

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
OUT_DEFAULT = REPO / "generated" / "layers" / "L8_interpret"
ALLAH = "{ll~ah"
TOPK = 10
MIN_HALF = 5          # root must occur in >= this many ayat in EACH half
SEED = 99
DEMO_VERSES = ["1:2", "2:255", "112:1", "24:35", "96:1", "55:1", "36:1", "3:7", "17:1", "53:1"]


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
    root_ar = {r: a for r, a in con.execute("SELECT root_id,root_arabic FROM roots")}
    rows = con.execute("SELECT surah_number s,ayah_number a,pos,segment_type st,lemma_id,root_id "
                       "FROM morphology ORDER BY surah_number,ayah_number").fetchall()
    con.close()

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

    # ── STABILITY: two independent halves ──
    def half_assoc(half_keys):
        co = defaultdict(Counter); ray = Counter(); n = 0
        for k in half_keys:
            rs = ayah_roots[k]; n += 1
            for r in rs:
                ray[r] += 1
            for a, b in combinations(rs, 2):
                co[a][b] += 1; co[b][a] += 1
        def topk(r):
            scored = []
            for b, c in co[r].items():
                if c >= 2 and ray[r] and ray[b]:
                    v = math.log((c * n) / (ray[r] * ray[b]))
                    if v > 0:
                        scored.append((v, b))
            scored.sort(reverse=True)
            return [b for _, b in scored[:TOPK]], ray
        return topk, ray

    A = keys[0::2]; B = keys[1::2]
    topkA, rayA = half_assoc(A)
    topkB, rayB = half_assoc(B)
    tested = [r for r in root_bw if rayA[r] >= MIN_HALF and rayB[r] >= MIN_HALF]

    setsA = {r: set(topkA(r)[0]) for r in tested}
    setsB = {r: set(topkB(r)[0]) for r in tested}

    def jac(s1, s2):
        if not s1 and not s2:
            return 0.0
        u = len(s1 | s2)
        return len(s1 & s2) / u if u else 0.0

    real = [jac(setsA[r], setsB[r]) for r in tested if setsA[r] or setsB[r]]
    real_mean = statistics.mean(real) if real else 0.0
    rnd = random.Random(SEED)
    others = tested[:]
    null = []
    for r in tested:
        if not setsA[r]:
            continue
        r2 = rnd.choice(others)
        null.append(jac(setsA[r], setsB[r2]))
    null_mean = statistics.mean(null) if null else 0.0
    # permutation distribution of the null mean
    null_dist = []
    for _ in range(200):
        s = [jac(setsA[r], setsB[rnd.choice(others)]) for r in tested if setsA[r]]
        null_dist.append(statistics.mean(s))
    p = (sum(1 for x in null_dist if x >= real_mean) + 1) / (len(null_dist) + 1)

    stability = {
        "method": "L8-interpret-1.0", "topk": TOPK, "tested_roots": len(tested),
        "question": "do self-derived concept neighbourhoods replicate across two independent corpus halves?",
        "real_mean_jaccard": round(real_mean, 4),
        "mismatched_null_mean": round(statistics.mean(null_dist), 4),
        "null_max": round(max(null_dist), 4), "p": round(p, 4),
        "fold_factor": round(real_mean / null_mean, 1) if null_mean else None,
        "verdict": "concept definitions are STABLE" if real_mean > max(null_dist) else "not stable",
    }

    # ── SELF-TAFSIR demonstration ──
    df = Counter()
    for k in keys:
        for r in ayah_roots[k]:
            df[r] += 1
    rare = {r for r, d in df.items() if 3 <= d <= 40}
    inv = defaultdict(list)
    for k in keys:
        for r in ayah_roots[k]:
            if r in rare:
                inv[r].append(k)
    def idf(r):
        return math.log(N / df[r])

    def explain(key):
        score = Counter(); shared = defaultdict(list)
        for r in ayah_roots[key]:
            if r in rare:
                for b in inv[r]:
                    if b != key and b[0] != key[0]:
                        score[b] += idf(r); shared[b].append(r)
        out_links = []
        for b, w in score.most_common(3):
            out_links.append({"ayah": f"{b[0]}:{b[1]}", "weight": round(w, 3),
                              "shared_concepts": [{"root_bw": root_bw[r], "root_ar": root_ar[r]}
                                                  for r in shared[b]]})
        return out_links

    demos = {}
    for v in DEMO_VERSES:
        s, a = v.split(":"); key = (int(s), int(a))
        if key in ayah_roots:
            demos[v] = explain(key)

    (out / "stability.json").write_text(json.dumps(stability, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "self_tafsir_demo.json").write_text(
        json.dumps({"method": "L8-interpret-1.0",
                    "note": "for each verse, cross-sura verses that explain it + the shared concept-roots",
                    "demonstrations": demos}, ensure_ascii=False, indent=1), encoding="utf-8")

    if not args.quiet:
        st = stability
        print("L8 — Self-interpretation capstone\n")
        print(f"  STABILITY ({st['tested_roots']} roots, two independent halves):")
        print(f"    real cross-half agreement = {st['real_mean_jaccard']}  "
              f"mismatched null = {st['mismatched_null_mean']} (max {st['null_max']})  "
              f"p={st['p']}  → {st['verdict']}  (~{st['fold_factor']}x)")
        print("\n  SELF-TAFSIR examples (verse → cross-sura verses that explain it, via shared concepts):")
        for v in DEMO_VERSES:
            if v in demos and demos[v]:
                top = demos[v][0]
                cons = " ".join(c["root_ar"] for c in top["shared_concepts"][:4])
                print(f"    {v:>7} → {top['ayah']:>7}   (shared: {cons})")
        print(f"\n  Wrote 2 files to {out}")


if __name__ == "__main__":
    main()
