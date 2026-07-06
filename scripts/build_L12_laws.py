#!/usr/bin/env python3
"""
scripts/build_L12_laws.py

Monad — Layer L12: Sunan (laws of the world inside the log).

Framing: the ayat are the execution log of a universe whose maker documented
no rules. We reverse-engineer the engine's laws FROM THE LOG ALONE. Target:
the conditional/causal regularities the text itself reports ("if X then Y"),
not the generative grammar of the text.

Self-sufficient: the only input is generated/monad.db. The substrate's own
morphology marks conditional constructions — COND particles (<in/law/man/...),
T-<i*aA (idha), and RSLT (fa- of the apodosis) — so the log itself segments
each event into protasis (condition) and apodosis (result). No dictionary,
translation, or tafsir is read.

Pipeline:

  1 — EVENTS: one event per RSLT token, paired with the nearest preceding
      conditional marker in the same ayah. Protasis roots = STEM roots of the
      words from the marker word up to (excluding) the RSLT word; apodosis
      roots = STEM roots from the RSLT word to the end of the ayah, capped at
      the next conditional marker. Events with an empty side are dropped.

  2 — CANDIDATE LAWS: directed root pairs (A -> B), A in protasis, B in
      apodosis, set-semantics per event, support >= MIN_SUPPORT events.

  3 — FALSIFICATION: seeded permutation null (N=2000) that shuffles apodosis
      root-sets across events (protases fixed; marginals preserved => pure
      co-frequency is controlled). Per-law empirical p + Benjamini-Hochberg q;
      GLOBAL test: #pairs with support>=MIN_SUPPORT and max support vs null.
      Two-half presence check (events split by global ayah sequence; a stable
      law appears with support >= 2 in each half — presence, not significance,
      per the quran_root honesty rule). Reverse-direction count reported.

  4 — TIERS: صریح p<=0.005 & two-half stable; قوی p<=0.01; محتمل p<=0.05;
      otherwise نامشخص (kept only in candidates, not in verified laws).

Deterministic (seeded), offline. Outputs in generated/layers/L12_laws/.
Persian glosses are NOT produced here — labels are added only in the report,
after derivation (approved output-labelling policy).
"""

import json
import random
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DB = REPO / "generated" / "monad.db"
OUT = REPO / "generated" / "layers" / "L12_laws"
SEED = 12
N_NULL = 2000
MIN_SUPPORT = 3

IDHA_FORMS = ("<i*aA", "<i*aA^")


def is_marker(tag, form):
    return tag == "COND" or (tag == "T" and form in IDHA_FORMS)


def load_events(con):
    """Extract conditional events (protasis roots -> apodosis roots) per ayah."""
    rows = con.execute(
        """SELECT m.surah_number, m.ayah_number, a.ayah_sequential,
                  m.word_position, m.tag, m.form_buckwalter, m.segment_type,
                  r.root_arabic
             FROM morphology m
             JOIN ayahs a ON a.surah_number = m.surah_number
                         AND a.ayah_number = m.ayah_number
             LEFT JOIN roots r ON r.root_id = m.root_id
            ORDER BY m.surah_number, m.ayah_number,
                     m.word_position, m.token_position"""
    ).fetchall()

    by_ayah = defaultdict(list)
    for sura, ayah, seq, wpos, tag, form, seg, root in rows:
        by_ayah[(sura, ayah, seq)].append((wpos, tag, form, seg, root))

    events, dropped_empty = [], 0
    for (sura, ayah, seq), toks in sorted(by_ayah.items()):
        markers = sorted({w for (w, tag, form, seg, root) in toks
                          if is_marker(tag, form)})
        rslts = sorted({w for (w, tag, form, seg, root) in toks
                        if tag == "RSLT"})
        if not markers or not rslts:
            continue
        stem_roots = defaultdict(set)  # word_position -> roots
        for w, tag, form, seg, root in toks:
            if seg == "STEM" and root:
                stem_roots[w].add(root)
        for j in rslts:
            prev = [m for m in markers if m < j]
            if not prev:
                continue
            i = prev[-1]
            nxt = [m for m in markers if m > j]
            end = nxt[0] if nxt else max(stem_roots, default=j) + 1
            protasis = sorted(set().union(*[stem_roots[w] for w in range(i, j)
                                            if w in stem_roots] or [set()]))
            apodosis = sorted(set().union(*[stem_roots[w] for w in range(j, end)
                                            if w in stem_roots] or [set()]))
            marker_form = next(f for (w, t, f, s, r) in toks
                               if w == i and is_marker(t, f))
            if not protasis or not apodosis:
                dropped_empty += 1
                continue
            events.append({
                "sura": sura, "ayah": ayah, "seq": seq,
                "marker": marker_form, "marker_pos": i, "rslt_pos": j,
                "protasis_roots": protasis, "apodosis_roots": apodosis,
            })
    return events, dropped_empty


