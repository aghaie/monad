# Concept Survival Report — Phase 17 (B)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase17-frequency-null-1.0`.

Phase B re-evaluates the Phase-3 concept discoveries against a root-frequency null:
would similar concepts emerge from frequency alone?

---

## 1. Test

Concept **cohesion** = the mean within-ayah co-occurrence of each concept's member
roots. If a concept is a genuine cluster, its member roots should co-occur more
than a root-frequency null (200 realizations preserving root frequencies, shuffling
root→ayah assignments).

| Quantity | Value |
|---|---|
| Observed cohesion | **4.17** |
| Null cohesion (mean) | 2.58 |
| **z-score** | **+29.8** |
| Ratio observed / null | **1.62×** |
| Structure fraction | 38% |

---

## 2. Findings

- **Concept clusters significantly exceed frequency** (z = +29.8). The member roots
  of a concept co-occur far more than chance — concepts capture genuine
  co-occurrence structure, not just frequency aggregation. **Hypothesis H1 survives.**
- **But the effect size is moderate** (1.62× the null baseline). Of a concept's
  member-root cohesion, ~38% is structure above the frequency floor and ~62% is the
  frequency baseline that any frequency-preserving data would produce. So concepts
  are *genuine but not pure* structure.

This is the honest two-part reading: concept clustering is **statistically real**
(it would not emerge from frequency alone) yet **quantitatively modest** (most of
the raw co-occurrence is the frequency baseline).

---

## 3. Would concepts emerge from frequency alone?

| Question | Answer |
|---|---|
| Would *similar* concepts emerge from frequency alone? | **No** — root co-occurrence is 1.6× above the frequency null (z = 29.8); the clustering is genuine |
| Is concept cohesion mostly structure or mostly frequency? | the magnitude is mostly the frequency baseline (62%), but the excess (38%) is significant structure |

---

## 4. Verdict

> **Concept structure survives frequency control** (z = +29.8): member roots
> co-occur significantly more than a root-frequency null, so the Phase-3 concepts
> are genuine clusters, not frequency artifacts. The effect is real but moderate in
> magnitude (1.6×). Hypothesis H1 survives.

---

## 5. Reproduce

```bash
python3 scripts/build_frequency_null.py
python3 scripts/validate_frequency_null.py --rebuild
```

Source: `generated/frequency_null/concept_survival.json`.
