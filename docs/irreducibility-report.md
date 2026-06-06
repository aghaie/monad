# Irreducibility Report — Phase 5 (F)

**Date:** 2026-06-06. **Method version:** `phase5-compression-1.0`. **Status:**
complete.

Phase 5 (F) searches for structures that **cannot be compressed further**: sets
of concepts that are mutually reachable through the dependency / ordering
relations and therefore cannot be linearised into a hierarchy or reduced without
breaking a cycle. These are the strongly-connected components (SCC, size ≥ 2) of
the directed relation graphs. Purely graph-theoretic; nothing is named or
interpreted.

---

## 1. Irreducible dependency cores (`DEPENDS_ON ∪ REQUIRES`)

**7** strongly-connected components of size ≥ 2 — the irreducible cores of the
dependency graph:

| Size | Edge density | Concepts |
|---:|---:|---|
| 9 | 0.278 | `003, 004, 034, 053, 060, 061, 084, 085, 088` |
| 4 | 0.583 | `039, 048, 076, 089` |
| 3 | 0.833 | `027, 036, 072` |
| 3 | 0.667 | `002, 090, 091` |
| 3 | 0.667 | `009, 035, 067` |
| 3 | 0.667 | `029, 068, 081` |
| 2 | 1.000 | `073, 074` |

(`CONCEPT_` prefixes omitted in the concept column.) Source:
`irreducible_structures.json`.

---

## 2. Structural findings (no interpretation)

1. **One large irreducible core.** The size-9 SCC
   (`003, 004, 034, 053, 060, 061, 084, 085, 088`) is the structural heart of
   the dependency graph: a 9-concept mutually-dependent cluster that cannot be
   ordered or compressed. Seven of its nine members are also top-12
   foundational concepts, and the set is exactly the secondary core that emerges
   when the dominant hub is removed (`hub-removal-report.md §3`). Three
   independent methods converge on it.
2. **The high-NPMI cluster is irreducible.** The 4-SCC `039, 048, 076, 089`
   (density 0.583) is the Phase-4 high-NPMI / high-lift `PREDICTS` cluster. Its
   tightness is now confirmed as a genuine mutual-dependency cycle, not just
   co-occurrence.
3. **The strongest pair is a perfect 2-cycle.** `073 ↔ 074` (density 1.0) is the
   Phase-4 NPMI-0.864 pair — the smallest irreducible structure, mutually
   dependent in both directions.
4. **Small recursive triangles.** Four size-3 SCCs (densities 0.667–0.833)
   complete the catalogue. The dependency graph is thus a shallow hierarchy
   studded with seven small recursive knots.

---

## 3. Directional irreducibility (`+ PRECEDES + PREDICTS`)

When ordering relations are added, the directional graph collapses into **one
giant SCC of 94 concepts** — almost everything is mutually reachable through
ordering. The ordering layer is therefore **globally irreducible**: there is no
hierarchy of "what precedes what" across the corpus; precedence is pervasively
cyclic.

| Graph | SCCs ≥ 2 | Largest |
|---|---:|---:|
| `DEPENDS_ON ∪ REQUIRES` | 7 | 9 |
| `+ PRECEDES + PREDICTS` | 1 | 94 |

---

## 4. Irreducibility without the dominant hub

Removing `CONCEPT_007` and recomputing:

| Graph | SCCs ≥ 2 (no hub) | Largest |
|---|---:|---:|
| `DEPENDS_ON ∪ REQUIRES` | **7** | **9** |
| `+ PRECEDES + PREDICTS` | 1 | 85 |

The **7 dependency cores are fully independent of the dominant hub** — all
survive its removal intact (largest still 9). The giant directional SCC shrinks
only modestly (94 → 85). The irreducible structure is therefore an intrinsic
property of the periphery, not an artefact of the hub.

---

## 5. Interpretation of "irreducible" for compression

These SCCs are the formal reason the system resists compression below a floor:
within an SCC, **no member can be dropped without losing a dependency relation
that no other concept can supply**. The 9-concept core alone forces any
hierarchy-preserving reconstruction to retain all nine. Combined with the
strict full-membership reconstruction rule, this lower-bounds the minimum core
and explains the convex compression curve in `compression-analysis-report.md`.

---

## 6. Limitations

- SCCs are computed over the Phase-4 directed relations with their fixed
  thresholds; a different relation population would redraw them.
- "Irreducible" is a graph property (mutual reachability), not a semantic claim.
- No meaning is assigned to any component or its members.

---

## 7. Reproduce

```bash
python3 scripts/build_compression.py
python3 scripts/validate_compression.py --rebuild
```
