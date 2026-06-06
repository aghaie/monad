# Principle Hierarchy Report — Phase 8 (E)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase8-principles-1.0`.

Phase E lifts the Phase-4 directed dependency relations (`DEPENDS_ON ∪ REQUIRES`)
to the principle level and analyses the resulting structure: principle
dependencies, layers, cycles, recursion, and reducibility. Purely graph-theoretic;
no meaning assigned.

---

## 1. Principle dependency graph

A directed edge `P_i → P_j` exists for every cross-principle dependency relation
whose source concept is in `P_i` and target in `P_j` (weighted by count).

- **66 directed principle-dependency edges** across the 16 principles.
- **14 of 16 principles carry self-dependencies** (intra-principle
  `DEPENDS_ON`/`REQUIRES`) — they are **recursive**: principles that depend on
  themselves through their own members. Only `PRINCIPLE_010` and `PRINCIPLE_016`
  have none.

Highest-degree principles in the dependency graph mirror the coverage ranking —
`PRINCIPLE_001` (the hub-bearing module) has the highest dependency in/out
activity (99 dependency relations incident).

---

## 2. Layers (SCC condensation + longest-path)

Condensing strongly-connected components and layering by longest path yields a
**shallow 4-level hierarchy**:

| Level | Principles | Components | Note |
|---:|---:|---:|---|
| 0 | 2 | 2 | source principles (incl. `PRINCIPLE_001`, hub-bearing) |
| 1 | **11** | **1** | the single irreducible cycle (size-11 SCC) |
| 2 | 2 | 2 | |
| 3 | 1 | 1 | sink |

The hierarchy is real but thin: two source principles feed a single massive
recursive core, which feeds a short tail. There is no deep multi-level ladder of
principles deriving from principles.

---

## 3. The size-11 cyclic principle cluster

Eleven of the sixteen principles form **one strongly-connected component** — they
are mutually reachable through dependency relations and therefore **cannot be
linearised into a hierarchy**:

```
PRINCIPLE_002, 005, 007, 008, 009, 010, 011, 012, 013, 014, 015
```

This is the principle-level analogue of Phase 5's 94-concept directional SCC:
**the principle layer is itself globally cyclic.** Most principles do not sit
above or below one another — they co-depend. (Full treatment in
`irreducible-principles-report.md`.)

---

## 4. Recursion

Principle recursion appears in two forms:

1. **Self-dependency** — 14 principles contain internal `DEPENDS_ON`/`REQUIRES`
   among their own members (a principle constrains itself).
2. **Mutual dependency** — the size-11 SCC, where principles cyclically depend on
   each other.

Both confirm that the dependency structure does not bottom out in independent
foundational principles; it loops.

---

## 5. Findings (no interpretation)

1. **Principles do not form a clean hierarchy.** A 4-level condensation exists,
   but 11 of 16 principles collapse into one cyclic core at level 1.
2. **Principles are recursive.** 14/16 depend on themselves; the core 11
   depend on each other.
3. **No principle is a pure foundation.** Only two principles are dependency
   sources (level 0), and they still receive `REQUIRES` incidence; none is an
   isolated generative root.
4. **The hierarchy is orthogonal to the modules.** Dependency edges
   overwhelmingly cross module boundaries (this is the same 90% inter-principle
   structure seen in coverage), which is why the lifted graph is so densely
   cyclic.

---

## 6. Outputs

`principle_hierarchy.json` (layers, cyclic clusters, recursion) and
`principle_dependencies.json` (the directed principle graph: 66 edges, per-node
in/out/self degrees).

---

## 7. Limitations

- Built from Phase-4 `DEPENDS_ON`/`REQUIRES` only; adding `PRECEDES`/`PREDICTS`
  would (as at the concept level) only enlarge the cyclic core.
- "Cyclic" / "irreducible" are graph properties (mutual reachability), not
  semantic claims.

---

## 8. Reproduce

```bash
python3 scripts/build_principles.py
python3 scripts/validate_principles.py --rebuild
```
