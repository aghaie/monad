# Compression Report — Phase 19X (C)

**Phase:** 19X · **Method version:** `numerics-discovery-1.0` · **Date:** 2026-06-07.

## 1. Objective

Find the divisor(s) that most "compress" the corpus's integer totals — i.e. divide the most
of them — as the well-posed core of the numerical search, and measure whether any divisor's
joint-divisibility is beyond chance.

## 2. Method

For each divisor d, count how many of the 10 scalar totals are ≡ 0 mod d; compare to the
expected K/d via the binomial survival P(X ≥ count | Binomial(10, 1/d)). Lower p = more
compressive. (Significance under multiple-testing and the frequency null is in the
significance and frequency-null reports.)

## 3. Results

**Top compressing divisors (uncorrected):**

| divisor | scalars divisible | expected | binom p | which scalars |
|---|--:|--:|--:|---|
| 86 | 2 / 10 | 0.12 | 0.0057 | n_total_letters, n_meccan_surahs |
| 473 | 1 / 10 | 0.02 | 0.021 | n_total_letters |
| 16 | 3 / 10 | 0.62 | 0.021 | n_distinct_lemmas, n_root_bearing_tokens, n_total_letters |
| 43 | 2 / 10 | 0.23 | 0.022 | n_total_letters, n_meccan_surahs |
| 2 | 8 / 10 | 5.00 | 0.055 | (8 even totals) |

## 4. Interpretation

The "most compressive" divisor is **86** — but it divides only 2 of 10 totals, one of which
is **n_meccan_surahs = 86 itself** (self-divisibility), and the other is the
orthography-dependent letter count. This is a coincidence of two numbers, not a structural
law. The next candidates (473, 43, 16) likewise hinge on the fragile letter count and on a
single self-referential value. The divisor that divides the *most* totals is the trivial
d = 2 (8 of 10 are even — expected 5), which is not significant (p = 0.055) and is exactly
what one expects of arbitrary integers. **No divisor compresses the totals in a way that
exceeds chance** (formal test in `significance-report.md` and `frequency-null-report.md`).

## 5. Falsification Attempts

The compression finding is attacked by the family-wise frequency null
(`frequency-null-report.md`): random integers of matched magnitude reach the same best
compression 22.7% of the time (FWER p = 0.227), so the real totals are **not** unusually
compressible. Bonferroni and FDR (`significance-report.md`) reject all 499 compression
tests.

## 6. Limitations

- The top finding leans on `n_total_letters`, the most orthography-sensitive feature.
- 10 totals is a small family; the binomial tail is coarse for such small K.

## 7. Conclusion

No divisor compresses the Quran's integer totals beyond chance. The apparent leader (86) is
a self-divisibility-plus-letter-count coincidence and does not survive any control.

Source: `generated/numerics/compression_scores.json`.
