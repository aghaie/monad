# Decision-Stability Report — Phase Δ (K)

**Phase:** Δ · **Method version:** `decision-architecture-1.0` · **Date:** 2026-06-08.
(Named distinctly to avoid the generic `stability-report.md`.)

## 1. Objective
Test whether decision edges are reproducible under resampling: bootstrap, subsampling, threshold sweep.

## 2. Method
Bootstrap (K=200) directionality CI; subsampling (drop 10/20/40%, K=50 each) persistence; an edge is
"stable" iff its bootstrap CI excludes 0.5 and it persists ≥ 90% under subsampling.

## 3. Results
**13 of 45 edges are directionally stable** (e.g. condition→choice, condition→action, knowledge→resolution,
uncertainty→resolution, conflict→knowledge, condition→consequence). But — as in Phase Z — **stability is
not reality**: of these 13 reproducible edges, only **3 also exist beyond the frequency null**
(condition→choice, knowledge→resolution, knowledge→uncertainty). The other 10 are reproducibly-directional
*frequency artifacts*.

## 4. Interpretation
Reproducibility over-credits the architecture by ~4× (13 stable vs 3 real). Combining stability with the
falsification battery leaves **3 full survivors** — and they do not form a connected agent. The stability
battery alone would have suggested a 13-edge architecture; the frequency null shows it is mostly artifact.

## 5. Falsification Attempts
The stability battery is corroborated by the frequency null: 10 of 13 "stable" edges are frequency
artifacts and are removed.

## 6. Limitations
Bootstrap uses a within-ayah flow approximation (corroborated by exact subsampling).

## 7. Conclusion
**13 edges are reproducibly directional, but only 3 are also real beyond frequency.** Stability alone
over-credits the decision architecture; the robust core is 3 isolated edges.

Source: `generated/decision_architecture/decision_stability.json`.
