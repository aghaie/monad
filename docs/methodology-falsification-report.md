# Methodology-Falsification Report — Phase Q (J)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`quranic-methodology-1.0`.

Phase J attacks the central claim. We do not assume the Quran has a method; we test six
competing hypotheses against the corpus statistics and keep only what survives. The
test imports no external method — every verdict rests on the Quran's own
method-vocabulary counts.

---

## 1. The hypotheses

| ID | Hypothesis | Result | Evidence |
|---|---|---|---|
| **H1** | The Quran offers *no* defined method of understanding | **FALSIFIED** | 6,173 method-vocabulary tokens; 208 commanding imperatives — method is pervasive |
| **H2** | The Quran relies on *faith only* | **FALSIFIED** | 1,468 reasoning-vocabulary tokens + 649 observation tokens — reason/observation heavily invoked |
| **H3** | The Quran relies on *reason only* | **FALSIFIED** | it also invokes signs (آيات), observation (نظر/سمع), nature, and the text |
| **H4** | The Quran relies on *the text only* | **FALSIFIED** | it points outward — 291 nature-ayahs carry signs/cognition; history via stories |
| **H5** | The Quran relies on *nature only* | **FALSIFIED** | it also invokes the text (كتاب/قرآن), reason, and history |
| **H6** | The Quran offers an *integrative (combined)* method | **SURVIVES** | it integrates observation + signs (nature/history/self) + reason + the text — no single source |

**Five single-source hypotheses are falsified; one survives: the integrative
method.**

---

## 2. Why H1 fails

The "no method" hypothesis cannot stand against 6,173 method-vocabulary tokens and 208
imperatives *commanding* cognitive acts (look, remember, ask, reason, travel, read).
Method-talk is not incidental; it is one of the corpus's densest semantic fields.

## 3. Why the single-source hypotheses (H2–H5) all fail

Each "X only" hypothesis is refuted by the *presence of the others*: the Quran reasons
(against faith-only), but also points to signs and observation (against reason-only);
it is a text that repeatedly points *outside itself* to nature and history (against
text-only); and it grounds itself in the text and reason as well as nature (against
nature-only). No single source is sufficient to describe the method, because the corpus
deploys all of them together.

## 4. Why H6 survives

The surviving structure is **integration**: the recurring pattern is *observe a sign —
in nature, history, the self, or the text — and reason/reflect/remember toward a
conclusion.* Signs co-occur with reason (94), nature (77), text (44), self (38), and
history (18) simultaneously; nature is cast as sign; story is cast as lesson; and the
text describes itself functionally (clarification, guidance, reminder). The method is
not one source but the *coordination* of several, all addressed to cognition.

---

## 5. Verdict

> **H1–H5 are falsified; H6 survives.** The Quran does provide an internal methodology
> for understanding itself, and it is **integrative** — observe the signs (in text,
> nature, history, and the human self) and reason / reflect / remember — not a
> single-source method. This is the Quran's own stated method, measured from the Quran
> alone, with no external method imported.

---

## 6. Honest limits

This is a *descriptive co-occurrence* result, not a proof that the method is correct or
that following it yields truth. The contemplative roots most associated with deliberate
reading (تدبّر, تفکّر) are rare (8 and 17 verbal calls); the weight of the method falls
on knowing, remembering, looking, and asking. The "nature-as-sign" framing is
concentrated in the cosmological roots, not uniform. The phase shows the Quran *states*
a method; it does not and cannot (within the prohibitions) adjudicate that method's
validity.

---

## 7. Reproduce

```bash
python3 scripts/build_quranic_methodology.py
python3 scripts/validate_quranic_methodology.py --rebuild
```

Source: `generated/quranic_methodology/falsification_results.json`.
