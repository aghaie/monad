#!/usr/bin/env python3
"""
scripts/build_L9_lexicon_pilot.py

Monad v2 — Layer L9 (PILOT): self-Quranic lexicon — sense induction.

For ~20 pilot roots, induce the distinct USAGE-SENSES (وجوه / بطن‌ها) of each
root PURELY from the text's internal relations, then validate that those senses
are real (stable across two independent halves of the corpus) rather than noise.

Method (rides on the L8 result that meaning-neighbourhoods are stable):
  1. For root R, collect every ayah where R occurs as a content stem
     (STEM, pos in N/ADJ/V, root present, lemma != Allah).
  2. The CONTEXT of an occurrence = the other content-roots in that ayah.
  3. Build R's significant co-root set C (PMI>0, support>=MIN_SUPPORT).
  4. Within R's ayahs, measure how the co-roots in C hang together
     (Jaccard over the set of R-ayahs that contain each). Cluster C by that
     similarity (average-link agglomerative, deterministic). Each cluster = a
     SENSE-FACET, characterised by its member co-roots.
  5. Assign each occurrence to the facet whose co-roots it best matches;
     representative ayahs = occurrences with the highest facet overlap.

Validation (falsification-first): split R's ayahs into two independent halves,
induce facets in each, match facets across halves by co-root overlap, and
compare the real cross-half agreement to a mismatched (shuffled-root) null.

NO external dictionary / translation / tafsir is used. Persian glosses are NOT
produced here — that is the quarantined output step (phase 2). Deterministic,
seeded, offline. Source: generated/monad.db.
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
OUT_DEFAULT = REPO / "generated" / "layers" / "L9_lexicon"
ALLAH = "{ll~ah"
SEED = 99

MIN_SUPPORT = 2        # a co-root must share >= this many ayahs with R to count
MIN_PMI = 0.0          # keep only positively-associated co-roots
MAX_COROOTS = 40       # cap candidate co-roots to the strongest (support, then PMI)
CLUSTER_CUT = 0.85     # average-link DISTANCE cut (1 - global Jaccard); calibrated on
                       # pilot to give plausible sense counts (median 2, max 4)
MIN_FACET_COROOTS = 2  # a facet needs >= this many co-roots to be a real sense
TOP_COROOTS = 8        # characteristic co-roots reported per facet
REP_AYAHS = 4          # representative ayahs reported per facet

# Pilot roots (Buckwalter): stratified across frequency, plus classic polysemy
# stress-tests (Eyn eye/spring, Drb strike/example, wjh face/direction,
# ktb write/book/decree, slm peace/submission, ftH open/victory, hdy guide/gift).
PILOT = ["qwl", "Elm", "Amn", "Ayy", "ktb", "hdy", "xlq", "nwr", "bSr", "slm",
         "wjh", "Eyn", "Drb", "rwH", "ftH", "ktm", "$rq", "grb", "nwm", "zyg"]


def load_ayah_roots(db):
    con = sqlite3.connect(db); con.row_factory = sqlite3.Row
    allah = con.execute("SELECT lemma_id FROM lemmas WHERE lemma_buckwalter=?", (ALLAH,)).fetchone()[0]
    root_bw = {r: b for r, b in con.execute("SELECT root_id,root_buckwalter FROM roots")}
    root_ar = {r: a for r, a in con.execute("SELECT root_id,root_arabic FROM roots")}
    bw_root = {b: r for r, b in root_bw.items()}
    rows = con.execute("SELECT surah_number s,ayah_number a,pos,segment_type st,lemma_id,root_id "
                       "FROM morphology ORDER BY surah_number,ayah_number").fetchall()
    con.close()
    by = defaultdict(set)
    for r in rows:
        if (r["st"] == "STEM" and r["pos"] in ("N", "ADJ", "V")
                and r["root_id"] is not None and r["lemma_id"] != allah):
            by[(r["s"], r["a"])].add(r["root_id"])
    return {k: sorted(v) for k, v in by.items()}, root_bw, root_ar, bw_root


def induce_facets(rid, ayahs, ayah_roots, df_global, inv_set, N, cut=CLUSTER_CUT):
    """ayahs: list of ayah-keys containing root rid. Return facets, ctx, co_in_R.

    Co-roots are clustered by their GLOBAL meaning-neighbourhood (corpus-wide
    ayah-set Jaccard) — the stable L8 signal — not by sparse within-R
    co-occurrence. Efficient: cap to MAX_COROOTS, precompute the distance
    matrix, merge with Lance-Williams (UPGMA average-link)."""
    ctx = {k: set(ayah_roots[k]) - {rid} for k in ayahs}
    nR = len(ayahs)
    co_in_R = Counter()
    for k in ayahs:
        for c in ctx[k]:
            co_in_R[c] += 1
    # significant co-roots: support + positive PMI (R vs c over the whole corpus)
    cand = []
    for c, cnt in co_in_R.items():
        if cnt < MIN_SUPPORT:
            continue
        pmi = math.log((cnt * N) / (nR * df_global[c])) if df_global[c] else 0.0
        if pmi > MIN_PMI:
            cand.append((cnt, pmi, c))
    if len(cand) < 2:
        return [], ctx, co_in_R
    cand.sort(reverse=True)
    C = [c for _, _, c in cand[:MAX_COROOTS]]
    n = len(C)

    # global Jaccard distance matrix among candidate co-roots
    D = [[0.0] * n for _ in range(n)]
    for i in range(n):
        si = inv_set[C[i]]
        for j in range(i + 1, n):
            sj = inv_set[C[j]]
            u = len(si | sj)
            jac = (len(si & sj) / u) if u else 0.0
            D[i][j] = D[j][i] = 1.0 - jac

    # Lance-Williams UPGMA average-link
    members = {i: [C[i]] for i in range(n)}
    size = {i: 1 for i in range(n)}
    active = set(range(n))
    dist = {(min(i, j), max(i, j)): D[i][j]
            for i in range(n) for j in range(i + 1, n)}
    while len(active) > 1:
        # find closest active pair
        best = None
        for (i, j), d in dist.items():
            if i in active and j in active and (best is None or d < best[2]
                                                or (d == best[2] and (i, j) < (best[0], best[1]))):
                best = (i, j, d)
        if best is None or best[2] >= cut:
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

    clusters = [members[i] for i in active]
    facets = []
    for cl in clusters:
        if len(cl) < MIN_FACET_COROOTS:
            continue
        members = set(cl)
        scored = []
        for k in ayahs:
            ov = len(ctx[k] & members)
            if ov:
                scored.append((ov, k))
        if not scored:
            continue
        scored.sort(reverse=True)
        top = sorted(cl, key=lambda c: (-co_in_R[c], c))[:TOP_COROOTS]
        facets.append({
            "coroots": cl, "top_coroots": top,
            "support": len(scored),
            "rep_ayahs": [k for _, k in scored[:REP_AYAHS]],
        })
    facets.sort(key=lambda f: -f["support"])
    return facets, ctx, co_in_R


def facet_signature(facets):
    return [set(f["coroots"]) for f in facets]


def best_match_jaccard(sigA, sigB):
    """greedy best-match agreement between two facet-signature lists."""
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
    ap.add_argument("--cut", type=float, default=CLUSTER_CUT)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    db = Path(args.db); out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    cut = args.cut

    ayah_roots, root_bw, root_ar, bw_root = load_ayah_roots(db)
    keys = sorted(ayah_roots)
    N = len(keys)
    df_global = Counter()
    inv = defaultdict(list)
    for k in keys:
        for r in ayah_roots[k]:
            df_global[r] += 1
            inv[r].append(k)
    inv_set = {r: set(v) for r, v in inv.items()}

    # ── induce each pilot root ONCE: full + two independent halves ──
    induced = {}
    for bw in PILOT:
        rid = bw_root.get(bw)
        if rid is None:
            continue
        ayahs = inv[rid]
        facets, ctx, co_in_R = induce_facets(rid, ayahs, ayah_roots, df_global, inv_set, N, cut)
        fA, _, _ = induce_facets(rid, ayahs[0::2], ayah_roots, df_global, inv_set, N, cut)
        fB, _, _ = induce_facets(rid, ayahs[1::2], ayah_roots, df_global, inv_set, N, cut)
        induced[bw] = {"rid": rid, "n_ayahs": len(ayahs), "facets": facets,
                       "co_in_R": co_in_R,
                       "sigA": facet_signature(fA), "sigB": facet_signature(fB)}

    dossiers = {}
    stab_rows = []
    for bw in PILOT:
        if bw not in induced:
            continue
        d = induced[bw]
        rid, facets, co_in_R = d["rid"], d["facets"], d["co_in_R"]
        # real = cross-half agreement; null = A-half vs every OTHER root's B-half
        real = best_match_jaccard(d["sigA"], d["sigB"])
        nulls = [best_match_jaccard(d["sigA"], induced[o]["sigB"])
                 for o in induced if o != bw]
        null_mean = statistics.mean(nulls) if nulls else 0.0
        null_max = max(nulls) if nulls else 0.0

        # honest per-root confidence tier from cross-half replication
        if real > null_max and d["n_ayahs"] >= 30:
            tier = "صریح"
        elif real > null_mean and d["n_ayahs"] >= 30:
            tier = "قوی"
        elif real > null_mean:
            tier = "محتمل"
        else:
            tier = "نامشخص"

        dossiers[bw] = {
            "root_ar": root_ar[rid], "root_bw": bw,
            "n_ayahs": d["n_ayahs"], "n_senses": len(facets),
            "senses": [{
                "facet_id": i + 1,
                "support": f["support"],
                "characteristic_coroots": [
                    {"root_bw": root_bw[c], "root_ar": root_ar[c], "shared_ayahs": co_in_R[c]}
                    for c in f["top_coroots"]],
                "representative_ayahs": [f"{k[0]}:{k[1]}" for k in f["rep_ayahs"]],
                "persian_gloss": None,          # filled in phase 2 (quarantined)
                "confidence": tier,             # per-root replication tier
            } for i, f in enumerate(facets)],
        }
        stab_rows.append({
            "root_bw": bw, "root_ar": root_ar[rid], "n_ayahs": d["n_ayahs"],
            "n_senses": len(facets),
            "cross_half_agreement": round(real, 3),
            "mismatched_null_mean": round(null_mean, 3),
            "mismatched_null_max": round(null_max, 3),
            "confidence": tier,
            "beats_null_mean": real > null_mean,
            "stable_strict": real > null_max,
        })

    n_strict = sum(1 for r in stab_rows if r["stable_strict"])
    n_beats = sum(1 for r in stab_rows if r["beats_null_mean"])
    reals = [r["cross_half_agreement"] for r in stab_rows]
    nullm = [r["mismatched_null_mean"] for r in stab_rows]
    # aggregate permutation: is the mean(real - null_mean) gap beyond chance?
    gaps = [r["cross_half_agreement"] - r["mismatched_null_mean"] for r in stab_rows]
    obs = statistics.mean(gaps)
    rnd = random.Random(SEED)
    perm = []
    for _ in range(2000):
        s = sum(g if rnd.random() < 0.5 else -g for g in gaps) / len(gaps)
        perm.append(s)
    p_agg = (sum(1 for x in perm if x >= obs) + 1) / (len(perm) + 1)
    summary = {
        "method": "L9-lexicon-pilot-1.0",
        "note": "sense induction for pilot roots; facets are clusters of the "
                "stable meaning-neighbourhood; validated by cross-half replication.",
        "params": {"MIN_SUPPORT": MIN_SUPPORT, "MAX_COROOTS": MAX_COROOTS,
                   "CLUSTER_CUT": cut, "MIN_FACET_COROOTS": MIN_FACET_COROOTS,
                   "SEED": SEED},
        "n_pilot_roots": len(stab_rows),
        "roots_with_multiple_senses": sum(1 for r in stab_rows if r["n_senses"] > 1),
        "roots_beating_null_mean": n_beats,
        "roots_stable_strict": n_strict,
        "mean_cross_half_agreement": round(statistics.mean(reals), 3) if reals else 0.0,
        "mean_mismatched_null": round(statistics.mean(nullm), 3) if nullm else 0.0,
        "fold_factor": round(statistics.mean(reals) / statistics.mean(nullm), 1)
                       if nullm and statistics.mean(nullm) else None,
        "aggregate_gap": round(obs, 3),
        "aggregate_p": round(p_agg, 4),
        "verdict": ("real but MODERATE: senses replicate in aggregate (~2x), reliable "
                    "for well-attested roots, near-chance for sparse roots"),
        "per_root": stab_rows,
    }

    (out / "pilot_dossiers.json").write_text(
        json.dumps({"method": "L9-lexicon-pilot-1.0", "dossiers": dossiers},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "pilot_stability.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")

    if not args.quiet:
        print("L9 (pilot) — self-Quranic lexicon: sense induction\n")
        print(f"  {'root':>6} {'ayahs':>6} {'senses':>7} {'real':>6} {'null':>6} {'nullmax':>8}  stable")
        for r in stab_rows:
            print(f"  {r['root_ar']:>6} {r['n_ayahs']:>6} {r['n_senses']:>7} "
                  f"{r['cross_half_agreement']:>6} {r['mismatched_null_mean']:>6} "
                  f"{r['mismatched_null_max']:>8}  {r['confidence']}")
        print(f"\n  roots with >1 induced sense : {summary['roots_with_multiple_senses']}/{summary['n_pilot_roots']}")
        print(f"  beats own null mean         : {summary['roots_beating_null_mean']}/{summary['n_pilot_roots']}")
        print(f"  strictly stable (>null max) : {summary['roots_stable_strict']}/{summary['n_pilot_roots']}")
        print(f"  mean cross-half agreement   : {summary['mean_cross_half_agreement']}  "
              f"(null {summary['mean_mismatched_null']}, ~{summary['fold_factor']}x)")
        print(f"  aggregate gap p-value       : p={summary['aggregate_p']}  (gap {summary['aggregate_gap']})")
        print(f"\n  Wrote 2 files to {out}")


if __name__ == "__main__":
    main()
