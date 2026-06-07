# Reality-Falsification Report — Phase R (G)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`reality-discovery-1.0`.

> **Filename note (immutability):** the Phase R spec listed this report as
> `docs/falsification-report.md`, but that filename already belongs to Phase 7 and prior
> phase outputs are never overwritten. This report is therefore written as
> `reality-falsification-report.md`. No prior file was modified.

Phase G attacks every candidate law. For each, we search the Quran itself for
**counter-examples**: ayah-windows where the antecedent appears with the *opposite*
outcome. A law survives only if its supporting co-occurrences strictly outnumber its
internal counter-examples.

---

## 1. The attack

For each candidate (antecedent → outcome), support = windows with the asserted outcome;
counter = windows with the opposite outcome (collapse↔thriving):

| ID | Pattern | Support | Counter-examples | Net | Result |
|---|---|--:|--:|--:|---|
| L15 | deed → recompense | 74 | 0 | +74 | **SURVIVES** |
| L03 | denial → collapse | 143 | 96 | +47 | **SURVIVES** |
| L04 | arrogance → collapse | 39 | 19 | +20 | **SURVIVES** |
| L06 | belying → collapse | 59 | 43 | +16 | **SURVIVES** |
| L07 | crime → collapse | 17 | 9 | +8 | **SURVIVES** |
| L09 | gratitude → thriving | 17 | 10 | +7 | **SURVIVES** |
| L08 | sin → collapse | 9 | 6 | +3 | **SURVIVES** |
| L02 | corruption → collapse | 13 | 11 | +2 | **SURVIVES** |
| L10 | patience → thriving | 16 | 15 | +1 | **SURVIVES** |
| L12 | righteous-deed → thriving | 39 | 43 | −4 | **REFUTED** |
| L01 | injustice → collapse | 74 | 81 | −7 | **REFUTED** |
| L14 | guidance → thriving | 51 | 62 | −11 | **REFUTED** |
| L11 | faith → thriving | 160 | 179 | −19 | **REFUTED** |

**9 candidate laws survive; 4 are refuted by Quran-internal counter-examples.**

---

## 2. The honest result — and why it matters

This is **not** a clean victory, and it is reported as it is. Four candidate laws
fail — including the morally intuitive **injustice → collapse** (74 support vs 81
counter) and three positive laws (**faith**, **guidance**, **righteous-deed** →
thriving). They fail because, within a ±1-ayah window, their antecedents co-occur with
the *opposite* outcome as often as (or more than) the asserted one.

The structural reason is the Quran's **antithetical style**: it pairs belief with
disbelief, the rewarded with the punished, the delivered with the destroyed, in adjacent
ayahs. So a window around "those who believe" catches both نصر/فلح (thriving) *and* the
عذاب of the contrasting clause; a window around ظلم (injustice) catches both هلك (the
oppressor's ruin) *and* نصر/نجاة (the oppressed's deliverance). The simple co-occurrence
test cannot separate the law from the contrast that frames it.

**This is a genuine limit, not a defect to hide.** The survivors are the laws whose
outcome-association is strong enough to *outweigh* the antithetical pairing — chiefly
the **collapse** direction (denial, arrogance, belying, crime, sin, corruption all →
downfall) plus the two clearest positive antecedents (gratitude, patience) and the
general deed→recompense.

---

## 3. The asymmetry

The **collapse** laws are markedly more robust than the **thriving** laws: 6 of 8
negative-conduct laws survive, but only 2 of 5 positive-conduct laws do, and faith,
guidance, and righteous-deed → thriving all fail the internal test. The Quran's
*downfall* senna is internally cleaner than its *flourishing* sunna — a finding that
runs against an apologetic reading and is reported precisely because the project forbids
protecting prior conclusions.

---

## 4. Verdict

> **9 of 13 candidate laws survive internal falsification; 4 are refuted.** The Quran's
> conduct→outcome regularities are internally real but not internally clean: the
> collapse direction survives robustly, the flourishing direction only partially, and
> several intuitive laws (including injustice→collapse) cannot be separated from the
> Quran's own antithetical pairing within a co-occurrence window. The survivors proceed
> to mapping and compression; the refuted are not carried forward as laws.

---

## 5. Reproduce

```bash
python3 scripts/build_reality.py
python3 scripts/validate_reality.py --rebuild
```

Source: `generated/reality/falsification_results.json`.
