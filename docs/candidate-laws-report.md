# Candidate-Laws Report — Phase R (F)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`reality-discovery-1.0`.

Phase F marks — but does **not** yet declare — laws. A pattern becomes a
`CANDIDATE_LAW` only if it is strong (lift > 1), cross-domain (≥ 3 of 10 domains), and
supported (≥ 5 co-occurring ayahs). Declaration waits for falsification (Phase G).

---

## 1. Marking criteria

`min_lift = 1.0` · `min_domains = 3` · `min_cooccurrence = 5`

| ID | Pattern | Lift | Domains | Co-occ. | Status |
|---|---|--:|--:|--:|---|
| L15 | deed → recompense | 7.13 | 10 | 74 | **CANDIDATE_LAW** |
| L03 | denial → collapse | 4.77 | 10 | 143 | **CANDIDATE_LAW** |
| L09 | gratitude → thriving | 4.54 | 9 | 17 | **CANDIDATE_LAW** |
| L02 | corruption → collapse | 4.29 | 8 | 13 | **CANDIDATE_LAW** |
| L12 | righteous-deed → thriving | 4.23 | 10 | 39 | **CANDIDATE_LAW** |
| L11 | faith → thriving | 4.08 | 10 | 160 | **CANDIDATE_LAW** |
| L07 | crime → collapse | 4.05 | 8 | 17 | **CANDIDATE_LAW** |
| L01 | injustice → collapse | 3.95 | 10 | 74 | **CANDIDATE_LAW** |
| L04 | arrogance → collapse | 3.95 | 9 | 39 | **CANDIDATE_LAW** |
| L08 | sin → collapse | 3.77 | 9 | 9 | **CANDIDATE_LAW** |
| L06 | belying → collapse | 3.56 | 9 | 59 | **CANDIDATE_LAW** |
| L14 | guidance → thriving | 3.51 | 10 | 51 | **CANDIDATE_LAW** |
| L10 | patience → thriving | 3.17 | 8 | 16 | **CANDIDATE_LAW** |
| L13 | justice → thriving | 1.54 | 3 | 2 | below_threshold |
| L05 | transgression → collapse | 1.19 | 4 | 3 | below_threshold |

---

## 2. Finding

> **13 of 15 patterns qualify as CANDIDATE_LAW** — strong, cross-domain, and supported.
> They are *not* yet declared laws; the next phase attacks each one with Quran-internal
> counter-examples. Two patterns (justice→thriving, transgression→collapse) fall below
> the support threshold and are set aside honestly — their co-occurrence is too sparse
> to mark.

---

## 3. Reproduce

```bash
python3 scripts/build_reality.py
python3 scripts/validate_reality.py --rebuild
```

Source: `generated/reality/candidate_laws.json`.
