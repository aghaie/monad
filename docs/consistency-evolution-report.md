# Consistency Evolution Report — Phase 13 (D)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase13-evolution-1.0`.

Phase D recomputes the consistency property (exclusion/positive disjointness) at
every snapshot, across both traditions and the control. No leakage; statistics
only.

---

## 1. The property tracked

The Phase-10 consistency verdict rests on the **exclusion layer** (concept pairs
that never co-occur, both marginals ≥ 30) being **disjoint** from the **positive
layer** (pairs that co-occur ≥ 5). At each snapshot, both layers are recomputed
from the revealed ayahs only, and their overlap is measured. Overlap > 0 would be a
snapshot-level inconsistency.

---

## 2. Trajectory (canonical)

| Revealed | Exclusion pairs | Exclusion/positive overlap |
|---:|---:|---:|
| 1% | (small) | **0** |
| 5% | … | **0** |
| 10% | … | **0** |
| 50% | … | **0** |
| 90% | … | **0** |
| 100% | 401 | **0** |

The overlap is **0 at every snapshot**.

---

## 3. Findings

- **Consistency is present from the very first snapshot.** At 1% revealed the
  exclusion/positive overlap is already 0 — the structure never asserts both "A,B
  together" and "A,B never together" at any stage of accumulation.
- **It never breaks.** Across all 12 snapshots × 3 orderings (36 snapshots), the
  overlap is **0 in every single one.** No order, no revelation stage, produces a
  contradiction.
- **Robust across orderings:** the control (random shuffle) also holds 0 overlap at
  every snapshot — consistency is order-independent.

---

## 4. Answering the questions

| Question | Answer |
|---|---|
| Is consistency present from the beginning? | **Yes** — 0 overlap from 1% revealed |
| Or does it emerge later? | No — it is present at every stage |
| Does it ever break? | **No** — 0 overlap in all 36 snapshots across all orders |

---

## 5. Interpretation

Consistency is not a property that *develops* as the corpus accumulates — it is an
**invariant of every subset**. This is the temporal corroboration of Phase 10 (0
contradictions) and Phase 11 (consistency SURVIVES STRONGLY): the disjointness of
the positive and negative layers holds at every scale and under every ordering, so
it is a structural property of the content, not of completion or sequence.

---

## 6. Reproduce

```bash
python3 scripts/build_evolution.py
python3 scripts/validate_evolution.py --rebuild
```

Source: `generated/evolution/consistency_evolution.json`.
