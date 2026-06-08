# Representation-Sensitivity Report — Phase Ψ (F)

**Phase:** Ψ · **Method version:** `residual-nature-1.0` · **Date:** 2026-06-08.

## 1. Objective
Test whether the ~80% residual is an artifact of root-space, or survives changes of representation
(root / lemma / word).

## 2. Method
Recompute the explained fraction (frequency) and residual fraction at each level (root, lemma,
surface word form), using the same per-unit NLL framework.

## 3. Results
| level | vocabulary | residual fraction |
|---|--:|--:|
| root | 1,642 | 79.6% |
| lemma | 4,832 | 75.1% |
| word (form) | 12,204 | 72.4% |

## 4. Interpretation
The large residual **persists across all representations** (72–80%). It is **not** a root-space
artifact: whether the unit is a root, a lemma, or a surface word, ~three-quarters of the per-unit
selection information is unexplained by frequency. The residual is a property of the text's lexical
content at every granularity, not of one analytic choice.

## 5. Falsification Attempts
"The residual is a representation artifact" is falsified — it survives root→lemma→word changes with
similar magnitude.

## 6. Limitations
Three lexical representations were tested; a fundamentally non-lexical representation (phonological,
syntactic-dependency) is outside scope and could differ — genuinely unknown.

## 7. Conclusion
**The residual survives representation changes (72–80% at root/lemma/word)** — it is not a root-space
artifact but an intrinsic property of the text's lexical content.

Source: `generated/residual_nature/representation_results.json`.
