# Contrast Report — Phase Σ (D)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`sigma-semantics-1.0`.

Phase D searches for concepts that function as Quran-internal opposites — not
lexical or dictionary opposites, but concepts that the Quran's own usage keeps
apart.

---

## 1. Definition of a Quran-internal opposite

A pair (A, B) is a **contrast** if they **never co-occur** (co = 0) despite **both
being frequent** (marginals ≥ 30). This is evidence-based opposition: the corpus
systematically never places them together.

| Quantity | Value |
|---|---|
| Contrast pairs | **401** |

---

## 2. Strongest contrasts (evidence only)

Ranked by combined marginal (the most frequent pairs that never co-occur). Anchors
are evidence labels, never glossed:

| A (anchor) | never with | B (anchor) | combined marginal |
|---|---|---|---:|
| `CONCEPT_060` (`سوا`) | ✗ | `CONCEPT_103` (`مري`) | 663 |
| `CONCEPT_002` (`ولد`) | ✗ | `CONCEPT_045` (`سقط`) | 582 |
| `CONCEPT_015` (`سال`) | ✗ | `CONCEPT_045` (`سقط`) | 358 |
| `CONCEPT_018` (`روح`) | ✗ | `CONCEPT_090` (`حلل`) | 305 |
| `CONCEPT_018` (`روح`) | ✗ | `CONCEPT_091` (`عرف`) | 300 |

(Full list in `contrasts.json`.) These are reported as opaque concept pairs with
anchor evidence — the Quran's own systematic separations, with no claim about what
they mean.

---

## 3. Findings

- **Quran-internal opposition emerges** — 401 frequent concept pairs that never
  co-occur. These are evidence-based contrasts, not imported antonyms.
- **Contrast is a real part of the semantic network.** Each concept's contrasts
  contribute to its definition (Phase B) and boundary (Phase C). Opposition is
  measured, not assumed.
- **No semantic valence is claimed.** The structure shows A and B are kept apart; it
  does **not** say one is "good" and the other "bad" — that would be interpretation.

---

## 4. Verdict

> **Quran-internal opposites emerge.** 401 frequent concept pairs never co-occur —
> evidence-based contrasts that the corpus systematically maintains. These are real
> relational oppositions (not lexical antonyms) and form part of every recoverable
> concept's definition; no valence or meaning is assigned.

---

## 5. Reproduce

```bash
python3 scripts/build_semantics.py
python3 scripts/validate_semantics.py --rebuild
```

Source: `generated/semantics/contrasts.json`.
