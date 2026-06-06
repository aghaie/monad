# Recursive Stability Report — Phase 15 (F)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase15-consistency-propagation-1.0`.

Phase F investigates whether the recursive structures — SCCs and cycles — preserve
consistency. Each SCC is checked for internal self-negation and removed.

---

## 1. SCC analysis

For each of the 7 irreducible dependency SCCs:

| Quantity | Value |
|---|---:|
| SCCs tested | 7 (sizes 9, 4, 3, 3, 3, 3, 2) |
| SCCs with an internal exclusion pair (self-negating) | **0** |
| Maximum contradictions created by any SCC removal | **0** |

- **No SCC is self-negating** — no SCC contains an internal exclusion pair (members
  that depend on one another yet never co-occur). Every cycle is backed by real
  co-occurrence among its members, as Phase 10 found.
- **Removing any SCC creates 0 contradictions** — the recursive cores are not
  carrying the consistency property.

---

## 2. Are cycles preserving consistency?

**No.** The relationship is the reverse of what the hypothesis supposes:

- The SCCs are **consistent because M is consistent**, not the other way round.
- A cycle (mutual dependency) is self-supporting whenever its members co-occur —
  which they do — but this is a *consequence* of the matrix's coherence, not a
  *mechanism* that produces it.
- Removing the cycles leaves consistency intact (0 contradictions), so they cannot
  be what maintains it.

---

## 3. Stability contribution / conflict resistance

| Question | Answer |
|---|---|
| Do SCCs contribute stability to consistency? | **No** — their removal changes nothing |
| Do cycles resist conflict? | There are no conflicts to resist |
| Do recursive structures reinforce consistency? | **No** — consistency is matrix-level, not cycle-level |

---

## 4. Verdict

> **Cycles do not maintain consistency.** No SCC is self-negating, and removing any
> SCC creates 0 contradictions. The recursive structures are consistent because the
> activation matrix is consistent — not vice versa. Hypothesis H3 ("SCCs maintain
> consistency") is **falsified**.

---

## 5. Reproduce

```bash
python3 scripts/build_consistency_propagation.py
python3 scripts/validate_consistency_propagation.py --rebuild
```

Source: `generated/consistency_propagation/recursive_stability.json`.
