# Semantic Anchor Report — Phase Σ (I)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`sigma-semantics-1.0`.

Phase I searches for **semantic** anchors — concepts whose removal destroys the
ability to define many others. Not frequency hubs; not graph hubs. This is the
decisive positive result of Phase Σ.

---

## 1. Method

**Definitional centrality** = the number of other concepts a concept helps define
(appears in their neighbourhoods). A **semantic anchor** has high definitional
centrality **beyond what its frequency predicts** — measured as the *residual*
(definitional centrality − frequency-expected centrality).

---

## 2. The decisive finding: semantic anchors ≠ the frequency hub

| Concept | Anchor | Def. centrality | Marginal | Freq-expected | **Residual** |
|---|---|---:|---:|---:|---:|
| `CONCEPT_027` | `ربو` | 12 | **52** | 0.8 | **+11.2** |
| `CONCEPT_089` | `عصر` | 8 | 21 | 0.3 | +7.7 |
| `CONCEPT_001` | `يسر` | 14 | 429 | 6.6 | +7.4 |
| `CONCEPT_093` | `عوم` | 7 | 12 | 0.2 | +6.8 |
| `CONCEPT_073` | `كتم` | 7 | 48 | 0.7 | +6.3 |
| **`CONCEPT_007`** (frequency hub) | `اله` | 11 | **5,906** | 92 | **−81.4** |

**The semantic anchors are NOT the frequency hub.** `CONCEPT_027` (marginal **52**,
a low-frequency concept) defines 12 other concepts — 14× what its frequency
predicts. Meanwhile the frequency hub `CONCEPT_007` (marginal 5,906) has residual
**−81.4**: it defines *fewer* concepts than its frequency predicts. **Definitional
centrality is a different structure from frequency centrality.**

---

## 3. Why this matters

This is the strongest evidence in Phase Σ that the semantic layer is **genuine, not
a frequency artifact**:

- If meaning were pure frequency (the Phase-16/17 deflation), the semantic anchors
  would be the frequency hubs. They are **not**.
- Low-frequency concepts like `CONCEPT_027` and `CONCEPT_089` anchor the definitions
  of many others — they hold a distinctive position that the corpus reuses widely.
- The frequency hub, despite co-occurring with everything, is **not** a semantic
  anchor (negative residual): its ubiquity makes it weakly informative for
  definition.

The semantic network has its **own anchoring structure**, orthogonal to frequency.

---

## 4. Are semantic anchors present?

| Question | Answer |
|---|---|
| Are semantic anchors present? | **Yes** — high-residual definitional anchors |
| Are they the frequency hub? | **No** — the hub has residual −81.4 |
| Does a small semantic core exist? | partly (Phase G), but its genuine part is these anchors |

---

## 5. Verdict

> **Semantic anchors are present and genuinely distinct from frequency.** Concepts
> like `CONCEPT_027` (`ربو`, marginal 52) define many others far beyond their
> frequency (residual +11.2), while the frequency hub `CONCEPT_007` is *not* a
> semantic anchor (residual −81.4). Definitional centrality is its own structure —
> the strongest evidence that the internal semantic layer is genuine, not a frequency
> artifact.

---

## 6. Reproduce

```bash
python3 scripts/build_semantics.py
python3 scripts/validate_semantics.py --rebuild
```

Source: `generated/semantics/semantic_anchors.json`.
