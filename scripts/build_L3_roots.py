#!/usr/bin/env python3
"""
scripts/build_L3_roots.py

Monad v2 — Layer L3: Self-grounded Root Lexicon in Name-Coordinates (الجذور).

The first FULL meaning layer. For every root, "meaning" is represented entirely
by internal relations (no external gloss):

  * name_coordinates — the root's PPMI association with each of the L2 anchor
                       names (its position in the divine-name space; the law of
                       interpretation made numeric).
  * relational_neighbors — top roots it co-occurs with (PPMI).
  * field_neighbors    — roots with the most similar name-profile (cosine):
                       the root's semantic field, grounded in the names.
  * defining_ayat      — provenance: ayat that most tie the root to its top name.
  * tier               — صریح/قوی/محتمل/نامشخص by attestation (abstain when sparse).

Validation: masked-root recovery — can the network recover a hidden root from its
ayah context? (self-interpretation at the root level), held-out, vs baseline.

Source data (permitted): generated/monad.db (L0), generated/layers/L2_names/.
Writes: generated/layers/L3_roots/.  Deterministic, offline, no external semantics.
"""

import argparse
import json
import math
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DB_DEFAULT = REPO / "generated" / "monad.db"
L2_DEFAULT = REPO / "generated" / "layers" / "L2_names" / "discovered_names.json"
OUT_DEFAULT = REPO / "generated" / "layers" / "L3_roots"

ALLAH_LEMMA_BW = "{ll~ah"
MIN_COOC = 3            # PPMI hapax cutoff (learned in L2)
TIER_STRONG = 10       # token_count >= 10 → قوی meaning representation
TIER_PROB = 3          # 3..9 → محتمل ; <3 → نامشخص (abstain)
KFOLD = 5
TOP_NEIGH = 10
TOP_FIELD = 6


