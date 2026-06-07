# Concept-Predictivity Report — Phase P (F, secondary)

**Phase:** P · **Method version:** `predictivity-discovery-1.0` · **Date:** 2026-06-07.
**Secondary experiment — explicitly conditioned on concept stability and the
frozen-membership caveat. It does NOT carry the verdict.**

## 1. Objective

Test the same masked-completion task at the level of Phase-3 **concepts** (the Monad
object), and judge whether any signal there is trustworthy given that concepts are
method-relative (Phase 11, ARI 0.22).

## 2. Method

Masked-concept completion. Concept activation per ayah uses **frozen full-corpus
memberships** (variant 2a): concept *c* is active in an ayah if any of its member roots is
present. Predictive statistics (df, co-occurrence, PPMI) are still **training-only** per
fold. Vocabulary = 103 concepts. Predictors B0/S1/N as before. Cells: R1 5-fold ×
{single, 25%, 50%}. Stability is reported separately (`concept_stability.json`).

## 3. Results

**Concept / R1 5-fold:**

| mask | n | MRR B0 | MRR S1 | H@1 B0/S1 | H@5 B0/S1 | H@10 B0/S1 | ppl B0/S1 | info-gain (bits) [95% CI] |
|---|--:|--:|--:|--|--|--|--|--|
| single | 24,177 | 0.316 | **0.370** | .173/.232 | .442/.506 | .669/.682 | 28.4/29.5 | **−0.055** [−0.085,−0.022] |
| 25% | 6,831 | 0.332 | **0.380** | .190/.235 | .455/.528 | .679/.702 | 27.1/25.5 | **+0.088** [+0.039,+0.137] |
| 50% | 12,329 | 0.323 | **0.349** | .180/.192 | .449/.523 | .672/.705 | 27.8/25.0 | **+0.153** [+0.126,+0.180] |

- On **ranking** (MRR, Hits@1/5/10), S1 **beats** B0 in all three mask modes.
- On **calibrated perplexity/info-gain**, S1 is slightly *worse* at single-mask
  (−0.055 bits) but *better* at 25%/50% (+0.088, +0.153).
- Concept structure beats the frequency null (real MRR 0.375 vs null 0.289; see
  `frequency-null-control-report.md`).
- Concept "stability" cosine across folds = 0.9999 (see Limitations — this number is
  near-tautological, NOT a vindication of stability).

## 4. Interpretation

At the concept level the picture **inverts** the root-level result on ranking: knowing
which concepts co-occur **does** help rank a held-out concept. Two facts explain the
inversion, and both undercut treating it as a positive discovery:

1. **Coarser vocabulary.** 103 dense concept nodes make co-occurrence far more
   informative than 1,548 sparse roots — but this is a property of aggregation, not new
   information.
2. **Membership circularity (decisive caveat).** Concepts are *defined* as co-occurrence
   clusters of roots (Phase 3). Predicting a concept from co-occurring concepts therefore
   partly re-reads the clustering that built them — the "definitional leak" pre-registered
   in the spec. The concept-level ranking gain is **confounded** by this circularity and
   cannot be read as clean predictive structure.

## 5. Falsification Attempts

The concept signal was attacked by (1) the frequency null — it survives (S1 > N); (2) the
single-mask perplexity test — it **fails** (info-gain −0.055, CI excludes 0 negative); (3)
the stability/circularity audit — the gain is confounded by membership definition. So the
ranking gain survives the null but not the circularity and calibration attacks; it is not
a clean, trustworthy positive.

## 6. Limitations

- **The 0.9999 stability cosine is misleading and is reported as such.** It measures the
  cosine of per-fold concept *df-vectors* under *frozen* memberships with *random* folds —
  near-tautologically ≈ 1. It does **not** test clustering reproducibility. The genuine
  instability bound is Phase-11 ARI = 0.22; per-fold re-clustering (variant 2b) was **not**
  implemented. Concept-level results are therefore conditioned on an *untested* clustering
  stability and on frozen-membership circularity.
- Because of the circularity, a concept-level "win" cannot be promoted to the phase
  verdict; the verdict rests on the root level.

## 7. Conclusion

Concept-level structure improves *ranking* over frequency, but the gain is **confounded by
membership circularity and an untested clustering, and fails the calibrated single-mask
test**. It is a caveated, non-decisive signal — not evidence of genuine predictive
structure. The verdict is set by the root level.

Source: `generated/predictivity/concept_predictivity.json`, `concept_stability.json`.
