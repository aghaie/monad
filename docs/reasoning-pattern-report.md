# Reasoning-Pattern Report — Phase Q (D)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`quranic-methodology-1.0`.

Phase D looks for *recurring reasoning structures* — does the Quran repeat a fixed
argumentative move? We measure the sign→cognition pattern (the famous "for a people
who reason" refrain), the nature→sign pattern, and the story→lesson pattern, purely by
ayah co-occurrence and imperfect-verb counts.

---

## 1. The sign → cognition refrain

For each cognition root: ayahs where آيات co-occurs with it, and the imperfect-verb
("...یعقلون / یتفکّرون / یعلمون" refrain) token count:

| Root | Meaning | Sign+cognition ayahs | Imperfect refrain tokens |
|---|---|--:|--:|
| علم | know | 43 | 334 |
| ذكر | remember | 24 | 71 |
| عقل | reason | 13 | 48 |
| فكر | reflect | 10 | 17 |
| دبر | ponder | 3 | 8 |

The imperfect forms (یعلمون، یعقلون، یتفکّرون …) are the closing-refrain construction
the Quran attaches to its signs — and they are abundant (334 for علم, 71 for ذكر,
48 for عقل).

---

## 2. Other recurring patterns

| Pattern | Count |
|---|--:|
| Nature → signs (nature roots co-occur with آيات) | 77 ayahs |
| Story → signs (قصص/عبرة/مثل co-occur with آيات) | 18 ayahs |

---

## 3. Finding

> The Quran has a **dominant, repeated reasoning structure**: present a sign (آية),
> then invoke cognition — *"...so that a people who reason / reflect / know"*. This
> sign→cognition move recurs across the corpus (the imperfect refrain alone fires 334×
> for علم, 71× for ذكر, 48× for عقل). Nature is repeatedly cast *as* sign (77 ayahs),
> and stories carry signs (18). The method is not a loose vocabulary — it is a
> **recurring inferential pattern**: observe a sign → reason toward a conclusion.

---

## 4. Reproduce

```bash
python3 scripts/build_quranic_methodology.py
python3 scripts/validate_quranic_methodology.py --rebuild
```

Source: `generated/quranic_methodology/reasoning_patterns.json`.
