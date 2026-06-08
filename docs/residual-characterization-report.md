# Residual-Characterization Report — Phase Ω(B) (F)

**Phase:** Ω(B) · **Method version:** `explanation-boundary-1.0` · **Date:** 2026-06-08.

## 1. Objective
Determine the character of the ~80% residual: is it random, or structured (clustered,
long-range, hierarchical, cyclic, compressible)?

## 2. Method
Measure the co-occurrence signal the frequency model ignores: the mean pairwise PPMI among
co-present roots (over a 2,000-ayah sample). Positive mean PPMI ⇒ the residual carries real
association structure, not noise.

## 3. Results
- Residual co-occurrence signal: **mean PPMI = 1.731 bits** (> 0) — co-present roots are
  positively associated beyond their marginals.
- This signal exceeds the frequency-null 95th percentile (`null-attack-report.md`).

## 4. Interpretation
**The residual is NOT random — it is structured co-occurrence.** Roots that share an ayah are
genuinely associated (mean PPMI 1.73 bits), the same relational network Phase 17 found at 3.9×
the frequency null. **But this structure does not predict held-out content (Phase P).** So the
residual is the paradoxical object the whole project converges on: **structured but
unexplainable** — real association that carries no generalizable predictive/explanatory
information.

## 5. Falsification Attempts
The "residual is just noise" hypothesis is falsified (mean PPMI > 0, beats null). The "residual
is explainable structure" hypothesis is also falsified (Phase P non-predictiveness). Both
horns are reported.

## 6. Limitations
Characterization is at the pairwise level; higher-order residual structure exists but Phase
9/12/P show it is also non-generalizable.

## 7. Conclusion
**The residual is structured co-occurrence (mean PPMI 1.73 bits, beats nulls) yet
unexplainable (non-predictive).** Real structure, no usable explanation.

Source: `generated/explanation_boundary/residual_characterization.json`.
