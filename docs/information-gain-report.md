# Information-Gain Report — Phase P (D, headline metric)

**Phase:** P · **Method version:** `predictivity-discovery-1.0` · **Date:** 2026-06-07.

## 1. Objective

Quantify, in bits, the held-out predictive information the structure model adds over the
frequency baseline — the single headline number `info-gain = mean(NLL_base − NLL_struct)`.
Positive = structure predicts better; negative = structure predicts worse.

## 2. Method

Per masked instance, both models assign a proper probability to the true unit over the
training vocabulary. NLL = −log₂ P(true). Info-gain is the paired mean of
(NLL_base − NLL_struct) in bits/unit; perplexity = 2^mean-NLL. Primary cell (root / R1
5-fold / single) carries a B = 1000 bootstrap CI; other cells carry SE-based 95% CIs.

## 3. Results

**Primary cell (root / R1 5-fold / single, n = 43,743):**
- mean NLL B0 = 8.466 bits → **perplexity 354**
- mean NLL S1 = 11.782 bits → **perplexity 3,522**
- **info-gain = −3.316 bits/unit** (bootstrap 95% CI [−3.391, −3.242]; null band −3.617
  [−3.684, −3.526])

**Root info-gain across regimes/masks (bits):**

| cell | info-gain |
|---|--:|
| R1-5 single | −3.316 |
| R1-5 25% | −2.156 |
| R1-5 50% | −1.107 |
| R1 k=10 single | −3.374 |
| R2 blocks single | −3.061 |
| R3 fwd-25 | −2.542 |
| R3 fwd-50 | −2.327 |
| R3 fwd-75 | −1.750 |
| R4 len-strat single | −3.366 |

**Concept info-gain (bits):** single −0.055 [−0.085, −0.022]; 25% +0.088; 50% +0.153.

Pre-registered minimum meaningful effect = +0.05 bits. **No root cell reaches it; every
root cell is negative.**

## 4. Interpretation

In bits, the structure model is **information-negative at the root level**: it makes
held-out roots *less* predictable than frequency alone, by 1.1–3.4 bits depending on mask
fraction (the gap shrinks as more units are masked because more context overlap exists, but
never turns positive). At the concept level the bits are near zero — slightly negative at
single-mask, slightly positive for partial masking — i.e. concept structure is roughly
break-even on calibrated information, and its apparent value lives in *ranking*, not *bits*
(and is confounded; see `concept-predictivity-report.md`).

The honest reading of the magnitude: a −3.3-bit gap is large partly because the fixed-λ
log-linear model is **overconfident** (poorly calibrated). The *sign*, however, is robust
and is corroborated by the calibration-free ranking metrics, which also favour frequency.
So the conclusion "structure adds no positive information" does not depend on the
magnitude or on calibration.

## 5. Falsification Attempts

The headline number was attacked by (1) bootstrap (1000 resamples) — the CI excludes 0 on
the negative side; (2) the null band — the real value (−3.316) is *above* the null band
(−3.617), confirming real co-occurrence carries some bits, but still far below 0; (3)
cross-regime replication — negative in all 9 root cells. The claim "info-gain > 0" is
falsified everywhere at the root level.

## 6. Limitations

- Perplexity magnitude is calibration-sensitive (λ = 1, untuned by pre-registration). The
  bits number should be read as **directional**, with the ranking metrics as the
  calibration-free corroborator.
- Info-gain measures average held-out log-loss; it does not separately credit the small
  mean-rank-percentile improvement S1 shows at root level (a head-vs-tail redistribution).

## 7. Conclusion

**Held-out predictive information gain is negative at the root level (−3.3 bits, primary
cell; negative in all 9 cells) and ≈ 0 / confounded at the concept level.** The structure
adds no positive predictive information over frequency. The pre-registered minimum effect
(+0.05 bits) is not met anywhere at the root level.

Source: `generated/predictivity/information_decomposition.json`, `root_predictivity.json`.
