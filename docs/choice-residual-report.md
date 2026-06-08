# Choice-Residual Report — Phase Φ (H, I)

**Phase:** Φ · **Method version:** `counterfactual-discovery-1.0` · **Date:** 2026-06-08.

## 1. Objective
Measure the choice-residual after all constraints, and compare it to the Phase Ψ residual: is the
unexplained ~80% merely freedom of choice, or unusually constrained choice?

## 2. Method
Choice-residual = the free lexical choice remaining after the constraints = H_choice per draw (the
generator entropy the constraints cannot remove). Compare to Phase Ψ's ~80% irreducible lexical
residual.

## 3. Results
| quantity | value |
|---|--:|
| choice-residual per draw | 8.503 bits |
| choice-residual total | ~377,803 bits |
| fraction of uniform choice remaining | 79.6% |
| structural constraints reduce residual by | 0 bits |

## 4. Interpretation
**The Phase Ψ residual IS the choice-residual.** Ψ measured ~80% irreducible lexical specificity; Φ
shows that this residual is exactly the **free lexical choice** that the discovered constraints leave
open — ~8.50 bits/draw the structure does not reduce. So the unexplained ~80% is **freedom of choice
within weak (frequency-dominated) constraints**, not an unusually constrained selection. The two phases
converge: Ψ said "irreducible lexical specificity"; Φ says "that specificity is free choice the
constraints do not determine."

## 5. Falsification Attempts
"The residual is unusually constrained choice" is falsified — the residual equals the generator's free
entropy; constraints reduce it by 0 beyond frequency.

## 6. Limitations
Residual is measured as per-draw entropy; the coherence (form) constraint is real but acts on a
different axis and does not reduce identity freedom.

## 7. Conclusion
**The Phase Ψ residual = the choice-residual = ~8.50 bits/draw of free lexical choice (~80%).** The
unexplained 80% is freedom of choice within weak constraints, not constrained selection.

Source: `generated/counterfactual/choice_residual.json`.
