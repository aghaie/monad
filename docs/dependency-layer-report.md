# Dependency-Layer Report — Phase 5 (E)

**Date:** 2026-06-06. **Method version:** `phase5-compression-1.0`. **Status:**
complete.

Phase 5 (E) assigns each concept a **structural dependency position** only. No
meaning is attached to any level. "Level 0" is a graph property (depends on
nothing), not a semantic claim of primacy.

---

## 1. Method

The dependency graph is the directed union of `DEPENDS_ON` and `REQUIRES` edges:
`src → tgt` means *src structurally needs tgt*. Because the graph contains
cycles, strongly-connected components are first **condensed** (each SCC becomes a
single node); the condensation is a DAG. Each component's level is the **longest
downward dependency chain**:

- **Level 0** = components with no outgoing dependency edge (structural sinks —
  they depend on nothing). `level(n) = 1 + max(level(successor))`.
- Concepts with no dependency edge at all are **unlayered** (no dependency
  position).

---

## 2. Layer occupancy

| Level | Concepts | Count |
|---:|---|---:|
| 0 | `CONCEPT_007`, `CONCEPT_066`, `CONCEPT_095` | 3 |
| 1 | (56 concepts) | 56 |
| 2 | (21 concepts) | 21 |
| 3 | (6 concepts) | 6 |
| 4 | (3 concepts) | 3 |
| 5 | `CONCEPT_001` | 1 |
| 6 | `CONCEPT_003, 004, 034, 053, 060, 061, 084, 085, 088` (one SCC) | 9 |
| 7 | `CONCEPT_016` | 1 |
| — | unlayered: `CONCEPT_086, 100, 102` | 3 |

Condensation components: 80. Max level: 7. Source: `dependency_layers.json`.

---

## 3. Structural findings (no interpretation)

1. **Three structural sinks.** `CONCEPT_007, 066, 095` depend on nothing
   (Level 0). `CONCEPT_007` is also the dominant hub — most dependency chains
   terminate at it, consistent with Phase 4.
2. **A wide base, a thin spire.** 56 of 100 dependency-bearing concepts sit at
   Level 1 (depend directly on a sink). Occupancy thins monotonically upward
   (21 → 6 → 3 → 1) — the dependency hierarchy is **shallow and broad**, not a
   deep ladder.
3. **The top of the hierarchy is a recursive core, not a single concept.**
   Level 6 is occupied by an entire 9-concept strongly-connected component (the
   largest irreducible core; see `irreducibility-report.md`). Layering cannot
   separate its members — they are mutually dependent — so they share one level.
   `CONCEPT_016` (Level 7) sits structurally *above* even that core.
4. **The same band recurs.** The Level-6 SCC is exactly the secondary core that
   emerges when the dominant hub is removed (`hub-removal-report.md §3`). The
   layering and the hub-removal experiment independently identify the same
   sub-structure.
5. **Three concepts have no dependency position** (`CONCEPT_086, 100, 102`) —
   the three Phase-4 isolated concepts. They participate in no `DEPENDS_ON` /
   `REQUIRES` relation.

---

## 4. Recursive layering

Because 7 SCCs of size ≥ 2 exist (catalogued in `irreducibility-report.md`),
the dependency structure is **recursive, not a pure hierarchy**: each such SCC
is a layer that cannot be internally ordered. The layering above is therefore
defined on the SCC-condensed DAG; within a layer, members may mutually depend.

---

## 5. Limitations

- **Level is structural position only.** Level 0 ≠ "most fundamental in
  meaning"; it is "no outgoing dependency edge". No semantic ordering is implied.
- **Direction convention.** `src → tgt` (src needs tgt) is the Phase-4
  `DEPENDS_ON` / `REQUIRES` orientation. Reversing it would invert the level
  numbering; the partition is unchanged.
- **Cycle handling.** SCC condensation is required because the raw graph is
  cyclic; longest-path layering is well-defined only on the condensation.

---

## 6. Reproduce

```bash
python3 scripts/build_compression.py
python3 scripts/validate_compression.py --rebuild
```
