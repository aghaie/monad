# Methodology-Stability Report — Phase Z (H)

**Phase:** Z · **Method version:** `self-methodology-1.0` · **Date:** 2026-06-07.

## 1. Objective

Test whether the directionality of the candidate edges is *stable* under resampling — i.e.
reproducible, not a one-sample accident — via bootstrap, subsampling, and a threshold sweep.
(Stability is necessary but not sufficient; reality beyond frequency/order is tested
separately in the falsification report.)

## 2. Method

- **Bootstrap (K = 200):** resample ayahs with replacement; recompute each edge's
  directionality; 95% CI. Stable-direction iff the CI excludes 0.5.
- **Subsampling:** drop 10/20/40% of ayahs (K = 50 each); fraction of subsamples in which
  the edge keeps direction > 0.5. Persistent iff ≥ 0.90 at every drop level.
- **Threshold sweep:** count candidate edges over MIN_SUPPORT ∈ {5,8,12,20} × dir-margin ∈
  {0.55,0.60,0.65}.
- An edge is **"stable"** iff bootstrap-CI-excludes-0.5 **and** subsample-persistence ≥ 0.90.

## 3. Results

**10 of 85 edges are directionally stable** (CI excludes 0.5 and persist ≥ 0.90):

| edge | dir | boot CI | subsample persist (10/20/40%) |
|---|--:|---|---|
| read → guidance | 0.733 | [0.571, 1.000] | 1.00 / 0.98 / 0.92 |
| read → judge | 0.680 | [1.000, 1.000] | 1.00 / 1.00 / 1.00 |
| ask → remember | 0.676 | [0.600, 1.000] | 1.00 / 1.00 / 0.96 |
| observe → ponder | 0.656 | [1.000, 1.000] | 1.00 / 1.00 / 0.94 |
| listen → knowledge | 0.650 | [0.675, 0.938] | 1.00 / 1.00 / 1.00 |
| **ask → knowledge** | 0.632 | [0.722, 0.964] | 1.00 / 1.00 / 1.00 |
| read → remember | 0.600 | [0.533, 0.938] | 1.00 / 1.00 / 0.92 |
| **observe → misguidance** | 0.591 | [0.680, 0.949] | 1.00 / 1.00 / 1.00 |
| denial → misguidance | 0.568 | [0.679, 0.941] | 1.00 / 1.00 / 0.96 |
| remember → knowledge | 0.567 | [0.545, 0.805] | 1.00 / 1.00 / 0.98 |

Threshold sweep: candidate-edge counts decline smoothly with stricter MIN_SUPPORT and
dir-margin (full grid in `methodology_stability.json`).

## 4. Interpretation

Ten edges are **reproducibly directional** — their direction is not a sampling fluke. But
**stability is not reality.** A reproducible direction can still be exactly what frequency
and text-order alone would produce. The falsification report shows that **8 of these 10
stable edges do NOT exceed the frequency and/or mushaf-order nulls** — their reproducibility
is reproducible-artifact. Only **`ask → knowledge`** and **`observe → misguidance`** are both
stable *and* real beyond the nulls. So the stability battery, on its own, would over-credit
the method by 5× (10 vs 2).

## 5. Falsification Attempts

This phase attacks edges by resampling (bootstrap/subsampling). The complementary, stronger
attack — against frequency/order/length nulls — is in
`self-methodology-falsification-report.md`, and it removes 8 of the 10 stable edges. The
two batteries together leave 2 survivors.

## 6. Limitations

- Bootstrap on ayahs with replacement uses a within-ayah-only flow approximation for speed;
  the subsampling battery (exact recompute) corroborates it.
- Stability says nothing about whether an edge beats a null — that is the falsification
  report's job, and it is decisive here.

## 7. Conclusion

**10 of 85 edges are directionally stable, but only 2 of those are also real beyond the
frequency/order nulls.** Stability alone over-credits the method; it must be combined with
the falsification battery, after which 2 edges remain.

Source: `generated/self_methodology/methodology_stability.json`.
