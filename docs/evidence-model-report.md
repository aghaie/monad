# Evidence-Model Report — Phase Q (C)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`quranic-methodology-1.0`.

If the Quran commands the reader to recognise *signs* (آيات), what does it offer *as*
evidence? Phase C measures, for the 353 ayahs that invoke آيات, which categories of
evidence co-occur with them.

---

## 1. Evidence types cited alongside آيات

353 ayahs invoke آيات. Their co-occurring evidence categories:

| Evidence type | Sign-ayahs also containing it | Fraction |
|---|--:|--:|
| **Reason** (عقل، فكر، دبر، ذكر، علم، حكم) | 94 | 0.266 |
| **Nature** (سماء، أرض، ليل، نهار، خلق …) | 77 | 0.218 |
| **Text** (سؤال، قراءة، تلاوة) | 44 | 0.125 |
| **Human self** (إنس، بشر، خلق، نفس) | 38 | 0.108 |
| **History / story** (قصص، عبرة، مثل) | 18 | 0.051 |

---

## 2. Finding

> The Quran grounds its **signs** in a *plurality* of evidence types. The signs are
> presented for **reasoning** (the largest co-occurrence, 94 ayahs), drawn most often
> from **nature** (77) and the **text itself** (44), with the **human self** (38) and
> **history** (18) also invoked. No single evidence source dominates — the آيات are
> distributed across nature, text, self, and history, all addressed to reason.

This is the first quantitative sign that the Quran's method is **integrative**: its
evidence base is multi-source, not single-source. (Tested formally in Phase J,
H3–H5.)

---

## 3. Reproduce

```bash
python3 scripts/build_quranic_methodology.py
python3 scripts/validate_quranic_methodology.py --rebuild
```

Source: `generated/quranic_methodology/evidence_model.json`.
