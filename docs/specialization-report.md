# Specialization Report — Phase 14 (D)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase14-locality-1.0`.

Phase D measures each discovered region's contribution to the structural functions
(hub support, motif vocabulary, consistency, SCC formation, identity). Are some
regions general-purpose, some specialized?

---

## 1. Functional contribution

Because the corpus is one homogeneous field (see `region-discovery-report.md`), the
regions are not structurally distinct *territories*. The meaningful specialisation
is **functional and size-driven**, measured per structural function over the whole
corpus (`redundancy-report.md` gives the counts):

| Function | Providing surahs | Coverage | Specialisation |
|---|---:|---:|---|
| Consistency | 114 | 100% | **ubiquitous** (every surah preserves it) |
| Hub support | 104 | 91% | **ubiquitous** |
| SCC support | 43 | 38% | **common** |
| Motif generation | 21 | 18% | **rare** (concentrated in large surahs) |

---

## 2. Findings

- **Hub support and consistency are general-purpose:** essentially every surah
  carries the hub and preserves the consistency property. These functions are not
  localised at all.
- **Motif generation is the one specialised function:** only ~18% of surahs
  individually generate a rich motif vocabulary (≥ 8 triad classes) — and these are
  the **large surahs** (2, 3, 4, 7, …). A small surah simply lacks enough verses to
  realise the full motif vocabulary internally. This is a **size effect**, not a
  thematic specialisation.
- **SCC support is intermediate:** ~38% of surahs individually contain a size-9+
  strongly-connected component.

---

## 3. General-purpose vs specialized regions

| Region type | Finding |
|---|---|
| General-purpose (covers ≥ 70% of concepts) | the large surahs / dense regions — they reproduce most of the global structure alone |
| Specialized | **none in the thematic sense** — the only specialisation is that motif/SCC density scales with surah length |

There are **no regions that specialise in a distinct structural role** (e.g. "a
hub-support region" vs "a consistency region"). Every region does everything; the
larger ones simply do more of it because they contain more verses.

---

## 4. Verdict

> The corpus has **no thematic structural specialisation.** Hub support and
> consistency are ubiquitous; motif and SCC generation scale with surah size. The
> only "specialised" regions are the large surahs, which are general-purpose at
> higher volume — a size gradient, not a division of structural labour.

---

## 5. Reproduce

```bash
python3 scripts/build_locality.py
python3 scripts/validate_locality.py --rebuild
```

Source: `generated/locality/specialization_analysis.json`,
`redundancy_analysis.json`.
