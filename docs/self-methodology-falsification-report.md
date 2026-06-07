# Self-Methodology-Falsification Report — Phase Z (I)

**Phase:** Z · **Method version:** `self-methodology-1.0` · **Date:** 2026-06-07.
(Named distinctly: Phase Q owns `methodology-falsification-report.md`; prior outputs are
immutable.)

## 1. Objective

The decisive phase. Attack every candidate edge of the Quran's method graph with the
controls Phases Q and X **never applied** — frequency, surah-length, and mushaf-order nulls —
and keep only what survives. This is where the "Quran describes its own method" hypothesis
either holds or breaks.

## 2. Method

For each of the 85 candidate edges, two questions:
- **Does it exist beyond frequency?** Node-level configuration null (K = 100): preserve each
  ayah's node-count and each node's document frequency, destroy co-occurrence (curveball
  swaps). An edge *exists beyond frequency* iff its real directed support exceeds the null's
  95th percentile.
- **Is it directional beyond text order?** Mushaf-order null (K = 100): preserve co-occurrence
  but destroy **all** order — random word order within ayahs **and** shuffled ayah order
  within surahs. An edge is *directional beyond order* iff its real directionality exceeds the
  order null's 95th percentile. (Word-order-only and ayah-order-only nulls are reported
  separately.)
- **Surah-length control:** recompute each edge's orientation on the short-ayah and long-ayah
  halves (median split); *length-stable* iff direction > 0.5 in both halves.

A **full survivor** must: exist beyond frequency **and** be directional beyond order **and**
be length-stable **and** be bootstrap/subsample-stable (`methodology-stability-report.md`).

## 3. Results

| metric | value |
|---|--:|
| candidate edges | 85 |
| **exist beyond the frequency null** | **10 / 85 (11.8%)** |
| directional beyond the order null | 15 / 85 |
| directionally stable (bootstrap+subsample) | 10 / 85 |
| **FULL survivors (all controls)** | **2 / 85** |
| largest connected survivor backbone | **2 nodes** (one edge) |

**The 10 edges that exist beyond the frequency null** (real support vs null p95; whether
direction beats the order null; length-stable):

| edge | dir | support | freq-null p95 | dir > order? | length-stable? |
|---|--:|--:|--:|:--:|:--:|
| listen → reflect | 0.765 | 17 | 14 | yes | no |
| **ask → knowledge** | 0.632 | 106 | 93 | **yes** | **yes** |
| read → remember | 0.600 | 45 | 42 | no | yes |
| **observe → misguidance** | 0.591 | 132 | 115 | **yes** | **yes** |
| ponder → listen | 0.583 | 12 | 11 | no | no |
| listen → observe | 0.582 | 122 | 111 | yes | yes |
| remember → understanding | 0.575 | 40 | 30 | no | no |
| knowledge → judge | 0.536 | 192 | 146 | no | no |
| guidance → misguidance | 0.500 | 90 | 52 | no | no |
| certainty → guidance | 0.500 | 14 | 12 | no | no |

**Full survivors (all controls):** `ask → knowledge` and `observe → misguidance`.

## 4. Interpretation

The method graph **largely collapses** under controls Q and X never applied:

1. **The associative field is mostly frequency.** Only **10 of 85** node co-occurrences
   exceed the frequency null — **88% of the "method" associations are explained by word
   frequency alone.** The dense graph of Phase A is mostly a frequency shadow.
2. **The direction is mostly text-order.** Of the 10 real associations, only 4 beat the
   mushaf-order null, and only 2 of those are also length-stable and resample-stable. The
   "pipeline/sequence" claim — that the Quran *orders* observe → reflect → know — does not
   robustly survive shuffling word and ayah order.
3. **Two edges survive everything:** `ask → knowledge` (asking precedes knowing — a genuine,
   robust directional regularity) and `observe → misguidance` (observing precedes
   misguidance — anti-confirmatory for a clean method, consistent with Phase X's bivalent
   perception). They share no node, so they form **no connected method**.

The honest reading: the Quran contains real epistemic regularities (2 of them survive every
control), but it does **not** encode a connected, directional *method* once frequency and
order artifacts are removed.

## 5. Falsification Attempts

This **is** the falsification stage, and it is unsparing: each edge faced a frequency null, a
mushaf-order null (plus separate word-order and ayah-order nulls), a surah-length split, a
bootstrap, and a subsampling battery. 83 of 85 candidate edges failed at least one. No
threshold was relaxed to admit more survivors.

## 6. Limitations

- The configuration null is node-level (preserving node df + ayah node-count); a root-level
  or syntactic null could differ, but would only be *stricter*, not more lenient.
- Length control is a median split; finer stratification was not run.
- The 16-node vocabulary is the spec's; the survivor count is small and a different
  vocabulary could shift *which* 2 edges survive, but the **collapse pattern** (≈ 12%
  existence, ≈ 2 full survivors) is the finding.

## 7. Conclusion

**Under frequency, order, and length controls the Quran's method graph collapses:** 88% of
associations are frequency artifacts, the directional pipeline does not survive order
shuffling, and only **2 isolated edges** (`ask → knowledge`, `observe → misguidance`) pass
every control — forming no connected method.

Source: `generated/self_methodology/methodology_falsification.json`.
