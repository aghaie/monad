#!/usr/bin/env python3
"""
scripts/build_L9_lexicon.py

Monad v2 — Layer L9 (FULL): the self-Quranic lexicon for ALL 1,642 roots.

Builds two artifacts, purely from the text's internal relations (no external
dictionary / translation / tafsir as input):

  1. root_dossiers.json — for every root: its stable meaning-neighbourhood
     (the validated L8 signal, ~10x), and — where they REPLICATE across two
     independent halves — its distinct usage-senses (وجوه/بطن) with a per-root
     confidence tier. Roots whose senses do not replicate (or are too sparse)
     get a single-neighbourhood dossier marked "finer senses: نامشخص".

  2. ayah_dossiers.json — for every ayah (6,236): its content roots (each
     linkable to a root dossier) and the cross-Quran verses that explain it
     (reused from L8_interpret/evidence_index.json).

Method for sense induction is the pilot-validated, distinctiveness-ranked
clustering (see docs/L9-lexicon-pilot-report.md): cluster a root's PMI-ranked
co-roots by their global meaning-neighbourhood; validate by cross-half
replication against a GLOBAL between-root null.

Persian glosses are NOT produced here — that is the quarantined output step.
Deterministic, seeded, offline. Source: generated/monad.db + L8 evidence.
"""

import argparse
import json
import math
import random
import statistics
import sqlite3
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DB_DEFAULT = REPO / "generated" / "monad.db"
L8_EVID = REPO / "generated" / "layers" / "L8_interpret" / "evidence_index.json"
OUT_DEFAULT = REPO / "generated" / "layers" / "L9_lexicon"
ALLAH = "{ll~ah"
SEED = 99

# pilot-validated parameters (docs/L9-lexicon-pilot-report.md)
MIN_SUPPORT = 2
MIN_PMI = 0.0
MAX_COROOTS = 40
CLUSTER_CUT = 0.85
MIN_FACET_COROOTS = 2
TOP_COROOTS = 8
REP_AYAHS = 4
NEIGHBOURHOOD_K = 10      # size of the stable L8 single-meaning neighbourhood
NULL_SAMPLES = 8000       # random between-root pairs for the global null


def load_ayah_roots(db):
    con = sqlite3.connect(db); con.row_factory = sqlite3.Row
    allah = con.execute("SELECT lemma_id FROM lemmas WHERE lemma_buckwalter=?", (ALLAH,)).fetchone()[0]
    root_bw = {r: b for r, b in con.execute("SELECT root_id,root_buckwalter FROM roots")}
    root_ar = {r: a for r, a in con.execute("SELECT root_id,root_arabic FROM roots")}
    rows = con.execute("SELECT surah_number s,ayah_number a,pos,segment_type st,lemma_id,root_id "
                       "FROM morphology ORDER BY surah_number,ayah_number").fetchall()
    con.close()
    by = defaultdict(set)
    for r in rows:
        if (r["st"] == "STEM" and r["pos"] in ("N", "ADJ", "V")
                and r["root_id"] is not None and r["lemma_id"] != allah):
            by[(r["s"], r["a"])].add(r["root_id"])
    con = sqlite3.connect(db)
    all_ayahs = [(s, a) for s, a in
                 con.execute("SELECT surah_number,ayah_number FROM ayahs "
                             "ORDER BY surah_number,ayah_number")]
    con.close()
    return {k: sorted(v) for k, v in by.items()}, root_bw, root_ar, all_ayahs


