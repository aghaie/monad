# Redundancy Report — Phase 14 (F)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase14-locality-1.0`.

Phase F measures whether each structural function appears once, multiple times, or
everywhere — i.e. how much backup structure exists.

---

## 1. Function redundancy

For each structural function, the number of surahs that substantially provide it:

| Function | Providing surahs | Fraction | Redundancy |
|---|---:|---:|---|
| Consistency | 114 / 114 | 1.00 | **ubiquitous** |
| Hub support (≥ 0.8 participation) | 104 / 114 | 0.91 | **ubiquitous** |
| SCC support (size-9+ internal) | 43 / 114 | 0.38 | **common** |
| Motif generation (≥ 8 classes internal) | 21 / 114 | 0.18 | **rare** |

---

## 2. Findings

- **Consistency is maximally redundant** — every one of the 114 surahs preserves
  the exclusion/positive disjointness internally. There is total backup: the
  consistency property cannot be removed by deleting any subset of surahs.
- **Hub support is near-ubiquitous** — 104 of 114 surahs activate `CONCEPT_007` in
  ≥ 80% of their ayahs. The hub is supported everywhere; it has no single carrier.
- **SCC support is common** — 38% of surahs individually contain a size-9+ SCC.
- **Motif generation is rare** — only 18% of surahs individually realise ≥ 8 triad
  classes. These are the large surahs; smaller surahs lack the verse volume to
  generate the full vocabulary alone. But because 21 surahs each generate it, the
  vocabulary still has multiple independent sources.

---

## 3. How much backup exists? Can one region replace another?

- **Hub and consistency:** essentially infinite backup — present in (nearly) every
  surah. Any surah can stand in for any other for these functions.
- **Motif / SCC generation:** moderate backup — ~21 / 43 independent providers.
  Removing one large surah does not remove the function; another supplies it (the
  motif vocabulary survives every single-region ablation, see
  `ablation-report.md`).

---

## 4. Verdict

> **The corpus carries massive structural redundancy.** Consistency and hub support
> are present in (nearly) every surah; motif and SCC generation each have ~20–40
> independent providers. No structural function depends on a single region — every
> function is backed up many times over. This is the redundancy basis for the
> ablation result that no region is indispensable.

---

## 5. Reproduce

```bash
python3 scripts/build_locality.py
python3 scripts/validate_locality.py --rebuild
```

Source: `generated/locality/redundancy_analysis.json`.
