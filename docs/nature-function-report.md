# Nature-Function Report — Phase Q (G)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`quranic-methodology-1.0`.

Why does the Quran point to the sky, the earth, night and day, rain and plants?
Phase G tests whether nature is invoked *as evidence* — as signs to reason about — by
measuring the fraction of nature-ayahs that also carry signs/cognition vocabulary.

---

## 1. Nature as sign

Across **1,141 nature-ayahs**, **291 (25.5%)** also carry آيات or cognition vocabulary.
Per nature-root:

| Root | Meaning | Ayahs | With signs | With cognition | Methodological frac. |
|---|---|--:|--:|--:|--:|
| دبب | beasts | 18 | 4 | 6 | 0.56 |
| ليل | night | 81 | 17 | 23 | 0.49 |
| نبت | plants | 23 | 5 | 6 | 0.48 |
| سمو | sky | 352 | 28 | 103 | 0.37 |
| ارض | earth | 440 | 32 | 114 | 0.33 |
| نهر | day | 102 | 15 | 18 | 0.32 |
| خلق | creation | 218 | 15 | 49 | 0.29 |
| نعم | cattle | 128 | 7 | 27 | 0.27 |
| بشر | humankind | 119 | 8 | 17 | 0.21 |
| انس | humans | 93 | 2 | 15 | 0.18 |
| شجر | trees | 26 | 0 | 3 | 0.12 |
| مطر | rain | 9 | 0 | 0 | 0.00 |

---

## 2. Finding

> The Quran invokes nature **as signs to be reasoned about**, not as mere description.
> A quarter of all nature-ayahs (291/1141) carry signs or cognition vocabulary, and for
> the canonical sign-pairs — **night (0.49)**, **plants (0.48)**, **sky (0.37)**,
> **earth (0.33)** — the methodological fraction is far higher. Sky and earth alone
> account for 217 of the 291 cognition co-occurrences. Nature is the Quran's largest
> single field of evidence, addressed to reason.

Honest limits: some nature-roots are *not* methodologically framed — rain (مطر, 0.00),
trees (شجر, 0.12), humans-as-إنس (0.18) appear largely outside the signs/cognition
frame. The "nature-as-sign" method is concentrated in the cosmological roots (sky,
earth, night/day, creation), not uniform across all of nature.

---

## 3. Reproduce

```bash
python3 scripts/build_quranic_methodology.py
python3 scripts/validate_quranic_methodology.py --rebuild
```

Source: `generated/quranic_methodology/nature_functions.json`.
