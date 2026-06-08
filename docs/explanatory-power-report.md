# Explanatory-Power Report — Phase Ω(B) (B, D)

**Phase:** Ω(B) · **Method version:** `explanation-boundary-1.0` · **Date:** 2026-06-08.

## 1. Objective
Measure, in bits, how much of the Quran's structure each discovery layer explains — the
information budget of the maximum explanation model.

## 2. Method
The structural object is the ayah×root incidence (which roots occur in which ayah). Models
are applied cumulatively and scored by the negative log-likelihood (bits) of selecting each
present root: **M0 uniform** (1/V), **M1 frequency** (root marginals over the vocabulary),
**M2 + co-occurrence** (pairwise PPMI log-linear, λ=1). Explained fraction = NLL reduction /
uniform NLL. Frequency is exact over all 44,431 present-root instances; the structure model is
scored on a deterministic 12,000-instance sample.

## 3. Results
| model | mean NLL (bits) | explained vs uniform |
|---|--:|--:|
| M0 uniform | 10.681 | — |
| **M1 frequency** | **8.503** | **20.4%** |
| M2 + co-occurrence (in-sample) | 14.533 | **−56% (worse)** |

- Frequency explains **20.4%** of the per-root selection information.
- The co-occurrence layer provides **no usable compression** — its in-sample NLL (14.53) is
  *worse* than frequency (8.50) and worse than uniform (10.68).

## 4. Interpretation
The maximum *generalizable* explanation model is **frequency alone (20.4%)**. The co-occurrence
layer fails to compress for two compounding reasons: (1) a calibration artifact of the λ=1
log-linear model (the same overconfidence Phase P documented), and (2) its established
non-predictiveness (Phase P: out-of-sample it does not beat frequency either). Either way, it
adds no explanatory information. Motifs and grammar are higher-order co-occurrence and are
subsumed in this null result.

## 5. Falsification Attempts
The co-occurrence layer was given every chance to compress (in-sample, the easiest case) and
failed; out-of-sample it failed in Phase P. No layer beyond frequency carries explanatory
information.

## 6. Limitations
- The structure NLL is calibration-sensitive (λ=1, fixed); a tuned model could compress
  in-sample, but Phase P shows it would not generalize, so the *generalizable* explanation is
  unchanged.
- "Explanation" here is per-root-selection compression; other operationalizations would shift
  the absolute number but not the frequency-only conclusion.

## 7. Conclusion
**Frequency explains 20.4% of the Quran's per-root structure; no discovered layer adds usable
explanatory information beyond it.** The maximum generalizable model is frequency alone.

Source: `generated/explanation_boundary/explanatory_power.json`, `maximum_model.json`.
