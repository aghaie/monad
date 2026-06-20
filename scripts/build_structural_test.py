#!/usr/bin/env python3
"""
scripts/build_structural_test.py

Monad v2 — STRUCTURAL test of the name-coherence principle ("all concepts cohere
with the divine names"), giving the principle its fairest chance after the
distributional test failed. Structural, not distributional; frequency-matched
controls + permutation null throughout.

Two structural questions on the root co-occurrence network (which is real, per L3):

  COVERAGE  — does every concept lie near a name? For each non-name root, its
              strongest PPMI association to ANY of the 16 name-roots, compared to
              its strongest association to a frequency-matched RANDOM set of 16
              roots. If names cover the space better than random comparable words,
              the principle has structural support.

  CENTRALITY — are the 16 name-roots more central (weighted PageRank) in the
              meaning-network than frequency-matched random roots?

Reads: generated/monad.db + generated/layers/L2_names/discovered_names.json
Writes: generated/layers/structural_test/
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
DB = REPO / "generated" / "monad.db"
L2 = REPO / "generated" / "layers" / "L2_names" / "discovered_names.json"
OUT = REPO / "generated" / "layers" / "structural_test"
ALLAH = "{ll~ah"
MIN_COOC = 3
N_NULL = 300
SEED = 2024
DAMP = 0.85
PR_ITERS = 60
MIN_TOK = 3          # attested roots only


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--quiet", action="store_true"); args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    qawi = [d for d in json.loads(L2.read_text(encoding="utf-8"))["names_ranked"]
            if d["tier"].startswith("قوی")]
    name_lids = [d["lemma_id"] for d in qawi]

    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row
    allah = con.execute("SELECT lemma_id FROM lemmas WHERE lemma_buckwalter=?", (ALLAH,)).fetchone()[0]
    root_bw = {r: b for r, b in con.execute("SELECT root_id,root_buckwalter FROM roots")}
    tok = {r: c for r, c in con.execute("SELECT root_id,token_count FROM roots")}
    name_roots = set()
    for nid in name_lids:
        rr = con.execute("SELECT root_id FROM morphology WHERE lemma_id=? AND root_id IS NOT NULL "
                         "GROUP BY root_id ORDER BY COUNT(*) DESC LIMIT 1", (nid,)).fetchone()
        if rr:
            name_roots.add(rr[0])
    rows = con.execute("SELECT surah_number s,ayah_number a,pos,segment_type st,lemma_id,root_id "
                       "FROM morphology ORDER BY surah_number,ayah_number").fetchall()
    con.close()

    by = defaultdict(list)
    for r in rows:
        by[(r["s"], r["a"])].append(r)
    root_ay = Counter(); co = defaultdict(Counter); N = 0
    for key, toks in by.items():
        roots = sorted({t["root_id"] for t in toks
                        if t["st"] == "STEM" and t["pos"] in ("N", "ADJ", "V")
                        and t["root_id"] is not None and t["lemma_id"] != allah})
        if not roots:
            continue
        N += 1
        for r in roots:
            root_ay[r] += 1
        for i in range(len(roots)):
            for j in range(i + 1, len(roots)):
                co[roots[i]][roots[j]] += 1; co[roots[j]][roots[i]] += 1

    def ppmi(a, b):
        c = co[a][b]
        if c < MIN_COOC or not root_ay[a] or not root_ay[b]:
            return 0.0
        v = math.log((c * N) / (root_ay[a] * root_ay[b]))
        return v if v > 0 else 0.0

    name_roots = {r for r in name_roots if root_ay[r] > 0}
    attested = [r for r in root_ay if tok.get(r, 0) >= MIN_TOK]
    non_name = [r for r in attested if r not in name_roots]
    rnd = random.Random(SEED)

    # frequency-matched random set the same size as name_roots
    def matched_set():
        chosen = []
        used = set()
        for nr in name_roots:
            c = tok.get(nr, 1)
            band = [r for r in non_name if r not in used and 0.6 * c <= tok.get(r, 0) <= 1.6 * c]
            if not band:
                band = [r for r in non_name if r not in used]
            pick = rnd.choice(sorted(band))
            chosen.append(pick); used.add(pick)
        return chosen

    # ── COVERAGE ──
    def mean_coverage(name_like):
        nl = set(name_like)
        vals = []
        for r in non_name:
            if r in nl:
                continue
            vals.append(max((ppmi(r, n) for n in name_like), default=0.0))
        return statistics.mean(vals) if vals else 0.0

    real_cov = mean_coverage(name_roots)
    null_cov = [mean_coverage(matched_set()) for _ in range(N_NULL)]
    p_cov = (sum(1 for x in null_cov if x >= real_cov) + 1) / (N_NULL + 1)

    # ── CENTRALITY (weighted PageRank) ──
    nodes = [r for r in root_ay]
    w = defaultdict(dict); wsum = Counter()
    for a in nodes:
        for b, c in co[a].items():
            pm = ppmi(a, b)
            if pm > 0:
                w[a][b] = pm; wsum[a] += pm
    pr = {r: 1.0 / len(nodes) for r in nodes}
    for _ in range(PR_ITERS):
        nxt = {r: (1 - DAMP) / len(nodes) for r in nodes}
        dangling = 0.0
        for a in nodes:
            if wsum[a] == 0:
                dangling += pr[a]
        dshare = DAMP * dangling / len(nodes)
        for a in nodes:
            if wsum[a] == 0:
                continue
            share = DAMP * pr[a] / wsum[a]
            for b, pm in w[a].items():
                nxt[b] += share * pm
        for r in nodes:
            nxt[r] += dshare
        pr = nxt
    ranked = sorted(nodes, key=lambda r: pr[r])
    pct_rank = {r: i / (len(ranked) - 1) for i, r in enumerate(ranked)}

    def mean_centrality_pct(roots):
        return statistics.mean(pct_rank[r] for r in roots if r in pct_rank)

    real_cen = mean_centrality_pct(name_roots)
    null_cen = [mean_centrality_pct(matched_set()) for _ in range(N_NULL)]
    p_cen = (sum(1 for x in null_cen if x >= real_cen) + 1) / (N_NULL + 1)

    def stats(xs):
        return {"mean": round(statistics.mean(xs), 4), "sd": round(statistics.pstdev(xs), 4),
                "max": round(max(xs), 4)}

    result = {
        "method": "structural-test-1.0", "seed": SEED, "n_null": N_NULL,
        "name_roots": sorted(root_bw[r] for r in name_roots),
        "coverage": {
            "question": "is every concept nearer a name than a freq-matched random word-set?",
            "real_mean_max_ppmi": round(real_cov, 4), "null": stats(null_cov),
            "empirical_p": round(p_cov, 4),
            "verdict": "names cover better" if real_cov > max(null_cov) else "no structural advantage",
        },
        "centrality": {
            "question": "are name-roots more central than freq-matched random roots?",
            "real_mean_percentile": round(real_cen, 4), "null": stats(null_cen),
            "empirical_p": round(p_cen, 4),
            "verdict": "names more central" if real_cen > max(null_cen) else "no structural advantage",
        },
    }
    (out / "structural_test.json").write_text(json.dumps(result, ensure_ascii=False, indent=1),
                                              encoding="utf-8")

    if not args.quiet:
        cv = result["coverage"]; ce = result["centrality"]
        print("STRUCTURAL TEST of the name-coherence principle "
              f"({len(name_roots)} name-roots, freq-matched null ×{N_NULL})\n")
        print(f"  COVERAGE:   real={cv['real_mean_max_ppmi']}  "
              f"null={cv['null']['mean']}±{cv['null']['sd']} (max {cv['null']['max']})  "
              f"p={cv['empirical_p']}  → {cv['verdict']}")
        print(f"  CENTRALITY: real={ce['real_mean_percentile']}  "
              f"null={ce['null']['mean']}±{ce['null']['sd']} (max {ce['null']['max']})  "
              f"p={ce['empirical_p']}  → {ce['verdict']}")


if __name__ == "__main__":
    main()
