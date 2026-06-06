# Distribution Analysis Report — Phase 2 (Quran Internal Lexicon)

**Scope.** How roots and lemmas are spread across the 114 surahs and across the
Meccan/Medinan classification recorded in `generated/monad.db`. Derived solely
from Quran-internal distribution. Reproducible via `scripts/build_lexicon.py`.

**Layer.** Strictly statistical. The Meccan/Medinan labels are taken **as data
already present in the database** (`surahs.revelation_type`); this report
measures how vocabulary distributes against that label. It makes **no**
historical, chronological, or theological claim — only "root X's tokens fall
n% in surahs labelled medinan".

Data product: `distribution_profiles.json` (per-entity surah counts, evenness,
coverage, concentration, Meccan/Medinan split).

---

## 1. Statistics computed per entity

For every root and lemma:

| Field | Meaning |
|---|---|
| `surah_count` | distinct surahs touched |
| `surah_coverage` | `surah_count / 114` |
| `entropy_bits` | Shannon entropy of the surah distribution |
| `evenness` | entropy normalised to [0,1]; 1.0 = perfectly uniform spread |
| `top_surah_share` | fraction of occurrences in the single busiest surah |
| `meccan_occurrences` / `medinan_occurrences` | split by `revelation_type` |

`evenness` and `top_surah_share` are the two poles of a **dispersion axis**:
broad/uniform vocabulary at one end, locally-concentrated vocabulary at the
other.

---

## 2. The dispersion axis

**Most dispersed roots** (high coverage, high evenness — pervasive backbone):

| Root | Occ | Coverage | Evenness |
|---|---:|---:|---:|
| ربب | 980 | 0.82 | 0.87 |
| كون | 1,390 | 0.75 | 0.87 |
| اله | 2,851 | 0.75 | 0.82 |
| علم | 854 | 0.75 | 0.87 |
| خلق | 261 | 0.66 | 0.94 |

**Most concentrated roots** (≥15 occ, single-surah dominance — topic-locked):

| Root | Occ | Top-surah share | Surahs |
|---|---:|---:|---:|
| الو | 37 | 0.84 | 6 |
| كتم | 21 | 0.48 | 7 |
| كيل | 16 | 0.44 | 7 |
| طلق | 23 | 0.43 | 10 |
| فرض | 18 | 0.39 | 7 |
| شهر | 21 | 0.38 | 9 |

**Finding.** ربب is the most *pervasive* root in the corpus (94/114 surahs);
الو is among the most *concentrated* (84% of occurrences in one surah). The
lexicon spans a continuum from text-wide vocabulary to passage-bound vocabulary,
and the engine quantifies exactly where each root sits.

---

## 3. Meccan / Medinan distributional skew

Using `revelation_type` as a pre-existing label, vocabulary splits sharply.
(Thresholds: roots with ≥40 total occurrences.)

**Most Medinan-skewed roots**

| Root | Medinan % | mec / med |
|---|---:|---|
| نفق | 88% | 13 / 98 |
| نسو | 85% | 9 / 50 |
| قتل | 78% | 37 / 133 |
| حلل | 75% | 13 / 38 |
| توب | 74% | 23 / 64 |
| جهد | 73% | 11 / 30 |
| اثم | 73% | 13 / 35 |

**Most Meccan-skewed roots**

| Root | Medinan % | mec / med |
|---|---:|---|
| نذر | 13% | 113 / 17 |
| وحي | 12% | 69 / 9 |
| قرا | 11% | 78 / 10 |
| جرم | 9% | 60 / 6 |
| سحر | 6% | 59 / 4 |
| ملا | 5% | 38 / 2 |

**Finding (distributional only).** Two distinct vocabulary regimes appear. The
Medinan-skewed band is dominated by roots of community regulation — نفق
(hypocrisy/spending), نسو (women), قتل (fighting/killing), حلل (lawfulness), توب
(repentance), جهد (striving), اثم (sin). The Meccan-skewed band is dominated by
roots of proclamation and confrontation — نذر (warning), وحي (revelation), قرا
(recitation), سحر (sorcery), ملا (the chiefs). This is a measured association
between vocabulary and the database's revelation-type label; the report draws no
conclusion about *why* the distribution is shaped this way.

---

## 4. Coverage statistics across the lexicon

- A small set of ~30 backbone roots reach >60% surah coverage; the long tail of
  roots is highly localised (most roots appear in fewer than 10 surahs).
- The lemma layer is more concentrated still: because lemmas subdivide roots,
  the average lemma touches fewer surahs than the average root.
- Concentration (`top_surah_share`) and coverage are strongly anti-correlated by
  construction; together they give a stable two-number fingerprint of each
  entity's spread.

---

## 5. Limitations

- Meccan/Medinan labels are inherited from `surahs.revelation_type`; their
  provenance is the source dataset, not this engine. Skew figures are only as
  reliable as that label.
- Coverage/evenness ignore *sequence*; a root concentrated early vs. late in the
  mushaf has the same coverage. `first_occurrence`/`last_occurrence` in the
  profiles capture position separately.
- Entities with very few occurrences have unstable dispersion statistics; the
  skew tables apply a ≥40-occurrence floor for this reason.
- All findings are distributional associations, not historical or causal claims.
