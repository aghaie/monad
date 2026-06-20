#!/usr/bin/env python3
"""
scripts/build_L4_words.py

Monad v2 — Layer L4: Word / Form meaning on the RELATIONAL network.

Built on the empirically-grounded foundation (Charter Article B-3): meaning is
relational. Question: does morphological FORM (pattern/wazn, derivation, voice,
participle) carry meaning beyond the bare root?

Leakage control is structural, by design: the self-prediction test predicts WHICH
LEMMA of a root is used from context, with the root held FIXED (so the root can
never be the cue). Two context instruments are compared, in fairness:
  * ayah-bag   — all other content roots in the ayah (coarse)
  * local ±4   — roots within 4 word positions (the right instrument for form/sense)
If either disambiguates the form above the most-frequent-form baseline, word-forms
carry contextual meaning beyond the root.

Deliverables: word_lexicon.json, pattern_stats.json, self_prediction.json.
Source: generated/monad.db. Deterministic, offline, no external semantics.
"""

import argparse
import json
import math
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DB_DEFAULT = REPO / "generated" / "monad.db"
OUT_DEFAULT = REPO / "generated" / "layers" / "L4_words"
ALLAH = "{ll~ah"
MIN_COOC = 3
KFOLD = 5
WINDOW = 4
TIER_STRONG = 10
TIER_PROB = 3
VERB_FORMS = ["VIII", "VII", "III", "IX", "VI", "IV", "II", "V", "X", "I"]


