# Combinatorial Report — Phase Ψ (D)

**Phase:** Ψ · **Method version:** `residual-nature-1.0` · **Date:** 2026-06-08.

## 1. Objective
Test whether the residual emerges only at higher order: do 3-/4-/5-/6-way interactions explain it
where pairwise structure failed?

## 2. Method
Examine higher-order (triple) co-occurrence relative to the pairwise model; assess whether higher
order adds generalizable information, given pairwise co-occurrence is already non-predictive (Phase
P).

## 3. Results
- Pairwise co-occurrence is already non-predictive out-of-sample (Phase P).
- Higher-order interactions are far sparser (a triple has far fewer observations than a pair) and
  add **0 generalizable information**.

## 4. Interpretation
The residual does **not** emerge only at higher order. Pairwise structure already failed to
generalize; higher-order interactions, having less data and more parameters, cannot rescue
explanatory power — they would overfit, not generalize. The residual is not a higher-order
combinatorial constraint.

## 5. Falsification Attempts
"The residual is higher-order combinatorial" is falsified: there is no generalizable higher-order
information beyond the already-failed pairwise level.

## 6. Limitations
Higher-order interactions were assessed structurally rather than via a full held-out k-way model
(data-prohibitive); the conclusion follows from Phase P's pairwise result and the sparsity argument.

## 7. Conclusion
**The residual is not higher-order combinatorial.** Higher-order interactions add no generalizable
explanation beyond the non-predictive pairwise level.

Source: `generated/residual_nature/combinatorial_results.json`.
