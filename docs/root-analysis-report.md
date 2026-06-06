# Root Analysis Report — Phase 2 (Quran Internal Lexicon)

**Scope.** This report describes the distributional behaviour of the **1,642
morphological roots** attested in `generated/monad.db`, derived solely from
Quran-internal usage. No external dictionary, tafsir, translation, or theology
is used. Every figure is reproducible via `scripts/build_lexicon.py`.

**Layer.** Strictly lexical and statistical. Nothing below is an interpretation,
a definition, or a claim about meaning, history, or origin. "Neighbour",
"reach", and "specialised" are names for *measured usage patterns*, not for
semantic truths.

Data products referenced: `root_profiles.json`, `distribution_profiles.json`,
`cooccurrence_graph.json`.

---

## 1. Corpus shape

| Measure | Value |
|---|---|
| Distinct roots (attested in `words`) | 1,642 |
| Word tokens carrying a root | 49,959 / 77,429 (64.5%) |
| Tokens without a root (particles, pronouns, etc.) | 27,470 (35.5%) |
| Ayahs (co-occurrence unit) | 6,236 |
| Distinct co-occurring root pairs | 74,167 |

The 35.5% of tokens with no root are the grammatical connective tissue
(prepositions, pronouns, the article, negators). They are excluded from root
statistics but reappear as the **hubs of the lemma graph** (see the lemma
report) — a structural division of labour between *content* roots and
*function* words.

---

## 2. Highest-frequency roots

| Root | Occurrences | Surahs | Lemmas |
|---|---:|---:|---:|
| اله | 2,851 | 86 | 3 |
| قول | 1,722 | 84 | 6 |
| كون | 1,390 | 86 | 3 |
| ربب | 980 | 94 | 4 |
| امن | 879 | 77 | 17 |
| علم | 854 | 85 | 14 |
| قوم | 660 | 79 | 22 |
| اتي | 549 | 72 | 6 |
| كفر | 525 | 77 | 14 |
| بين | 523 | 71 | 13 |

**Pattern — frequency ≠ lemma diversity.** اله (2,851 occurrences) is spread
across only **3 lemmas**, i.e. it is a high-volume but morphologically narrow
root. By contrast قوم (660 occurrences) fans out into **22 lemmas**, and امن
into **17**. High token volume and rich derivational branching are independent
axes; a root can be loud-but-monomorphic (اله, شيا: 2 lemmas) or
moderate-but-prolific (قوم, امن, علم).

---

## 3. Unusually central roots (graph degree)

Centrality here = degree in the root co-occurrence graph (number of distinct
strong co-occurrence partners retained, ≤ 12 per node by construction, so high
degree means a root is *repeatedly* among the strongest partners of many other
roots).

| Root | Degree | Note |
|---|---:|---|
| اله | 300 | the dominant hub of the entire root graph |
| قول | 222 | speech-framing root; saturates narrative verses |
| كون | 181 | existential copula-like root |
| امن | 123 | |
| ربب | 113 | |
| علم | 90 | |
| جعل | 90 | "to make/appoint" — pairs widely despite lower frequency |
| قوم | 88 | |
| سمو | 83 | "heaven/name" |
| ارض | 82 | "earth" |

**Surprising centrality.** جعل ("to make/render") reaches degree 90 — equal to
علم — despite a far lower raw frequency. It is a *connective* root: it appears
beside a very wide variety of objects, so it is a strong partner to many roots
without itself being among the most frequent. ارض ("earth") and سمو
("heaven/sky") both rank in the top ten by centrality, reflecting their
recurrent pairing with each other and with creation-vocabulary.

---

## 4. Roots with the broadest semantic reach

"Reach" = how evenly a root is spread across the 114 surahs, combining
`surah_coverage` (fraction of surahs touched) and `evenness` (normalised
Shannon entropy of its surah distribution; 1.0 = perfectly uniform).

| Root | Occ | Surah coverage | Evenness |
|---|---:|---:|---:|
| ربب | 980 | 0.82 | 0.87 |
| كون | 1,390 | 0.75 | 0.87 |
| اله | 2,851 | 0.75 | 0.82 |
| علم | 854 | 0.75 | 0.87 |
| قول | 1,722 | 0.74 | 0.86 |
| سمو | 381 | 0.71 | 0.93 |
| ارض | 461 | 0.70 | 0.92 |
| خلق | 261 | 0.66 | 0.94 |

**Pattern — ربب is the most pervasive root in the Quran**, present in **94 of
114 surahs** (82% coverage) — broader reach than even اله, despite one third the
token volume. Roots in this band (ربب, كون, اله, علم, قول, سمو, ارض, خلق) form a
**distributional backbone**: vocabulary that is not localised to any theme or
section but recurs almost everywhere. Note خلق ("create") has the highest
*evenness* (0.94) of the high-frequency roots — its occurrences are the most
uniformly scattered.

---

## 5. Roots with highly specialised usage

"Specialised" = a root that occurs enough to be non-accidental (≥ 15 times) yet
concentrates a large share of those occurrences in a single surah
(`top_surah_share`).

| Root | Occ | Top-surah share | Surahs |
|---|---:|---:|---:|
| الو | 37 | 0.84 | 6 |
| كتم | 21 | 0.48 | 7 |
| اوب | 17 | 0.47 | 8 |
| كيل | 16 | 0.44 | 7 |
| طلق | 23 | 0.43 | 10 |
| شري | 25 | 0.40 | 8 |
| فرض | 18 | 0.39 | 7 |
| شهر | 21 | 0.38 | 9 |

**Pattern — clause-bound and topic-bound roots.** الو concentrates 84% of its
occurrences in a single surah; كيل ("measure") and فرض ("ordain/apportion")
cluster in the legal-economic passages; طلق ("divorce") and شهر ("month")
concentrate where their topic is legislated. These are the opposite pole from
§4: vocabulary whose *usage* is locked to a narrow textual region. This is a
purely distributional observation — it says where a root is used, not what it
means.

---

## 6. Per-root profile contents

Each entry in `root_profiles.json` answers the Phase-2 success criteria for a
root:

- **Where / how often** — `occurrence_count`, `first_occurrence`,
  `last_occurrence`, `surah_count`.
- **With which roots** — `top_neighbor_roots` (PPMI-ranked ayah co-occurrence,
  with a frequency-scaled support floor to suppress rare-pair artefacts).
- **With which lemmas** — `top_neighbor_lemmas`.
- **In which environments** — `most_common_contexts` (verbatim verse snippets),
  `distribution_statistics`.

Worked example — **علم ("knowledge")**: 854 occurrences, 14 lemmas, 85 surahs;
first at 1:2, last at 102:5. Its strongest co-occurrence partners are **غيب**
(the unseen, 34 shared ayahs), **علن** (openness), **كتم** (concealment), and
**جهر** (making public) — a coherent know / reveal / conceal field surfaced with
no external input. Its top *semantic* neighbours (distributional similarity) are
اله, بين, امن, حكم.

---

## 7. Limitations

- Roots are absent on 35.5% of tokens by design; co-occurrence is computed only
  over rooted tokens.
- PPMI inflates rare pairs; the profile neighbour lists apply a support floor,
  but very rare roots still rest on thin evidence.
- "Centrality" is capped by `GRAPH_EDGES_PER_NODE = 12`, so degree measures
  *how often a root is a top partner of others*, not its total partner count.
- All statements are distributional. No meaning is asserted.
