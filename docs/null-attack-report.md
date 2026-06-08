# Null-Attack Report — Phase Ω(B) (G)

**Phase:** Ω(B) · **Method version:** `explanation-boundary-1.0` · **Date:** 2026-06-08.

## 1. Objective
Attack the residual with a strong null: is the residual's co-occurrence structure real, or
reproducible by a frequency-preserving model?

## 2. Method
Frequency-preserving configuration null (curveball): preserve every root's document frequency
and every ayah's size, destroy co-occurrence; recompute the residual co-occurrence signal
(mean PPMI). 50 realizations → null band; the residual survives iff the real signal exceeds the
null 95th percentile.

## 3. Results
| quantity | bits |
|---|--:|
| real residual co-occurrence signal | 1.731 |
| null mean | 1.256 |
| null 95th percentile | 1.283 |

**Residual structure survives the null: YES** (1.731 > 1.283).

## 4. Interpretation
The residual's co-occurrence is **genuine** — not reproducible by a frequency-preserving
scramble. This confirms (independently of Phase 17) that a real relational network underlies
the residual. But "real" is not "explainable": the same structure is non-predictive (Phase P).
So the residual **survives the null yet remains unexplainable** — exactly the PARTIAL verdict
of Q3.

## 5. Falsification Attempts
This report *is* the null attack. The residual does not collapse; the "residual is a frequency
artifact" hypothesis is rejected. (The complementary "residual is explainable" hypothesis was
rejected by Phase P.)

## 6. Limitations
50 realizations give a stable null band (spread < 0.03 bits); the margin (0.45 bits) far
exceeds it. A node/root-level null was used; a syntactic null would be stricter but could only
shrink, not create, the margin.

## 7. Conclusion
**The residual is real co-occurrence structure (beats the frequency null) — but, per Phase P,
non-predictive.** Structured, genuine, and unexplained.

Source: `generated/explanation_boundary/null_attack.json`.
