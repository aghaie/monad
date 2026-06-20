#!/usr/bin/env python3
"""
scripts/build_L2_names.py

Monad v2 — Layer L2: Divine Names / Anchors (الأسماء).

The keystone. Discovers, PURELY INTERNALLY, the attributes predicated of God and
establishes them as the semantic anchor axes. No external name list is used
(the traditional al-asmāʾ al-ḥusnā is quarantined for the L8 scorecard only).

Discovery combines three internal, documented signals (no syntactic treebank is
available in QAC v0.4, so perfect extraction is impossible — we therefore RANK
candidates, assign confidence tiers, and flag known confounds honestly rather
than assert a closed list):

  1. predicate-of-Allah : STEM ADJ/N, INDEF, NOM|ACC, within 5 words after an
                          "Allah" token, counted over distinct ayat   (seed)
  2. name-community     : names sit adjacent to other names (عزيزٌ حكيم); a
                          candidate is reinforced by the seed of its pair-partners
  3. predicate-dominance: a true name is PREDOMINANTLY used as a divine predicate
                          (high seed / total-frequency ratio); common nouns
                          (شيء، عذاب) are not.

  name_score = seed × avg_partner_seed × (seed / frequency)

Then: each discovered name's co-occurring content roots (PPMI) form its anchor
signature; a held-out self-prediction tests the central thesis — does an ayah's
CONTENT predict which divine name seals it?

Reads:  generated/monad.db        Writes: generated/layers/L2_names/
Deterministic, offline, reproducible. No external semantics.
"""

import argparse
import json
import math
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_DEFAULT = REPO_ROOT / "generated" / "monad.db"
OUT_DEFAULT = REPO_ROOT / "generated" / "layers" / "L2_names"

ALLAH_LEMMA_BW = "{ll~ah"
WIN = 5                 # predicate window after an Allah token (words)
SEED_MIN = 3            # minimum predicate-of-Allah ayat to enter the candidate pool
KFOLD = 5
# Tier thresholds (documented; calibrated for sensible separation, reported as-is)
QAWI_SEED_MIN = 5
QAWI_RATIO_MIN = 0.30      # seed / frequency (predicate-dominance)
# avg_partner_seed cut placed at the natural gap observed in the data: genuine
# names cluster at >=14 (they pair with other strong names); rare fixed-collocation
# confounds (قرض 'loan', ثمن 'price') sit at <=9.3. 12 separates them cleanly.
QAWI_PARTNERSEED_MIN = 12.0


