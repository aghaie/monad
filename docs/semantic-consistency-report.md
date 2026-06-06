# Semantic Consistency Report — Phase Σ (H)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`sigma-semantics-1.0`.

Phase H asks whether a concept's meaning stays stable across the corpus — measuring
semantic drift, consistency, and fragmentation.

---

## 1. Method

Each concept's **neighbour profile** (its co-occurrence vector) is computed in two
halves of the corpus and compared by cosine. High cosine = stable meaning across
regions; low = drift / fragmentation. Stable ⇔ cosine ≥ 0.5.

---

## 2. Result

| Quantity | Value |
|---|---|
| Recoverable/partial concepts measured | 89 |
| **Stable across corpus halves** | **80** |
| Mean cross-half cosine | **0.81** |

**80 of 89 concepts keep a stable neighbourhood across corpus halves** (mean cosine
0.81). A concept's relational meaning is largely **the same in different regions of
the Quran** — it does not fragment.

---

## 3. Findings

- **Meaning is largely consistent, not fragmented.** The high mean cosine (0.81)
  means a concept associates with the same other concepts wherever it appears. Its
  relational position is stable across the corpus.
- **9 concepts drift** (cosine < 0.5) — concepts whose neighbourhood differs between
  regions. These are candidates for *distributed* or *region-dependent* meaning and
  are flagged in falsification.
- **This corroborates Phase 13/14** (the structure is scale-invariant and
  homogeneous): a concept's meaning is stable because its relational structure is
  present consistently throughout the corpus.

---

## 4. Does meaning remain stable?

| Question | Answer |
|---|---|
| Semantic consistency | high — 80/89 stable, mean cosine 0.81 |
| Semantic drift | low — only 9 concepts drift |
| Semantic fragmentation | minimal |
| Semantic evolution | none detected (stable, not evolving) |

---

## 5. Verdict

> **Relational meaning is stable across the corpus.** 80 of 89 concepts keep a
> consistent neighbourhood across corpus halves (mean cosine 0.81) — meaning does not
> fragment. A concept's relational position is the same wherever it appears, so the
> internal definitions are corpus-wide, not region-local.

---

## 6. Reproduce

```bash
python3 scripts/build_semantics.py
python3 scripts/validate_semantics.py --rebuild
```

Source: `generated/semantics/semantic_consistency.json`.
