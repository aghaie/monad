# Explanation-Redundancy Report — Phase Ω(B) (C)

**Phase:** Ω(B) · **Method version:** `explanation-boundary-1.0` · **Date:** 2026-06-08.
*(Named distinctly: Phase 14 owns `redundancy-report.md`.)*

## 1. Objective
Determine which discovery layers carry independent explanatory information and which only
re-describe earlier layers.

## 2. Method
Measure the marginal bits each cumulative layer removes (frequency → co-occurrence → motif/
grammar), separating in-sample and generalizable information.

## 3. Results
| layer | marginal bits removed | independent (generalizable)? |
|---|--:|---|
| frequency | +2.18 | **yes** |
| co-occurrence (pairwise PPMI) | −6.03 (worse) | **no** |
| motifs / grammar (higher-order co-occurrence) | subsumed | **no** |

## 4. Interpretation
**Only the frequency layer carries independent generalizable explanatory information.** The
co-occurrence layer is fully redundant for explanation (worse in-sample by calibration; 0
out-of-sample by Phase P). Motifs (Phase 9) and grammar (Phase 12) are higher-order
co-occurrence — re-descriptions of the same relational signal — and inherit its
non-generalizability. The project's discoveries beyond frequency are *real descriptions* but
*redundant explanations*.

## 5. Falsification Attempts
The redundancy claim is the strongest possible attack on the project's own structure findings;
they survive as descriptions but not as independent explanatory information.

## 6. Limitations
Redundancy is judged on per-root compression / prediction; a representation outside
co-occurrence (e.g. phonological) is untested here.

## 7. Conclusion
**Frequency is the only non-redundant explanatory layer.** Co-occurrence, motifs, and grammar
add description, not generalizable explanation.

Source: `generated/explanation_boundary/redundancy.json`.
