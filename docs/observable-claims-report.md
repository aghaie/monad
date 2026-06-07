# Observable-Claims Report — Phase R (B, C)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`reality-discovery-1.0`.

Phase B asks *what* the Quran wants observed in each phenomenon (not the thing, but its
order, change, creation, succession). Phase C then isolates the **observable** claims —
excluding the unseen and the hereafter, which cannot be tested in the world.

---

## 1. What the Quran asks to observe (Phase B)

The Quran does not present phenomena as static objects but as carriers of *process*. For
each domain we count co-occurrence with observation-modes (order, change, creation,
ruin/succession). Across domains, the recurring instruction is to observe **creation,
order, change, and the succession/ruin of what came before** — phenomena as signs of a
process, not inert facts. (Per-domain mode counts in `reality_patterns.json →
observation_modes`.)

---

## 2. The observable-claims corpus (Phase C)

| Quantity | Value |
|---|--:|
| Ayahs referencing observable phenomena (10 domains) | 3,859 |
| **Observable claims** (after excluding unseen/hereafter) | **3,402** |
| Excluded as eschatological/unseen (آخرة، جنّة، بعث، غيب، حشر، قبر، خلد، صور) | 457 |
| Observable fraction | **0.88** |

---

## 3. Finding

> **88% of the Quran's domain-claims are about the OBSERVABLE world.** After removing
> the 457 ayahs that mix in the unseen and the hereafter, 3,402 ayahs remain that make
> claims testable, in principle, against the visible world — about nature, peoples,
> history, conduct, and their outcomes. The Quran's reality-discourse is
> overwhelmingly about *this* world, and it asks the reader to observe **process**
> (creation, order, change, succession) rather than static objects.

This is the corpus of claims Phases D–J interrogate.

---

## 4. Honest boundary

These are claims the Quran *makes about* the observable world. Whether each holds in the
external world cannot be tested here — no external dataset is permitted. Phases D–J test
only what the corpus can: whether the Quran asserts these patterns *cross-domain* and
*consistently with itself*.

---

## 5. Reproduce

```bash
python3 scripts/build_reality.py
python3 scripts/validate_reality.py --rebuild
```

Source: `generated/reality/observable_claims.json`, `reality_patterns.json`.
