# Threshold Sweep Report — Phase 11 (A)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase11-validation-1.0`.

Phase A varies every major threshold low → extreme and records the affected
statistics. Findings that move sharply with threshold are method-sensitive;
findings that hold are robust. No protection of prior conclusions.

---

## 1. Root-graph edge threshold (concept-count proxy)

Canonical Phase-3 `MIN_EDGE = 0.3`.

| Threshold | Components (≥2) | Largest | Non-trivial nodes |
|---:|---:|---:|---:|
| 0.10 | 38 | **1,350** | 1,447 |
| 0.20 | 38 | 1,350 | 1,447 |
| 0.30 | 38 | 1,350 | 1,447 |
| 0.50 | 141 | 28 | 472 |

**Highly threshold-sensitive.** Below 0.5 the root similarity graph has a single
1,350-root giant component; at 0.5 it shatters into 141 small components. The
number of "natural" concept clusters therefore depends strongly on the threshold
— corroborating the Phase-B finding that the exact **103-concept count is
method/threshold-relative** (see `survivor-analysis-report.md`).

---

## 2. Co-occurrence support threshold (proposition-edge proxy)

Canonical Phase-4 `SUPPORT_MIN = 5`.

| Threshold | Edges | Hub degree | Max degree | Hub = max-degree? |
|---:|---:|---:|---:|:--:|
| 2 | 1,977 | 102 | 102 | ✓ |
| 5 | 1,215 | 99 | 99 | ✓ |
| 10 | 809 | 89 | 89 | ✓ |
| 20 | 501 | 71 | 71 | ✓ |

**Robust.** Edge count falls smoothly with threshold, but **CONCEPT_007 is the
maximum-degree node at every threshold** — its hub status does not depend on the
support cutoff.

---

## 3. Exclusion marginal threshold (consistency)

Canonical Phase-10 `MARGINAL_MIN = 30`.

| Threshold | Exclusion pairs | Exclusion-with-positive-relation |
|---:|---:|---:|
| 10 | 1,593 | **0** |
| 30 | 401 | **0** |
| 50 | 181 | **0** |
| 100 | 2 | **0** |

**Robust and decisive.** The *number* of mutually-exclusive pairs depends on the
threshold (1,593 → 2), but the **consistency property is threshold-invariant**: at
**every** threshold, zero exclusion pairs also carry a positive relation. The
Phase-10 disjointness (and hence the 0-contradictions verdict) does not depend on
the marginal cutoff.

---

## 4. Summary

| Swept quantity | Sensitivity | Implication |
|---|---|---|
| Root-graph edge threshold | **high** | concept count is threshold-relative |
| Co-occurrence support | low (hub-wise) | hub dominance is threshold-invariant |
| Exclusion marginal | counts vary, property invariant | consistency is threshold-invariant |

The threshold sweep cleanly separates the **fragile** finding (exact concept
count) from the **robust** findings (hub dominance, consistency).

---

## 5. Reproduce

```bash
python3 scripts/build_validation.py
python3 scripts/validate_validation.py --rebuild
```

Source: `generated/validation/threshold_sweeps.json`.
