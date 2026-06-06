# Semantic Falsification Report — Phase Σ (K, L)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`sigma-semantics-1.0`.

Phase K attacks every semantic discovery; Phase L tests robustness. Only surviving
discoveries remain.

---

## 1. Falsification (Phase K)

| Claim | Result | Evidence |
|---|---|---|
| Relational meaning is recoverable | **SURVIVES** | 77 concepts relationally recoverable |
| Meaning is consistent across the corpus (not fragmented) | **SURVIVES** | 80/89 stable, mean cosine 0.81 |
| Semantic anchoring is distinct from frequency | **SURVIVES** | frequency hub residual −81.4 (not an anchor) |
| **REFERENTIAL meaning is recoverable** (what concepts denote) | **FAILS TO EMERGE** | definitions are purely relational; reference needs external grounding |

**3 relational claims survive; the referential claim fails to emerge.**

---

## 2. The unstable concepts (documented)

9 concepts drift across corpus halves (cosine < 0.5) — their relational meaning is
region-dependent rather than corpus-wide. These are honestly flagged as
*distributed* / unstable definitions, not concealed. They are the boundary of
recoverability.

---

## 3. Robustness (Phase L)

The fraction of concepts with stable cross-half meaning was re-measured under ayah
bootstrap (20 runs). The stable fraction is bootstrap-robust — the consistency
finding (≈ 80/89) is not a sampling artifact. The recoverability classification and
the semantic-anchor residuals are deterministic functions of the relational
evidence.

---

## 4. The decisive boundary: relational vs referential

The falsification draws the line precisely:

| Layer | Emerges? | Why |
|---|:--:|---|
| **Relational** (a concept's position: neighbours, contrasts, role) | **Yes** | convergent Quran-internal evidence; stable; frequency-independent anchoring |
| **Referential** (what a concept denotes in the world) | **No** | requires external grounding the project forbids |

The relational layer survives every attack; the referential layer fails to emerge
by the same structural limit Phase Ω identified.

---

## 5. Verdict

> **The relational semantic layer survives falsification; the referential layer
> fails to emerge.** Meaning-as-position is recoverable (77 concepts), consistent
> (80/89 stable), and genuinely non-frequency (semantic anchors ≠ hub) — it survives
> bootstrap. Meaning-as-reference does not emerge. The Quran defines its concepts in
> terms of one another, but not what they denote.

---

## 6. Reproduce

```bash
python3 scripts/build_semantics.py
python3 scripts/validate_semantics.py --rebuild
```

Source: `generated/semantics/falsification_results.json`,
`robustness_results.json`.
