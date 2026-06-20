#!/usr/bin/env python3
"""
scripts/build_robustness.py

Monad v2 — Robustness / Falsification study on the L2 and L3 self-prediction
signals. Asks the hard question: are the effects REAL, or artifacts of method /
frequency? Three decisive tests (deterministic; fixed RNG → reproducible):

  A. L2 permutation null  — shuffle the (content → sealing-name) labels and
     re-run. If the true accuracy sits far above the null distribution, the
     content genuinely predicts the name (not a procedural artifact).
  B. L2 leakage test      — remove the sealing name's OWN root from the ayah
     content. If accuracy stays above baseline, the signal is not just the
     name's root leaking into its own context.
  C. L3 mismatched-context null — predict each masked root from a RANDOM other
     ayah's context. If the true (matched) context does much better, recovery
     is genuinely contextual.

Reads: generated/monad.db + generated/layers/L2_names/discovered_names.json
Writes: generated/layers/robustness/
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
OUT = REPO / "generated" / "layers" / "robustness"
ALLAH = "{ll~ah"
MIN_COOC = 3
KFOLD = 5
N_PERM_L2 = 50
N_PERM_L3 = 20
SEED = 12345


# ── L2 self-prediction (parametrised by label list, optional root to drop) ──
def l2_selfpred(instances, labels, name_list, drop_target_root=False):
    """instances: list of (content_frozenset, target_root). labels: aligned name ids."""
    idx = list(range(len(instances)))
    folds = [idx[i::KFOLD] for i in range(KFOLD)]
    top1 = tot = 0
    for k in range(KFOLD):
        test = folds[k]
        train = [i for j in range(KFOLD) if j != k for i in folds[j]]
        nr = defaultdict(Counter); n_cnt = Counter(); r_cnt = Counter(); T = len(train)
        for i in train:
            content, troot = instances[i]; nm = labels[i]
            c = content - {troot} if drop_target_root else content
            n_cnt[nm] += 1
            for r in c:
                nr[nm][r] += 1; r_cnt[r] += 1
        def ppmi(nm, r):
            co = nr[nm][r]
            if co == 0 or T == 0 or not r_cnt[r]:
                return 0.0
            v = math.log((co / T) / ((n_cnt[nm] / T) * (r_cnt[r] / T)))
            return v if v > 0 else 0.0
        for i in test:
            content, troot = instances[i]; true_nm = labels[i]
            c = content - {troot} if drop_target_root else content
            best = None; best_s = -1.0
            for nm in name_list:
                s = sum(ppmi(nm, r) for r in c)
                if s > best_s or (s == best_s and (best is None or nm < best)):
                    best_s = s; best = nm
            if best == true_nm:
                top1 += 1
            tot += 1
    return 100.0 * top1 / tot if tot else 0.0


# ── L3 masked-root recovery on a single split (parametrised by context pairing) ──
def l3_split(pairs, train_co, train_ray, Nt, context_perm=None):
    """pairs: list of (masked_root, context_tuple). context_perm: optional index
    permutation so masked_root i is predicted from context of pairs[perm[i]]."""
    top1 = tot = 0
    n = len(pairs)
    for i in range(n):
        true_r = pairs[i][0]
        ctx = pairs[context_perm[i]][1] if context_perm is not None else pairs[i][1]
        score = Counter()
        for c in ctx:
            a = train_ray[c]
            if a == 0:
                continue
            for cand, cc in train_co[c].items():
                if cc < MIN_COOC:
                    continue
                v = math.log((cc * Nt) / (a * train_ray[cand])) if train_ray[cand] else 0.0
                if v > 0:
                    score[cand] += v
        best = score.most_common(1)
        if best and best[0][0] == true_r:
            top1 += 1
        tot += 1
    return 100.0 * top1 / tot if tot else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT)); ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    qawi = [d for d in json.loads(L2.read_text(encoding="utf-8"))["names_ranked"]
            if d["tier"].startswith("قوی")]
    name_ids = [d["lemma_id"] for d in qawi]; name_set = set(name_ids)

    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row
    allah = con.execute("SELECT lemma_id FROM lemmas WHERE lemma_buckwalter=?", (ALLAH,)).fetchone()[0]
    name_root = {}
    for nid in name_ids:
        rr = con.execute("SELECT root_id FROM morphology WHERE lemma_id=? AND root_id IS NOT NULL "
                         "GROUP BY root_id ORDER BY COUNT(*) DESC LIMIT 1", (nid,)).fetchone()
        name_root[nid] = rr[0] if rr else None
    rows = con.execute("SELECT surah_number s,ayah_number a,word_position wp,pos,segment_type st,"
                       "lemma_id,root_id FROM morphology ORDER BY surah_number,ayah_number").fetchall()
    con.close()

    by = defaultdict(list)
    for r in rows:
        by[(r["s"], r["a"])].append(r)

    # L2 sealed instances
    l2_inst = []; l2_labels = []
    # L3 ayah content roots
    ayah_roots = {}
    for key, toks in by.items():
        mw = max(t["wp"] for t in toks)
        content = frozenset(t["root_id"] for t in toks
                            if t["st"] == "STEM" and t["pos"] in ("N", "ADJ", "V")
                            and t["root_id"] is not None and t["lemma_id"] != allah)
        ayah_roots[key] = tuple(sorted(content))
        for t in toks:
            if t["st"] == "STEM" and t["lemma_id"] in name_set and t["wp"] >= mw - 2:
                l2_inst.append((content, name_root[t["lemma_id"]]))
                l2_labels.append(t["lemma_id"])

    # ── Test A: L2 permutation null ──
    real_l2 = l2_selfpred(l2_inst, l2_labels, name_ids)
    rnd = random.Random(SEED)
    null_l2 = []
    for _ in range(N_PERM_L2):
        perm = l2_labels[:]; rnd.shuffle(perm)
        null_l2.append(l2_selfpred(l2_inst, perm, name_ids))
    p_l2 = (sum(1 for x in null_l2 if x >= real_l2) + 1) / (N_PERM_L2 + 1)

    # ── Test B: L2 leakage (drop target name's own root) ──
    leak_l2 = l2_selfpred(l2_inst, l2_labels, name_ids, drop_target_root=True)

    # ── Test C: L3 mismatched-context null (single deterministic split) ──
    pairs = []
    keys = sorted(ayah_roots)
    for ki, key in enumerate(keys):
        roots = ayah_roots[key]
        if not (2 <= len(roots) <= 15):
            continue
        for r in roots:
            pairs.append((r, tuple(x for x in roots if x != r), ki))
    test = [(r, c) for (r, c, ki) in pairs if ki % 5 == 0]
    train_keys = [keys[ki] for ki in {ki for (_, _, ki) in pairs if ki % 5 != 0}]
    train_co = defaultdict(Counter); train_ray = Counter(); Nt = 0
    for key in train_keys:
        roots = ayah_roots[key]; Nt += 1
        for r in roots:
            train_ray[r] += 1
        for i in range(len(roots)):
            for j in range(i + 1, len(roots)):
                train_co[roots[i]][roots[j]] += 1; train_co[roots[j]][roots[i]] += 1
    real_l3 = l3_split(test, train_co, train_ray, Nt)
    rnd3 = random.Random(SEED + 1)
    null_l3 = []
    for _ in range(N_PERM_L3):
        perm = list(range(len(test))); rnd3.shuffle(perm)
        null_l3.append(l3_split(test, train_co, train_ray, Nt, context_perm=perm))
    p_l3 = (sum(1 for x in null_l3 if x >= real_l3) + 1) / (N_PERM_L3 + 1)

    def stats(xs):
        return {"mean": round(statistics.mean(xs), 3), "sd": round(statistics.pstdev(xs), 3),
                "max": round(max(xs), 3), "min": round(min(xs), 3)}

    result = {
        "method": "robustness-1.0", "seed": SEED,
        "L2_permutation_null": {
            "real_top1_pct": round(real_l2, 3), "n_perm": N_PERM_L2,
            "null": stats(null_l2), "empirical_p": round(p_l2, 4),
            "verdict": "REAL (beats null)" if real_l2 > max(null_l2) else "NOT robust",
        },
        "L2_leakage_test": {
            "real_top1_pct": round(real_l2, 3),
            "without_name_own_root_top1_pct": round(leak_l2, 3),
            "drop_pct_points": round(real_l2 - leak_l2, 3),
            "note": "if accuracy survives removing the name's own root, it is not mere leakage",
        },
        "L3_mismatched_context_null": {
            "real_top1_pct": round(real_l3, 3), "n_perm": N_PERM_L3,
            "null": stats(null_l3), "empirical_p": round(p_l3, 4),
            "verdict": "REAL (context informative)" if real_l3 > max(null_l3) else "NOT robust",
        },
    }
    (out / "robustness.json").write_text(json.dumps(result, ensure_ascii=False, indent=1),
                                         encoding="utf-8")

    if not args.quiet:
        a = result["L2_permutation_null"]; b = result["L2_leakage_test"]; c = result["L3_mismatched_context_null"]
        print("Robustness / Falsification study\n")
        print(f"A. L2 permutation null: real={a['real_top1_pct']}%  "
              f"null={a['null']['mean']}±{a['null']['sd']}% (max {a['null']['max']}%)  "
              f"p={a['empirical_p']}  → {a['verdict']}")
        print(f"B. L2 leakage: real={b['real_top1_pct']}%  "
              f"without name's own root={b['without_name_own_root_top1_pct']}%  "
              f"(drop {b['drop_pct_points']} pts)")
        print(f"C. L3 mismatched-context null: real={c['real_top1_pct']}%  "
              f"null={c['null']['mean']}±{c['null']['sd']}% (max {c['null']['max']}%)  "
              f"p={c['empirical_p']}  → {c['verdict']}")


if __name__ == "__main__":
    main()
