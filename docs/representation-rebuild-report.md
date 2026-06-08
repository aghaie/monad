# Representation-Rebuild Report — Phase Ξ (D)

**Phase:** Ξ · **Method version:** `foundation-audit-1.0` · **Date:** 2026-06-08.

## 1. Objective
Rebuild the corpus's core measurements under completely different representations — no representation
privileged — and see what changes.

## 2. Method
At root, lemma, and word levels, recompute three representation-comparable invariants: frequency skew
(Gini), explained-by-frequency / residual fraction (per-unit NLL), and coherence (mean PPMI) vs a
configuration null (K=30). (Ayah/surah/sequence/positional are different granularities; root/lemma/word is
the comparable cross-representation rebuild.)

## 3. Results
| level | V | explained (freq) | residual | freq Gini | coherence real | null p95 | beyond null? |
|---|--:|--:|--:|--:|--:|--:|:--:|
| root | 1,642 | 0.204 | 0.796 | 0.799 | 1.766 | 1.316 | yes |
| lemma | 4,832 | 0.249 | 0.751 | 0.833 | 2.235 | 1.732 | yes |
| word | 12,204 | 0.276 | 0.724 | 0.828 | 2.180 | 1.825 | yes |

## 4. Interpretation
The three measurements are **stable across representations**: frequency is strongly skewed (Gini ≈ 0.80–
0.83) at every level; frequency explains only ~20–28% (residual ~72–80%) at every level; and real
coherence exceeds the frequency null at every level. The absolute numbers shift slightly (more units →
slightly less residual) but the **qualitative facts are invariant**. The representation choice (root vs
lemma vs word) does not change the core information-theoretic picture.

## 5. Falsification Attempts
The rebuild is itself the test: if the invariants were root-space artifacts, lemma/word would differ
qualitatively. They do not.

## 6. Limitations
Three lexical representations are compared; a non-lexical representation (phonological/syntactic) is out of
scope and could differ — genuinely unknown.

## 7. Conclusion
**The information-theoretic invariants (frequency skew, ~75–80% residual, coherence beyond null) hold at
root, lemma, and word** — they are not artifacts of root space.

Source: `generated/foundation_audit/representation_rebuilds.json`.
