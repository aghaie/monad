# Ablation Report — Phase 14 (E)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase14-locality-1.0`.

Phase E removes each discovered region (its surahs) and recomputes the global
structures — hub dominance, consistency, motif vocabulary, SCC size, concept
coverage. Which regions are structurally critical? Which are redundant?

---

## 1. Method

For each of the 54 regions, the region's surahs are deleted and the global graph is
rebuilt from the remainder. The damage to hub rank, consistency overlap, motif
class count, and largest-SCC size is measured against the full-corpus reference.

| Global reference | Value |
|---|---|
| Hub rank | 1 (share 0.968) |
| Consistency overlap | 0 |
| Triad classes | 12 |
| Largest SCC | 91 |
| Active concepts | 103 |

---

## 2. Results

| Outcome across all 54 region removals | Result |
|---|---|
| Any removal breaks the hub (hub no longer rank-1)? | **No** |
| Any removal breaks consistency (overlap > 0)? | **No** |
| Any removal destroys the motif vocabulary? | **No** (worst case loses a few classes, recovered elsewhere) |

**No single region is indispensable for the hub or consistency.** Removing any one
region leaves `CONCEPT_007` rank-1 and the consistency overlap at 0. The hub and
consistency are carried redundantly across the whole corpus.

---

## 3. Criticality ranking

Regions are ranked by combined motif-class loss + SCC reduction. The most "critical"
regions are simply the **largest** ones (those containing the long surahs), because
removing more verses removes more motif/SCC structure — but even removing the
single largest region does not break the hub or consistency. Criticality tracks
*volume removed*, not a unique structural role.

---

## 4. Which regions are critical / redundant?

| Question | Answer |
|---|---|
| Which regions are structurally critical? | **None individually** — no region is a single point of failure for hub or consistency |
| Which regions are redundant? | **All of them** for the core functions — the hub and consistency survive every single-region removal |
| What does region removal damage? | only **volume-dependent** structure (motif richness, SCC size), proportional to verses removed |

---

## 5. Verdict

> **No region is indispensable.** The hub and consistency are carried redundantly
> across the entire corpus and survive the removal of any single region. The only
> damage from ablation is proportional to the volume of text removed (motif/SCC
> density), confirming the homogeneous-field picture: the structure has no critical
> localised dependency.

---

## 6. Reproduce

```bash
python3 scripts/build_locality.py
python3 scripts/validate_locality.py --rebuild
```

Source: `generated/locality/ablation_analysis.json`.
