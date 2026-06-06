# Imperative-Method Report — Phase Q (B)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`quranic-methodology-1.0`.

Phase B asks whether the Quran merely *mentions* understanding or actively *commands*
it. We count imperative-mood (IMPV) tokens of the cognition / observation / inquiry
roots — what the Quran tells the reader to *do*. Mood is read from the morphology
`features_raw` field (`IMPV`), purely from the corpus.

---

## 1. Commanded method-actions

The corpus contains **1,876 imperative tokens** in total; **208** of them command a
method-action:

| Root | Category | Imperatives |
|---|---|--:|
| ذكر | remember / recall | 56 |
| نظر | look / observe | 48 |
| علم | know | 31 |
| سال | ask / inquire | 16 |
| سمع | listen | 13 |
| شهد | witness | 10 |
| حكم | judge / discern | 7 |
| سير | travel (and see) | 7 |
| تلو | recite | 7 |
| قرا | read | 6 |
| بصر | perceive | 4 |
| بين | make clear | 3 |

---

## 2. Finding

> Understanding is **commanded, not merely described.** The Quran issues 208
> imperative tokens telling the reader to *look* (نظر), *remember* (ذكر), *ask* (سأل),
> *listen* (سمع), *witness* (شهد), *travel and observe* (سير), and *read/recite*
> (قرأ/تلا). The single most-commanded action is **remembrance/recall (ذكر, 56)**,
> followed by **observation (نظر, 48)**. The method has imperative force: the reader is
> directed to perform cognitive acts, not to passively receive.

This falsifies any reading on which the Quran offers no method (tested formally in
Phase J, H1).

---

## 3. Reproduce

```bash
python3 scripts/build_quranic_methodology.py
python3 scripts/validate_quranic_methodology.py --rebuild
```

Source: `generated/quranic_methodology/imperatives.json`.
