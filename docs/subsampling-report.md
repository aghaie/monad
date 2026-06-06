# Subsampling Report — Phase 11 (C)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase11-validation-1.0`.

Phase C removes 5/10/20/30/40% of ayahs, **100 times per level** (`SEED =
20261111`), rebuilds the activation statistics, and measures survival. No
protection of prior conclusions.

---

## 1. Survival by removal level

| Removed | Hub share (mean) | Hub remains rank-1 | Concept survival (mean) | Exclusion disjointness |
|---:|---:|---:|---:|---:|
| 5% | 0.96804 | **1.000** | 1.0000 | 1.000 |
| 10% | 0.96816 | **1.000** | 1.0000 | 1.000 |
| 20% | 0.96804 | **1.000** | 0.99990 | 1.000 |
| 30% | 0.96823 | **1.000** | 0.99952 | 1.000 |
| 40% | 0.96782 | **1.000** | 0.99835 | 1.000 |

---

## 2. Findings

- **Hub dominance is invariant.** CONCEPT_007 remains the rank-1 concept in
  **100% of all 500 subsamples**, at every removal level; its share stays at
  0.968 ± 0.001 even when 40% of the corpus is deleted.
- **Concepts persist.** Concept survival stays ≈ 1.0 even at 40% removal — only at
  the heaviest level do a handful of the rarest concepts (marginal < 5) occasionally
  drop out (survival 0.998). The 103-concept *population* is subsample-robust even
  though its *boundaries* are method-sensitive (Phase B).
- **Consistency persists.** Exclusion/positive disjointness holds in 100% of every
  level — removing up to 40% of ayahs never manufactures a contradiction.

---

## 3. Interpretation

Subsampling — deleting large fractions of the evidence — is the most aggressive
test of whether a finding depends on specific ayahs. The hub, the concept
population, and the consistency property all survive removal of up to 40% of the
corpus with negligible variation. These findings are not artifacts of particular
ayahs.

---

## 4. Reproduce

```bash
python3 scripts/build_validation.py
python3 scripts/validate_validation.py --rebuild
```

Source: `generated/validation/subsampling_results.json`.
