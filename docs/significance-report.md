# Significance Report — Phase 19X (G)

**Phase:** 19X · **Method version:** `numerics-discovery-1.0` · **Date:** 2026-06-07.
**The most important phase:** multiple-testing control.

## 1. Objective

Apply rigorous multiple-testing correction so that no numerical pattern is accepted merely
because thousands of tests were run. With ~5% of tests passing p < 0.05 by chance, this phase
decides what, if anything, is real.

## 2. Method

The **well-posed test family** is scalar joint-divisibility: for each divisor 2–500, the
binomial p that the 10 totals are jointly divisible (499 tests). Sequence divisibility/residue
tests are **excluded** from the significance pool — they are invariant to structure shuffling
(`structure-null-report.md`) and non-significant under the frequency-preserving null
(`frequency-null-report.md`), so a uniform-null p there is not valid significance. On the 499
well-posed tests:
- **Bonferroni:** reject p ≤ α/N = 0.05/499 = 1.0×10⁻⁴.
- **Benjamini–Hochberg FDR** at α = 0.05.
- **Family-wise permutation** (1,000 random-integer corpora; `frequency-null-report.md`).

## 3. Results

| quantity | value |
|---|--:|
| well-posed tests (N) | 499 |
| Bonferroni threshold (α/N) | 1.0×10⁻⁴ |
| minimum p-value (divisor 86) | 5.7×10⁻³ |
| **survive Bonferroni** | **0** |
| **survive FDR** | **0** |
| family-wise permutation p | 0.227 |

## 4. Interpretation

**Nothing survives correction.** The single most significant divisor (86, p = 0.0057) is two
orders of magnitude short of the Bonferroni threshold (0.0001), and FDR rejects all 499 tests.
The family-wise permutation independently agrees (p = 0.227). Across every layer of control —
Bonferroni, FDR, and permutation — **there is no numerical pattern in the Quran's integer
totals that exceeds chance.** This is the decisive result of Phase 19X.

## 5. Falsification Attempts

This report is the correction itself: it attacks the entire family of findings simultaneously
with the three standard multiple-testing controls. The strongest raw finding fails all three.
No threshold was relaxed.

## 6. Limitations

- The well-posed family is restricted to scalar totals by design (the only family with a
  clean null); sequence tests were excluded with explicit justification, not to suppress
  positives but because their uniform-null significance is invalid.
- A larger, genuinely independent scalar family would give finer resolution; with 10 totals
  the binomial tail is coarse, but coarser resolution cannot manufacture significance that
  the permutation null also rejects.

## 7. Conclusion

**0 of 499 well-posed tests survive Bonferroni or FDR; family-wise permutation p = 0.227.**
After full multiple-testing control there is **no statistically significant numerical
structure** in the Quran's integer totals.

Source: `generated/numerics/significance_results.json`.
