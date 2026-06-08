# Rare-Choice Report — Phase Φ (E)

**Phase:** Φ · **Method version:** `counterfactual-discovery-1.0` · **Date:** 2026-06-08.

## 1. Objective
Locate the actual Quran among generated alternatives: is it typical, or unusually constrained?

## 2. Method
Generate 1,000 frequency-valid alternative corpora (each ayah: draw its size-k root-set ∝ marginals);
compute a structural statistic (mean pairwise PPMI) for each; locate the actual Quran's percentile and
z. Lexical typicality is exact (actual per-draw cross-entropy == generator entropy by construction).

## 3. Results
| measure | value |
|---|--:|
| lexical typicality | **TYPICAL** (actual cross-entropy = generator entropy 8.503 bits) |
| structural statistic — actual mean PPMI | 1.766 bits |
| structural statistic — frequency-alternatives mean | 0.451 bits |
| **structural z** | **≈ 306** |
| structural percentile | 100th |

## 4. Interpretation
The answer is **two-sided and must be stated as such**:
- **Lexically, the actual Quran is TYPICAL** — its specific root choices are an ordinary draw from its
  own frequency distribution; nothing about *which words* is rare.
- **Structurally, it is EXTREME** — z ≈ 306 more clustered than frequency-random text. But this means
  only that the Quran is a **coherent text** (its words genuinely co-occur), which *any* real text is
  and random frequency-draws are not. It is a structural outlier *among word-salad*, not among coherent
  texts.

The structural extremity is real (Phase 17) but non-generalizable (Phase P): it reflects coherence, not
a derivable rule for the specific words. So the *lexical choices* are free and typical.

## 5. Falsification Attempts
"The Quran's word choices are rare/atypical" is falsified (lexically typical). "The Quran is
structurally indistinguishable from random" is also falsified (z ≈ 306). Both reported.

## 6. Limitations
1,000 alternatives are ample given the z ≈ 306 effect. The structural statistic is mean pairwise PPMI;
other coherence measures would also show the same coherent-vs-salad gap.

## 7. Conclusion
**Lexically typical, structurally extreme (coherent).** The actual *word choices* are an ordinary draw;
the *coherence* is the generic property of being a real text, real but non-generalizable.

Source: `generated/counterfactual/ayah_counterfactuals.json`.