def induce_facets(rid, ayahs, ayah_roots, df_global, inv_set, N):
    """Distinctiveness-ranked sense induction (pilot-validated)."""
    ctx = {k: set(ayah_roots[k]) - {rid} for k in ayahs}
    nR = len(ayahs)
    if nR < 2:
        return [], Counter()
    co_in_R = Counter()
    for k in ayahs:
        for c in ctx[k]:
            co_in_R[c] += 1
    cand = []
    for c, cnt in co_in_R.items():
        if cnt < MIN_SUPPORT:
            continue
        pmi = math.log((cnt * N) / (nR * df_global[c])) if df_global[c] else 0.0
        if pmi > MIN_PMI:
            cand.append((pmi, cnt, c))
    if len(cand) < 2:
        return [], co_in_R
    cand.sort(reverse=True)
    C = [c for _, _, c in cand[:MAX_COROOTS]]
    pmi_of = {c: p for p, _, c in cand}
    n = len(C)

    D = [[0.0] * n for _ in range(n)]
    for i in range(n):
        si = inv_set[C[i]]
        for j in range(i + 1, n):
            sj = inv_set[C[j]]
            u = len(si | sj)
            jac = (len(si & sj) / u) if u else 0.0
            D[i][j] = D[j][i] = 1.0 - jac

    members = {i: [C[i]] for i in range(n)}
    size = {i: 1 for i in range(n)}
    active = set(range(n))
    dist = {(i, j): D[i][j] for i in range(n) for j in range(i + 1, n)}
    while len(active) > 1:
        best = None
        for (i, j), d in dist.items():
            if i in active and j in active and (best is None or d < best[2]
                                                or (d == best[2] and (i, j) < (best[0], best[1]))):
                best = (i, j, d)
        if best is None or best[2] >= CLUSTER_CUT:
            break
        i, j, _ = best
        ni, nj = size[i], size[j]
        for k in list(active):
            if k == i or k == j:
                continue
            dik = dist.get((min(i, k), max(i, k)), 1.0)
            djk = dist.get((min(j, k), max(j, k)), 1.0)
            dist[(min(i, k), max(i, k))] = (ni * dik + nj * djk) / (ni + nj)
        members[i] += members[j]
        size[i] = ni + nj
        active.discard(j)

    facets = []
    for idx in active:
        cl = members[idx]
        if len(cl) < MIN_FACET_COROOTS:
            continue
        mem = set(cl)
        scored = [(len(ctx[k] & mem), k) for k in ayahs if ctx[k] & mem]
        if not scored:
            continue
        scored.sort(reverse=True)
        top = sorted(cl, key=lambda c: (-pmi_of.get(c, 0.0), c))[:TOP_COROOTS]
        facets.append({"coroots": cl, "top_coroots": top,
                       "support": len(scored),
                       "rep_ayahs": [k for _, k in scored[:REP_AYAHS]]})
    facets.sort(key=lambda f: -f["support"])
    return facets, co_in_R


def signature(facets):
    return [set(f["coroots"]) for f in facets]


