# Principle Coverage Report — Phase 8 (B, C, D)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase8-principles-1.0`.

Explanatory power (Phase B), removal impact (Phase C), and minimum principle sets
(Phase D) over the 16 discovered principles. All numbers are structural counts;
no meaning is assigned.

---

## 1. The two coverage senses

| Sense | Definition | Ceiling (all 16 principles) |
|---|---|---|
| **internal / generating** | relation's concepts all inside one principle | **9.9%** |
| **incidence / governing** | ≥ 1 of relation's concepts inside a principle | **100%** |

Of 6,832 relations: **679 intra-principle (9.9%)**, **6,153 inter-principle
(90.1%)**. The gap between the two ceilings *is* the answer: principles **govern**
all structure trivially (every concept is in some principle) but **generate**
almost none of it on their own.

---

## 2. Phase B — explanatory power per principle

| Principle | Size | Incident cov. | Internal cov. | Dep. incident | Dep. internal | Compr. contrib. |
|---|---:|---:|---:|---:|---:|---:|
| `PRINCIPLE_002` | 11 | 36.8% | 3.7% | 26.4% | 4.6% | 0.149 |
| `PRINCIPLE_011` | 5 | 28.9% | 0.6% | 15.8% | 1.4% | 0.099 |
| `PRINCIPLE_001` | 13 | 24.8% | 0.7% | 34.9% | 0.4% | 0.145 |
| `PRINCIPLE_003` | 9 | 21.8% | 0.6% | 9.5% | 0.4% | 0.085 |
| `PRINCIPLE_005` | 8 | 19.6% | 0.6% | 9.9% | 0.7% | 0.076 |
| `PRINCIPLE_007` | 8 | 18.1% | 1.0% | 12.3% | 1.1% | 0.080 |
| `PRINCIPLE_015` | 3 | 14.0% | 0.3% | — | — | 0.046 |
| `PRINCIPLE_010` | 5 | 11.3% | 0.2% | — | — | 0.044 |
| … | … | … | … | … | … | … |
| `PRINCIPLE_016` | 1 | 0.0% | 0.0% | 0.0% | 0.0% | 0.000 |

(Full table in `principle_coverage.json`.) Internal coverage never exceeds 3.7%;
incidence coverage is large for the modules holding the most-connected concepts.

**Is there one dominant principle?** No. `PRINCIPLE_002` governs the most (36.8%
incident) but no single principle governs ≥ 50%, and none generates more than
3.7%. Explanatory power is spread across the top ~4 principles, not concentrated
in one.

---

## 3. Phase C — principle removal (impact ranking)

Removing a principle deletes its member concepts; `relations_lost` = relations
incident to any member; `fragmentation_added` = increase in concept-graph
components.

| Rank | Principle | Relations lost | Fraction | Dependencies lost | Fragmentation |
|---:|---|---:|---:|---:|---:|
| 1 | `PRINCIPLE_002` | 2,511 | 36.8% | 75 | +1 |
| 2 | `PRINCIPLE_011` | 1,976 | 28.9% | 45 | −1 |
| 3 | `PRINCIPLE_001` | 1,697 | 24.8% | **99** | −6 |
| 4 | `PRINCIPLE_003` | 1,490 | 21.8% | 27 | 0 |
| 5 | `PRINCIPLE_005` | 1,340 | 19.6% | 28 | +1 |
| 6 | `PRINCIPLE_007` | 1,236 | 18.1% | 35 | +2 |

No single removal fragments the graph substantially (the hub-bearing
`PRINCIPLE_001` even *reduces* component count by absorbing isolates). Removal
impact tracks how many high-incidence concepts a principle holds, not self-
containment — consistent with the inter-principle dominance.

---

## 4. Phase D — minimum principle sets

Greedy maximum-coverage over principles, for 50/60/70/80/90/95% of the 6,832
relations.

### Incidence (governing) — reachable

| Target | Principles needed | Compression ratio | Set |
|---:|---:|---:|---|
| 50% | 2 | 0.125 | `002, 001` |
| 60% | 3 | 0.188 | + `011` |
| 70% | 3 | 0.188 | (same 3 reach 70%) |
| 80% | 4 | 0.250 | + `003` |
| 90% | 6 | 0.375 | + `005, 007` |
| 95% | 8 | 0.500 | + two more |

A small set of principles **governs** most structure: 4 principles touch 80%, 8
touch 95%, and all structure is touched once every concept's principle is
included.

### Internal (generating) — unreachable

| Target | Reachable? | Ceiling |
|---:|:--:|---:|
| 50% | ✗ | **9.9%** |
| 60%–95% | ✗ | 9.9% |

**No set of principles — of any size — generates more than 9.9% of the
structure.** Every target from 50% upward is unreachable in the self-contained
sense. This is the decisive Phase-D result.

---

## 5. Answering the secondary questions

| Question | Evidence-based answer |
|---|---|
| Principles to explain 50–95% (governing)? | 2 / 3 / 3 / 4 / 6 / 8 |
| Principles to explain 50–95% (generating)? | **none** — ceiling 9.9% |
| One dominant principle? | **No** — top governs 36.8%, generates 3.7% |
| Several independent principles? | **No** — 11 of 16 form one mutual-dependency cycle (`hierarchy` report) |
| Hierarchical principles? | Partially — a shallow 4-layer hierarchy wraps the cycle |
| Cyclic principles? | **Yes** — one size-11 irreducible principle cluster |
| Irreducible principles? | **Yes** — and a 90.1% irreducible inter-principle residue |

---

## 6. Interpretation of the gap (structural only)

The 90.1% inter-principle residue is the formal statement that the discovered
structure is **relational across modules**, not generated within them. A
foundational-principle reduction in the strict (generating) sense does **not**
exist for this corpus. The looser (governing) reduction exists but is trivial —
it only says the most-connected concepts sit in a few large modules. No meaning
is attached to either statement.

---

## 7. Reproduce

```bash
python3 scripts/build_principles.py
python3 scripts/validate_principles.py --rebuild
```
