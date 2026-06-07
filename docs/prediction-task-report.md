# Prediction-Task Report — Phase P (A, C)

**Phase:** P — Structural Predictivity / Held-Out Information Engine ·
**Method version:** `predictivity-discovery-1.0` · **Date:** 2026-06-07.

## 1. Objective

Define the task that lets Monad answer its first *generalization* question: **does the
discovered structure predict held-out Quranic content beyond lexical frequency?** Every
prior phase was descriptive on the full corpus; this phase needs a task on which a
structure model and a frequency model can be compared on data neither was fitted to. The
task definition is important because the verdict is only as trustworthy as the fairness
and leakage-freedom built into it.

## 2. Method

**Task — masked-unit completion.** For a held-out ayah with observed unit-set U (its
distinct roots, or its activated concepts), one unit *u* ∈ U is masked and predicted from
the remaining **context** C = U \ {u}. Each candidate unit in the training vocabulary is
scored; the rank and the model-probability of the true *u* are recorded.

**Units.** Primary = **roots** (corpus-given, fixed, method-independent). Secondary =
**concepts** (Phase-3 clusters; frozen full-corpus memberships, variant 2a).

**Predictors.**
- **B0 (frequency baseline):** smoothed unigram prior `P0(u) = (df(u)+α)/(T+αV)`,
  **context-blind**.
- **B1 (degree baseline):** rank by co-occurrence degree — guards against structure
  merely re-expressing frequency-as-degree.
- **S1 (structure):** log-linear `P1(u|C) ∝ P0(u)·2^(Σ_{c∈C} PPMI(u,c))`, PPMI from
  training co-occurrence, weight λ = 1.
- **S2 (directional):** S1 with **ordered** (a-before-b) PPMI features.
- **N (frequency null):** S1 computed on a configuration null (df + ayah-size preserved,
  co-occurrence destroyed).

**Fairness lock.** S1 is an additive extension of B0: with an uninformative (empty)
context, `evidence = 0` and S1 reduces **exactly** to B0 (NLL and rank identical —
asserted by the validator). All predictors use an **identical min-rank tie convention**.
Any deviation of S1 from B0 is therefore driven solely by training co-occurrence
evidence. (A non-empty context legitimately reweights collocates; the model is a proper
context predictor, not one given a free pass to never underperform.)

**Metrics.** MRR, Hits@{1,5,10}, mean rank-percentile (rank/V), perplexity = 2^mean-NLL,
and the headline **information gain = mean(NLL_base − NLL_struct)** in bits/unit (paired
per instance, with CI).

**Constants (pre-registered, fixed before any run).** α = 0.5 · λ = 1.0 · K_null = 30 ·
seed = 20260607 · null-eval cap = 8000 instances · bootstrap = 1000 (primary cell) ·
min meaningful effect = 0.05 bits and Hits@10 +0.02.

## 3. Results

- Corpus: **6,214** root-bearing ayahs; mean **7.15** distinct roots/ayah; root
  vocabulary ≈ 1,548 per training fold; **103** concepts.
- Instance counts (root, R1 5-fold): single-mask **43,743**; 25%-mask 11,530; 50%-mask
  22,033. Coverage 0.988 (OOV masked units excluded symmetrically; 523 at single-mask).
- The same instance set is scored by every predictor (apples-to-apples).

No predictive comparison appears in this report; it defines the task only. Results are in
`root-predictivity-report.md`, `concept-predictivity-report.md`,
`frequency-null-control-report.md`, `information-gain-report.md`.

## 4. Interpretation

The task isolates exactly the quantity in question. Because B0 is context-blind and S1 is
B0 plus context-evidence, the *difference* between them measures relational information —
the value of knowing **which** other units share the ayah. A structure that merely
re-encodes frequency cannot beat B0 here; only genuine relational predictivity can.

## 5. Falsification Attempts

The design pre-commits to attacks executed in later phases: S1 must beat B0 (or it carries
no information), must beat B1 (or it is only degree), must beat N (or its edge is
frequency-shaped), and must clear a minimum effect size (or the effect is negligible). The
fairness lock was attacked directly by the validator (empty-context invariance) and holds.

## 6. Limitations

- λ = 1 is fixed (no tuning, to prevent optimizing toward a positive result); this can
  leave the log-linear model **miscalibrated** on perplexity. The ranking metrics (MRR,
  Hits) are calibration-free and are reported alongside, so the verdict does not rest on
  calibration alone.
- The task predicts a *masked unit from co-present units*; it does not test prediction of
  an ayah from scratch (ill-posed without an external anchor).
- Concepts are method-relative (Phase 11, ARI 0.22); the concept-level task is secondary
  and explicitly conditioned on that instability.

## 7. Conclusion

A leakage-free, fairness-locked, frequency-controlled masked-unit completion task is
defined, with roots as the rigorous primary unit and concepts secondary. It is the
instrument on which Phase P's pre-registered verdict is computed.

Source: `generated/predictivity/prediction_task.json`.
