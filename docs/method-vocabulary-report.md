# Method-Vocabulary Report — Phase Q (A)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`quranic-methodology-1.0`.

Every prior phase asked *what* the Quran is. Phase Q asks a different question:
**does the Quran itself say how it should be understood?** No external method is
imported — not philosophical, theological, mystical, academic, traditional, modern,
or even Monad's own. We measure only the Quran's own method-vocabulary,
descriptively, from the corpus. Concepts stay opaque; Arabic roots are evidence,
never glossed.

---

## 1. The method-vocabulary

Phase A locates every corpus root the Quran uses to talk about *how to know*, grouped
by function. **6,173 method-vocabulary tokens** in total.

| Group | Roots (token_count) |
|---|---|
| **Cognition / reason** | علم 854, حكم 210, ذكر 292, دبر 44, عقل 49, فكر 18, فهم — |
| **Observation / perception** | بصر 148, سمع 185, نظر 129, شهد 160, سير 27 |
| **Evidence / signs** | بين 523, ايي 382, برهن — |
| **Inquiry / text** | سال 129, قرا 88, تلو 63 |
| **Self-description** | كتب 319, هدي 316, نور 194, فرق 72 |
| **Nature** | ارض 461, سمو 381, خلق 261, نعم …, ليل 81, نهر 102, … |
| **Story** | مثل 169, قصص 30, عبر 9 |

The vocabulary of *method* is not marginal: cognition (علم alone 854), evidence
(بين 523, آيات 382), and observation (سمع, بصر, شهد) are among the most frequent
non-grammatical roots in the corpus.

---

## 2. Distribution

The method-vocabulary is spread across both revelation halves (Meccan and Medinan),
not confined to one period — observation, signs, and reasoning appear throughout. The
per-root Meccan/Medinan split is recorded in `method_vocabulary.json`.

---

## 3. Co-occurrence

The method-words cluster together within ayahs. The strongest method-word pairings
(shared-ayah counts, top of `top_method_cooccurrences`) bind **آيات (signs) ↔ cognition
roots** and **nature ↔ signs** — the first structural hint of an internal method:
the Quran presents *signs* and commands *reasoning* about them in the same breath.

---

## 4. Finding

> The Quran possesses a large, distributed, internally-clustered vocabulary *about how
> to understand* — 6,173 tokens across cognition, observation, evidence, inquiry, and
> self-description. Method-talk is pervasive, not incidental. Whether it forms a
> coherent *method* is tested in Phases B–J.

---

## 5. Reproduce

```bash
python3 scripts/build_quranic_methodology.py
python3 scripts/validate_quranic_methodology.py --rebuild
```

Source: `generated/quranic_methodology/method_vocabulary.json`.
