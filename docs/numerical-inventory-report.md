# Numerical-Inventory Report — Phase 19X (A)

**Phase:** 19X — Blind Numerical Structure Discovery Engine ·
**Method version:** `numerics-discovery-1.0` · **Date:** 2026-06-07.

## 1. Objective

Enumerate every integer-valued quantity extractable from the Quran, with **no number
privileged**, as the raw material for a blind search for non-random numerical structure.
The phase is designed to be valid whether or not any particular number (e.g. 19) was ever
claimed by anyone.

## 2. Method

Integer features are extracted directly from the Phase-1 database: scalar **totals** and
integer **sequences**. Letters are counted with an Arabic-letter regex over
`text_normalized` (one consistent rule; orthography-dependence flagged). No external data.

## 3. Results

**Scalar totals (10):**

| feature | value | | feature | value |
|---|--:|---|---|--:|
| n_surahs | 114 | | n_morphology_tokens | 128,219 |
| n_ayahs | 6,236 | | n_root_bearing_tokens | 49,968 |
| n_word_tokens | 77,429 | | n_total_letters | 325,424 |
| n_distinct_roots | 1,642 | | n_meccan_surahs | 86 |
| n_distinct_lemmas | 4,832 | | n_medinan_surahs | 28 |

**Integer sequences (7):** surah_ayah_counts (114), surah_word_counts (114),
surah_letter_counts (114), ayah_word_counts (6,236), ayah_letter_counts (6,236),
root_frequencies (1,642), lemma_frequencies (4,832); plus an order-dependent
root_first_occurrence sequence (1,642).

Divisor scan range: **2 … 500**, every divisor treated identically.

## 4. Interpretation

This is the feature space over which divisibility, compression, and residue structure are
searched. It contains the quantities that appear in numerical claims about the Quran (surah
count 114, etc.) alongside many others, so any real structure should surface — and any
spurious structure should be exposed by the controls.

## 5. Falsification Attempts

None at this stage; Phase A only enumerates. Every feature is provisional input to the
null/correction battery.

## 6. Limitations

- **Letter counts are orthography-dependent.** A different normalization (hamza/alef
  variants, pause marks) would change `n_total_letters`; this is the single most fragile
  feature and is flagged wherever it appears in a finding.
- Some totals are partly dependent (e.g. n_ayahs = Σ surah_ayah_counts); joint-divisibility
  tests treat them as quasi-independent and note the caveat.

## 7. Conclusion

A 10-scalar, 7-sequence integer feature space is extracted blind, over divisors 2–500. It
is the substrate for the divisibility scan and the controls.

Source: `generated/numerics/numerical_features.json`.
