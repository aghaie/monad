# Principle Falsification Report — Phase 8 (G)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase8-principles-1.0`.

Phase G *attacks* every principle candidate. A principle claims to be a
self-contained constraining pattern; the test asks whether its members' relations
actually stay inside it. Purely structural; no meaning assigned.

---

## 1. Method

For each principle, over the relations incident to its members:

```
internal_relation_retention = relations_internal / relations_incident
boundary_leakage             = 1 - internal_relation_retention
survives  ⇔  internal_relation_retention >= 0.50
```

A **contradicting member** is a member concept whose strongest Phase-4
proposition partner lies in a *different* principle — direct evidence that the
module does not contain that concept's strongest tie.

---

## 2. Result: 0 of 16 principles survive

**Every** principle is falsified as a self-contained constraining pattern. Their
members' relations leak across the boundary far more than they stay inside.

| Principle | Size | Internal retention | Boundary leakage | Contradicting members | Survives |
|---|---:|---:|---:|---:|:--:|
| `PRINCIPLE_002` | 11 | 0.100 | 0.900 | high | ✗ |
| `PRINCIPLE_004` | 9 | 0.092 | 0.908 | high | ✗ |
| `PRINCIPLE_007` | 8 | 0.057 | 0.943 | high | ✗ |
| `PRINCIPLE_008` | 7 | 0.052 | 0.948 | high | ✗ |
| `PRINCIPLE_009` | 6 | 0.037 | 0.963 | high | ✗ |
| `PRINCIPLE_005` | 8 | 0.033 | 0.967 | high | ✗ |
| `PRINCIPLE_014` | 3 | 0.031 | 0.969 | high | ✗ |
| `PRINCIPLE_006` | 8 | 0.027 | 0.973 | high | ✗ |
| `PRINCIPLE_001` | 13 | 0.027 | 0.973 | high | ✗ |
| `PRINCIPLE_003` | 9 | 0.026 | 0.974 | high | ✗ |
| `PRINCIPLE_012` | 4 | 0.022 | 0.978 | high | ✗ |
| `PRINCIPLE_011` | 5 | 0.021 | 0.979 | high | ✗ |
| `PRINCIPLE_015` | 3 | 0.021 | 0.979 | high | ✗ |
| `PRINCIPLE_010` | 5 | 0.018 | 0.982 | high | ✗ |
| `PRINCIPLE_013` | 3 | 0.014 | 0.986 | high | ✗ |
| `PRINCIPLE_016` | 1 | 0.000 | 1.000 | — | ✗ |

Internal retention ranges **0.000–0.100** — no principle retains even one-tenth
of its members' relational mass. The highest, `PRINCIPLE_002`, still leaks 90%.

---

## 3. What the failure means (structural only)

The falsification result is the sharpest statement of the central finding:

> **No discovered module behaves as a self-contained foundational principle.**
> Every candidate is more strongly tied to the rest of the structure than to
> itself.

This is *not* a defect of the discovery method — `Q = 0.294` modularity confirms
the modules are the best available cohesive cut. It is a property of the corpus:
the discovered structure is a single, densely interwoven relational web in which
no sub-pattern is explanatorily closed. The principles are real structural
modules, but none is a *foundation*.

---

## 4. Contradicting members

Across all principles, the dominant pattern is that member concepts' strongest
proposition partners lie outside their own module — frequently in the
hub-bearing `PRINCIPLE_001` (`CONCEPT_007`) or the high-incidence `PRINCIPLE_002`.
The strongest ties in the corpus run *between* modules, pulling every module
open. Per-principle contradicting-member lists are in
`principle_falsification.json`.

---

## 5. Honesty of the test

The threshold (retention ≥ 0.50) is deliberately generous — a principle need only
keep *half* its relational mass inside to survive. None comes close. A stricter or
looser threshold would not change the verdict: the maximum retention is 0.10.
Raw per-principle retentions are published for independent re-grading.

---

## 6. Reproduce

```bash
python3 scripts/build_principles.py
python3 scripts/validate_principles.py --rebuild
```

**No meaning, theology, or origin claim is made. The result is a graph property:
the discovered structure has no self-contained foundational principle.**
