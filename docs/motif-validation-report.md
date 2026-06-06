# Motif Validation Report — Phase 11 (G)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase11-validation-1.0`.

Phase G challenges the Phase-9 motif findings by injecting noise into the
proposition graph (edge removal 5/10/20%, degree-preserving rewiring 10/20%, 20
trials each) and recomputing the triad census. No protection of prior conclusions.

---

## 1. Vocabulary stability (edge removal)

| Removed | Triad classes (mean) | Motifs-for-80% (mean) | Largest SCC (mean) | Dominant-motif unchanged |
|---:|---:|---:|---:|---:|
| 5% | 13.0 | 5.0 | 93.8 | 0.50 |
| 10% | 13.0 | 5.0 | 93.2 | 0.00 |
| 20% | 13.0 | 5.0 | 92.3 | 0.00 |

(Rewiring regimes give the same vocabulary and compression stability; see
`noise_results.json`.)

---

## 2. Findings

- **The 13-class vocabulary is invariant.** All 13 directed-triad classes appear
  at every noise level (mean 13.0). The motif vocabulary is a genuine structural
  property, not a threshold artifact.
- **The 5-motifs-for-80% compression is invariant** (mean 5.0 at every level). The
  small structural vocabulary that explains 80% of triads is robust.
- **The giant SCC persists** (~92–93 nodes) — the globally-cyclic core survives
  20% edge perturbation.
- **The dominant motif is NOT stable.** `top_motif_unchanged_probability` falls
  from 0.50 (5% removal) to 0.00 (10–20%). The single most-frequent triad class
  (`MOTIF_001`, mutual-path) **flips** under modest perturbation.

---

## 3. The honest split

| Motif finding | Verdict |
|---|---|
| 13-class vocabulary exists | **SURVIVES STRONGLY** |
| ~5 motifs cover 80% of structure | **SURVIVES STRONGLY** |
| Globally-cyclic SCC | **SURVIVES STRONGLY** |
| *Which* motif is #1 | **FRAGILE** (hub-driven, flips under 10% noise) |

This confirms — rather than contradicts — Phases 9 and 10: `MOTIF_001` was flagged
there as hub-bound (74% of its instances pass through CONCEPT_007) and failed its
own falsification. Phase 11 independently shows its #1 ranking does not survive
noise. The **motif vocabulary and its compressibility are robust; the identity of
the single most common motif is an artifact of the hub.**

---

## 4. Verdict

> **Phase-9 motif vocabulary SURVIVES STRONGLY** for the claims actually made
> (13 classes; 5-for-80%; globally-cyclic core). The only fragile sub-finding —
> the dominant-motif ranking — was already caveated in Phase 9 and is not relied
> upon.

---

## 5. Reproduce

```bash
python3 scripts/build_validation.py
python3 scripts/validate_validation.py --rebuild
```

Source: `generated/validation/motif_validation.json`, `noise_results.json`.
