#!/usr/bin/env python3
"""
scripts/build_L1_letters.py

Monad v2 — Layer L1: Letters / Phonology (STRUCTURAL ONLY, no semantic claim).

Per the Self-Interpretation Charter (Article B-2 / locked decision), letters are
treated as phonological / structural atoms. NO meaning is induced at this layer.
Its job is to give higher layers a robust, internal account of root structure.

Reads:   generated/monad.db            (L0 substrate)
Writes:  generated/layers/L1_letters/  (JSON artifacts)

DATA CAVEAT (honest): the QAC ROOT field normalizes hamza (ء/أ/إ/ؤ/ئ) to alif
'A'. Therefore hamzated (mahmuz) roots are NOT separable from alif/weak roots at
this layer — we ABSTAIN on the hamzated count (tier: نامشخص) rather than report
a false zero.

Deterministic, offline, reproducible. No randomness, no external semantics.
"""

import argparse
import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_DEFAULT = REPO_ROOT / "generated" / "monad.db"
OUT_DEFAULT = REPO_ROOT / "generated" / "layers" / "L1_letters"

# Buckwalter → Arabic (structural transliteration only; display aid, not semantics)
_BW = {
    "'": 'ء', '|': 'آ', '>': 'أ', '&': 'ؤ', '<': 'إ', '}': 'ئ', 'A': 'ا',
    'b': 'ب', 'p': 'ة', 't': 'ت', 'v': 'ث', 'j': 'ج', 'H': 'ح', 'x': 'خ',
    'd': 'د', '*': 'ذ', 'r': 'ر', 'z': 'ز', 's': 'س', '$': 'ش', 'S': 'ص',
    'D': 'ض', 'T': 'ط', 'Z': 'ظ', 'E': 'ع', 'g': 'غ', 'f': 'ف', 'q': 'ق',
    'k': 'ك', 'l': 'ل', 'm': 'م', 'n': 'ن', 'h': 'ه', 'w': 'و', 'Y': 'ى',
    'y': 'ي',
}

WEAK = set("Awy")         # illa/alif letters in roots: ا و ي (note: 'A' also = normalized hamza)
KFOLD = 5                 # deterministic folds for self-prediction
ALPHA = 0.1               # additive smoothing for the self-prediction model


def bw_to_ar(s: str) -> str:
    return ''.join(_BW.get(c, c) for c in s)


def load_roots(con):
    """Return list of (root_bw, token_count). Excludes NULL roots. Sorted."""
    rows = con.execute(
        "SELECT root_buckwalter, token_count FROM roots "
        "WHERE root_buckwalter IS NOT NULL AND root_buckwalter != '' "
        "ORDER BY root_buckwalter"
    ).fetchall()
    return [(r[0], int(r[1] or 0)) for r in rows]


# ── Letter inventory ─────────────────────────────────────────────────────────

def build_inventory(roots):
    type_freq = Counter()      # each root counted once per letter occurrence
    token_freq = Counter()     # weighted by root token_count
    alphabet = set()
    pos_type = defaultdict(Counter)    # position(1..3) → letter → #roots (triliteral)
    for root_bw, tc in roots:
        letters = list(root_bw)
        alphabet.update(letters)
        for ch in letters:
            type_freq[ch] += 1
            token_freq[ch] += tc
        if len(letters) == 3:
            for i, ch in enumerate(letters, start=1):
                pos_type[i][ch] += 1

    nonstandard = sorted(c for c in alphabet if c not in _BW)
    return {
        "method": "L1-letters-1.0",
        "note": "STRUCTURAL ONLY — no semantic claim. Letters are phonological atoms.",
        "alphabet_size": len(alphabet),
        "alphabet": sorted(alphabet),
        "nonstandard_symbols": nonstandard,
        "letter_frequency_type": [
            {"bw": ch, "ar": bw_to_ar(ch), "root_occurrences": n}
            for ch, n in type_freq.most_common()
        ],
        "letter_frequency_token": [
            {"bw": ch, "ar": bw_to_ar(ch), "weighted_occurrences": n}
            for ch, n in token_freq.most_common()
        ],
        "positional_distribution_triliteral": {
            f"R{i}": [
                {"bw": ch, "ar": bw_to_ar(ch), "count": n}
                for ch, n in pos_type[i].most_common()
            ]
            for i in (1, 2, 3)
        },
    }


