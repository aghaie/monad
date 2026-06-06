# Region Discovery Report — Phase 14 (B, C)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase14-locality-1.0`.

Phase B builds structural fingerprints and a similarity matrix; Phase C discovers
structural regions by clustering fingerprints — **using no surah names, chronology,
metadata, or human labels.** Regions emerge only from measurable structural
behaviour.

---

## 1. Structural fingerprints (Phase B)

Each surah's fingerprint is its **concept-activation profile** (the fraction of the
surah's ayahs activating each of the 103 concepts) plus structural scalars (hub
dependence, density, SCC participation). Two similarities are computed:

| Similarity | Mean cosine | Meaning |
|---|---:|---|
| **Raw** (full profile) | **0.835** | near-uniform — all surahs share the dominant hub + common concepts |
| **Discriminative** (TF-IDF, ubiquitous concepts down-weighted) | 0.282 | exposes the weak distinctive differences |

**The raw fingerprints are nearly uniform (mean cosine 0.835):** 99% of surah pairs
are connected at cosine ≥ 0.5. **The corpus is, to first order, ONE homogeneous
structural field** — every surah activates the same dominant concepts in similar
proportions. Region structure can only be found in the *residual* (discriminative)
signal after the common component is removed.

---

## 2. Region discovery (Phase C)

Clustering the **discriminative** fingerprint-similarity graph (cosine ≥ 0.4) by
deterministic modularity maximisation yields **54 regions** — but they are **weak**:

| Property | Value |
|---|---|
| Regions discovered | **54** (incl. 30 singletons) |
| Largest regions | size 8, 8, 7, 6, 4 … |
| Mean cohesion (size ≥ 2) | ~0.28 (low) |
| Mean separation | ~0.82 |

The largest regions group **short surahs** that share distinctive (rare) concepts:
- `REGION_001`: surahs 8, 80, 81, 91, 92, 97, 99, 106
- `REGION_002`: surahs 59, 70, 84, 89, 90, 93, 100, 107
- `REGION_003`: surahs 9, 12, 62, 72, 83, 101, 103

The large surahs (2, 3, 4, 7 …) are mostly **singletons** — each has a broad,
distinctive profile that resembles no other.

---

## 3. Do natural structural regions emerge?

**Weakly.** The honest answer is two-layered:

1. **At the raw level:** **No** — the corpus is one homogeneous structural field
   (mean cosine 0.835). There are no sharply separated structural regions.
2. **At the discriminative level:** ~54 weak clusters emerge (low cohesion ~0.28),
   largely reflecting **surah length / sparsity** — short surahs with similar rare-
   concept signatures group together, long surahs stand alone.

The regional structure is therefore **shallow and size-driven**, not a partition
into structurally distinct provinces.

---

## 4. Robustness

Region count is stable under the discriminative-similarity threshold sweep: **62 /
54 / 54** regions at thresholds 0.3 / 0.4 / 0.5. The weak-region finding is not a
threshold artifact.

---

## 5. Verdict

> The corpus is **predominantly one homogeneous structural field** (raw fingerprint
> cosine 0.835). Discriminative clustering exposes ~54 *weak* regions (cohesion
> ~0.28) that mostly track surah length, not distinct structural roles. No sharply
> separated structural regions emerge.

---

## 6. Reproduce

```bash
python3 scripts/build_locality.py
python3 scripts/validate_locality.py --rebuild
```

Source: `generated/locality/structural_fingerprints.json`,
`region_candidates.json`, `region_similarity.json`.
