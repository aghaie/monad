# Frequency-Null Report — Phase 19X (D)

**Phase:** 19X · **Method version:** `numerics-discovery-1.0` · **Date:** 2026-06-07.

## 1. Objective

Compare every numerical finding against frequency-preserving null models, so that nothing is
accepted that random data of the same distribution would also produce. This is one of the two
decisive controls (with multiple-testing correction).

## 2. Method

Two complementary nulls:
- **Scalar family-wise null (1,000 realizations):** generate 10 random integers, each within
  half-to-double the magnitude of the corresponding real total; recompute the full
  divisibility scan; record the minimum p-value (the single most "significant" divisor). The
  family-wise p is the fraction of null corpora whose best finding is at least as extreme as
  the real best.
- **Frequency-preserving sequence demonstration (100 resamples):** for representative
  sequences (surah ayah counts, ayah word counts, root frequencies), resample with
  replacement from the sequence's own value multiset and recompute the maximum residue
  non-uniformity; compare to the real value.

## 3. Results

**Scalar family-wise null (1,000 realizations):**

| quantity | value |
|---|--:|
| real best scalar-compression p | 0.0057 |
| null best-p mean | 0.0173 |
| null best-p 5th percentile | 0.00086 |
| **family-wise permutation p** | **0.227** |

The real best (0.0057) is well above the null's 5th percentile (0.00086) — random integers
routinely do better.

**Frequency-preserving sequence demonstration:**

| sequence | frequency-preserving p | verdict |
|---|--:|---|
| surah_ayah_counts | 1.00 | artifact |
| ayah_word_counts | 0.56 | artifact |
| root_frequencies | 0.58 | artifact |

## 4. Interpretation

Both nulls return **non-significance**. The most extreme scalar-compression pattern is
reached by chance 22.7% of the time — not unusual. And the sequence "findings" that a naïve
uniform null flagged are **fully reproduced** by frequency-preserving resampling (p = 0.56–
1.00): they are artifacts of the natural (Zipfian/clustered) shape of Quranic frequency
distributions, not numerical design. This is the formal confirmation of the divisibility
report's diagnosis.

## 5. Falsification Attempts

This report *is* the frequency-null attack. Every candidate numerical pattern was given the
chance to exceed a matched-frequency null; **none did.** The control was run at the
pre-registered scale (1,000 realizations for the scalar family).

## 6. Limitations

- The scalar null draws integers in [v/2, 2v] per real total; a wider or narrower band shifts
  the null slightly but cannot turn a p = 0.227 into significance.
- The sequence demonstration uses 100 resamples on 3 representative sequences; the analytic
  argument (residue is a multiset property, invariant to resampling order) generalises it.

## 7. Conclusion

**No numerical pattern survives the frequency null.** The scalar compression is reached by
random integers 22.7% of the time; the sequence residue "findings" are reproduced by
frequency-preserving resampling. Both are artifacts of natural distributions.

Source: `generated/numerics/frequency_null_results.json`.
