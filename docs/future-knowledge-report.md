# Future-Knowledge Report — Phase Ω(B) (I)

**Phase:** Ω(B) · **Method version:** `explanation-boundary-1.0` · **Date:** 2026-06-08.

## 1. Objective
Separate model-limited residual (removable by better models) from data/representation-limited
residual (irreducible) — i.e. if our knowledge were 10× better, how much residual would remain?

## 2. Method
Use Phase P's decisive result as the asymptote: out-of-sample, co-occurrence and higher-order
(motif/grammar) models do **not** beat frequency. So a perfect model of the discovered
*representation* cannot push held-out NLL below the frequency floor. The model-limited residual
is therefore ~0; the residual is data/representation-limited.

## 3. Results
| quantity | value |
|---|--:|
| in-sample gain a 10× model could add (overfitting) | ~negative (no compression) |
| **generalizable gain from better models** | **0.0** |
| **data/representation-limited residual** | **79.6%** |
| model-limited residual | **0.0%** |

## 4. Interpretation
**The ~80% residual is data/representation-limited, not model-limited.** Better modeling of the
co-occurrence representation would not reduce it — Phase P already proved that adding structure
does not improve generalization. The boundary is not "we need a smarter model"; it is "this
representation contains no more generalizable information." The only way past the frontier would
be a genuinely *different representation* of the text (e.g. phonological, or external grounding —
the latter forbidden), not a better model of the same co-occurrence data.

## 5. Falsification Attempts
The "more modeling will help" hypothesis is falsified by Phase P's 0/7-regime, −3.32-bit
out-of-sample result, which this phase adopts as the empirical ceiling.

## 6. Limitations
The extrapolation is bounded by what Phase P tested (pairwise + directional co-occurrence); a
fundamentally different representation is outside its scope and could, in principle, explain
more — that remains genuinely unknown.

## 7. Conclusion
**The residual is data/representation-limited (~80%); a 10× better model of the same
representation yields ~0 generalizable gain.** The frontier is saturated for co-occurrence.

Source: `generated/explanation_boundary/future_knowledge.json`.
