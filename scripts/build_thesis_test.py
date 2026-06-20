#!/usr/bin/env python3
"""
scripts/build_thesis_test.py

Monad v2 — The FAIR thesis test. Does ayah content cohere with the divine names
once ALL leakage is removed and we test at the right granularity (name family,
not exact name)?

Controls, built in from the start:
  * leakage-free content: every ayah's content roots EXCLUDE all 16 anchor-name
    roots (so a name can never be predicted from its own root or a sibling name's
    root).
  * families discovered internally and PER-FOLD (no test leakage): names are
    agglomeratively clustered by their leakage-free content signatures on the
    training split only.
  * held-out 5-fold; compared to honest baselines (most-frequent name / family).

Two metrics:
  exact   — predicted name == true sealing name
  family  — predicted name's family == true name's family

Reads: generated/monad.db + generated/layers/L2_names/discovered_names.json
Writes: generated/layers/thesis_test/
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
L2 = REPO / "generated" / "layers" / "L2_names" / "discovered_names.json"
OUT = REPO / "generated" / "layers" / "thesis_test"
ALLAH = "{ll~ah"
KFOLD = 5
KS = [3, 4, 5]          # family granularities to report


def cosine(a, b):
    if not a or not b:
        return 0.0
    dot = sum(a[k] * b.get(k, 0.0) for k in a)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def cluster(names, sig, k):
    """Deterministic agglomerative average-linkage clustering to k families."""
    clusters = [[n] for n in names]
    pair_cos = {}
    for a, b in combinations(names, 2):
        pair_cos[tuple(sorted((a, b)))] = cosine(sig[a], sig[b])

    def avg_link(ci, cj):
        vals = [pair_cos[tuple(sorted((a, b)))] for a in ci for b in cj]
        return sum(vals) / len(vals) if vals else 0.0

    while len(clusters) > k:
        best = None; best_v = -2.0
        for i, j in combinations(range(len(clusters)), 2):
            v = avg_link(clusters[i], clusters[j])
            key = (v, tuple(sorted(clusters[i])), tuple(sorted(clusters[j])))
            if v > best_v or (v == best_v and key < best):
                best_v = v; best = key; bi, bj = i, j
        merged = clusters[bi] + clusters[bj]
        clusters = [c for x, c in enumerate(clusters) if x not in (bi, bj)] + [merged]
    fam = {}
    for fid, c in enumerate(sorted(clusters, key=lambda c: sorted(c))):
        for n in c:
            fam[n] = fid
    return fam


def build_sig(instances, idxs, name_ids):
    """leakage-free name signature: PPMI(name, content-root) over given instances."""
    nr = defaultdict(Counter); n_cnt = Counter(); r_cnt = Counter(); T = len(idxs)
    for i in idxs:
        content, nm = instances[i]
        n_cnt[nm] += 1
        for r in content:
            nr[nm][r] += 1; r_cnt[r] += 1
    sig = {}
    for nm in name_ids:
        v = {}
        for r, co in nr[nm].items():
            if co >= 2 and r_cnt[r] and n_cnt[nm]:
                pm = math.log((co / T) / ((n_cnt[nm] / T) * (r_cnt[r] / T)))
                if pm > 0:
                    v[r] = pm
        sig[nm] = v
    return sig, nr, n_cnt, r_cnt, T


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--quiet", action="store_true"); args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    qawi = [d for d in json.loads(L2.read_text(encoding="utf-8"))["names_ranked"]
            if d["tier"].startswith("قوی")]
    name_ids = [d["lemma_id"] for d in qawi]
    name_bw = {d["lemma_id"]: d["lemma_bw"] for d in qawi}
    name_set = set(name_ids)

    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row
    allah = con.execute("SELECT lemma_id FROM lemmas WHERE lemma_buckwalter=?", (ALLAH,)).fetchone()[0]
    name_roots = set()
    for nid in name_ids:
        rr = con.execute("SELECT root_id FROM morphology WHERE lemma_id=? AND root_id IS NOT NULL "
                         "GROUP BY root_id ORDER BY COUNT(*) DESC LIMIT 1", (nid,)).fetchone()
        if rr:
            name_roots.add(rr[0])
    rows = con.execute("SELECT surah_number s,ayah_number a,word_position wp,pos,segment_type st,"
                       "lemma_id,root_id FROM morphology ORDER BY surah_number,ayah_number").fetchall()
    con.close()

    by = defaultdict(list)
    for r in rows:
        by[(r["s"], r["a"])].append(r)

    # leakage-free sealed instances
    instances = []
    for key, toks in by.items():
        mw = max(t["wp"] for t in toks)
        content = frozenset(t["root_id"] for t in toks
                            if t["st"] == "STEM" and t["pos"] in ("N", "ADJ", "V")
                            and t["root_id"] is not None and t["lemma_id"] != allah
                            and t["root_id"] not in name_roots)        # ← kill ALL name-root leakage
        for t in toks:
            if t["st"] == "STEM" and t["lemma_id"] in name_set and t["wp"] >= mw - 2:
                instances.append((content, t["lemma_id"]))
    folds = [list(range(len(instances)))[i::KFOLD] for i in range(KFOLD)]

    def ppmi_pred(nr, n_cnt, r_cnt, T, content):
        best = None; best_s = -1.0
        for nm in name_ids:
            s = 0.0
            for r in content:
                co = nr[nm][r]
                if co and r_cnt[r]:
                    v = math.log((co / T) / ((n_cnt[nm] / T) * (r_cnt[r] / T)))
                    if v > 0:
                        s += v
            if s > best_s or (s == best_s and (best is None or nm < best)):
                best_s = s; best = nm
        return best

    results = {}
    families_display = None
    for k in KS:
        exact_hit = fam_hit = base_exact = base_fam = tot = 0
        for fi in range(KFOLD):
            test = folds[fi]; train = [i for j in range(KFOLD) if j != fi for i in folds[j]]
            sig, nr, n_cnt, r_cnt, T = build_sig(instances, train, name_ids)
            fam = cluster(name_ids, sig, k)
            if k == 4 and fi == 0:
                families_display = defaultdict(list)
                for n, f in fam.items():
                    families_display[f].append(name_bw[n])
            top_name = n_cnt.most_common(1)[0][0]
            fam_counts = Counter(fam[nm] for i in train for nm in [instances[i][1]])
            top_fam = fam_counts.most_common(1)[0][0]
            for i in test:
                content, true_nm = instances[i]
                pred = ppmi_pred(nr, n_cnt, r_cnt, T, content)
                if pred == true_nm:
                    exact_hit += 1
                if pred is not None and fam[pred] == fam[true_nm]:
                    fam_hit += 1
                if top_name == true_nm:
                    base_exact += 1
                if top_fam == fam[true_nm]:
                    base_fam += 1
                tot += 1

        def pct(x):
            return round(100.0 * x / tot, 2)
        results[f"families_{k}"] = {
            "exact": {"model_top1_pct": pct(exact_hit), "baseline_pct": pct(base_exact)},
            "family": {"model_pct": pct(fam_hit), "baseline_pct": pct(base_fam),
                       "verdict": ("model_beats_baseline" if fam_hit > base_fam
                                   else "no_improvement")},
        }

    summary = {
        "method": "thesis-test-1.0",
        "question": "leakage-free: does ayah content cohere with the divine name FAMILY that seals it?",
        "controls": ["ALL 16 name-roots removed from content (zero leakage)",
                     "families clustered per-fold on training only",
                     "held-out 5-fold", "honest baselines"],
        "sealed_instances": len(instances),
        "example_families_k4_fold0": {str(f): ns for f, ns in (families_display or {}).items()},
        "results": results,
    }
    (out / "thesis_test.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1),
                                          encoding="utf-8")

    if not args.quiet:
        print("FAIR THESIS TEST — leakage-free, family-level\n")
        print(f"  sealed instances: {len(instances)}   (all 16 name-roots removed from content)")
        if families_display:
            print("  example families (k=4):")
            for f, ns in sorted(families_display.items()):
                print(f"    F{f}: {' '.join(ns)}")
        print(f"\n  {'granularity':14s}{'exact model/base':>20}{'FAMILY model/base':>22}  verdict")
        for k in KS:
            r = results[f"families_{k}"]
            e = r["exact"]; fa = r["family"]
            print(f"  {k} families   {e['model_top1_pct']:>7}/{e['baseline_pct']:<6} "
                  f"   {fa['model_pct']:>8}/{fa['baseline_pct']:<7}  {fa['verdict']}")


if __name__ == "__main__":
    main()
