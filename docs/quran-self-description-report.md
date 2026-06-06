# Quran Self-Description Report — Phase Q (H)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`quranic-methodology-1.0`.

How does the Quran describe *itself*? Phase H measures, for the 348 ayahs that refer to
the text (كتاب / قرآن), which self-descriptors co-occur — guidance, light, reminder,
criterion, clarification.

---

## 1. Self-descriptors

348 self-reference ayahs (containing كتاب or قرآن). Co-occurring descriptors:

| Descriptor | Meaning | Co-occurs with self-reference | Total ayahs |
|---|---|--:|--:|
| بين | clarification (bayān) | 64 | 454 |
| هدي | guidance (hudā) | 34 | 268 |
| ذكر | reminder (dhikr) | 33 | 264 |
| نور | light (nūr) | 16 | 174 |
| فرق | criterion (furqān) | 16 | 66 |

---

## 2. Finding

> The Quran most often describes itself — alongside its own self-reference — as
> **clarification (بيان, 64)**, then **guidance (هدى, 34)**, **reminder (ذكر, 33)**,
> **light (نور, 16)**, and **criterion (فرقان, 16)**. Every one of these descriptors is
> *functional and cognitive*: the text presents itself as an instrument for
> understanding — something that clarifies, guides, reminds, illuminates, and
> distinguishes — rather than solely as an object of belief. The Quran's self-image is
> continuous with the method it commands: it casts itself as the tool by which the
> reader is to *see clearly*, *remember*, and *discern*.

---

## 3. Reproduce

```bash
python3 scripts/build_quranic_methodology.py
python3 scripts/validate_quranic_methodology.py --rebuild
```

Source: `generated/quranic_methodology/self_descriptions.json`.
