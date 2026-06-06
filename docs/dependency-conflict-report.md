# Dependency Conflict Report — Phase 10 (C)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase10-consistency-1.0`.

Phase C searches the dependency graph for incompatible structures: `A requires B`
and `A requires not-B`, `A depends on B` while `B prevents A`, or equivalent.
Structural evidence only; high burden of proof.

---

## 1. Searches and results

| Search | Rule | Result |
|---|---|---:|
| `REQUIRES(A,B)` that is also EXCLUSION (A,B never co-occur) | C1 | **0** |
| Mutual dependency `A↔B` with EXCLUSION (self-negating) | C5 | **0** |
| `REQUIRES` cycles (circular necessity) | — | **0** |

All three dependency-contradiction searches return **zero**.

---

## 2. C1 — necessity vs prevention

A genuine `A requires B / B prevents A` contradiction would appear as a `REQUIRES`
edge whose endpoints are also a strong EXCLUSION pair (co = 0). **None exists.**
Every `REQUIRES(A,B)` has `co(A,B) ≈ marginal(A) > 0` by construction — A and B
co-occur whenever A is present. A `REQUIRES` edge and an EXCLUSION on the same pair
cannot both hold in one matrix, and the data confirms it: 0 collisions.

---

## 3. C5 — self-negating mutual dependency

There are **18 mutual-dependency pairs** (`A DEPENDS_ON B` and `B DEPENDS_ON A`).
A self-negating one would require the pair to also be EXCLUSION (depend on each
other yet never co-occur — impossible). **0 of the 18** are exclusion pairs; every
mutual dependency is backed by real co-occurrence. (Their consistency is analysed
in `recursive-consistency-report.md`.)

---

## 4. Circular necessity

The `REQUIRES` graph is **acyclic** — 0 directed cycles. There is no chain
`A requires B requires … requires A`. (Even if there were, a necessity cycle
implies mutual co-presence — set equality — which is consistent, not
contradictory; but none occurs.)

---

## 5. The 314 raw `DEPENDS_ON` patterns (context)

Without the obligation distinction, a naive search finds 314 cases where a concept
`DEPENDS_ON` two targets that never co-occur. After gating EXCLUSION by marginal
significance (both ≥ 30) the count is 39 (treated in
`proposition-conflict-report.md`), and **all are falsified**: `DEPENDS_ON` is a
tendency (`P(A|B) ≥ 0.3`), not a requirement, so depending on two exclusive things
in different ayahs is not a contradiction. The dependency graph contains no
genuine prevention/requirement conflict.

---

## 6. Verdict

> **0 genuine dependency contradictions.** No necessity–exclusion collision, no
> self-negating mutual dependency, no circular necessity. The dependency layer is
> internally consistent.

---

## 7. Reproduce

```bash
python3 scripts/build_consistency.py
python3 scripts/validate_consistency.py --rebuild
```

Source: `generated/consistency/dependency_conflicts.json`.
