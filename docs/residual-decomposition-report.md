# Residual-Decomposition Report — Phase Ψ (A)

**Phase:** Ψ — Residual Nature Discovery Engine · **Method version:** `residual-nature-1.0` ·
**Date:** 2026-06-08.

## 1. Objective
Partition the Ω(B) residual (~80% of per-root structure) into measurable sources — surah-topical
frequency vs irreducible lexical specificity vs structural/higher-order/long-range — and measure
each contribution. Measurement only; no interpretation.

## 2. Method
Per-root negative log-likelihood (bits) under: uniform (log₂V), global frequency, and per-surah
(topical) marginals with add-α smoothing and leave-one-ayah-out. The surah-topical contribution =
the NLL reduction of surah-conditioning below global frequency.

## 3. Results
| model | mean NLL (bits) |
|---|--:|
| uniform | 10.681 |
| global frequency | 8.503 |
| per-surah (topical, leave-one-out) | 8.923 |

- Residual after global frequency = **79.6%** of uniform.
- **Surah-topical gain = −0.42 bits** (surah conditioning is *worse* than global frequency).
- Composition of the residual: **surah-topical compresses 0%; irreducible lexical ≈ 100%**;
  structural/higher-order/long-range = 0 (per Phase P and the later reports).

## 4. Interpretation
Surah-topical conditioning does **not** compress the residual — per-surah marginals over 1,642
roots are too data-sparse to beat the better-estimated global frequency. So at the per-ayah level
the residual is **~100% irreducible lexical specificity**. A *real* topical signal nonetheless
exists (the real surah grouping beats a surah-shuffle null — see `residual-null-assault-report.md`),
but it is lexical and **sub-compressing**: it does not reduce the description length below global
frequency. The residual is the specific identity of which root occurs in each ayah.

## 5. Falsification Attempts
The "residual compresses to surah-topic" hypothesis is falsified (negative gain). The topical signal
is separately tested against a shuffle null (it survives, but does not compress).

## 6. Limitations
Per-surah estimation is data-limited; a model with more per-surah data could extract more topical
signal, but the null test shows the available signal is small and the compression is nil.

## 7. Conclusion
**The residual does not compress to surah-topic; it is ~100% irreducible lexical specificity** at
the per-ayah level, with a faint real-but-non-compressing topical signal.

Source: `generated/residual_nature/residual_decomposition.json`.