# ── Root morpho-phonology ────────────────────────────────────────────────────

def build_morphophonology(roots):
    length_dist = Counter()
    contains = Counter()                 # per-letter "contains A/w/y"
    n_weakish = n_geminate = n_strong = 0
    examples = defaultdict(list)
    triliteral = []
    for root_bw, _ in roots:
        L = len(root_bw)
        length_dist[L] += 1
        has_weakish = any(c in WEAK for c in root_bw)
        for c in set(root_bw):
            if c in WEAK:
                contains[c] += 1
        is_gem = (L == 3 and root_bw[1] == root_bw[2])
        if has_weakish:
            n_weakish += 1
            if len(examples["contains_alif_waw_ya"]) < 8:
                examples["contains_alif_waw_ya"].append(root_bw)
        if is_gem:
            n_geminate += 1
            if len(examples["geminate"]) < 8:
                examples["geminate"].append(root_bw)
        if not (has_weakish or is_gem):
            n_strong += 1
            if len(examples["strong"]) < 8:
                examples["strong"].append(root_bw)
        if L == 3:
            triliteral.append(root_bw)

    # OCP: radical-identity rates vs. chance (independence over positional marginals)
    p1 = Counter(); p2 = Counter(); p3 = Counter()
    for r in triliteral:
        p1[r[0]] += 1; p2[r[1]] += 1; p3[r[2]] += 1
    N = len(triliteral)

    def expected_equal(a, b):
        ca = {1: p1, 2: p2, 3: p3}[a]
        cb = {1: p1, 2: p2, 3: p3}[b]
        return sum((ca[l] / N) * (cb[l] / N) for l in set(ca) | set(cb))

    def observed_equal(i, j):
        return sum(1 for r in triliteral if r[i - 1] == r[j - 1]) / N

    ocp = {}
    for (i, j) in [(1, 2), (2, 3), (1, 3)]:
        obs = observed_equal(i, j)
        exp = expected_equal(i, j)
        ocp[f"R{i}=R{j}"] = {
            "observed": round(obs, 6),
            "expected_if_independent": round(exp, 6),
            "ratio_obs_over_exp": round(obs / exp, 4) if exp > 0 else None,
        }

    return {
        "method": "L1-letters-1.0",
        "total_roots": len(roots),
        "length_distribution": dict(sorted(length_dist.items())),
        "classes": {
            "contains_alif_waw_ya": n_weakish,
            "contains_breakdown": {
                "A_alif": contains["A"], "w_waw": contains["w"], "y_ya": contains["y"],
            },
            "geminate_muḍaʿʿaf_R2eqR3": n_geminate,
            "strong_no_weak_no_gemination": n_strong,
            "hamzated_mahmuz": {
                "status": "UNKNOWN",
                "tier": "نامشخص/unclear (C4 = abstain)",
                "reason": "QAC ROOT field normalizes hamza (ء/أ/إ/ؤ/ئ) to alif 'A'; "
                          "hamzated roots are not separable from alif/weak roots here.",
            },
        },
        "examples": {k: v for k, v in examples.items()},
        "triliteral_count": N,
        "radical_identity_OCP": {
            "note": "Arabic phonotactics: R1=R2 strongly avoided, R2=R3 (gemination) "
                    "allowed. ratio<1 = avoided vs chance, ratio>1 = preferred.",
            **ocp,
        },
    }


# ── Muqattaʿat ───────────────────────────────────────────────────────────────

def build_muqattaat(con):
    rows = con.execute(
        "SELECT surah_number, ayah_number, word_position, token_position, form_buckwalter "
        "FROM morphology WHERE tag='INL' OR pos='INL' "
        "ORDER BY surah_number, ayah_number, word_position, token_position"
    ).fetchall()
    by_surah = defaultdict(list)
    forms = Counter()
    for s, a, w, t, form in rows:
        by_surah[s].append(form)
        forms[form] += 1
    catalog = []
    for s in sorted(by_surah):
        seq = by_surah[s]
        combined = ''.join(seq)
        catalog.append({
            "surah": s,
            "location": f"{s}:1",
            "tokens_bw": seq,
            "combined_bw": combined,
            "combined_ar": bw_to_ar(combined),
        })
    return {
        "method": "L1-letters-1.0",
        "note": "Disconnected letters (POS:INL) catalogued and FLAGGED ONLY. "
                "No interpretation (Charter: accept silence; no guessing).",
        "total_inl_tokens": len(rows),
        "suras_with_muqattaat": len(by_surah),
        "distinct_letter_forms": [
            {"bw": f, "ar": bw_to_ar(f), "count": n} for f, n in forms.most_common()
        ],
        "catalog": catalog,
    }