def pattern_desc(features_raw, pos):
    parts = set(features_raw.split("|"))
    form = next((f for f in VERB_FORMS if f"({f})" in features_raw), None)
    if "PCPL" in parts and "ACT" in parts:
        base = "ACT-PCPL"
    elif "PCPL" in parts and "PASS" in parts:
        base = "PASS-PCPL"
    elif pos == "V":
        asp = next((a for a in ("PERF", "IMPF", "IMPV") if a in parts), "V")
        voice = "PASS" if "PASS" in parts else "ACT"
        base = f"V-{asp}-{voice}"
    else:
        base = pos or "?"
    return f"{base}|{form}" if form else base


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
    lem_bw = {l: b for l, b in con.execute("SELECT lemma_id,lemma_buckwalter FROM lemmas")}
    lem_ar = {l: a for l, a in con.execute("SELECT lemma_id,lemma_arabic FROM lemmas")}
    root_bw = {r: b for r, b in con.execute("SELECT root_id,root_buckwalter FROM roots")}
    root_ar = {r: a for r, a in con.execute("SELECT root_id,root_arabic FROM roots")}
    rows = con.execute("SELECT surah_number s,ayah_number a,word_position wp,pos,segment_type st,"
                       "features_raw fr,lemma_id,root_id FROM morphology "
                       "ORDER BY surah_number,ayah_number,word_position").fetchall()
    con.close()

    by = defaultdict(list)
    for r in rows:
        by[(r["s"], r["a"])].append(r)

    lemma_root = {}; lemma_pat = defaultdict(Counter); lemma_tok = Counter()
    lemma_ay = Counter(); root_ay = Counter(); lr_co = defaultdict(Counter); N = 0
    root_lemmas = defaultdict(set)
    ayah_content = {}            # key -> sorted list of (wp, lemma, root)
    for key, toks in by.items():
        content = []
        for t in toks:
            if (t["st"] == "STEM" and t["pos"] in ("N", "ADJ", "V")
                    and t["lemma_id"] is not None and t["root_id"] is not None
                    and t["lemma_id"] != allah):
                content.append((t["wp"], t["lemma_id"], t["root_id"]))
                lemma_tok[t["lemma_id"]] += 1
                lemma_root[t["lemma_id"]] = t["root_id"]
                lemma_pat[t["lemma_id"]][pattern_desc(t["fr"], t["pos"])] += 1
                root_lemmas[t["root_id"]].add(t["lemma_id"])
        content.sort()
        ayah_content[key] = content
        if content:
            N += 1
            lem_set = {l for _, l, _ in content}; root_set = {r for _, _, r in content}
            for l in lem_set:
                lemma_ay[l] += 1
            for r in root_set:
                root_ay[r] += 1
            for l in lem_set:
                for r in root_set:
                    lr_co[l][r] += 1

    def ppmi_global(l, r):
        c = lr_co[l][r]
        if c < MIN_COOC or not lemma_ay[l] or not root_ay[r]:
            return 0.0
        v = math.log((c * N) / (lemma_ay[l] * root_ay[r]))
        return v if v > 0 else 0.0

    def tier(l):
        c = lemma_tok[l]
        return "قوی/strong" if c >= TIER_STRONG else "محتمل/probable" if c >= TIER_PROB else "نامشخص/abstain"

    # ── word lexicon ──
    lexicon = {}; tier_counts = Counter()
    for l in sorted(lemma_tok, key=lambda l: lem_bw.get(l, "")):
        rt = lemma_root[l]; tcnt = tier(l); tier_counts[tcnt] += 1
        assoc = sorted(((r, ppmi_global(l, r)) for r in lr_co[l] if r != rt),
                       key=lambda t: -t[1])
        assoc = [(r, v) for r, v in assoc if v > 0][:10]
        lexicon[lem_bw[l]] = {
            "lemma_ar": lem_ar.get(l, ""), "root_bw": root_bw.get(rt, "?"),
            "root_ar": root_ar.get(rt, ""), "pattern": lemma_pat[l].most_common(1)[0][0],
            "token_count": lemma_tok[l], "tier": tcnt,
            "top_associated_roots": [{"root_bw": root_bw.get(r, "?"), "root_ar": root_ar.get(r, ""),
                                      "ppmi": round(v, 4)} for r, v in assoc],
        }

    pat_counter = Counter()
    for l in lemma_tok:
        pat_counter[lemma_pat[l].most_common(1)[0][0]] += 1
    pattern_stats = {"method": "L4-words-1.0", "distinct_patterns": len(pat_counter),
                     "patterns": [{"pattern": p, "lemmas": n} for p, n in pat_counter.most_common()]}

    # ── self-prediction: within-root form disambiguation (root fixed; ayah vs local ±W) ──
    polyroots = {r for r, ls in root_lemmas.items() if len(ls) >= 2}
    instances = []   # (key, root, true_lemma, wp)
    for key, content in ayah_content.items():
        if len(content) < 2:
            continue
        for wp, l, r in content:
            if r in polyroots:
                instances.append((key, r, l, wp))
    keys_sorted = sorted({i[0] for i in instances})
    fold_of = {k: idx % KFOLD for idx, k in enumerate(keys_sorted)}

    m_ayah = m_local = base_hit = tot = 0
    for k in range(KFOLD):
        train_keys = {i[0] for i in instances if fold_of[i[0]] != k}
        co = defaultdict(Counter); lay = Counter(); ray = Counter(); Nt = 0
        root_lemma_cnt = defaultdict(Counter)
        for key in train_keys:
            content = ayah_content[key]
            lem_set = {l for _, l, _ in content}; root_set = {r for _, _, r in content}
            Nt += 1
            for l in lem_set:
                lay[l] += 1
                root_lemma_cnt[lemma_root[l]][l] += 1
            for r in root_set:
                ray[r] += 1
            for l in lem_set:
                for r in root_set:
                    co[l][r] += 1

        def tr_ppmi(l, r):
            c = co[l][r]
            if c < MIN_COOC or not lay[l] or not ray[r]:
                return 0.0
            v = math.log((c * Nt) / (lay[l] * ray[r]))
            return v if v > 0 else 0.0

        def predict(cands, ctx_roots):
            best = None; best_s = -1.0
            for cand in sorted(cands):
                s = sum(tr_ppmi(cand, cr) for cr in ctx_roots)
                if s > best_s or (s == best_s and (best is None or cand < best)):
                    best_s = s; best = cand
            return best

        for key, r, true_l, wp in instances:
            if fold_of[key] != k:
                continue
            cands = root_lemma_cnt[r]
            tot += 1
            if not cands:
                continue
            content = ayah_content[key]
            ayah_ctx = [rr for _, _, rr in content if rr != r]
            local_ctx = [rr for w2, _, rr in content if rr != r and abs(w2 - wp) <= WINDOW]
            base = cands.most_common(1)[0][0]
            if predict(cands, ayah_ctx) == true_l:
                m_ayah += 1
            if predict(cands, local_ctx) == true_l:
                m_local += 1
            if base == true_l:
                base_hit += 1

    def pct(x):
        return round(100.0 * x / tot, 2) if tot else 0.0
    selfpred = {
        "method": "L4-words-1.0",
        "task": "within-root form disambiguation from context (root fixed → no root leakage)",
        "kfold": KFOLD, "window": WINDOW, "instances": tot, "polysemous_roots": len(polyroots),
        "model_ayah_bag": {"top1_pct": pct(m_ayah)},
        "model_local_window": {"top1_pct": pct(m_local)},
        "baseline": {"top1_pct": pct(base_hit), "desc": "most frequent form of the root"},
        "verdict": ("forms_carry_contextual_meaning"
                    if max(m_ayah, m_local) > base_hit else "no_improvement_over_baseline"),
        "reading": "if a model > baseline, context determines which word-form of a root is used ⇒ "
                   "forms carry contextual meaning beyond the root. Negative ⇒ at this granularity "
                   "the root, not the specific form, is the carrier of relational meaning.",
    }

    def dump(name, obj):
        p = out / name; p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
        return p.stat().st_size
    sizes = {
        "word_lexicon.json": dump("word_lexicon.json",
                                  {"method": "L4-words-1.0", "min_cooc": MIN_COOC, "lemmas": lexicon}),
        "pattern_stats.json": dump("pattern_stats.json", pattern_stats),
        "self_prediction.json": dump("self_prediction.json", selfpred),
    }
    manifest = {
        "layer": "L4", "name": "word / form meaning (relational)", "method": "L4-words-1.0",
        "foundation": "relational network (Charter Article B-3)", "source": db.name,
        "leakage_control": "self-prediction holds the root fixed; the root cannot be a cue",
        "confidence_tiers": dict(tier_counts),
        "totals": {"lemmas": len(lexicon), "distinct_patterns": len(pat_counter),
                   "polysemous_roots": len(polyroots)},
        "self_prediction": {"model_ayah_top1_pct": selfpred["model_ayah_bag"]["top1_pct"],
                            "model_local_top1_pct": selfpred["model_local_window"]["top1_pct"],
                            "baseline_top1_pct": selfpred["baseline"]["top1_pct"],
                            "verdict": selfpred["verdict"]},
        "output_bytes": sizes,
    }
    dump("manifest.json", manifest)

    if not args.quiet:
        print("L4 — Word / Form meaning (relational)")
        print(f"  lemmas: {len(lexicon)}   tiers: {dict(tier_counts)}")
        print(f"  distinct morphological patterns: {len(pat_counter)}")
        print("  top patterns: " + ", ".join(f"{p}({n})" for p, n in pat_counter.most_common(6)))
        sp = selfpred
        print(f"\n  SELF-PREDICTION — within-root form disambiguation ({sp['instances']} instances, "
              f"{sp['polysemous_roots']} polysemous roots; root fixed = no leakage):")
        print(f"    model (ayah-bag)   top1={sp['model_ayah_bag']['top1_pct']}%")
        print(f"    model (local ±{WINDOW})   top1={sp['model_local_window']['top1_pct']}%")
        print(f"    baseline           top1={sp['baseline']['top1_pct']}%  (most frequent form of the root)")
        print(f"    verdict: {sp['verdict']}")
        print(f"\n  Wrote {len(sizes)+1} files to {out}")


if __name__ == "__main__":
    main()
