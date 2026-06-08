# Phase Ω(B) — Final Report: Explanation Boundary Discovery Engine

**Method version:** `explanation-boundary-1.0` · **Date:** 2026-06-08. Deterministic,
byte-identical (`validate_explanation_boundary.py --rebuild`). Measurement only — proves and
disproves nothing, fills no gap with interpretation, and writes **"we do not know"** where the
model stops.

*(Named Ω(B): the earlier Phase Ω — World Model Discovery Engine — keeps its outputs and
`phase-omega-final-report.md`; this phase is separate, under `generated/explanation_boundary/`.)*

## 1. Objective
Measure the **explanation boundary** of the project: after applying all stable discoveries, how
much of the Quran's structure is explained, and how much remains unexplained?

## 2. Method (summary)
The structural object is the ayah×root incidence. Explanation is measured as in-sample
compression (bits) of per-root selection under cumulative models — uniform → frequency →
co-occurrence (pairwise PPMI) — with motifs/grammar subsumed as higher-order co-occurrence. The
residual is extracted, characterized, attacked with a frequency-preserving null, and extrapolated
(Phase P as the out-of-sample ceiling) to separate model-limited from data-limited residual.

## 3. Results (headline)
| quantity | value |
|---|--:|
| NLL uniform / frequency / co-occurrence (bits) | 10.68 / 8.50 / 14.53 |
| **explained (generalizable, = frequency)** | **20.4%** |
| **unexplained (residual)** | **79.6%** |
| residual co-occurrence signal | 1.731 bits (> null p95 1.283 → real) |
| generalizable gain from better models | 0.0 |
| data-limited residual | 79.6% |

---

## The five final questions

### Q1 — How much of the Quran's structure is explained by current discoveries?
**~20.4%** — explained entirely by **lexical frequency**. The discovered relational structure
(proposition network, motifs, grammar, semantics) adds real description but **no generalizable
explanation beyond frequency** (it fails to compress in-sample and does not predict out-of-sample,
Phase P).

### Q2 — How much is unexplained?
**~79.6%.** The majority of the information about which root occurs in which ayah is residual.

### Q3 — Is the unexplained part stronger than the nulls? (YES / NO / PARTIAL)
**PARTIAL.** The residual is **real co-occurrence structure** — its association signal (1.73
bits) exceeds the frequency-preserving null (p95 = 1.28), so it is not noise and not a frequency
artifact. **But it is non-predictive** (Phase P): it cannot be used to explain held-out content.
The residual is **structured but unexplainable** — real, yet beyond the reach of any discovered
model.

### Q4 — Is the current explanation frontier saturated? (YES / NO)
**YES.** A 10×-better model of the co-occurrence representation yields **~0 generalizable gain**
(Phase P: adding structure does not beat frequency out-of-sample, 0/7 regimes, −3.32 bits). The
residual is **data/representation-limited, not model-limited.** The frontier is where frequency
stops, and more modeling of the same representation will not move it.

### Q5 — What is the largest unknown region of the Quran?
**The specific referential/lexical content of ayahs — which concept/root occurs where, beyond
frequency.** This is the ~80% residual. It is real structure (it beats the nulls) but
unexplainable by any model Monad has built. It is the **same referential layer that Phase Σ
(relational-not-referential meaning) and the World-Model phase (semantic non-emergence) showed
never emerges structurally.** Per the phase's prohibition: **we do not know it**, and we do not
fill it with interpretation.

---

## 4. Interpretation
Phase Ω(B) places a number on the limit the whole project has been circling. Monad's
generalizable explanatory power over the Quran's structure is **~20%, and it is frequency.** The
remaining **~80%** is genuine structure (it survives every null) that **no discovered model can
explain or predict** — and, per Phase P, no better model of this representation will. The honest
shape of the result is a triangle: the residual is *not random* (Q3/null attack), *not explainable*
(Phase P), and *not model-limited* (Q4/future-knowledge). It is the irreducible, referential
content of the text under a co-occurrence representation — measured, bounded, and left
explicitly unknown.

## 5. Falsification Attempts
Every explanatory claim was attacked: the co-occurrence layer was given the easiest case
(in-sample) and failed to compress; the residual was attacked with a frequency-preserving null and
did not collapse; the "better models will help" hypothesis was rejected via Phase P. The 20/80
frontier survives.

## 6. Limitations
- "Explanation" is operationalized as per-root-selection compression; the absolute 20/80 split is
  representation-specific, though the frequency-saturation conclusion is robust.
- The structure NLL is calibration-sensitive (λ=1); but Phase P's calibration-free held-out result
  yields the same conclusion, so the verdict does not depend on it.
- The frontier is for the **co-occurrence representation** Monad built. A fundamentally different
  representation (phonological, or external grounding — forbidden) could, in principle, explain
  more. That is genuinely unknown and is not claimed either way.

## 7. Conclusion
**~20% of the Quran's per-root structure is explained (by frequency); ~80% is unexplained.** The
unexplained residual is real co-occurrence structure (beats the nulls) that is non-predictive
(Phase P) and data/representation-limited (Q4) — structured, genuine, and beyond current
explanation. The largest unknown region is the referential content of the text — which Monad
measures precisely and, by design, leaves as **"we do not know."**

---

### Outputs
`generated/explanation_boundary/`: 9 data products + `explanation_manifest.json`. Tooling:
`scripts/build_explanation_boundary.py`, `scripts/validate_explanation_boundary.py`. Reports:
`discovery-inventory-report.md`, `explanatory-power-report.md`, `explanation-redundancy-report.md`,
`residual-structure-report.md`, `residual-characterization-report.md`, `null-attack-report.md`,
`explanation-frontier-report.md`, `future-knowledge-report.md`, this report.

### Reproduce
```bash
python3 scripts/build_explanation_boundary.py
python3 scripts/validate_explanation_boundary.py --rebuild
```

**Phase Ω(B) complete. No further phase started automatically.**
