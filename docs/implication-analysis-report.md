# Implication Analysis Report — Phase 4

**Date:** 2026-06-06. **Source:**
`generated/propositions/implication_candidates.json`.

This report describes the `PREDICTS` layer: the conditional probability that
concept B activates `w` ayahs **after** concept A activates, computed only
within the same surah and restricted to windows `w ∈ {1, 2, 3}`. No causal
inference is claimed — `PREDICTS` is purely a sequence-conditional
distribution.

---

## 1. Definition

For each window `w` and ordered pair `(A, B)` with `A ≠ B`:

```
first_count[A]   = #i where A active at ayah_seq i and i+w is in the same surah
co_seq[w][A, B]  = #i where A active at i and B active at i+w (same surah)
P(B@i+w | A@i)   = co_seq[w][A, B] / first_count[A]
lift             = P(B@i+w | A@i) / P(B)
```

Edge emitted if `P(B@i+w | A@i) ≥ 0.20 ∧ lift ≥ 1.5 ∧ co_seq ≥ 5`.

Each edge stores `confidence` (the conditional probability), `lift`,
`support_count`, and `stability_score`.

---

## 2. Counts per window

| Window `w` | Edges | Mean lift | Max lift | Mean conf. | Mean support |
|---:|---:|---:|---:|---:|---:|
| 1 | 182 | 3.11 |  97.77 | 0.363 | 24.6 |
| 2 | 193 | 2.74 | 117.33 | 0.356 | 23.3 |
| 3 | 172 | 2.84 |  61.75 | 0.380 | 23.0 |
| **All** | **547** | 2.89 | 117.33 | 0.366 | 23.6 |

Edge count is roughly flat across windows, with `w = 2` slightly highest.
Mean conditional probability is also flat (0.35–0.38).

---

## 3. Top edges by lift (per window)

### `w = 1`

| src → tgt | lift | conf | support |
|---|---:|---:|---:|
| `CONCEPT_076 → CONCEPT_039` | 97.77 | 0.417 | 5 |
| `CONCEPT_089 → CONCEPT_039` | 58.66 | 0.250 | 5 |
| `CONCEPT_046 → CONCEPT_033` | 19.55 | 0.208 | 5 |
| `CONCEPT_039 → CONCEPT_021` | 13.41 | 0.308 | 8 |
| `CONCEPT_089 → CONCEPT_021` | 10.89 | 0.250 | 5 |

### `w = 2`

| src → tgt | lift | conf | support |
|---|---:|---:|---:|
| `CONCEPT_048 → CONCEPT_039` | 117.33 | 0.500 | 5 |
| `CONCEPT_046 → CONCEPT_033` |  20.40 | 0.217 | 5 |
| `CONCEPT_039 → CONCEPT_013` |   7.51 | 0.240 | 6 |
| `CONCEPT_035 → CONCEPT_013` |   6.26 | 0.200 | 11 |
| `CONCEPT_075 → CONCEPT_001` |   4.74 | 0.333 | 5 |

### `w = 3`

| src → tgt | lift | conf | support |
|---|---:|---:|---:|
| `CONCEPT_089 → CONCEPT_039` | 61.75 | 0.263 | 5 |
| `CONCEPT_039 → CONCEPT_089` | 58.10 | 0.200 | 5 |
| `CONCEPT_039 → CONCEPT_021` | 13.95 | 0.320 | 8 |
| `CONCEPT_089 → CONCEPT_021` | 11.47 | 0.263 | 5 |
| `CONCEPT_058 → CONCEPT_028` |  9.08 | 0.250 | 5 |

---

## 4. Decay-of-prediction across windows

For edges present in **all three** windows, conditional probability is
roughly stable, not monotonically decaying — consistent with concepts that
co-cluster across whole sub-sequences inside a surah, rather than
propagating step by step.

A small cluster (notably `CONCEPT_039`, `CONCEPT_048`, `CONCEPT_076`,
`CONCEPT_089`, `CONCEPT_021`) appears repeatedly at the top of every window.
This is the same tight high-NPMI sub-cluster identified in
`proposition-discovery-report.md §4`.

---

## 5. Stability and support

- 547 edges total, almost all with `stability_score == 1.0`.
- Mean support is small (~23 ayahs). Distribution is heavy-tailed: a few
  edges have support in the hundreds while most cluster near the minimum.

---

## 6. Limitations

- `PREDICTS` is sequence-conditional probability, not causation, not
  temporal narrative order (the Quran is non-chronological), and not
  cross-surah.
- Windows are fixed `{1, 2, 3}`. Larger windows would smear distinctions;
  smaller windows are impossible (`w=0` collapses to `CO_OCCURS`).
- Cross-surah pairs are excluded — a within-surah locality assumption that
  may understate predictive structure when surahs are short.
- High-lift, low-support edges depend on a handful of ayahs. The `support`
  column should always be consulted alongside `lift`.

---

## 7. Open questions (not answered here)

- Are the same high-lift edges present at `w ∈ {4, 5}`, or does locality
  decay sharply past `w = 3`?
- Is there asymmetry between Meccan and Medinan distributions inside the
  same edge set?
- Do `PREDICTS` edges align with `PRECEDES` edges (positional precedence
  within an ayah)?
