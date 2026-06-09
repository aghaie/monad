# Q9 — Name-Removal Report (Phase ΩΣ)

**Method:** `foundational-questions-1.0` · corpus-only · deterministic.

## 1. Objective
Remove all people, places, and proper names; rebuild every structure. **How much survives?**

## 2. Method
Delete all `POS=PN` proper-noun tokens, then recompute the three representation-comparable invariants at
root level — frequency Gini, frequency-residual fraction, and coherence-beyond-configuration-null — before vs
after removal.

## 3. Results
| invariant | before | after | ratio |
|---|--:|--:|--:|
| frequency Gini | 0.799 | 0.791 | 0.990 |
| residual fraction | 0.796 | 0.806 | 1.013 |
| coherence beyond null | yes | yes | retained |

Proper nouns are **5.0%** of all tokens (3,911 / 77,915).

## 4. Interpretation
Structure is **name-independent**. Names are a small fraction (5%) of the corpus, and removing them leaves
the frequency skew, the ~80% residual, and the real co-occurrence coherence essentially unchanged. The
Quran's measurable structure does not rest on proper names — the system of relations among common roots is
what carries it.

## 5. Falsification Attempts
The post-removal coherence is re-tested against a fresh configuration null and still exceeds it — the
surviving structure is not a frequency artifact. Subsampling (stability report) leaves the conclusion intact.

## 6. Limitations
PN tagging is taken from morphology; a handful of borderline names could shift the 5% slightly, not the
conclusion.

## 7. Conclusion
**MOST survives (~95%).** Names are 5% of tokens; with them removed, all three structural invariants are
unchanged. Quranic structure is name-independent.
