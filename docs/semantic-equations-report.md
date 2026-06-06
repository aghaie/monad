# Semantic Equations Report — Phase Σ (F)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`sigma-semantics-1.0`.

Phase F searches for Quran-internal semantic equations — relational identities
among concepts — and tests them.

---

## 1. Equation forms (all Quran-internal)

| Equation | Form | Test |
|---|---|---|
| `REQUIRES` | A is always accompanied by D | co(A,D) ≥ 0.9·marginal(A) |
| `BEHAVES_LIKE` | A behaves like B | top neighbour weight ≥ 0.4 |

Each equation relates two **opaque concepts**; no external term appears.

---

## 2. Findings

- **Equations emerge and are testable.** REQUIRES equations (A always with D) and
  BEHAVES_LIKE equations (A's neighbourhood ≈ B) are extracted and checked against
  co-occurrence. Most hold by construction (they are derived from the same matrix).
- **REQUIRES equations are dominated by the hub.** Most "A is always accompanied by
  D" equations have D = `CONCEPT_007` (the frequency hub, present with everything).
  These are frequency identities, weakly informative.
- **BEHAVES_LIKE equations carry genuine semantic content** — when two concepts
  share a high-weight neighbourhood (≥ 0.4), they occupy nearly the same relational
  position. These equivalences (e.g. concepts that behave alike) are the genuine
  semantic-equation residue beyond frequency.

---

## 3. Honest reading

The equations are **relational identities**, not external definitions. "A behaves
like B" means A and B share the same company in the corpus — a genuine internal
equivalence — but it does not say what either denotes. The REQUIRES equations are
largely frequency (hub-mediated). The phase reports both, distinguishing the
frequency-driven equations from the genuine BEHAVES_LIKE equivalences.

---

## 4. Verdict

> **Quran-internal semantic equations emerge and are testable.** BEHAVES_LIKE
> equivalences (shared high-weight neighbourhoods) carry genuine relational content;
> REQUIRES equations are largely hub-frequency. Equations express relational
> identity among concepts, not external meaning.

---

## 5. Reproduce

```bash
python3 scripts/build_semantics.py
python3 scripts/validate_semantics.py --rebuild
```

Source: `generated/semantics/semantic_equations.json`.
