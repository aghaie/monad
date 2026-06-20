# L3 — Self-grounded Root Lexicon Report

- **Layer:** L3 (Monad v2). The first FULL meaning layer.
- **Claim level:** meaning of a root = its internal relations + its coordinates in the L2 name-space.
- **Confidence tiers:** صریح/قوی/محتمل/نامشخص (by attestation; abstain when sparse).
- **Source data:** `generated/monad.db` (L0) + `generated/layers/L2_names/` (L2 anchors).
- **Reproducibility:** `validate_L3_roots.py` passes 12/12, byte-identical re-run.

## What "meaning" is here

No external gloss is ever used. Each root is represented by:

- **name_coordinates** — its PPMI association with each of the 16 L2 anchor
  names: the root's position in the divine-name space. *This is the law of
  interpretation made numeric — a concept located by its coherence with the
  names.*
- **relational_neighbors** — the roots it most co-occurs with (PPMI).
- **field_neighbors** — roots with the most similar name-profile (cosine): the
  root's semantic field, grounded in the names.
- **defining_ayat** — provenance for the strongest name link.
- **tier** — by attestation: قوی (≥10 tokens, 593 roots), محتمل (3–9, 453),
  نامشخص/abstain (<3, 589 — too sparse to characterise; we do not guess).

## The name-coordinates are meaningful

| Root | Name-coordinates (top, PPMI) | Reading |
|------|------------------------------|---------|
| رحم (rḥm) | رحیم 2.99 · رؤوف 2.79 · غفور 2.77 | mercy ≈ proximity to the mercy/forgiveness names |
| علم (ʿlm) | علیم 2.15 · واسع 2.03 · سمیع 1.76 · حکیم 1.36 | knowledge ≈ the Knowing / All-encompassing / Hearing / Wise |
| کتب (ktb) | شهید 1.34 · وکیل 1.32 · حکیم · علیم | writing/recording ≈ the Witness / Trustee |

The representation recovers, with **zero external input**, that the root for
"mercy" lives next to the names of mercy — the thesis at work for ordinary
vocabulary.

## Self-prediction — does the network recover its own roots?

**Task:** held-out (5-fold), mask one content root in an ayah and recover it from
the other roots (root-root PPMI). 35,596 instances over 1,635 candidate roots.

| Predictor | top-1 | top-3 |
|-----------|------:|------:|
| **Model** (Σ PPMI over context roots) | **9.70%** | **17.73%** |
| Baseline (most frequent root) | 3.54% | 8.68% |
| Random floor | 0.061% | ~0.18% |

**Verdict: model beats baseline and random by a wide margin.** A hidden root is
recoverable from its ayah context far above chance — the relational network
genuinely encodes root identity. Self-interpretation works at the root level.

## Honest coverage note

Of 1,635 roots, **221** are directly name-anchored (they co-occur with an anchor
name ≥ 3 times); the rest are represented by their relational fingerprint only.
So name-anchoring is **strong where it reaches**, but 16 names + ayah-level
co-occurrence do not yet anchor every root. Coverage will widen as later layers
add finer context and promote محتمل names. The 9.7% top-1 recovery is strong for
a 1,635-way task but far from complete — evidence the network carries real
self-referential meaning, not a claim of finished understanding.

## Prohibitions observed

No external glosses, dictionaries, tafsir, translations, or pretrained models.
The lexicon is built entirely from the corpus and the internally-discovered names.