def pair_counts(protases, apodoses):
    c = Counter()
    for p, a in zip(protases, apodoses):
        for x in p:
            for y in a:
                c[(x, y)] += 1
    return c


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    events, dropped_empty = load_events(con)
    con.close()

    protases = [set(e["protasis_roots"]) for e in events]
    apodoses = [set(e["apodosis_roots"]) for e in events]
    obs = pair_counts(protases, apodoses)
    candidates = {pr: n for pr, n in obs.items() if n >= MIN_SUPPORT}

    # permutation null: shuffle apodosis sets across events
    rng = random.Random(SEED)
    ge = Counter()                 # per-candidate: #perms with count >= observed
    null_npairs, null_max = [], []
    idx = list(range(len(events)))
    for _ in range(N_NULL):
        rng.shuffle(idx)
        c = pair_counts(protases, [apodoses[k] for k in idx])
        null_npairs.append(sum(1 for n in c.values() if n >= MIN_SUPPORT))
        null_max.append(max(c.values(), default=0))
        for pr, n_obs in candidates.items():
            if c.get(pr, 0) >= n_obs:
                ge[pr] += 1

    obs_npairs = len(candidates)
    obs_max = max(candidates.values(), default=0)
    p_global_npairs = (1 + sum(1 for v in null_npairs if v >= obs_npairs)) / (N_NULL + 1)
    p_global_max = (1 + sum(1 for v in null_max if v >= obs_max)) / (N_NULL + 1)

    # two-half split by global ayah sequence (median event)
    seqs = sorted(e["seq"] for e in events)
    mid = seqs[len(seqs) // 2]
    half1 = [k for k, e in enumerate(events) if e["seq"] < mid]
    half2 = [k for k, e in enumerate(events) if e["seq"] >= mid]
    c1 = pair_counts([protases[k] for k in half1], [apodoses[k] for k in half1])
    c2 = pair_counts([protases[k] for k in half2], [apodoses[k] for k in half2])

    # assemble laws
    laws = []
    for (a, b), n in sorted(candidates.items(), key=lambda kv: (-kv[1], kv[0])):
        p = (1 + ge[(a, b)]) / (N_NULL + 1)
        laws.append({
            "antecedent": a, "consequent": b, "support": n,
            "p": round(p, 6),
            "reverse_support": obs.get((b, a), 0),
            "half1_support": c1.get((a, b), 0),
            "half2_support": c2.get((a, b), 0),
            "two_half_stable": c1.get((a, b), 0) >= 2 and c2.get((a, b), 0) >= 2,
            "reflexive": a == b,
            "evidence": sorted(f'{e["sura"]}:{e["ayah"]}' for e in events
                               if a in set(e["protasis_roots"])
                               and b in set(e["apodosis_roots"])),
        })

    # Benjamini-Hochberg q over candidates
    m = len(laws)
    order = sorted(range(m), key=lambda k: laws[k]["p"])
    qmin = 1.0
    for rank_from_end, k in enumerate(reversed(order)):
        rank = m - rank_from_end
        qmin = min(qmin, laws[k]["p"] * m / rank)
        laws[k]["q"] = round(qmin, 6)

    for law in laws:
        if law["p"] <= 0.005 and law["two_half_stable"]:
            law["tier"] = "صریح"
        elif law["p"] <= 0.01:
            law["tier"] = "قوی"
        elif law["p"] <= 0.05:
            law["tier"] = "محتمل"
        else:
            law["tier"] = "نامشخص"
    verified = [l for l in laws if l["tier"] != "نامشخص"]

    validation = {
        "n_events": len(events),
        "n_events_dropped_empty": dropped_empty,
        "n_ayahs_with_events": len({(e["sura"], e["ayah"]) for e in events}),
        "n_candidate_pairs": obs_npairs,
        "min_support": MIN_SUPPORT,
        "seed": SEED, "n_null": N_NULL,
        "global_test": {
            "observed_n_pairs_at_support": obs_npairs,
            "null_n_pairs_mean": round(sum(null_npairs) / N_NULL, 3),
            "null_n_pairs_max": max(null_npairs),
            "p_n_pairs": round(p_global_npairs, 6),
            "observed_max_support": obs_max,
            "null_max_support_mean": round(sum(null_max) / N_NULL, 3),
            "null_max_support_max": max(null_max),
            "p_max_support": round(p_global_max, 6),
        },
        "two_half_split_seq": mid,
        "n_half1_events": len(half1), "n_half2_events": len(half2),
        "tiers": dict(sorted(Counter(l["tier"] for l in laws).items())),
    }

    (OUT / "events.json").write_text(
        json.dumps({"events": events}, ensure_ascii=False, indent=2,
                   sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "law_candidates.json").write_text(
        json.dumps({"laws": laws}, ensure_ascii=False, indent=2,
                   sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "laws_verified.json").write_text(
        json.dumps({"laws": verified}, ensure_ascii=False, indent=2,
                   sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2,
                   sort_keys=True) + "\n", encoding="utf-8")

    print(f"events: {len(events)} (dropped empty-side: {dropped_empty})")
    print(f"candidates (support>={MIN_SUPPORT}): {obs_npairs}  "
          f"[null mean {validation['global_test']['null_n_pairs_mean']}, "
          f"p={p_global_npairs:.4f}]")
    print(f"max support: {obs_max}  [p={p_global_max:.4f}]")
    print("tiers:", validation["tiers"])


if __name__ == "__main__":
    main()
