# Consistency Pathways Report — Phase 15 (D)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase15-consistency-propagation-1.0`.

Phase D searches for structural paths that connect potentially-conflicting
structures — the routes by which consistency would have to "propagate" to keep
conflicts apart.

---

## 1. Result

| Quantity | Value |
|---|---:|
| Conflicting structure pairs | **0** |
| Consistency-mediation routes required | **0** |
| Bridge concepts mediating conflicts | **0** |

**There are no conflicting structures to mediate.** With 0 contradictions and 0
candidate conflicts, there is nothing for a "consistency pathway" to keep apart.

---

## 2. Consistency is not a propagation phenomenon

The framing of Phase D — that consistency might *propagate* through paths that
connect conflicting structures — does not apply. Consistency here is **not
propagated**; it is a **local property of every concept pair**:

- A pair is either *positive* (co ≥ 5) or *exclusion* (co = 0), never both. This is
  decided pairwise, with no path or mediation.
- There is no "conflict" anywhere in the network that a pathway must route around.

So there are no shortest paths, redundant paths, or mediation routes for
consistency — because consistency is not a transmitted quantity. It is intrinsic to
every local measurement.

---

## 3. The one routing structure: necessity through the hub

The only path-like structure relevant to consistency is **necessity routing**: all
REQUIRES (necessity) edges route through high-marginal concepts, 96% through the
hub. The hub, co-occurring with everything, cannot anchor a conflict — so necessity
is "routed" through a node that is conflict-free by construction. This is a
structural explanation for the absence of necessity conflicts, not a propagation of
consistency.

---

## 4. Verdict

> **There are no consistency pathways** — because there are no conflicting
> structures to connect. Consistency is not a propagation phenomenon; it is a local
> per-pair property. The only routing structure is that necessity passes through the
> ubiquitous hub, which cannot anchor a conflict.

---

## 5. Reproduce

```bash
python3 scripts/build_consistency_propagation.py
python3 scripts/validate_consistency_propagation.py --rebuild
```

Source: `generated/consistency_propagation/consistency_pathways.json`.
