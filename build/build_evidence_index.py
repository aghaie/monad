#!/usr/bin/env python3
"""
build/build_evidence_index.py

Materializes the validated self-interpreting network into two artifacts the
engine serves:

  1. evidence_index.json — for EVERY ayah, the verses that most explain it
     (rare-root idf-weighted) AND the shared concept-roots that justify each
     link. Same method as scripts/build_L7_global.py + build_L8_interpret.py,
     extended to all 6236 ayat and enriched with shared roots per link.

  2. graph_communities.json — 114 suras as graph nodes with a deterministic
     force-directed layout, and the strongest inter-sura aggregate edges.

Deterministic (seeded), offline, no external semantics.
"""

import argparse
import json
import math
import random
import sqlite3
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DB_DEFAULT = REPO / "generated" / "monad.db"
EVID_OUT = REPO / "generated" / "layers" / "L8_interpret" / "evidence_index.json"
GRAPH_OUT = REPO / "generated" / "layers" / "L7_global" / "graph_communities.json"

ALLAH = "{ll~ah"
DF_LO, DF_HI = 3, 40
SEED = 11
TOPN = 12          # explainers kept per ayah (vs L7's 5) — same method, less truncation
TOP_EDGES = 400    # strongest inter-sura edges kept for the constellation
LAYOUT_ITERS = 400


def load_ayah_roots(db):
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    allah = con.execute("SELECT lemma_id FROM lemmas WHERE lemma_buckwalter=?", (ALLAH,)).fetchone()[0]
    root_bw = {r: b for r, b in con.execute("SELECT root_id,root_buckwalter FROM roots")}
    root_ar = {r: a for r, a in con.execute("SELECT root_id,root_arabic FROM roots")}
    suras = {n: (nm, c) for n, nm, c in
             con.execute("SELECT surah_number,name_arabic,ayah_count FROM surahs")}
    rows = con.execute("SELECT surah_number s,ayah_number a,pos,segment_type st,lemma_id,root_id "
                       "FROM morphology ORDER BY surah_number,ayah_number").fetchall()
    con.close()
    by = defaultdict(list)
    for r in rows:
        by[(r["s"], r["a"])].append(r)
    ayah_roots = {}
    for key, toks in by.items():
        ayah_roots[key] = {t["root_id"] for t in toks
                           if t["st"] == "STEM" and t["pos"] in ("N", "ADJ", "V")
                           and t["root_id"] is not None and t["lemma_id"] != allah}
    return ayah_roots, root_bw, root_ar, suras


def fr_layout(nodes, edges, seed, iters):
    """Compact deterministic Fruchterman-Reingold on a small node set."""
    rnd = random.Random(seed)
    pos = {n: [rnd.uniform(-1.0, 1.0), rnd.uniform(-1.0, 1.0)] for n in nodes}
    area = 1.0
    k = math.sqrt(area / max(1, len(nodes)))
    t = 0.1
    adj = [(e["source"], e["target"]) for e in edges]
    for _ in range(iters):
        disp = {n: [0.0, 0.0] for n in nodes}
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                a, b = nodes[i], nodes[j]
                dx = pos[a][0] - pos[b][0]
                dy = pos[a][1] - pos[b][1]
                dist = math.hypot(dx, dy) or 1e-4
                rep = (k * k) / dist
                ux, uy = dx / dist, dy / dist
                disp[a][0] += ux * rep; disp[a][1] += uy * rep
                disp[b][0] -= ux * rep; disp[b][1] -= uy * rep
        for a, b in adj:
            dx = pos[a][0] - pos[b][0]
            dy = pos[a][1] - pos[b][1]
            dist = math.hypot(dx, dy) or 1e-4
            att = (dist * dist) / k
            ux, uy = dx / dist, dy / dist
            disp[a][0] -= ux * att; disp[a][1] -= uy * att
            disp[b][0] += ux * att; disp[b][1] += uy * att
        for n in nodes:
            d = math.hypot(*disp[n]) or 1e-4
            pos[n][0] += (disp[n][0] / d) * min(d, t)
            pos[n][1] += (disp[n][1] / d) * min(d, t)
        t = max(t * 0.985, 0.001)
    return {n: [round(pos[n][0], 5), round(pos[n][1], 5)] for n in nodes}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(DB_DEFAULT))
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    ayah_roots, root_bw, root_ar, suras = load_ayah_roots(args.db)
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

    nbr = defaultdict(Counter)
    shared = defaultdict(lambda: defaultdict(list))
    inter = defaultdict(float)  # (sura_a, sura_b) with sura_a < sura_b
    for r in rare:
        wv = idf(r)
        ays = inv[r]
        for a, b in combinations(ays, 2):
            nbr[a][b] += wv; nbr[b][a] += wv
            shared[a][b].append(r); shared[b][a].append(r)
            if a[0] != b[0]:
                lo, hi = (a[0], b[0]) if a[0] < b[0] else (b[0], a[0])
                inter[(lo, hi)] += wv

    # evidence index — every ayah, even those with no explainers (empty list)
    index = {}
    for k in keys:
        refs = nbr[k].most_common(TOPN)
        index[f"{k[0]}:{k[1]}"] = [
            {"ayah": f"{b[0]}:{b[1]}", "weight": round(w, 3), "cross_sura": b[0] != k[0],
             "shared_roots": [{"root_id": r, "root_bw": root_bw[r], "root_ar": root_ar[r]}
                              for r in sorted(set(shared[k][b]))]}
            for b, w in refs]

    EVID_OUT.parent.mkdir(parents=True, exist_ok=True)
    EVID_OUT.write_text(json.dumps(
        {"method": "engine-evidence-1.0",
         "note": "for each ayah, verses that most explain it (rare-root idf-weighted) + shared concept-roots",
         "index": index}, ensure_ascii=False, indent=1), encoding="utf-8")

    # community graph — 114 sura nodes + strongest inter-sura edges + layout
    node_ids = sorted(suras)
    top_edges = sorted(inter.items(), key=lambda kv: -kv[1])[:TOP_EDGES]
    edges = [{"source": a, "target": b, "weight": round(w, 3)} for (a, b), w in top_edges]
    pos = fr_layout(node_ids, edges, SEED, LAYOUT_ITERS)
    nodes = [{"sura": s, "name_ar": suras[s][0], "ayah_count": suras[s][1],
              "x": pos[s][0], "y": pos[s][1]} for s in node_ids]

    GRAPH_OUT.parent.mkdir(parents=True, exist_ok=True)
    GRAPH_OUT.write_text(json.dumps(
        {"method": "engine-graph-1.0", "nodes": nodes, "edges": edges},
        ensure_ascii=False, indent=1), encoding="utf-8")

    if not args.quiet:
        nonempty = sum(1 for v in index.values() if v)
        print(f"evidence_index: {N} ayat ({nonempty} with explainers, {N - nonempty} abstaining)")
        print(f"graph_communities: {len(nodes)} suras, {len(edges)} edges")


if __name__ == "__main__":
    main()
