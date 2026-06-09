# Phase ΩΣ — Representation Independence Report

**Method:** `foundational-questions-1.0` · corpus-only · deterministic.

## 1. Objective
Verify whether the surviving findings hold across representation spaces (root / lemma / word).

## 2. Method
Recompute the three structural invariants that underpin the answerable questions — frequency Gini,
frequency-residual fraction, coherence-beyond-configuration-null — at root, lemma, and word level.

## 3. Results
| level | Gini | residual | coherence beyond null |
|---|--:|--:|:--:|
| root | 0.799 | 0.796 | yes |
| lemma | 0.833 | 0.751 | yes |
| word | 0.828 | 0.724 | yes |

Invariant checks: frequency-skew-high **3/3**, large-residual **3/3**, coherence-beyond-null **3/3** →
**3/3 agree**.

## 4. Interpretation
The structures behind the surviving answers — the frequency hub (Q1, Q2, Q4, Q13, Q14), the ~80% residual,
and the real coherence (Q7, Q9) — are **representation-invariant**: high skew, large residual, and
coherence-beyond-null all hold at root, lemma, and word. The findings are not artifacts of the root
tokenization. (This reproduces, independently, the Phase Ξ result.)

## 5. Falsification Attempts
Coherence is re-tested against a fresh configuration null at each representation; it clears it at all three.

## 6. Limitations
Representation comparison covers lexical tokenizations (root/lemma/word); non-lexical representations
(phonological, syntactic) are untested.

## 7. Conclusion
**Representation-independent (3/3 at every level).** Every surviving answer rests on invariants that hold
across root, lemma, and word.
