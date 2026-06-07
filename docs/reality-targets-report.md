# Reality-Targets Report — Phase R (A)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`reality-discovery-1.0`.

For the first time in Monad the direction reverses. Every prior phase looked *inward*
at the text. Phase R asks outward: **which phenomena in reality does the Quran invite us
to observe?** This is not a proof, defence, or refutation of the Quran — only an
extraction, then a test. Phase A extracts the *targets*: the observable phenomena the
Quran refers to, and which it explicitly calls آيات (signs).

---

## 1. The ten domains of observable phenomena

The Quran's reality-targets, by domain (corpus roots; phenomena stay opaque):

| Domain | Phenomena (roots) | Sign-ayahs in domain |
|---|---|--:|
| **nature** | sky, earth, sun, moon, stars, night, day, rain, sea, mountains, plants, trees, creation | high |
| **human** | human, humankind, self, heart, reason, death, life | — |
| **society** | people, nations, mankind, townships, cities | — |
| **history** | generations, messengers, tidings, narratives, succession, perishing, destruction, ruins, outcome | — |
| **ethics** | justice, injustice, truth, falsehood, good, evil, corruption, rectitude, equity | — |
| **psyche** | self, heart, fear, grief, tranquility, whispering, repose | — |
| **family** | spouse, offspring, kinship, marriage, lineage | — |
| **economy** | wealth, provision, earning, trade, usury, spending, poverty, affluence, hoarding | — |
| **power** | dominion, authority, might, abasement, strength, weakness, transgression, tyranny | — |
| **civilization** | building, construction, townships, cities, ruins, generations | — |

353 ayahs invoke آيات (signs) explicitly; the phenomena above are what those signs
point to.

---

## 2. Finding

> The Quran directs observation to a **broad, structured field of reality** — ten
> domains spanning the cosmos, the human person, society, history, ethics, the psyche,
> the family, the economy, power, and civilization. It does not point to a narrow
> religious sphere but to the *whole observable world*, and explicitly labels much of
> it آيات (signs to be read). This sets the targets; Phases B–J test what the Quran says
> *about* them.

---

## 3. Reproduce

```bash
python3 scripts/build_reality.py
python3 scripts/validate_reality.py --rebuild
```

Source: `generated/reality/reality_targets.json`.
