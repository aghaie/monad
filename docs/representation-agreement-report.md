# Representation-Agreement Report — Phase Ξ (E)

**Phase:** Ξ · **Method version:** `foundation-audit-1.0` · **Date:** 2026-06-08.

## 1. Objective
Measure which discoveries appear regardless of representation.

## 2. Method
Three representation-invariance checks across root/lemma/word: frequency-skew high (Gini > 0.6), large
residual (> 0.5), coherence beyond the frequency null.

## 3. Results
| invariant check | holds across root/lemma/word? |
|---|:--:|
| frequency skew high (Gini > 0.6) | **yes** |
| large residual (> 0.5) | **yes** |
| coherence beyond the null | **yes** |

**3 / 3 invariants agree across representations.** Residual by representation: root 0.796, lemma 0.751,
word 0.724.

## 4. Interpretation
All three information-theoretic facts are **representation-invariant**: they appear whether the unit is a
root, a lemma, or a word. These — frequency dominance, the large lexical residual, and the existence of
real coherence beyond frequency — are the findings that survive the change of coordinate system. The
specific concept/proposition graph is **not** among them (it is concept-clustering-dependent, A3).

## 5. Falsification Attempts
The agreement test is the representation attack; the three invariants survive it; the conceptual edifice
(not measured here as it cannot be rebuilt cross-representation without re-clustering) is excluded by the
Phase-11 ARI evidence.

## 6. Limitations
Agreement is over the three computable invariants; concept-level discoveries are classified via prior
evidence, not re-clustered per representation.

## 7. Conclusion
**3/3 information-theoretic invariants agree across representations** — frequency skew, large residual, and
coherence beyond null are representation-invariant.

Source: `generated/foundation_audit/representation_agreement.json`.