def match_agreement(sigA, sigB):
    if not sigA or not sigB:
        return 0.0
    used = set(); tot = 0.0
    for sa in sigA:
        best = 0.0; bj = -1
        for j, sb in enumerate(sigB):
            if j in used:
                continue
            u = len(sa | sb)
            jac = len(sa & sb) / u if u else 0.0
            if jac > best:
                best, bj = jac, j
        if bj >= 0:
            used.add(bj)
        tot += best
    return tot / len(sigA)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=str(DB_DEFAULT))
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    db = Path(args.db); out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    ayah_roots, root_bw, root_ar, all_ayahs = load_ayah_roots(db)
    keys = sorted(ayah_roots)
    N = len(keys)
    df_global = Counter()
    inv = defaultdict(list)
    for k in keys:
        for r in ayah_roots[k]:
            df_global[r] += 1
            inv[r].append(k)
    inv_set = {r: set(v) for r, v in inv.items()}
    all_roots = sorted(inv, key=lambda r: -len(inv[r]))

    # global co-occurrence neighbourhood (the stable L8 single meaning) per root
    co = defaultdict(Counter)
    for k in keys:
        rs = ayah_roots[k]
        for a, b in combinations(rs, 2):
            co[a][b] += 1; co[b][a] += 1

    def neighbourhood(r, min_co=2):
        scored = []
        for b, c in co[r].items():
            if c >= min_co and df_global[r] and df_global[b]:
                v = math.log((c * N) / (df_global[r] * df_global[b]))
                if v > 0:
                    scored.append((v, b))
        scored.sort(reverse=True)
        nb = [b for _, b in scored[:NEIGHBOURHOOD_K]]
        # coverage fallback for sparse roots whose co-roots never repeat
        if not nb and co[r]:
            nb = [b for _, b in sorted(((math.log((c * N) / (df_global[r] * df_global[b])), b)
                                        for b, c in co[r].items() if df_global[b]),
                                       reverse=True)[:NEIGHBOURHOOD_K]]
        return nb

    # ── induce every root once: full facets + two-half signatures ──
    if not args.quiet:
        print(f"L9 full — inducing senses for {len(all_roots)} roots …")
    induced = {}
    for n_done, rid in enumerate(all_roots):
        ayahs = inv[rid]
        facets, co_in_R = induce_facets(rid, ayahs, ayah_roots, df_global, inv_set, N)
        fA, _ = induce_facets(rid, ayahs[0::2], ayah_roots, df_global, inv_set, N)
        fB, _ = induce_facets(rid, ayahs[1::2], ayah_roots, df_global, inv_set, N)
        induced[rid] = {"facets": facets, "co_in_R": co_in_R,
                        "sigA": signature(fA), "sigB": signature(fB),
                        "real": match_agreement(signature(fA), signature(fB))}
        if not args.quiet and (n_done + 1) % 250 == 0:
            print(f"  … {n_done + 1}/{len(all_roots)}")

    # ── global between-root null: random A_i vs B_j (i != j) ──
    # restrict the pool to MULTI-FACET roots — the only ones that get tiered — so
    # degenerate single-facet 1.0 matches do not inflate the null percentiles.
    rnd = random.Random(SEED)
    pool = [rid for rid in all_roots
            if len(induced[rid]["sigA"]) >= 2 and len(induced[rid]["sigB"]) >= 2]
    null = []
    if len(pool) > 1:
        for _ in range(NULL_SAMPLES):
            a = rnd.choice(pool); b = rnd.choice(pool)
            if a != b:
                null.append(match_agreement(induced[a]["sigA"], induced[b]["sigB"]))
    null.sort()
    nn = len(null)

    def pct(p):
        if not null:
            return 1.0
        return null[min(nn - 1, int(p * nn))]
    p90, p95, p99 = pct(0.90), pct(0.95), pct(0.99)

    def emp_p(real):
        """empirical p-value: fraction of the between-root null >= real."""
        if not null:
            return 1.0
        # null is sorted ascending; count entries >= real
        lo, hi = 0, nn
        while lo < hi:
            mid = (lo + hi) // 2
            if null[mid] < real:
                lo = mid + 1
            else:
                hi = mid
        return (nn - lo + 1) / (nn + 1)

    def tier(rid):
        d = induced[rid]
        if not d["facets"] or len(d["facets"]) < 2:
            return "نامشخص"
        real = d["real"]; nay = len(inv[rid]); p = emp_p(real)
        if p < 0.01 and nay >= 30:
            return "صریح"
        if p < 0.05 and nay >= 15:
            return "قوی"
        if p < 0.10:
            return "محتمل"
        return "نامشخص"

    # ── root dossiers ──
    dossiers = {}
    tier_counts = Counter()
    for rid in all_roots:
        d = induced[rid]
        t = tier(rid)
        tier_counts[t] += 1
        emit_senses = t != "نامشخص"
        dossiers[root_bw[rid]] = {
            "root_ar": root_ar[rid], "n_ayahs": len(inv[rid]),
            "neighbourhood": [{"root_bw": root_bw[b], "root_ar": root_ar[b]}
                              for b in neighbourhood(rid)],
            "confidence": t,
            "cross_half_agreement": round(d["real"], 3),
            "replication_p": round(emp_p(d["real"]), 4) if len(d["facets"]) >= 2 else None,
            "n_senses": len(d["facets"]) if emit_senses else 0,
            "finer_senses": "resolved" if emit_senses else "نامشخص",
            "senses": ([{
                "facet_id": i + 1, "support": f["support"],
                "characteristic_coroots": [
                    {"root_bw": root_bw[c], "root_ar": root_ar[c],
                     "shared_ayahs": d["co_in_R"][c]} for c in f["top_coroots"]],
                "representative_ayahs": [f"{k[0]}:{k[1]}" for k in f["rep_ayahs"]],
                "persian_gloss": None,
            } for i, f in enumerate(d["facets"])] if emit_senses else []),
            "persian_gloss": None,
        }

    # ── ayah dossiers: roots + explaining verses (reuse L8 evidence) ──
    evid = {}
    if L8_EVID.exists():
        evid = json.loads(L8_EVID.read_text(encoding="utf-8")).get("index", {})
    ayah_dossiers = {}
    for k in all_ayahs:
        tag = f"{k[0]}:{k[1]}"
        roots_here = [{"root_bw": root_bw[r], "root_ar": root_ar[r]}
                      for r in ayah_roots.get(k, [])]
        ex = evid.get(tag, [])
        ayah_dossiers[tag] = {
            "roots": roots_here,
            "explaining_verses": [{"ayah": e["ayah"], "weight": e.get("weight"),
                                   "shared_roots": [s["root_ar"] for s in e.get("shared_roots", [])]}
                                  for e in ex[:8]],
        }

    summary = {
        "method": "L9-lexicon-1.0",
        "params": {"CLUSTER_CUT": CLUSTER_CUT, "MAX_COROOTS": MAX_COROOTS,
                   "MIN_SUPPORT": MIN_SUPPORT, "NEIGHBOURHOOD_K": NEIGHBOURHOOD_K,
                   "NULL_SAMPLES": NULL_SAMPLES, "SEED": SEED},
        "n_roots": len(all_roots), "n_ayahs": len(all_ayahs),
        "note_coverage": f"{len(all_roots)} roots occur as content stems (of "
                         f"{len(root_bw)} total); {len(all_ayahs) - len(keys)} ayahs "
                         "have no content root (e.g. مقطعات) and get an empty dossier.",
        "null_p90": round(p90, 3), "null_p95": round(p95, 3), "null_p99": round(p99, 3),
        "tier_counts": dict(tier_counts),
        "roots_with_resolved_senses": sum(v for t, v in tier_counts.items() if t != "نامشخص"),
        "ayahs_with_explaining_verses": sum(1 for a in ayah_dossiers.values() if a["explaining_verses"]),
        "note": "senses emitted only where they replicate across halves; otherwise "
                "single stable L8 neighbourhood with finer_senses=نامشخص. Persian "
                "glosses pending (quarantined output step).",
    }

    (out / "root_dossiers.json").write_text(
        json.dumps({"method": "L9-lexicon-1.0", "dossiers": dossiers},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "ayah_dossiers.json").write_text(
        json.dumps({"method": "L9-lexicon-1.0", "index": ayah_dossiers},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "lexicon_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")

    if not args.quiet:
        print(f"\n  roots: {summary['n_roots']}   ayahs: {summary['n_ayahs']}")
        print(f"  null percentiles: p90={summary['null_p90']} p95={summary['null_p95']} p99={summary['null_p99']}")
        print("  confidence tiers:")
        for t in ("صریح", "قوی", "محتمل", "نامشخص"):
            print(f"     {t}: {tier_counts.get(t, 0)}")
        print(f"  roots with resolved senses : {summary['roots_with_resolved_senses']}")
        print(f"  ayahs with explaining verses: {summary['ayahs_with_explaining_verses']}")
        print(f"\n  Wrote 3 files to {out}")


if __name__ == "__main__":
    main()
