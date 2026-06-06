# Definition Discovery Report — Phase Σ (B)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`sigma-semantics-1.0`.

Phase B searches for places where the Quran defines a concept — through
association, dependency, contrast, and antecedence — and builds candidate
definitions **entirely from other Quranic concepts**, never external words.

---

## 1. Method

For each recoverable concept, a definition is assembled from Quran-internal
relations only:

| Definition field | Source |
|---|---|
| `associated_with` | Phase-3 semantic-overlap neighbours (strongest co-membership) |
| `requires` | Phase-4 REQUIRES targets |
| `contrasts_with` | exclusion partners (never co-occur) |
| `preceded_by` | Phase-4 PREDICTS antecedents |

Every field is a list of **opaque concept ids**. The Arabic anchor is an evidence
label, not part of the definition.

---

## 2. Result

| Quantity | Value |
|---|---|
| Concepts defined (Quran→Quran) | **89** |

**89 concepts receive a definition built entirely from other concepts.** No
external word appears in any definition.

---

## 3. Example definition (evidence only)

`CONCEPT_016` (anchor evidence `جنن`):

```
CONCEPT_016 is the concept that:
  associates with   CONCEPT_097, CONCEPT_060, CONCEPT_072, CONCEPT_049, CONCEPT_036
  requires          CONCEPT_007
  is preceded by    CONCEPT_010, CONCEPT_011, CONCEPT_012
```

This is a complete Quran→Quran definition: `CONCEPT_016` is fixed by its relations
to seven other concepts. No external language is used; the anchor `جنن` is shown
only as the corpus-internal evidence of what root dominates it.

---

## 4. What the definitions are

The definitions are **relational positions**: each concept is located by the company
it keeps (associates), what it presupposes (requires), what it excludes (contrasts),
and what precedes it. This is a genuine internal semantic network — but it defines
each concept *circularly in terms of others*, never grounding any concept in
external reference. The network is self-contained: every definition points only
inward.

---

## 5. Verdict

> **The Quran can define 89 of its concepts in terms of one another.** Each
> definition is built entirely from other opaque concepts (associates, requires,
> contrasts, antecedents) with no external word. The definitions form a
> self-contained relational network — meaning expressed as position, not reference.

---

## 6. Reproduce

```bash
python3 scripts/build_semantics.py
python3 scripts/validate_semantics.py --rebuild
```

Source: `generated/semantics/definitions.json`.
