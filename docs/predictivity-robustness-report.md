# Predictivity-Robustness Report — Phase P (H/I)

**Phase:** P · **Method version:** `predictivity-discovery-1.0` · **Date:** 2026-06-07.
(Spec deliverable "robustness"; named distinctly because Phase 14 owns
`robustness-report.md` — prior phase outputs are immutable.)

## 1. Objective

Determine whether the Phase-P result is stable across holdout regimes, fold counts, mask
fractions, and (for concepts) cross-fold drift — i.e. whether the verdict is a robust
property of the corpus or an artifact of one configuration.

## 2. Method

The primary comparison (S1 vs B0) is recomputed across: 4 regimes (R1 random, R2 contiguous
blocks, R3 forward 25/50/75%, R4 length-stratified); 2 fold counts (k = 5, 10); 3 mask
fractions (single/25%/50%). "Regime passes" iff S1 beats B0 on MRR **and** info-gain > 0.
Concept cross-fold stability is reported as the mean pairwise cosine of per-fold concept
df-vectors (with an explicit caveat on what that does and does not measure).

## 3. Results

**Regime agreement:** S1 beats B0 in **0 of 7** root regimes.

**Cross-regime info-gain (bits, root single):** R1-10 −3.374 · R2 −3.061 · R3-25 −2.542 ·
R3-50 −2.327 · R3-75 −1.750 · R4 −3.366. (All negative.)

**Fold-count sensitivity:** R1 k=5 −3.316 vs k=10 −3.374 (negative, stable).

**Mask-fraction sensitivity:** single −3.316 · 25% −2.156 · 50% −1.107 (negative
throughout; magnitude shrinks with more masking but never crosses 0).

**Concept stability cosine:** 0.9999 (mean), 0.9999 (min) — **see Limitations; this is
near-tautological and is not evidence of clustering stability.**

## 4. Interpretation

The negative root-level result is **uniformly robust**: it does not depend on the split
(random/contiguous/forward/length-stratified), the fold count, or the mask fraction. The
forward regimes (R3) — the hardest, most realistic generalization direction — show the
structure failing *most* (S1 MRR drops to 0.060 at fwd-25). The length-stratified regime
(R4) matches R1, confirming the result is not a length artifact. Contiguous blocks (R2)
match R1, confirming it is not a local-adjacency-leakage artifact. The verdict is therefore
a property of the corpus, not of a configuration.

## 5. Falsification Attempts

The robustness analysis is itself an attempt to find *any* configuration in which structure
beats frequency. None was found (0/7 regimes; 0/9 root cells). The negative verdict
survives every perturbation tried.

## 6. Limitations

- **The concept stability cosine (0.9999) is reported but is misleading and must not be
  read as vindicating concept stability.** It reflects frozen memberships + random folds
  (df-vectors barely move). The real instability bound is Phase-11 ARI = 0.22; per-fold
  re-clustering (variant 2b) was not implemented. Concept-level numbers remain conditioned
  on that untested instability.
- Robustness here means stability of the *negative* result; it does not rule out that a
  *different* structure representation (syntactic, higher-order) might predict — that is an
  open question, not addressed.

## 7. Conclusion

**The negative root-level result is robust across all 7 regimes, both fold counts, and all
3 mask fractions (0/7 regimes pass).** The concept-level signal is non-robust by
construction (untested clustering, frozen-membership circularity). The verdict is stable.

Source: `generated/predictivity/robustness_results.json`.
