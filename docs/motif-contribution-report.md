# Motif Contribution Report — Phase 15 (E)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase15-consistency-propagation-1.0`.

Phase E measures each validated motif's contribution to consistency by removing the
motif's participating concepts and recomputing contradictions.

---

## 1. Motif ablation

For each of the 15 motif classes, the concepts participating in that motif were
removed from the activation matrix and the contradiction count recomputed:

| Quantity | Value |
|---|---:|
| Motif classes tested | 15 |
| Maximum contradictions created by any motif removal | **0** |

**No motif removal creates a single contradiction.** Whether the removed motif is
the dominant mutual-path (`MOTIF_001`), the reciprocal triangle (`MOTIF_009`), or
any other, the consistency count stays at 0.

---

## 2. Why motifs do not maintain consistency

Motifs are **graph-topology patterns** over the proposition graph (recurring
directed triad shapes). Consistency, however, is a property of the **activation
matrix** M — the exclusion/positive disjointness and the necessity structure. These
are orthogonal:

- Removing a motif removes edges/concepts from the topology, but the
  exclusion/positive layers of the surviving concepts remain disjoint.
- The necessity guarantee (hub-mediated) is unaffected by which triad shapes exist.

So motifs neither preserve nor avoid conflicts — there are no conflicts to avoid,
and the conflict-free property does not live in the motif structure.

---

## 3. Which motifs matter for consistency?

**None.** No motif contributes to consistency preservation, conflict avoidance, or
structural mediation, because there is nothing to preserve, avoid, or mediate at the
motif level. Consistency is a matrix-level property, not a motif-level one.

---

## 4. Verdict

> **No motif maintains consistency.** Removing any motif's concepts creates 0
> contradictions. Motifs are topology; consistency is a property of the activation
> matrix — they are orthogonal. Hypothesis H4 ("motifs maintain consistency") is
> **falsified**.

---

## 5. Reproduce

```bash
python3 scripts/build_consistency_propagation.py
python3 scripts/validate_consistency_propagation.py --rebuild
```

Source: `generated/consistency_propagation/motif_contribution.json`.
