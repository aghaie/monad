# Story-Function Report — Phase Q (F)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`quranic-methodology-1.0`.

Why does the Quran tell stories? Phase F tests whether the story vocabulary
(قصص، عبرة، مثل) functions *methodologically* — as material for reasoning — by
measuring what the 178 story-ayahs co-occur with.

---

## 1. The function of story

| Measure | Count |
|---|--:|
| Story-ayahs (قصص / عبرة / مثل) | 178 |
| …co-occurring with cognition (علم، عقل، فكر، ذكر، دبر) | 42 |
| …co-occurring with signs (آيات) | 18 |
| …co-occurring with عبرة (explicit "lesson") | 9 |

---

## 2. Finding

> The story vocabulary functions **methodologically, not merely narratively.**
> Story-ayahs co-occur with cognition (42) and signs (18), and the Quran labels stories
> with the explicit root **عبرة (lesson/instruction, 9 ayahs)** and frames them as
> **مثل (example/parable)**. Narrative is presented as *material to reason from* — a
> lesson, an example — rather than as history for its own sake. This makes story a
> third evidence-source in the Quran's method (alongside nature and the text),
> addressed, like the others, to cognition.

The honest caveat: only a minority of story-ayahs (42 of 178) carry explicit cognition
vocabulary in the same ayah; the methodological framing is real but localised to where
the Quran makes it explicit.

---

## 3. Reproduce

```bash
python3 scripts/build_quranic_methodology.py
python3 scripts/validate_quranic_methodology.py --rebuild
```

Source: `generated/quranic_methodology/story_functions.json`.
