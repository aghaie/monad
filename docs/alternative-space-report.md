# Alternative-Space Report — Phase Φ (B, C, G)

**Phase:** Φ · **Method version:** `counterfactual-discovery-1.0` · **Date:** 2026-06-08.

## 1. Objective
Measure the size of the space of structurally-valid alternative Quran-like texts, and where the actual
Quran lies within it.

## 2. Method
The alternative space under a constraint set = the max-entropy distribution matching it; its size is
the typical-set size **2^(N·H)**, computed **analytically and exactly** (strictly better than the
spec's Monte-Carlo estimate). N = 44,431 root-slots; H = per-draw entropy of the constrained
generator. Generator levels L0–L4 add structural constraints cumulatively.

## 3. Results
| quantity | value |
|---|--:|
| root-slots (N) | 44,431 |
| H per draw — uniform | 10.681 bits |
| H per draw — frequency | 8.503 bits |
| **log₂(alternatives), frequency-valid** | **377,803** → ~2^377,803 |
| log₂(alternatives), uniform | 474,654 |
| structural constraints' additional generalizable reduction | ~0 bits |

## 4. Interpretation
The space of frequency-valid alternative Quran-like texts is **astronomically large — ~2^377,803**.
Frequency shrinks it from the uniform ~2^474,654 (a ~20% reduction in per-draw choice). The structural
constraints (motif/dependency/grammar/locality) add **~0 generalizable reduction** to the
lexical-identity space (Phase P) — but note (see `rare-choice-report.md`) that requiring the actual
*co-occurrence form* is a strong filter relative to random text. The two effects live on different
axes: structure constrains coherence (form), frequency weakly constrains identity.

## 5. Falsification Attempts
The count is exact (analytic), not estimated; the structural-reduction = 0 claim is the lexical-
identity reduction, attacked and confirmed by Phase P.

## 6. Limitations
The frequency-space count treats draws as independent; the actual text has co-occurrence structure (a
form constraint), addressed separately. "Astronomically large" is exact in log₂, beyond enumeration in
absolute terms.

## 7. Conclusion
**The structurally-valid alternative space is ~2^377,803 — astronomically large.** Frequency reduces it
~20%; structural constraints reduce the lexical-identity space by ~0.

Source: `generated/counterfactual/alternative_space.json`, `global_counterfactuals.json`.