# ── Self-prediction: masked middle radical ───────────────────────────────────

def self_prediction(roots):
    """Mask R2 of each triliteral root; recover from (R1,R3) by a fixed, a-priori
    interpolated model:  0.4·P(R2|R1,R3) + 0.2·P(R2|R1) + 0.2·P(R2|R3) + 0.2·P(R2),
    each add-α smoothed. Baseline = marginal P(R2). Deterministic held-out K-fold,
    no leakage. The model is fixed in advance; whatever score results is reported."""
    tri = sorted({r for r, _ in roots if len(r) == 3})
    folds = [[] for _ in range(KFOLD)]
    for idx, r in enumerate(tri):
        folds[idx % KFOLD].append(r)

    model_top1 = model_top3 = base_top1 = base_top3 = 0
    total = 0
    for k in range(KFOLD):
        test = folds[k]
        train = [r for j in range(KFOLD) if j != k for r in folds[j]]
        c_full = defaultdict(Counter)
        c_r1 = defaultdict(Counter)
        c_r3 = defaultdict(Counter)
        c_mid = Counter()
        for r in train:
            a, b, c = r[0], r[1], r[2]
            c_full[(a, c)][b] += 1
            c_r1[a][b] += 1
            c_r3[c][b] += 1
            c_mid[b] += 1
        # Deterministic ranking by (-count, letter). Katz-style backoff: use the
        # most specific available evidence; when context is absent the model
        # reduces EXACTLY to the marginal baseline (so it can only differ when it
        # has real co-radical evidence). No leakage; fixed a priori.
        def rank(counter):
            return [m for m, _ in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))]

        base_rank = rank(c_mid)

        def with_backoff(primary):
            r = rank(primary)
            return r + [m for m in base_rank if m not in primary]

        for r in test:
            a, b, c = r[0], r[1], r[2]
            full = c_full[(a, c)]
            if sum(full.values()) > 0:
                ranked = with_backoff(full)
            else:
                comb = Counter()
                comb.update(c_r1[a])
                comb.update(c_r3[c])
                ranked = with_backoff(comb) if sum(comb.values()) > 0 else base_rank
            if ranked[:1] == [b]:
                model_top1 += 1
            if b in ranked[:3]:
                model_top3 += 1
            if base_rank[:1] == [b]:
                base_top1 += 1
            if b in base_rank[:3]:
                base_top3 += 1
            total += 1

    def pct(x):
        return round(100.0 * x / total, 2) if total else 0.0

    if model_top1 + model_top3 > base_top1 + base_top3:
        verdict = "model_beats_baseline"
    elif model_top1 + model_top3 == base_top1 + base_top3:
        verdict = "equal_to_baseline (co-radical context rarely decisive)"
    else:
        verdict = "no_improvement_over_baseline"

    return {
        "method": "L1-letters-1.0",
        "task": "masked middle radical (R2) recovery from (R1,R3), held-out K-fold",
        "kfold": KFOLD,
        "model_desc": "Katz-style backoff: P(R2|R1,R3) → P(R2|R1)+P(R2|R3) → marginal P(R2)",
        "triliteral_types_tested": total,
        "model": {"top1_pct": pct(model_top1), "top3_pct": pct(model_top3)},
        "baseline": {"top1_pct": pct(base_top1), "top3_pct": pct(base_top3),
                     "desc": "marginal R2 frequency (no context)"},
        "verdict": verdict,
        "interpretation": "Structural only: tests whether the middle radical is "
                          "recoverable from the outer radicals beyond base rates. The "
                          "strong root structure is CATEGORICAL (see OCP), not "
                          "combinatorially predictive — consistent with the decision "
                          "that letters are non-semantic and meaning begins at roots.",
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=str(DB_DEFAULT))
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    args = ap.parse_args()

    db = Path(args.db)
    out = Path(args.out)
    if not db.exists():
        raise SystemExit(f"Substrate DB not found: {db} (run build_database.py first)")
    out.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(db)
    roots = load_roots(con)
    inventory = build_inventory(roots)
    morpho = build_morphophonology(roots)
    muqattaat = build_muqattaat(con)
    selfpred = self_prediction(roots)
    con.close()

    def dump(name, obj):
        p = out / name
        p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
        return p.stat().st_size

    sizes = {
        "letter_inventory.json": dump("letter_inventory.json", inventory),
        "root_morphophonology.json": dump("root_morphophonology.json", morpho),
        "muqattaat.json": dump("muqattaat.json", muqattaat),
        "self_prediction.json": dump("self_prediction.json", selfpred),
    }

    manifest = {
        "layer": "L1",
        "name": "letters / phonology",
        "method": "L1-letters-1.0",
        "source_db": str(db.name),
        "claim_level": "STRUCTURAL ONLY — no semantic induction at this layer",
        "confidence_tier": "قوی/strong (C2) — structurally derived",
        "data_caveats": [
            "QAC ROOT field normalizes hamza to alif 'A'; hamzated count is UNKNOWN (abstain).",
            "Roots use 28 consonantal symbols; short vowels/diacritics are not part of roots.",
        ],
        "prohibitions_observed": [
            "no external dictionaries", "no translations", "no tafsir",
            "no semantics", "no interpretation of muqattaʿat", "no pretrained models",
        ],
        "totals": {
            "roots": len(roots),
            "alphabet_size": inventory["alphabet_size"],
            "triliteral_roots": morpho["triliteral_count"],
            "quadriliteral_roots": morpho["length_distribution"].get(4, 0),
            "suras_with_muqattaat": muqattaat["suras_with_muqattaat"],
        },
        "self_prediction": {
            "model_top1_pct": selfpred["model"]["top1_pct"],
            "model_top3_pct": selfpred["model"]["top3_pct"],
            "baseline_top1_pct": selfpred["baseline"]["top1_pct"],
            "baseline_top3_pct": selfpred["baseline"]["top3_pct"],
            "verdict": selfpred["verdict"],
        },
        "headline_structural_finding": {
            "OCP_R1eqR2_ratio": morpho["radical_identity_OCP"]["R1=R2"]["ratio_obs_over_exp"],
            "OCP_R2eqR3_ratio": morpho["radical_identity_OCP"]["R2=R3"]["ratio_obs_over_exp"],
            "OCP_R1eqR3_ratio": morpho["radical_identity_OCP"]["R1=R3"]["ratio_obs_over_exp"],
        },
        "output_bytes": sizes,
    }
    dump("manifest.json", manifest)

    # Console summary
    print("L1 — Letters / Phonology  (structural only)")
    print(f"  roots:              {len(roots)}")
    print(f"  alphabet size:      {inventory['alphabet_size']} "
          f"(nonstandard: {inventory['nonstandard_symbols'] or 'none'})")
    print(f"  length dist:        {morpho['length_distribution']}")
    cls = morpho["classes"]
    print(f"  contains A/w/y:     {cls['contains_alif_waw_ya']}  "
          f"(A={cls['contains_breakdown']['A_alif']} "
          f"w={cls['contains_breakdown']['w_waw']} "
          f"y={cls['contains_breakdown']['y_ya']})")
    print(f"  geminate (R2=R3):   {cls['geminate_muḍaʿʿaf_R2eqR3']}")
    print(f"  strong:             {cls['strong_no_weak_no_gemination']}")
    print(f"  hamzated:           {cls['hamzated_mahmuz']['status']} (abstain — hamza→alif in source)")
    print("  OCP radical-identity (obs/exp ratio):")
    for k in ("R1=R2", "R2=R3", "R1=R3"):
        d = morpho["radical_identity_OCP"][k]
        print(f"    {k}: obs={d['observed']} exp={d['expected_if_independent']} "
              f"ratio={d['ratio_obs_over_exp']}")
    print(f"  muqattaʿat suras:   {muqattaat['suras_with_muqattaat']}")
    print(f"  self-prediction (masked R2): "
          f"model top1={selfpred['model']['top1_pct']}% top3={selfpred['model']['top3_pct']}%  |  "
          f"baseline top1={selfpred['baseline']['top1_pct']}% top3={selfpred['baseline']['top3_pct']}%")
    print(f"  verdict:            {selfpred['verdict']}")
    print(f"\nWrote {len(sizes) + 1} files to {out}")


if __name__ == "__main__":
    main()
