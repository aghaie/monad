# Reality-Pattern Report — Phase R (D)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`reality-discovery-1.0`.

Phase D extracts the recurring *patterns* the Quran asserts about reality — directional
links from conduct to outcome — and measures each as a co-occurrence **lift** over its
base rate. No judgement yet; pure extraction.

---

## 1. The asserted patterns

For each antecedent root, the rate at which an outcome-class appears within ±1 ayah,
divided by that outcome's base rate across the corpus (lift):

| ID | Pattern | Antecedent ayahs | Co-occ. | P(outcome\|antecedent) | Base | **Lift** |
|---|---|--:|--:|--:|--:|--:|
| L15 | deed → recompense | 313 | 74 | 0.236 | 0.033 | **7.13** |
| L03 | denial → collapse | 465 | 143 | 0.308 | 0.065 | **4.77** |
| L09 | gratitude → thriving | 69 | 17 | 0.246 | 0.054 | **4.54** |
| L02 | corruption → collapse | 47 | 13 | 0.277 | 0.065 | **4.29** |
| L12 | righteous-deed → thriving | 170 | 39 | 0.229 | 0.054 | **4.23** |
| L11 | faith → thriving | 723 | 160 | 0.221 | 0.054 | **4.08** |
| L07 | crime → collapse | 65 | 17 | 0.262 | 0.065 | **4.05** |
| L01 | injustice → collapse | 290 | 74 | 0.255 | 0.065 | **3.95** |
| L04 | arrogance → collapse | 153 | 39 | 0.255 | 0.065 | **3.95** |
| L08 | sin → collapse | 37 | 9 | 0.243 | 0.065 | **3.77** |
| L06 | belying → collapse | 257 | 59 | 0.230 | 0.065 | **3.56** |
| L14 | guidance → thriving | 268 | 51 | 0.190 | 0.054 | **3.51** |
| L10 | patience → thriving | 93 | 16 | 0.172 | 0.054 | **3.17** |
| L13 | justice → thriving | 24 | 2 | 0.083 | 0.054 | 1.54 |
| L05 | transgression → collapse | 39 | 3 | 0.077 | 0.065 | 1.19 |

---

## 2. Finding

> **Every conduct→outcome pattern the Quran asserts shows positive lift.** Thirteen of
> fifteen show *strong* lift (3.2×–7.1×): an antecedent of conduct (denial, corruption,
> arrogance, gratitude, patience, faith, righteous deed) is followed, within an ayah, by
> its asserted outcome (collapse or thriving) three-to-seven times more often than that
> outcome's baseline rate. The single strongest is the general **deed → recompense**
> (عمل → جزاء, lift 7.13) — the Quran's most consistent reality-pattern is that *action
> meets consequence*.

Two patterns are weak: **justice → thriving** (lift 1.54, only 2 co-occurrences) and
**transgression → collapse** (lift 1.19) — honestly flagged as below the candidate
threshold in Phase F. The strong signal is real; it is not uniform.

---

## 3. Reproduce

```bash
python3 scripts/build_reality.py
python3 scripts/validate_reality.py --rebuild
```

Source: `generated/reality/reality_patterns.json`.