def load_ayah_tokens(con):
    rows = con.execute(
        "SELECT surah_number s, ayah_number a, word_position wp, token_position tp, "
        "pos, segment_type st, state, case_feature cf, lemma_id, root_id "
        "FROM morphology ORDER BY surah_number, ayah_number, word_position, token_position"
    ).fetchall()
    ayat = defaultdict(list)
    for r in rows:
        ayat[(r["s"], r["a"])].append(r)
    return ayat


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=str(DB_DEFAULT))
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    db = Path(args.db); out = Path(args.out)
    if not db.exists():
        raise SystemExit(f"Substrate DB not found: {db}")
    out.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(db); con.row_factory = sqlite3.Row
    allah_lid = con.execute("SELECT lemma_id FROM lemmas WHERE lemma_buckwalter=?",
                            (ALLAH_LEMMA_BW,)).fetchone()[0]
    lem_bw = {lid: bw for lid, bw in con.execute("SELECT lemma_id,lemma_buckwalter FROM lemmas")}
    lem_ar = {lid: ar for lid, ar in con.execute("SELECT lemma_id,lemma_arabic FROM lemmas")}
    root_bw = {rid: bw for rid, bw in con.execute("SELECT root_id,root_buckwalter FROM roots")}
    root_ar = {rid: ar for rid, ar in con.execute("SELECT root_id,root_arabic FROM roots")}
    ayat = load_ayah_tokens(con)
    con.close()

    # ── Signal 1: predicate-of-Allah seed + total ADJ/N frequency per lemma ──
    seed = Counter()          # lemma -> distinct ayat in predicate-of-Allah position
    freq = Counter()          # lemma -> total STEM ADJ/N occurrences (denominator)
    for key, toks in ayat.items():
        awps = [t["wp"] for t in toks if t["lemma_id"] == allah_lid]
        seen = set()
        for t in toks:
            if t["st"] == "STEM" and t["pos"] in ("ADJ", "N") and t["lemma_id"] is not None:
                freq[t["lemma_id"]] += 1
                if (t["lemma_id"] != allah_lid and t["state"] == "INDEF"
                        and t["cf"] in ("NOM", "ACC") and awps
                        and any(0 < t["wp"] - w <= WIN for w in awps)):
                    seen.add(t["lemma_id"])
        for lid in seen:
            seed[lid] += 1

    pool = {lid for lid, c in seed.items() if c >= SEED_MIN}

    # ── Signal 2: adjacency pairing graph (restricted to pool) ──
    edge = defaultdict(Counter)   # x -> y -> # distinct ayat adjacent
    for key, toks in ayat.items():
        stems = sorted([t for t in toks if t["st"] == "STEM" and t["pos"] in ("ADJ", "N")],
                       key=lambda t: (t["wp"], t["tp"]))
        seen_pairs = set()
        for i in range(len(stems) - 1):
            x, y = stems[i]["lemma_id"], stems[i + 1]["lemma_id"]
            if (stems[i + 1]["wp"] - stems[i]["wp"] == 1 and x in pool and y in pool
                    and x != y and (x, y) not in seen_pairs):
                seen_pairs.add((x, y))
                edge[x][y] += 1
                edge[y][x] += 1

    def avg_partner_seed(x):
        ws = edge[x]
        tot = sum(ws.values())
        if tot == 0:
            return 0.0
        return sum(w * seed[y] for y, w in ws.items()) / tot

    # ── name_score = seed × avg_partner_seed × (seed / frequency) ──
    scored = []
    for lid in pool:
        ratio = seed[lid] / freq[lid] if freq[lid] else 0.0
        aps = avg_partner_seed(lid)
        score = seed[lid] * aps * ratio
        tier = ("قوی/strong"
                if (seed[lid] >= QAWI_SEED_MIN and ratio >= QAWI_RATIO_MIN
                    and aps >= QAWI_PARTNERSEED_MIN)
                else "محتمل/probable")
        scored.append({
            "lemma_bw": lem_bw[lid], "lemma_ar": lem_ar[lid], "lemma_id": lid,
            "seed_predicate_of_allah": seed[lid], "frequency": freq[lid],
            "predicate_ratio": round(ratio, 3),
            "avg_partner_seed": round(aps, 2),
            "pair_partners": len(edge[lid]),
            "name_score": round(score, 2), "tier": tier,
            "partners_bw": [lem_bw[y] for y, _ in edge[lid].most_common(8)],
        })
    scored.sort(key=lambda d: -d["name_score"])
    qawi = [d for d in scored if d["tier"].startswith("قوی")]
    qawi_ids = {d["lemma_id"] for d in qawi}

    # ── Anchor signatures: co-occurring content roots (PPMI) per قوی name ──
    # ayah-level co-occurrence between a name lemma and content roots.
    name_ayat = defaultdict(set)      # lemma -> set of ayah keys
    root_ayat = defaultdict(set)      # root_id -> set of ayah keys
    name_root = defaultdict(Counter)  # lemma -> root -> co-occur ayat
    total_ayat = len(ayat)
    for key, toks in ayat.items():
        names_here = {t["lemma_id"] for t in toks
                      if t["st"] == "STEM" and t["lemma_id"] in qawi_ids}
        roots_here = {t["root_id"] for t in toks
                      if t["st"] == "STEM" and t["pos"] in ("N", "ADJ", "V")
                      and t["root_id"] is not None and t["lemma_id"] != allah_lid
                      and t["lemma_id"] not in qawi_ids}
        for n in names_here:
            name_ayat[n].add(key)
        for r in roots_here:
            root_ayat[r].add(key)
        for n in names_here:
            for r in roots_here:
                name_root[n][r] += 1

    def ppmi(n, r):
        co = name_root[n][r]
        if co == 0:
            return 0.0
        p_co = co / total_ayat
        p_n = len(name_ayat[n]) / total_ayat
        p_r = len(root_ayat[r]) / total_ayat
        val = math.log(p_co / (p_n * p_r)) if p_n * p_r > 0 else 0.0
        return max(0.0, val)

    # Min co-occurrence cutoff: PPMI over-rewards single accidental co-occurrences
    # (hapax roots), so signatures require a root to co-occur with the name >= 3
    # times before it can be a characteristic anchor dimension.
    MIN_COOC_SIG = 3
    signatures = {}
    for d in qawi:
        n = d["lemma_id"]
        roots_scored = sorted(
            ((r, name_root[n][r], round(ppmi(n, r), 4))
             for r in name_root[n] if name_root[n][r] >= MIN_COOC_SIG),
            key=lambda t: (-t[2], -t[1]))[:15]
        signatures[d["lemma_bw"]] = {
            "lemma_ar": lem_ar[n],
            "ayat": len(name_ayat[n]),
            "top_roots": [{"root_bw": root_bw.get(r, "?"), "root_ar": root_ar.get(r, ""),
                           "cooc": c, "ppmi": v} for r, c, v in roots_scored],
        }

    # ── Self-prediction (THE THESIS TEST): predict the sealing name from ayah content ──
    # sealed instances: (ayah_key, name_lemma) where a قوی name is in the last 3 words.
    instances = []
    for key, toks in ayat.items():
        mw = max(t["wp"] for t in toks)
        content = tuple(sorted({t["root_id"] for t in toks
                                if t["st"] == "STEM" and t["pos"] in ("N", "ADJ", "V")
                                and t["root_id"] is not None}))
        for t in toks:
            if (t["st"] == "STEM" and t["lemma_id"] in qawi_ids and t["wp"] >= mw - 2):
                instances.append((key, t["lemma_id"], content))
    instances.sort(key=lambda x: (x[0], x[1]))

    folds = [[] for _ in range(KFOLD)]
    for i, inst in enumerate(instances):
        folds[i % KFOLD].append(inst)

    name_list = sorted(qawi_ids)
    m_top1 = m_top3 = b_top1 = b_top3 = tot = 0
    for k in range(KFOLD):
        test = folds[k]
        train = [x for j in range(KFOLD) if j != k for x in folds[j]]
        # train PPMI(name, root) and name frequency from training instances
        nr = defaultdict(Counter); n_cnt = Counter(); r_cnt = Counter(); T = len(train)
        for _, nm, content in train:
            n_cnt[nm] += 1
            for r in content:
                nr[nm][r] += 1; r_cnt[r] += 1
        def tr_ppmi(nm, r):
            co = nr[nm][r]
            if co == 0 or T == 0:
                return 0.0
            v = math.log((co / T) / ((n_cnt[nm] / T) * (r_cnt[r] / T))) if r_cnt[r] else 0.0
            return max(0.0, v)
        base_rank = [nm for nm, _ in n_cnt.most_common()]
        for _, true_nm, content in test:
            scores = []
            for nm in name_list:
                s = sum(tr_ppmi(nm, r) for r in content if nm != r)
                scores.append((-s, nm))
            scores.sort()
            ranked = [nm for _, nm in scores]
            if ranked[:1] == [true_nm]:
                m_top1 += 1
            if true_nm in ranked[:3]:
                m_top3 += 1
            if base_rank[:1] == [true_nm]:
                b_top1 += 1
            if true_nm in base_rank[:3]:
                b_top3 += 1
            tot += 1

    def pct(x):
        return round(100.0 * x / tot, 2) if tot else 0.0

    n_candidates = len(name_list)
    rand_top1 = round(100.0 / n_candidates, 2) if n_candidates else 0.0
    selfpred = {
        "method": "L2-names-1.0",
        "task": "predict the divine name sealing an ayah from the ayah's content roots",
        "kfold": KFOLD, "sealed_instances": tot,
        "candidate_names": n_candidates, "random_floor_top1_pct": rand_top1,
        "model": {"top1_pct": pct(m_top1), "top3_pct": pct(m_top3),
                  "desc": "argmax over names of Σ PPMI(name, content-root), held-out"},
        "baseline": {"top1_pct": pct(b_top1), "top3_pct": pct(b_top3),
                     "desc": "most frequent name"},
        "verdict": ("model_beats_baseline" if (m_top1 > b_top1 and m_top3 >= b_top3)
                    else "no_improvement_over_baseline"),
        "thesis_note": "H1 (names cohere with content) is supported iff the model beats "
                       "baseline AND random; reported honestly either way.",
    }

    # ── Write outputs ──
    def dump(name, obj):
        p = out / name
        p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
        return p.stat().st_size

    discovered = {
        "method": "L2-names-1.0",
        "discovery_signals": ["predicate-of-Allah (INDEF NOM/ACC, window 5)",
                              "name-community pairing", "predicate-dominance ratio"],
        "thresholds": {"seed_min": SEED_MIN, "window": WIN, "qawi_seed_min": QAWI_SEED_MIN,
                       "qawi_ratio_min": QAWI_RATIO_MIN, "qawi_partnerseed_min": QAWI_PARTNERSEED_MIN},
        "caveat": "No syntactic treebank in QAC v0.4 → automatic name extraction has "
                  "irreducible noise (e.g. شيء in 'على كل شيء قدير'). Output is a RANKED "
                  "candidate set with confidence tiers, not a closed assertion. The "
                  "traditional 99-name list is NOT used (quarantined for L8).",
        "pool_size": len(pool),
        "qawi_count": len(qawi),
        "names_ranked": scored,
    }
    sizes = {
        "discovered_names.json": dump("discovered_names.json", discovered),
        "name_signatures.json": dump("name_signatures.json",
                                     {"method": "L2-names-1.0", "signatures": signatures}),
        "self_prediction.json": dump("self_prediction.json", selfpred),
    }
    manifest = {
        "layer": "L2", "name": "divine names / anchors", "method": "L2-names-1.0",
        "source_db": db.name,
        "claim_level": "anchor discovery — RANKED candidates with confidence tiers",
        "confidence_tiers": "صریح/قوی/محتمل/نامشخص",
        "prohibitions_observed": ["no external name list", "no dictionaries", "no tafsir",
                                  "no translations", "no pretrained models"],
        "totals": {"candidate_pool": len(pool), "qawi_names": len(qawi),
                   "sealed_instances": selfpred["sealed_instances"]},
        "self_prediction": {"model_top1_pct": selfpred["model"]["top1_pct"],
                            "model_top3_pct": selfpred["model"]["top3_pct"],
                            "baseline_top1_pct": selfpred["baseline"]["top1_pct"],
                            "baseline_top3_pct": selfpred["baseline"]["top3_pct"],
                            "random_floor_top1_pct": rand_top1,
                            "verdict": selfpred["verdict"]},
        "output_bytes": sizes,
    }
    dump("manifest.json", manifest)

    if not args.quiet:
        print("L2 — Divine Names / Anchors  (keystone)")
        print(f"  candidate pool (seed≥{SEED_MIN}): {len(pool)}")
        print(f"  قوی/strong names: {len(qawi)}")
        print(f"\n  {'lemma':12s}{'ar':9s}{'seed':>5}{'freq':>6}{'ratio':>7}{'partS':>7}{'score':>9}  tier")
        for d in scored[:34]:
            print(f"  {d['lemma_bw']:12s}{d['lemma_ar']:9s}{d['seed_predicate_of_allah']:>5}"
                  f"{d['frequency']:>6}{d['predicate_ratio']:>7}{d['avg_partner_seed']:>7}"
                  f"{d['name_score']:>9}  {d['tier']}")
        sp = selfpred
        print(f"\n  THESIS TEST — predict sealing name from ayah content ({sp['sealed_instances']} instances, "
              f"{n_candidates} names, random≈{rand_top1}%):")
        print(f"    model    top1={sp['model']['top1_pct']}%  top3={sp['model']['top3_pct']}%")
        print(f"    baseline top1={sp['baseline']['top1_pct']}%  top3={sp['baseline']['top3_pct']}%")
        print(f"    verdict: {sp['verdict']}")
        print(f"\n  Wrote {len(sizes)+1} files to {out}")


if __name__ == "__main__":
    main()
