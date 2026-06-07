# Predictivity-Falsification Report — Phase P (I, pre-registered decision)

**Phase:** P · **Method version:** `predictivity-discovery-1.0` · **Date:** 2026-06-07.
(Spec deliverable "falsification"; named distinctly because Phase 7 owns
`falsification-report.md` — prior outputs are immutable.)

## 1. Objective

Apply the **pre-registered** §9 decision criteria mechanically to the primary cell and
return the one-word verdict. No criterion, threshold, or baseline may be changed after
seeing results.

## 2. Method

The criteria were fixed in the spec and encoded as constants before any run. Evaluated on
the primary cell (root / R1 5-fold / single):

- **C1 — beats frequency:** info-gain > 0 **and** its CI excludes 0 **and** ppl_struct <
  ppl_base **and** MRR_struct > MRR_base.
- **C2 — beats the frequency null:** real S1 MRR > null S1 MRR (97.5-pct-separated).
- **C3 — not merely degree:** MRR_struct > MRR_degree.
- **C4 — minimum meaningful effect:** info-gain ≥ 0.05 bits **and** Hits@10 gain ≥ 0.02.
- **C5 — stable across regimes:** criteria hold in ≥ 3 of the regimes.

Verdict map: all of C1–C5 ⇒ GENUINE_STRUCTURE; C1 ∧ ¬C2 ⇒ FREQUENCY_SHAPED; ¬C1 ⇒
NON_PREDICTIVE.

## 3. Results

| Criterion | Required | Observed | Pass? |
|---|---|---|:--:|
| C1 beats frequency | info-gain > 0, MRR_s > MRR_b | info-gain **−3.316**; MRR 0.087 < 0.099 | **NO** |
| C2 beats null | real > null (MRR) | 0.087 > 0.018 | YES |
| C3 not degree | MRR_s > MRR_deg | 0.087 < 0.0986 | **NO** |
| C4 min effect | ≥ 0.05 bits & ΔH@10 ≥ 0.02 | −3.316 bits; ΔH@10 = **−0.017** | **NO** |
| C5 stable regimes | ≥ 3 pass | **0 of 7** | **NO** |

**VERDICT: `NON_PREDICTIVE`** (¬C1 ⇒ NON_PREDICTIVE).

Order vs co-presence: S2 info-gain −3.267 vs S1 −3.316 — neither helps; order does not
rescue the model (and ranks the true root worse: MRR 0.060).

## 4. Interpretation

Exactly one of the five criteria passes — **C2 (beats the null)** — and it is the one that
says the structure is *real*, not the one that says it is *useful*. The decisive criterion
C1 (beats frequency) fails, so the verdict is `NON_PREDICTIVE`: the discovered structure
does not add held-out predictive value over lexical frequency. C3 failing (structure < even
the degree baseline) and C4 failing (effect is negative, not merely small) reinforce this.
The result is not `FREQUENCY_SHAPED` — that category requires *beating* frequency with a
null-reproducible edge; here the structure does not beat frequency at all.

## 5. Falsification Attempts

This report **is** the falsification stage. The positive hypothesis ("structure predicts
beyond frequency") was given five independent chances to survive and survived **none** that
matter. The negative-outcome policy (pre-registered) was honoured: **no baseline was
weakened, no threshold was moved, and the verdict was not re-run to seek a pass.** The one
surviving criterion (C2) is reported as what it is — evidence the structure is real, not
evidence it predicts.

## 6. Limitations

- The verdict is computed on the root primary cell by design; the concept-level ranking
  gain (caveated, confounded by membership circularity) is recorded but, per
  pre-registration, does not override the root-level verdict.
- Calibration (λ = 1) inflates the perplexity magnitude but not the *direction*, which the
  λ-invariant ranking metrics confirm (C1 fails on MRR too).

## 7. Conclusion

**Pre-registered verdict: `NON_PREDICTIVE`.** Of the five criteria, only "beats the null"
passes; "beats frequency," "not degree," "minimum effect," and "stable regimes" all fail.
The discovered structure is real but not predictive beyond frequency.

Source: `generated/predictivity/falsification_results.json`.