def ppmi(co, a_ay, b_ay, N):
    if co < MIN_COOC or a_ay == 0 or b_ay == 0:
        return 0.0
    v = math.log((co * N) / (a_ay * b_ay))
    return v if v > 0 else 0.0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=str(DB_DEFAULT))
    ap.add_argument("--l2", default=str(L2_DEFAULT))
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    db = Path(args.db); out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    # L2 anchor names (permitted source data)
    l2 = json.loads(Path(args.l2).read_text(encoding="utf-8"))
    qawi = [d for d in l2["names_ranked"] if d["tier"].startswith("قوی")]
    name_ids = [d["lemma_id"] for d in qawi]
    name_bw = {d["lemma_id"]: d["lemma_bw"] for d in qawi}
    name_ar = {d["lemma_id"]: d["lemma_ar"] for d in qawi}
    name_set = set(name_ids)

    con = sqlite3.connect(db); con.row_factory = sqlite3.Row
    allah_lid = con.execute("SELECT lemma_id FROM lemmas WHERE lemma_buckwalter=?",
                            (ALLAH_LEMMA_BW,)).fetchone()[0]
    root_bw = {r: b for r, b in con.execute("SELECT root_id,root_buckwalter FROM roots")}
    root_ar = {r: a for r, a in con.execute("SELECT root_id,root_arabic FROM roots")}
    tok_count = {r: c for r, c in con.execute("SELECT root_id,token_count FROM roots")}
    rows = con.execute(
        "SELECT surah_number s, ayah_number a, pos, segment_type st, lemma_id, root_id "
        "FROM morphology ORDER BY surah_number, ayah_number"
    ).fetchall()
    con.close()

    # Per-ayah: content roots, and which anchor names are present
    ayah_roots = {}          # key -> sorted tuple of content root_ids
    ayah_names = {}          # key -> set of name lemma_ids present
    by = defaultdict(list)
    for r in rows:
        by[(r["s"], r["a"])].append(r)
    for key, toks in by.items():
        roots = sorted({t["root_id"] for t in toks
                        if t["st"] == "STEM" and t["pos"] in ("N", "ADJ", "V")
                        and t["root_id"] is not None and t["lemma_id"] != allah_lid})
        names = {t["lemma_id"] for t in toks
                 if t["st"] == "STEM" and t["lemma_id"] in name_set}
        ayah_roots[key] = tuple(roots)
        ayah_names[key] = names
    N = len(ayah_roots)

    # Co-occurrence: root-name, root-root, ayah counts
    root_ay = Counter()
    name_ay = Counter()
    root_name_co = defaultdict(Counter)
    root_root_co = defaultdict(Counter)
    rootname_ayat = defaultdict(lambda: defaultdict(list))   # root -> name -> [ayah keys]
    for key in ayah_roots:
        roots = ayah_roots[key]
        names = ayah_names[key]
        for r in roots:
            root_ay[r] += 1
        for n in names:
            name_ay[n] += 1
        for r in roots:
            for n in names:
                root_name_co[r][n] += 1
                rootname_ayat[r][n].append(key)
        for i in range(len(roots)):
            for j in range(i + 1, len(roots)):
                root_root_co[roots[i]][roots[j]] += 1
                root_root_co[roots[j]][roots[i]] += 1

    def tier_of(r):
        c = tok_count.get(r, 0)
        if c >= TIER_STRONG:
            return "قوی/strong"
        if c >= TIER_PROB:
            return "محتمل/probable"
        return "نامشخص/abstain"

    # ── Build name-coordinate vectors ──
    name_vec = {}            # root -> {name_id: ppmi}
    for r in root_ay:
        vec = {}
        for n in name_ids:
            v = ppmi(root_name_co[r][n], root_ay[r], name_ay[n], N)
            if v > 0:
                vec[n] = v
        name_vec[r] = vec

    # ── Field neighbors: cosine over name-vectors (attested roots only) ──
    attested = [r for r in root_ay if tok_count.get(r, 0) >= TIER_PROB and name_vec[r]]
    norm = {r: math.sqrt(sum(v * v for v in name_vec[r].values())) for r in attested}
    field_neighbors = defaultdict(list)
    for i, r in enumerate(sorted(attested)):
        vr = name_vec[r]
        if not vr:
            continue
        sims = []
        for r2 in attested:
            if r2 == r:
                continue
            v2 = name_vec[r2]
            dot = sum(vr[n] * v2.get(n, 0.0) for n in vr)
            if dot <= 0:
                continue
            sims.append((dot / (norm[r] * norm[r2]), r2))
        sims.sort(key=lambda t: (-t[0], root_bw.get(t[1], "")))
        field_neighbors[r] = sims[:TOP_FIELD]

    # ── Assemble lexicon ──
    lexicon = {}
    tier_counts = Counter()
    for r in sorted(root_ay, key=lambda r: root_bw.get(r, "")):
        if root_bw.get(r) is None:
            continue
        tier = tier_of(r); tier_counts[tier] += 1
        # name coordinates (sorted desc)
        coords = sorted(((name_bw[n], name_ar[n], round(v, 4))
                         for n, v in name_vec[r].items()), key=lambda t: -t[2])
        # relational neighbors
        neigh = sorted(((r2, ppmi(c, root_ay[r], root_ay[r2], N))
                        for r2, c in root_root_co[r].items()),
                       key=lambda t: -t[1])
        neigh = [(root_bw.get(r2, "?"), root_ar.get(r2, ""), round(v, 4))
                 for r2, v in neigh if v > 0][:TOP_NEIGH]
        # defining ayat: ayat tying root to its top name
        defining = []
        if coords:
            top_n = next(n for n in name_vec[r] if name_bw[n] == coords[0][0])
            for key in rootname_ayat[r][top_n][:3]:
                defining.append(f"{key[0]}:{key[1]}")
        fld = [{"root_bw": root_bw.get(r2, "?"), "root_ar": root_ar.get(r2, ""),
                "cosine": round(s, 4)} for s, r2 in field_neighbors.get(r, [])]
        lexicon[root_bw[r]] = {
            "root_ar": root_ar.get(r, ""),
            "token_count": tok_count.get(r, 0),
            "tier": tier,
            "name_coordinates": [{"name_bw": a, "name_ar": b, "ppmi": v} for a, b, v in coords],
            "relational_neighbors": [{"root_bw": a, "root_ar": b, "ppmi": v} for a, b, v in neigh],
            "field_neighbors": fld,
            "defining_ayat": defining,
        }

    # ── Self-prediction: masked-root recovery from ayah context (held-out) ──
    instances = []   # (ayah_key, masked_root, context_tuple)
    for key in sorted(ayah_roots):
        roots = ayah_roots[key]
        if not (2 <= len(roots) <= 15):
            continue
        for r in roots:
            instances.append((key, r, tuple(x for x in roots if x != r)))
    folds = [[] for _ in range(KFOLD)]
    for i, inst in enumerate(instances):
        folds[i % KFOLD].append(inst)

    m1 = m3 = b1 = b3 = tot = 0
    for k in range(KFOLD):
        test = folds[k]
        train_keys = {inst[0] for j in range(KFOLD) if j != k for inst in folds[j]}
        co = defaultdict(Counter); ray = Counter(); Nt = 0
        for key in train_keys:
            roots = ayah_roots[key]; Nt += 1
            for r in roots:
                ray[r] += 1
            for i in range(len(roots)):
                for j in range(i + 1, len(roots)):
                    co[roots[i]][roots[j]] += 1
                    co[roots[j]][roots[i]] += 1
        base_rank = [r for r, _ in ray.most_common(3)]
        for key, true_r, ctx in test:
            score = Counter()
            for c in ctx:
                a_ay = ray[c]
                if a_ay == 0:
                    continue
                for cand, cc in co[c].items():
                    if cc < MIN_COOC:
                        continue
                    v = math.log((cc * Nt) / (a_ay * ray[cand])) if ray[cand] else 0.0
                    if v > 0:
                        score[cand] += v
            ranked = [r for r, _ in score.most_common(3)]
            if ranked[:1] == [true_r]:
                m1 += 1
            if true_r in ranked[:3]:
                m3 += 1
            if base_rank[:1] == [true_r]:
                b1 += 1
            if true_r in base_rank[:3]:
                b3 += 1
            tot += 1

    def pct(x):
        return round(100.0 * x / tot, 2) if tot else 0.0
    n_roots = len([r for r in root_ay if root_bw.get(r)])
    selfpred = {
        "method": "L3-roots-1.0",
        "task": "masked content-root recovery from ayah context (root-root PPMI), held-out 5-fold",
        "instances": tot, "candidate_roots": n_roots,
        "random_floor_top1_pct": round(100.0 / n_roots, 3),
        "model": {"top1_pct": pct(m1), "top3_pct": pct(m3)},
        "baseline": {"top1_pct": pct(b1), "top3_pct": pct(b3), "desc": "most frequent root"},
        "verdict": ("model_beats_baseline" if (m1 > b1 and m3 >= b3)
                    else "no_improvement_over_baseline"),
    }

    # ── Write ──
    def dump(name, obj):
        p = out / name
        p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
        return p.stat().st_size

    sizes = {
        "root_lexicon.json": dump("root_lexicon.json",
                                  {"method": "L3-roots-1.0", "anchor_names": [name_bw[n] for n in name_ids],
                                   "min_cooc": MIN_COOC, "roots": lexicon}),
        "self_prediction.json": dump("self_prediction.json", selfpred),
    }
    manifest = {
        "layer": "L3", "name": "self-grounded root lexicon (name-coordinates)",
        "method": "L3-roots-1.0", "source": [db.name, "L2_names/discovered_names.json"],
        "claim_level": "first full meaning layer — meaning = internal relations + name-coordinates",
        "confidence_tiers": dict(tier_counts),
        "anchor_names": [name_bw[n] for n in name_ids],
        "prohibitions_observed": ["no external glosses", "no dictionaries", "no tafsir",
                                  "no translations", "no pretrained models"],
        "totals": {"roots": n_roots, "attested_roots": len(attested)},
        "self_prediction": {"model_top1_pct": selfpred["model"]["top1_pct"],
                            "model_top3_pct": selfpred["model"]["top3_pct"],
                            "baseline_top1_pct": selfpred["baseline"]["top1_pct"],
                            "baseline_top3_pct": selfpred["baseline"]["top3_pct"],
                            "random_floor_top1_pct": selfpred["random_floor_top1_pct"],
                            "verdict": selfpred["verdict"]},
        "output_bytes": sizes,
    }
    dump("manifest.json", manifest)

    if not args.quiet:
        print("L3 — Self-grounded Root Lexicon (name-coordinates)")
        print(f"  roots: {n_roots}   attested(>= {TIER_PROB}): {len(attested)}")
        print(f"  tiers: {dict(tier_counts)}")
        print(f"  anchor names: {len(name_ids)}  ({' '.join(name_bw[n] for n in name_ids)})")
        sp = selfpred
        print(f"\n  SELF-PREDICTION — masked root from context ({sp['instances']} instances, "
              f"{n_roots} roots, random≈{sp['random_floor_top1_pct']}%):")
        print(f"    model    top1={sp['model']['top1_pct']}%  top3={sp['model']['top3_pct']}%")
        print(f"    baseline top1={sp['baseline']['top1_pct']}%  top3={sp['baseline']['top3_pct']}%")
        print(f"    verdict: {sp['verdict']}")
        # show a couple example lexicon entries
        for rb in ("rHm", "Elm", "ktb"):
            if rb in lexicon:
                e = lexicon[rb]
                nc = ", ".join(f"{c['name_ar']}({c['ppmi']})" for c in e["name_coordinates"][:4])
                print(f"\n  {rb} ({e['root_ar']}, tier={e['tier']}): name-coords → {nc or '—'}")
        print(f"\n  Wrote {len(sizes)+1} files to {out}")


if __name__ == "__main__":
    main()
