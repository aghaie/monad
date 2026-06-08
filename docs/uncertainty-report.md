# Uncertainty Report — Phase Δ (D)

**Phase:** Δ · **Method version:** `decision-architecture-1.0` · **Date:** 2026-06-08.

## 1. Objective
How does the system behave under uncertainty (شك/ظن/غيب — doubt, conjecture, the unseen)?

## 2. Method
Directed flow into and out of the uncertainty node.

## 3. Results
- **Into uncertainty**: knowledge → uncertainty (dir 0.69, support 114) — the strongest.
- **Out of uncertainty**: uncertainty → consequence (0.71, 17), uncertainty → resolution (0.65, 23),
  uncertainty → action (0.61, 51), uncertainty → choice (0.55, 112).
- `uncertainty → resolution` is bootstrap-stable.

## 4. Interpretation
The dominant uncertainty edge — **knowledge → uncertainty** — is, on inspection, the fixed collocation
*عالِم الغيب* ("knower of the unseen"): علم precedes غيب as a phrase, not as a decision operation. So the
strongest "uncertainty" structure is **not** decision-under-uncertainty but a lexical collocation. The
genuinely decision-shaped uncertainty edges (uncertainty → choice/action/resolution) are weaker and
mostly do not survive the frequency null. The honest reading: the corpus does **not** robustly encode a
distinct "behaviour under uncertainty" architecture beyond frequency; what survives is a collocation.

## 5. Falsification Attempts
knowledge → uncertainty survives controls but is a collocation, not a decision step; the
decision-shaped uncertainty edges largely collapse under the frequency null.

## 6. Limitations
Uncertainty is operationalized via شك/ظن/غيب; the غيب ("unseen") root carries the collocation that
dominates the result.

## 7. Conclusion
**No robust decision-under-uncertainty architecture emerges**; the strongest uncertainty edge is the
*عالِم الغيب* collocation, not an information-processing step.

Source: `generated/decision_architecture/uncertainty_architecture.json`.
