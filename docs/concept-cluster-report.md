# Concept Cluster Report — Phase 3

**Scope.** Per-concept cluster quality — cohesion, internal density, external
separation, stability — and the distributional reach of each concept across
surahs. Identifies highly cohesive, highly stable, global, localized, and rare
concepts. Strictly structural; concepts referenced by opaque id with raw member
roots as evidence, none named or interpreted. Reproducible via
`scripts/build_concepts.py`.

Data products: `concept_candidates.json`, `concept_statistics.json`.

---

## 1. Cluster-quality metrics (per concept)

| Metric | Definition | Mean |
|---|---|---:|
| `internal_density` | connected within-concept root pairs ÷ all possible pairs | 0.813 |
| `cohesion_score` | mean confidence of internal edges | 0.406 |
| `external_separation` | internal weight ÷ (internal + boundary weight) | 0.369 |
| `cluster_stability` | mean Jaccard recovery under threshold perturbation (±0.02) | 0.778 |

`internal_density` and `cohesion_score` measure *internal tightness*;
`external_separation` measures *isolation from the rest of the graph*;
`cluster_stability` measures *robustness*. They are largely independent — a
concept can be tight yet poorly separated (embedded in the core) or loose yet
well separated (a detached clique).

---

## 2. Which concepts are highly stable?

Concepts recovered almost perfectly when the similarity threshold is perturbed
(`cluster_stability` = 1.0). Evidence + reach:

| Concept | Size | cohesion | separation | surah cov | center roots |
|---|---:|---:|---:|---:|---|
| CONCEPT_008 | 21 | 0.427 | 0.569 | 0.80 | رذل مضغ همد ترب علق |
| CONCEPT_034 | 8 | 0.368 | 0.222 | 0.75 | بغي فضل اجر صلح رحم |
| CONCEPT_052 | 6 | 0.574 | 0.692 | 0.04 | اثل عرم خمط سدر سيل |
| CONCEPT_053 | 6 | 0.361 | 0.146 | 0.82 | اخر عذب دنو كفر متع |
| CONCEPT_055 | 6 | 0.433 | 0.217 | 0.21 | وسط عقد كسو صوم حرر |

Stability is independent of reach: both a 21-root concept spanning 80% of surahs
(CONCEPT_008) and a 6-root concept confined to 4% of surahs (CONCEPT_052) reach
stability 1.0. High stability means the cluster's membership is not an artefact
of the exact threshold.

---

## 3. Which concepts are highly cohesive?

Top `cohesion_score` (densest internal confidence):

| Concept | Size | cohesion | separation | stability | center roots |
|---|---:|---:|---:|---:|---|
| CONCEPT_052 | 6 | 0.574 | 0.692 | 1.000 | اثل عرم خمط سدر سيل |
| CONCEPT_095 | 4 | 0.552 | 0.715 | 0.900 | سند خشب جسم صيح |
| CONCEPT_077 | 4 | 0.546 | 0.251 | 0.618 | ذبب سلب طلب نقذ |
| CONCEPT_036 | 8 | 0.539 | 0.545 | 0.864 | اسن عسل معي لذذ لبن |
| CONCEPT_003 | 32 | 0.534 | 0.798 | 0.953 | جنف ذكو خنزر زلم خنق |

The most cohesive concepts are mostly **small, well-separated cliques** (size
4–8) — but CONCEPT_003 is a striking exception: a **32-root** concept with both
high cohesion (0.534) *and* the near-highest separation (0.798) *and* broad reach
(coverage 0.89). It is simultaneously large, tight, isolated, and pervasive — an
unusually self-contained large structure.

---

## 4. Global vs. localized concepts (surah reach)

`distribution_profile.surah_coverage` = fraction of the 114 surahs touched by a
concept's member roots.

**Global concepts** (span most surahs):

| Concept | Size | surah cov | stability | center roots |
|---|---:|---:|---:|---|
| CONCEPT_007 | 24 | 0.97 | 0.40 | علم اله اتي امن بين |
| CONCEPT_003 | 32 | 0.89 | 0.95 | جنف ذكو خنزر زلم خنق |
| CONCEPT_081 | 4 | 0.87 | 1.00 | اله كفر بين يوم |
| CONCEPT_016 | 16 | 0.86 | 0.91 | خلد نهر جنن تحت جري |

**Localized concepts** (restricted to very few surahs, coverage ≈ 0.009 ⇒ ~1
surah):

| Concept | Size | surah cov | occ | center roots |
|---|---:|---:|---:|---|
| CONCEPT_041 | 7 | 0.009 | 7 | فتق رتق فهم نون نفح |
| CONCEPT_043 | 7 | 0.009 | 9 | قلع بلع روع حنذ سعد |
| CONCEPT_051 | 6 | 0.009 | 7 | جذو سرمد نوا وكز ذود |
| CONCEPT_057 | 5 | 0.009 | 5 | ضدد حتم حنن شعل مخض |

A clear bimodal reach pattern emerges: a band of **pervasive** concepts touching
85–97% of surahs, and a band of **single-surah** concepts whose entire root set
occurs within one chapter. CONCEPT_007 (coverage 0.97) is the most global; its
low stability (0.40) reflects a fuzzy, much-debated boundary — the opposite
profile to the sharp localized cliques.

---

## 5. Rare concepts

Lowest total occurrences (`distribution_profile.total_occurrences`):

| Concept | Size | occ | surah cov | medinan frac | center roots |
|---|---:|---:|---:|---:|---|
| CONCEPT_102 | 4 | 4 | 0.009 | 1.00 | لقب نبز جسس ليت |
| CONCEPT_057 | 5 | 5 | 0.009 | 0.00 | ضدد حتم حنن شعل مخض |
| CONCEPT_100 | 4 | 5 | 0.04 | 0.00 | هلع كبد كند كدح |
| CONCEPT_068 | 5 | 6 | 0.009 | 1.00 | نحب وطر جوف سلق عوق |
| CONCEPT_041 | 7 | 7 | 0.009 | 0.00 | فتق رتق فهم نون نفح |

Rare concepts are built from roots that occur only a handful of times total, yet
they still form coherent cliques (they always appear together). Several are
purely Meccan (`medinan_fraction = 0`) or purely Medinan (`= 1.0`) — i.e. their
whole vocabulary is confined to one revelation regime, a distributional fact
recorded without interpretation.

---

## 6. Cross-metric structure

- **Tight ⊥ separated.** Internal density (mean 0.81) is uniformly high; the
  discriminating axes are separation and reach.
- **Reach is bimodal:** pervasive (≥0.85) vs. single-surah (≈0.009), with fewer
  concepts in between.
- **Stability is broadly high (mean 0.78)** and uncorrelated with size or reach;
  the notable low-stability cases are the large fuzzy-boundary global concepts.

---

## 7. Limitations

- Cohesion/separation are computed on the base mutual-kNN graph at
  `MIN_EDGE = 0.30`; a different base threshold rescales them.
- Stability is estimated from two perturbation thresholds (±0.02); more
  perturbations would tighten the estimate.
- `surah_coverage` counts presence, not weight; a root appearing once vs. many
  times in a surah counts identically toward coverage.
- All quantities are structural; no concept is interpreted or named.
