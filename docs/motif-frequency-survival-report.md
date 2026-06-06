# Motif Frequency-Survival Report — Phase 17 (D)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase17-frequency-null-1.0`.

*(Named `motif-frequency-survival-report.md` to preserve the Phase-9
`motif-survival-report.md`; the Phase-17 spec's generic name collides with it.)*

Phase D re-evaluates the Phase-9 motif findings against the concept-frequency null:
which triad motif classes survive frequency control?

---

## 1. Per-motif survival

For each triad motif class: observed frequency vs the 1,000-null distribution
(z-score). A class **survives** if |z| ≥ 2.

| Quantity | Value |
|---|---|
| Triad motif classes | 13 |
| **Classes deviating significantly (|z| ≥ 2)** | **3** |
| Triad-class-count survival z | +2.7 |
| Motif-distribution structure fraction | 32.3% |

---

## 2. Findings

- **The motif *vocabulary* (which 13 classes exist) is largely frequency-generic** —
  any sufficiently dense graph has triads in all 13 directed classes, and the null
  reproduces most of them. The vocabulary itself carries little structure beyond
  frequency.
- **But the motif *distribution* is partly structural** — 3 of 13 classes deviate
  significantly from the null (|z| ≥ 2). Specific motifs (the reciprocal/convergent
  shapes Phase 9 flagged as over-represented) occur at rates the frequency null does
  not predict. These carry genuine structure.
- This refines Phase 9: the over/under-representation of specific motifs (which
  Phase 9 measured against a degree-preserving edge-swap null) is corroborated here
  against a more fundamental activation-frequency null — a subset of motifs genuinely
  exceeds frequency.

---

## 3. Which motifs survive?

The surviving classes are those Phase 9 found most over-represented (reciprocal /
convergent triads) — the patterns that reflect the specific co-occurrence structure
(strong associations, which themselves survive at 3.2×). The frequent open-path
motifs are closer to the frequency baseline. **Hypothesis H3 survives** (the motif
vocabulary contains structure beyond frequency), but most of the motif *magnitude*
is frequency.

---

## 4. Verdict

> **The motif distribution partly survives frequency control.** The 13-class
> vocabulary is largely frequency-generic, but **3 of 13 classes** deviate
> significantly from the null (|z| ≥ 2) — the specific over-represented
> reciprocal/convergent motifs carry genuine structure. Overall ~32% structure.
> Hypothesis H3 survives.

---

## 5. Reproduce

```bash
python3 scripts/build_frequency_null.py
python3 scripts/validate_frequency_null.py --rebuild
```

Source: `generated/frequency_null/motif_survival.json`.
