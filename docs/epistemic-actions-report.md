# Epistemic-Actions Report — Phase X (A)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`epistemology-discovery-1.0`.

Every prior phase asked what *structures* exist in the Quran. Phase X asks how the Quran
moves a human from **not-knowing to knowing** — its own epistemology, discovered, never
assumed. We assume nothing is central (not observation, not reason, not faith);
everything is measured. Phase A inventories the actions the Quran repeatedly asks a human
to *perform*.

---

## 1. The epistemic actions, ranked by verbal calls

(imperative + imperfect tokens — how often the Quran actually *calls* for the act)

| Action | Roots | Tokens | Imperative | Imperfect | Verbal calls |
|---|---|--:|--:|--:|--:|
| **observe** | نظر بصر راي شهد | 765 | 71 | 311 | **382** |
| **remember** | ذكر | 292 | 56 | 71 | 127 |
| **question** | سأل | 129 | 16 | 78 | 94 |
| **listen** | سمع | 185 | 13 | 61 | 74 |
| **reflect** | فكر دبر عقل | 111 | 0 | 73 | 73 |
| **read** | قرأ تلا | 151 | 13 | 56 | 69 |
| **travel** | سار | 27 | 7 | 10 | 17 |
| **compare** | مثل وزن كيل | 208 | 2 | 1 | 3 |

---

## 2. Finding

> **The Quran's epistemology is action-driven, and the dominant act is observation**
> (382 verbal calls — more than the next two combined). Knowing begins in *doing*: look,
> remember, ask, listen, reflect, read, travel. The verb is never absent — even the most
> abstract states are reached through a commanded act.
>
> Two honest notes: (1) **reflect** (تفكّر/تدبّر/تعقّل) is *never imperative* (0) — it
> appears only in the continuous "those who reflect" form, suggesting it is framed as an
> ongoing disposition rather than a one-off command. (2) **compare** (مثل) is almost
> never verbal (3 calls) — its 208 tokens are overwhelmingly the *noun* مَثَل (parable),
> so "comparison" enters the epistemology as material the text supplies, not an act it
> commands.

This sets the vocabulary; Phases B–F discover the *order* in which these acts lead to
knowing.

---

## 3. Reproduce

```bash
python3 scripts/build_epistemology.py
python3 scripts/validate_epistemology.py --rebuild
```

Source: `generated/epistemology/epistemic_actions.json`.
