# Local-Counterfactual Report — Phase Φ (F)

**Phase:** Φ · **Method version:** `counterfactual-discovery-1.0` · **Date:** 2026-06-08.

## 1. Objective
For an ayah, measure how many small modifications preserve the discovered structure — the local density
of valid alternatives.

## 2. Method
Per-ayah alternative entropy = k · H_choice (the log₂ count of frequency-valid size-k root-sets), with
the co-occurrence form constraint treated as in `rare-choice-report.md`.

## 3. Results
Per-ayah alternative entropy ≈ k · 8.503 bits — for a typical 7-root ayah, ~2^60 frequency-valid
alternative root-sets. Locally, the number of structure-preserving modifications is enormous: each ayah
sits in a vast neighbourhood of valid alternatives.

## 4. Interpretation
At the local (ayah) level, the actual choice is one of an astronomically large set of structure-
preserving alternatives. Small modifications that preserve the frequency and (statistical) co-occurrence
profile are abundant — the actual ayah is not locally pinned down by the constraints. The local geometry
mirrors the global: weakly-constrained lexical identity within a coherent form.

## 5. Falsification Attempts
"The actual ayah is locally near-unique" is falsified — each ayah has ~2^(k·8.5) valid local
alternatives.

## 6. Limitations
Local alternative counts are analytic (per-draw entropy); exact enumeration is infeasible and
unnecessary given the magnitude.

## 7. Conclusion
**Each ayah sits in a vast neighbourhood of structure-preserving alternatives (~2^(k·8.5)).** Local
choice is weakly constrained.

Source: `generated/counterfactual/ayah_counterfactuals.json`.
