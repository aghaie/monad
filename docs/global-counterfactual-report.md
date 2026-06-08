# Global-Counterfactual Report — Phase Φ (G)

**Phase:** Φ · **Method version:** `counterfactual-discovery-1.0` · **Date:** 2026-06-08.

## 1. Objective
Estimate the global feasible volume: how many complete Quran-like corpora satisfy all discovered
constraints simultaneously?

## 2. Method
Global feasible volume = the typical-set size of the full-corpus generator under the constraint set,
computed analytically as 2^(N·H) with N = 44,431 slots and H the per-draw entropy.

## 3. Results
**Global feasible volume ≈ 2^377,803** frequency-valid Quran-like corpora. The structural (co-occurrence
form) constraint filters this to coherent corpora, but does not measurably reduce the *lexical-identity*
volume (Phase P).

## 4. Interpretation
The global space of valid alternative corpora is **astronomically large** — 2^377,803 is beyond any
physical enumeration. Requiring coherence (the co-occurrence form) restricts to the subspace of coherent
texts, but within that subspace the lexical identity is essentially free. So at the global scale, the
actual Quran is one coherent realization among an unimaginably vast set of equally-valid alternatives;
the constraints do not single it out.

## 5. Falsification Attempts
"The constraints make the Quran globally near-unique" is falsified by the 2^377,803 feasible volume.

## 6. Limitations
The volume is exact in log₂; the form constraint's effect on the count is bounded by Phase P (≈0 on
identity) and is large on coherence (z ≈ 306) — a qualitative, not bit-exact, filter.

## 7. Conclusion
**Global feasible volume ≈ 2^377,803** — astronomically large. The actual Quran is one of an
unenumerable set of equally constraint-valid corpora.

Source: `generated/counterfactual/global_counterfactuals.json`.
