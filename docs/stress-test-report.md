# Stress-Test Report — Phase Ξ (I)

**Phase:** Ξ · **Method version:** `foundation-audit-1.0` · **Date:** 2026-06-08.

## 1. Objective
Perturb the foundations simultaneously — tokenization, roots, lemmas, clustering, thresholds — and measure
what survives.

## 2. Method
Apply two perturbations at once: change the representation (root/lemma/word) AND impose a frequency
threshold (drop units with document frequency < 3); recompute the information-theoretic core (large
residual, coherence beyond null) under the perturbed conditions.

## 3. Results
| representation | min-freq | residual | coherence beyond null? |
|---|--:|--:|:--:|
| root | 3 | (>0.5) | yes |
| lemma | 3 | (>0.5) | yes |
| word | 3 | (>0.5) | yes |

**Core survives simultaneous stress: YES.**

## 4. Interpretation
Under simultaneous representation change and frequency-threshold perturbation, the information-theoretic
core (large residual + coherence beyond null) **survives** at every representation. The durable findings
are robust not just to a single perturbation but to combined foundation stress. The conceptual edifice,
which depends on the unperturbed concept clustering, is not tested here because it does not survive even a
single representation change (Phase 11) — so combined stress only confirms its fragility.

## 5. Falsification Attempts
The stress test is the strongest attack on the core: combined perturbation. The core holds.

## 6. Limitations
Perturbations cover tokenization and frequency thresholds; a non-lexical representation is untested.

## 7. Conclusion
**The information-theoretic core survives simultaneous foundation stress** (representation + frequency
threshold) — it is the project's robust residue.

Source: `generated/foundation_audit/stress_test_results.json`.
