# Phase ΩΣ — Falsification Report

**Method:** `foundational-questions-1.0` · corpus-only · deterministic.

## 1. Objective
Attack every answer with the project's null battery and remove any that collapses.

## 2. Method
Per-question falsification matched to the claim type: configuration/frequency null for co-occurrence
inferences (Q9 coherence after name removal), within-surah order-shuffle null for geometry (Q12),
INTG-label baseline for interrogative lift (Q14). Census ratios (Q3, Q7, Q8, Q11) are exact corpus facts and
are flagged as not co-occurrence-falsifiable. A revelation-order null (Q10) is **not constructible** without
external chronology and is stated as such.

## 3. Results
| question | test | outcome |
|---|---|---|
| Q9 name-removal | config-null coherence after removal | **survives** (coherence still beyond null) |
| Q12 geometry | within-surah order-shuffle null | **fails** (z = −1.46, below null) → NO geometry |
| Q3/Q7/Q8/Q11 | exact census (no inference) | descriptive facts, not falsifiable |
| Q14 interrogative lift | frequency baseline | reduces to frequency (not a beyond-frequency finding) |
| Q1/Q2/Q5/Q13/Q14 (semantic) | — | collapse to frequency or UNKNOWN |
| Q10 order | revelation-order null not constructible | UNKNOWN (external data forbidden) |

## 4. Interpretation
Only **two** answers carry genuine null tests: Q9 (name-removal) **survives**, Q12 (geometry) **fails**. The
census-based answers (Q3, Q7, Q8, Q11) are exact facts. Everything semantic (Q1, Q2, Q5, Q13, Q14) either
collapses to the frequency hub or is UNKNOWN. This is the honest, pre-registered pattern: the corpus confirms
structural facts and refuses semantic ones.

## 5. Falsification Attempts
This report *is* the falsification stage; nothing was protected. The geometry claim was actively falsified.

## 6. Limitations
Only well-posed nulls are run; for questions that are blocked by construction (Q5, Q10), the absence of a
null is reported rather than faked.

## 7. Conclusion
**Q9 survives; Q12 is falsified; census facts stand; the semantic questions collapse or are UNKNOWN.** No
answer was preserved that could not withstand its applicable null.
