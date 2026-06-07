# Frequency-Null-Control Report — Phase P (G, decisive control)

**Phase:** P · **Method version:** `predictivity-discovery-1.0` · **Date:** 2026-06-07.
**This is the decisive criterion-2 control** — it separates "real co-occurrence structure"
from "predictive usefulness beyond frequency."

## 1. Objective

Determine how much of any predictive behaviour of the structure model is reproducible by
frequency alone. The null answers: *is the structure's prediction real co-occurrence, or
could a graph with the same marginals but scrambled co-occurrence predict equally well?*

## 2. Method

**Configuration null.** Per fold, the training incidence (ayah × unit) is randomized by
curveball (checkerboard) swaps that **preserve every ayah's size and every unit's document
frequency** while destroying co-occurrence. From each null realization the S1 statistics
(PPMI) are rebuilt and the masked-completion metrics recomputed on the **same** instance
sample (deterministic, cap 8,000). **K = 30** realizations give a null band (mean,
2.5–97.5 percentile). Run in **all regimes** (root) and at concept level. The matched real
S1 value is computed on the identical sample.

**Decisive criterion (pre-registered C2):** the real S1 must beat the null S1 on MRR with
the null's 97.5-percentile below the real value.

## 3. Results

**Root, all regimes (single-mask; MRR):**

| regime | real S1 MRR | null S1 MRR (mean) | real B0 MRR | Δ(real−null) | real beats null? |
|---|--:|--:|--:|--:|:--:|
| R1 k=5 | 0.0873 | 0.0185 | 0.0983 | +0.069 | **yes** |
| R1 k=10 | 0.0856 | 0.0175 | 0.0972 | +0.068 | yes |
| R2 blocks | 0.0834 | 0.0194 | 0.1017 | +0.064 | yes |
| R3 fwd-25% | 0.0595 | 0.0214 | 0.0944 | +0.038 | yes |
| R3 fwd-50% | 0.0740 | 0.0216 | 0.0947 | +0.052 | yes |
| R3 fwd-75% | 0.0789 | 0.0251 | 0.0800 | +0.054 | yes |
| R4 len-strat | 0.0892 | 0.0188 | 0.0969 | +0.070 | yes |

**Root info-gain band (R1 single):** real −3.316 bits; null −3.617 [−3.684, −3.526].

**Concept (R1 single):** real S1 MRR 0.375 vs null 0.289 (mean) — real beats null; real
info-gain −0.048 vs null −0.375.

## 4. Interpretation

Two facts hold simultaneously and must be read together:

1. **Real structure beats the null** in every regime (root MRR ≈ 0.087 vs null ≈ 0.018; a
   ~0.07 gap). The discovered co-occurrence is **real** — it is not reproducible by a
   marginal-preserving scramble. This is consistent with Phase 17's surviving relational
   network (D1).
2. **But the real structure still loses to the frequency baseline** (B0 MRR ≈ 0.098 >
   real S1 ≈ 0.087 > null ≈ 0.018). The structure sits *between* frequency and the null:
   more than random co-occurrence, less than the unigram prior.

So the null control confirms the structure is genuine **but not predictively useful**:
real co-occurrence carries information the scramble lacks, yet that information does **not**
translate into beating the simple frequency predictor. "Real" ≠ "predictive beyond
frequency."

## 5. Falsification Attempts

The null is the attack. The structure **survives** it (beats null everywhere) — so the
"the structure is just a scrambled-frequency artifact" hypothesis is rejected. But the
parallel attack by the frequency *baseline* (B0) **succeeds** against the structure — so
"the structure predicts beyond frequency" is also rejected. Both attacks were run in all
regimes; both verdicts are unanimous (7/7).

## 6. Limitations

- K = 30 gives a tight null band (percentile spread < 0.003 MRR) but is not exhaustive; the
  gaps here (~0.07) vastly exceed the band width, so the qualitative conclusion is safe.
- The null preserves marginals and ayah sizes but not higher-order/syntactic structure; a
  *syntactic* null (word-order-preserving) was out of scope and remains an open stronger
  test (it would only further shrink the structure's already-insufficient edge).

## 7. Conclusion

**The discovered structure beats the frequency-preserving null (it is real) but loses to
the frequency baseline (it is not predictively useful beyond frequency).** Criterion 2 is
met (beats null); criterion 1 (beats frequency) is not — which is why the verdict is
NON_PREDICTIVE, not GENUINE_STRUCTURE.

Source: `generated/predictivity/frequency_null_control.json`.
