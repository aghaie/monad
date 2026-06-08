# Selection-Pressure Report — Phase Φ (D)

**Phase:** Φ · **Method version:** `counterfactual-discovery-1.0` · **Date:** 2026-06-08.

## 1. Objective
Measure how much each discovered constraint reduces the alternative space, and rank them.

## 2. Method
Compute bits removed per constraint on two axes: (a) co-occurrence FORM — how atypical the actual
clustering is vs frequency-random text (z-score); (b) lexical IDENTITY — bits removed from the uniform
per-draw choice.

## 3. Results
| rank | constraint | axis | effect |
|---|---|---|---|
| 1 | co-occurrence structure (dependency/motif) | **form** | **strong** — actual text z ≈ 306 more clustered than frequency-random |
| 2 | frequency | **identity** | removes 20.4% of the uniform per-draw choice (~96,851 bits) |
| 3 | consistency / hub / locality | — | ~0 independent reduction (generic / = frequency / homogeneous) |

## 4. Interpretation
Selection pressure acts on **two different axes**. On **form**, co-occurrence structure is a *strong*
constraint — the actual Quran is z ≈ 306 more clustered than random frequency-matched text (it is a
*coherent* text, as any real text is; random frequency-draws are word-salad). On **identity**, only
frequency constrains (20.4%); the co-occurrence structure removes **0 generalizable bits** of
lexical-identity freedom (Phase P), because it constrains *which roots cluster*, not *which specific
identity occurs*. So the strongest selection pressure shapes coherence, not word choice.

## 5. Falsification Attempts
"Structure reduces lexical-identity freedom" is falsified (Phase P: 0 generalizable). "Structure is
weak overall" is also falsified (z ≈ 306 on form). Both are reported on their proper axes.

## 6. Limitations
The form/identity split is the honest reconciliation of a strong structural z-score with a zero
generalizable identity reduction; finer attribution per constraint is bounded by Phase P/17.

## 7. Conclusion
**Two axes:** co-occurrence structure strongly selects coherent FORM (z ≈ 306); frequency weakly
selects IDENTITY (20%); structure adds 0 to identity. The specific word choices are shaped by neither.

Source: `generated/counterfactual/selection_pressure.json`.
