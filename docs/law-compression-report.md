# Law-Compression Report — Phase R (I)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`reality-discovery-1.0`.

Phase I asks whether the surviving laws reduce to fewer, more fundamental سنن — or
whether no reduction is possible.

---

## 1. The compression

The 9 surviving laws group by outcome-class into **3 fundamental سنن**:

| Meta-سنّة | Consequent | Subsumes | Antecedents |
|---|---|--:|---|
| **corruption → downfall** | COLLAPSE | 6 laws (L02, L03, L04, L06, L07, L08) | denial, arrogance, belying, crime, sin, corruption |
| **constructive conduct → flourishing** | THRIVE | 2 laws (L09, L10) | gratitude, patience |
| **deed → recompense** | RECOMPENSE | 1 law (L15) | deed (the general law) |

**Reducible: yes.** 9 → 3.

---

## 2. Finding

> The surviving laws **compress genuinely** — 9 specific conduct→outcome laws collapse
> into **3 fundamental سنن**:
>
> 1. **Moral corruption brings downfall** — six different antecedents (denial,
>    arrogance, belying, crime, sin, corruption) all lead to one outcome: collapse. This
>    is the most robust سنّة in the corpus.
> 2. **Constructive conduct brings flourishing** — gratitude and patience lead to
>    increase. (Notably *thin*: faith, guidance, righteous-deed, and justice did **not**
>    survive Phase G, so this positive سنّة rests on only two antecedents.)
> 3. **The deed meets its recompense** — the general law (عمل → جزاء) that subsumes both
>    polarities: action, of any kind, meets a consequence.
>
> These three can themselves be read as one: **a moral order in which conduct
> determines outcome** — but the corpus evidence is strongest for the *downfall*
> direction and weakest for the *flourishing* direction.

---

## 3. The honest asymmetry

The compression is real but **lopsided**. The collapse سنّة draws on six robust
antecedents; the flourishing سنّة on only two. The Quran's internally cleanest reality-law
is that *corruption ends in ruin* — its assertion that *virtue ends in thriving* is
present but far less separable from counter-instances (Phase G). The minimal set is three
laws, but they are not of equal strength.

---

## 4. Reproduce

```bash
python3 scripts/build_reality.py
python3 scripts/validate_reality.py --rebuild
```

Source: `generated/reality/law_compression.json`.
