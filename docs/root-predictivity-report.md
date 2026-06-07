# Root-Predictivity Report — Phase P (E, primary)

**Phase:** P · **Method version:** `predictivity-discovery-1.0` · **Date:** 2026-06-07.
**This is the PRIMARY, headline-bearing experiment** (stable, method-independent units).

## 1. Objective

Test, at the level of the corpus's fixed roots, whether the discovered co-occurrence
structure (S1) predicts a held-out masked root better than the frequency baseline (B0).
Roots are the rigorous unit because they are corpus-given and not method-relative (unlike
concepts, Phase 11 ARI 0.22), so the result carries no concept-instability confound.

## 2. Method

Masked-root completion under the leakage-free holdout (`holdout-design-report.md`).
Predictors B0/B1/S1/S2 as defined in `prediction-task-report.md`. Identical min-rank tie
convention across predictors. Primary cell: root / R1 5-fold / single-mask (43,743
instances). Metrics: MRR, Hits@{1,5,10}, mean rank-percentile, perplexity, info-gain
(bits, bootstrap CI on the primary cell, B = 1000).

## 3. Results

**Primary cell — root / R1 5-fold (B0 = frequency, S1 = structure, deg = B1):**

| mask | n | MRR B0 | MRR S1 | MRR deg | H@1 B0/S1 | H@5 B0/S1 | H@10 B0/S1 | rank-pct B0/S1 | ppl B0/S1 | info-gain (bits) [95% CI] |
|---|--:|--:|--:|--:|--|--|--|--|--|--|
| single | 43,743 | **0.0990** | 0.0874 | 0.0986 | .043/.036 | .137/.116 | .199/.182 | .0995/.0927 | 354/3522 | **−3.316** [−3.391,−3.242] |
| 25% | 11,530 | 0.0965 | 0.0907 | 0.0962 | .040/.038 | .134/.121 | .194/.192 | .102/.094 | 365/1627 | −2.156 [−2.271,−2.041] |
| 50% | 22,033 | 0.0998 | 0.0891 | 0.0993 | .042/.033 | .140/.123 | .201/.196 | .100/.095 | 354/763 | −1.107 [−1.164,−1.051] |

**Across regimes (single-mask):**

| regime | n | MRR B0 | MRR S1 | H@10 B0/S1 | info-gain (bits) |
|---|--:|--:|--:|--|--:|
| R1 k=5 | 43,743 | 0.0990 | 0.0874 | .199/.182 | −3.316 |
| R1 k=10 | 43,812 | 0.0989 | 0.0892 | .199/.187 | −3.374 |
| R2 blocks | 43,577 | 0.0990 | 0.0793 | .198/.169 | −3.061 |
| R3 fwd-25% | 26,831 | 0.0945 | 0.0607 | .198/.130 | −2.542 |
| R3 fwd-50% | 16,696 | 0.0933 | 0.0743 | .191/.162 | −2.327 |
| R3 fwd-75% | 5,894 | 0.0801 | 0.0789 | .166/.167 | −1.750 |
| R4 len-strat | 43,746 | 0.0990 | 0.0879 | .199/.185 | −3.366 |

**S2 (directional/order) — R1 single:** MRR 0.0600 vs B0 0.0990; H@10 0.128 vs 0.199;
info-gain −3.267. Order does **not** help; it hurts more than co-presence.

**Degree baseline (B1):** MRR 0.0986 ≈ B0 0.0990 in every cell — degree and frequency are
interchangeable predictors.

## 4. Interpretation

On the decisive head metrics (MRR, Hits@1/5/10) and on calibrated perplexity/info-gain,
**the structure model is worse than the frequency baseline in every cell and every
regime.** Knowing which roots co-occur in an ayah does not help predict a held-out root;
it slightly *hurts*. One nuance points the other way: mean **rank-percentile** is slightly
*better* for S1 (0.0927 vs 0.0995) — i.e. S1 pulls mid-pack candidates up while pushing the
true root out of the top ranks where B0's frequency prior already nails common roots.
Structure therefore carries *some* weak signal, but it is net-negative on every metric that
the pre-registered criteria use. Degree ≈ frequency reproduces the Phase-16 lesson:
connectivity is frequency.

## 5. Falsification Attempts

The claim "structure predicts roots beyond frequency" was attacked from four directions
and **failed every one**: (1) B0 comparison — S1 < B0 on MRR/Hits/info-gain; (2) B1
comparison — S1 < degree; (3) regime agreement — **0 of 7** regimes show S1 > B0; (4)
order — S2 is worse still. The info-gain bootstrap CI excludes 0 on the negative side in
the primary cell. The negative result is itself robust (see `predictivity-robustness-report.md`).

## 6. Limitations

- The −3.3-bit perplexity gap is **partly calibration**: λ = 1 makes the log-linear model
  overconfident. But the calibration-free ranking metrics (MRR, Hits) also show S1 < B0,
  so the negative conclusion does **not** depend on calibration.
- A tuned-λ model could narrow the perplexity gap, but (a) tuning was pre-excluded to
  avoid optimizing toward success, and (b) ranking is λ-invariant and still negative.
- The mean-rank-percentile improvement is a genuine (small) positive signal not captured by
  the head metrics; it shows structure is not *information-free*, only not *useful beyond
  frequency* on the decisive metrics.

## 7. Conclusion

At the rigorous root level, **the discovered co-occurrence structure does not predict
held-out content beyond lexical frequency — it underperforms frequency on every
pre-registered metric, in all 7 regimes.** Order (S2) and degree (B1) do not rescue it.

Source: `generated/predictivity/root_predictivity.json`.
