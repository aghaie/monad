# L1 — Letters / Phonology Report

- **Layer:** L1 (Monad v2 self-interpreting pipeline)
- **Claim level:** STRUCTURAL ONLY — no semantic induction at this layer.
- **Confidence tier:** قوی/strong (C2) — structurally derived.
- **Source:** `generated/monad.db` (L0 substrate). Outputs: `generated/layers/L1_letters/`.
- **Reproducibility:** deterministic; `validate_L1_letters.py` passes 11/11, including a byte-identical re-run.

## Purpose

Give the higher layers a robust, internal account of root structure, while
treating letters strictly as phonological atoms (per the locked decision that
meaning begins at the root level, not the letter level).

## Findings

### 1. Letter inventory

- **28** distinct consonantal symbols across **1,642** roots; **no** non-standard
  symbols. Clean alphabet.
- Root lengths: **1,602 triliteral**, **40 quadriliteral**.

### 2. Root morpho-phonology

| Class | Count | Note |
|-------|------:|------|
| contains alif/wāw/yāʾ (A/و/ي) | 590 | A=135, w=312, y=203 |
| geminate (R2=R3, muḍaʿʿaf) | 153 | e.g. `Dll`, `rbb` |
| strong (no weak letter, no gemination) | 914 | |
| **hamzated (mahmūz)** | **UNKNOWN (abstain)** | The QAC ROOT field normalizes hamza (ء/أ/إ/ؤ/ئ) to alif `A`, so hamzated roots are **not separable** from alif/weak roots here. We record `UNKNOWN` (tier نامشخص) rather than a false zero. |

### 3. Headline structural finding — OCP (radical identity vs. chance)

The Obligatory Contour Principle of Arabic root phonology is cleanly present in
the Quranic root set (triliteral, N = 1,602):

| Identity | Observed | Expected (independent) | Obs / Exp |
|----------|---------:|-----------------------:|----------:|
| **R1 = R2** | 0.0000 | 0.0400 | **0.00** (categorically avoided) |
| **R2 = R3** | 0.0955 | 0.0510 | **1.87** (gemination preferred) |
| **R1 = R3** | 0.0050 | 0.0408 | **0.12** (strongly avoided) |

This matches known Arabic phonotactics exactly and confirms the substrate
carries real, measurable structure.

### 4. Muqaṭṭaʿāt (disconnected letters)

**29** suras open with disconnected letters (POS:INL). Catalogued and **flagged
only** — no interpretation offered (Charter: accept the Quran's silence; do not
fill the gap with a guess).

### 5. Self-prediction — masked middle radical

Held-out 5-fold. Recover a root's masked middle radical (R2) from its outer
radicals (R1, R3). Random floor ≈ 3.6% top-1 / 10.7% top-3 (~28 candidates).

| Predictor | top-1 | top-3 |
|-----------|------:|------:|
| Marginal baseline (frequency only) | 9.24% | 24.72% |
| Katz-style backoff (context-aware) | 2.25% | 11.36% |

**Verdict: no improvement over baseline.** Two principled models (fixed-weight
interpolation and Katz-style backoff) were tested a priori; neither beat the
marginal baseline, and the context model fell *below* random. The reason is
structural and honest: because every root is a unique triple, a shared (R1, R3)
frame in the training data is by construction completed by a *different* middle
radical than the held-out one — so co-radical context is anti-predictive. **Once
the categorical OCP constraints are satisfied, the middle radical is essentially
arbitrary.**

## Interpretation

Letters supply **structural constraints** (OCP, root classes) but **no
predictive or semantic content**. This negative result is independent empirical
support for the locked decision to treat letters as non-semantic and to begin
meaning-induction at the root level (L3). It also demonstrates that the
self-prediction backbone reports honest negatives — the property that will make
its eventual positives (at L2/L3) credible.

## Prohibitions observed

No external dictionaries, translations, tafsir, semantics, pretrained models;
no interpretation of the muqaṭṭaʿāt.
