# Residual-Structure Report — Phase Ω(B) (E)

**Phase:** Ω(B) · **Method version:** `explanation-boundary-1.0` · **Date:** 2026-06-08.

## 1. Objective
Extract the residual — the part of the Quran's structure the maximum model cannot explain.
This is the phase's most important output.

## 2. Method
Residual = Quran structure − explained structure, measured as the fraction of per-root
selection information remaining after the maximum generalizable model (frequency).

## 3. Results
- **Generalizable residual = 79.6%** of the per-root selection information (8.50 of 10.68
  bits remain after frequency).
- In-sample residual after the co-occurrence model is even larger (it fails to compress), so
  the post-frequency residual is the meaningful floor.

## 4. Interpretation
After everything Monad can generalizably explain, **~80% of the information about which root
occurs in which ayah is residual.** This is not a small correction term — it is the majority
of the structure. It corresponds to the *specific lexical/referential content* of each ayah:
which particular concepts appear where, beyond what their frequencies dictate.

## 5. Falsification Attempts
The residual is attacked in `null-attack-report.md` (is it real or noise?) and characterized
in `residual-characterization-report.md`.

## 6. Limitations
The residual fraction is tied to the per-root operationalization; its qualitative dominance
(majority of information) is robust to that choice.

## 7. Conclusion
**The residual is ~80% — the majority of the Quran's per-root structure is unexplained by the
maximum generalizable model.** It is the specific referential content of the text.

Source: `generated/explanation_boundary/residual_structure.json`.
