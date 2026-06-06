# Method-Repetition Report — Phase Q (E)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`quranic-methodology-1.0`.

A genuine method is *repeated*, not stated once. Phase E ranks the method-actions by
total verbal calls (imperative + imperfect) — how often the Quran actually *invokes*
each cognitive act.

---

## 1. Most-repeated method-actions

| Root | Category | Imperative | Imperfect | Total verbal calls |
|---|---|--:|--:|--:|
| علم | know | 31 | 334 | **365** |
| ذكر | remember | 56 | 71 | 127 |
| نظر | look | 48 | 56 | 104 |
| سال | ask | 16 | 78 | 94 |
| سمع | listen | 13 | 61 | 74 |
| تلو | recite | 7 | 51 | 58 |
| عقل | reason | 0 | 48 | 48 |
| حكم | discern | 7 | 39 | 46 |
| بين | clarify | 3 | 35 | 38 |
| شهد | witness | 10 | 24 | 34 |
| بصر | perceive | 4 | 25 | 29 |
| فكر | reflect | 0 | 17 | 17 |
| سير | travel | 7 | 10 | 17 |
| قرا | read | 6 | 5 | 11 |
| دبر | ponder | 0 | 8 | 8 |

(فهم, آيات-as-verb, برهان: 0 verbal calls.)

---

## 2. Finding

> The Quran **repeats methods of understanding, not just topics.** The most-repeated
> method-action is **knowing (علم, 365 verbal calls)**, then **remembering (ذكر, 127)**,
> **looking (نظر, 104)**, **asking (سؤال, 94)**, and **listening (سمع, 74)**. These are
> cognitive *acts*, invoked hundreds of times in verbal (commanding/continuous) form.
> The repetition is the signature of a method: the same operations of understanding are
> called for again and again across the corpus.

Note the honest limits: تدبّر (ponder) — the word most associated with deliberate
Quran-reading — appears only 8× in verbal form, and تفكّر (reflect) 17×. The weight of
the repeated method falls on **knowing, remembering, looking, asking** rather than on
the rarer contemplative roots.

---

## 3. Reproduce

```bash
python3 scripts/build_quranic_methodology.py
python3 scripts/validate_quranic_methodology.py --rebuild
```

Source: `generated/quranic_methodology/repetition_patterns.json`.
