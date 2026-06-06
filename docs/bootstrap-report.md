# Bootstrap Report — Phase 11 (D)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase11-validation-1.0`.

Phase D resamples the 6,101 active ayahs **with replacement, 1,000 times**
(`SEED = 20261111`), rebuilds the activation statistics, and reports confidence
intervals — not point estimates. No protection of prior conclusions.

---

## 1. CONCEPT_007 dominance

| Statistic | Value |
|---|---|
| Bootstrap runs | 1,000 |
| Hub share — mean | 0.96808 |
| Hub share — median | 0.96820 |
| Hub share — std | 0.00227 |
| Hub share — **95% CI** | **[0.96345, 0.97214]** |
| Hub share — min / max | 0.96066 / 0.97476 |
| **Remains rank-1 concept** | **1,000 / 1,000 (probability 1.000)** |

CONCEPT_007 is the most-activating concept in **every** bootstrap replicate, with
a share tightly concentrated near 0.968 (std 0.0023). Its dominance is not a
sampling artifact.

---

## 2. Concept-ranking persistence

| Statistic | Top-5 Jaccard | Top-10 Jaccard |
|---|---:|---:|
| mean | 0.821 | 0.921 |
| (vs canonical top-k by marginal) | | |

The most-activating concepts are bootstrap-stable: the top-10 set overlaps the
canonical top-10 at Jaccard 0.92, the top-5 at 0.82. The leading concepts (and
hence the strong-tier Phase-7 identity anchors built on them) are robust; the
small reshuffles at the rank boundary affect only lower-ranked concepts.

---

## 3. Active-concept count

All 103 concepts remain active (marginal > 0) across the bootstrap distribution —
no concept vanishes under resampling.

---

## 4. Exclusion disjointness (consistency)

On the 200 bootstrap runs where co-occurrence was recomputed, the
exclusion/positive disjointness held in **100%** — no resample produced a pair
that is both mutually-exclusive and positively related. The Phase-10 consistency
property is bootstrap-invariant.

---

## 5. Interpretation

Bootstrap resampling — the standard test for sampling-driven artifacts — leaves
the headline findings intact: hub dominance (prob 1.0, tight CI), top-concept
ranking (Jaccard 0.92), and consistency (disjointness prob 1.0). These are
properties of the corpus, not of the particular ayah sample.

---

## 6. Reproduce

```bash
python3 scripts/build_validation.py
python3 scripts/validate_validation.py --rebuild
```

Source: `generated/validation/bootstrap_results.json`.
