# Motif Conflict Report — Phase 10 (E)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase10-consistency-1.0`.

Phase E searches recurring motifs (Phase 9) for patterns that generate
incompatible structural expectations — local vs global inconsistency, motif
collisions. The sharpest test is **strict-order intransitivity**: a directed cycle
of *strict* precedence. High burden of proof; structural evidence only.

---

## 1. What a motif contradiction would be

A genuine motif/order contradiction (rule C4) is a **directed cycle in which every
edge is a strict order** (`PRECEDES` with asymmetry ≥ 0.95): A strictly before B,
B strictly before C, C strictly before A — an impossible intransitive strict
order. A directed 3-cycle of *weak* tendencies is **not** a contradiction (the
prohibitions forbid classifying cycles as contradictions).

---

## 2. Result

| Search | Result |
|---|---:|
| Directed-3-cycle motif instances (Phase 9 `MOTIF_015`) | 3 — **falsified** |
| **Strict-order `PRECEDES` cycles** | **0** |
| Weak (non-strict) `PRECEDES` cycles | 9 — **correctly excluded** |

---

## 3. The 9 PRECEDES cycles — all weak

The `PRECEDES` graph contains 9 elementary directed cycles (length ≤ 4). Every one
has a minimum edge asymmetry **far below the strict threshold (0.95)**:

| Cycle (C = CONCEPT_) | Min asymmetry | Min support |
|---|---:|---:|
| C001 → C090 → C061 → C030 → … | 0.33 | 18 |
| C001 → C091 → C016 → C038 → … | 0.30 | 10 |
| C001 → C091 → C088 → C030 → … | 0.33 | 15 |
| C005 → C088 → C097 → C049 → … | 0.30 | 15 |
| C006 → C084 → C097 → C049 → … | 0.30 | 16 |
| C006 → C085 → C049 → … | 0.42 | 16 |
| C006 → C085 → C097 → C049 → … | 0.50 | 16 |
| C061 → C088 → C090 → … | 0.33 | 18 |
| C061 → C091 → C088 → C090 → … | 0.33 | 15 |

A minimum asymmetry of 0.30–0.50 means that along every cycle there is at least one
edge where the "reverse" order occurs nearly as often as the forward order. These
are **non-transitive statistical tendencies** (a rock-paper-scissors pattern of
mild positional preference), **not** strict orderings. They are explicitly **not**
contradictions. Only **6 of 303** `PRECEDES` edges reach asymmetry ≥ 0.99, and
none of them lies on a cycle — so no cycle of strict edges exists.

---

## 4. The directed-3-cycle motif

Phase 9 found the directed-3-cycle motif (`MOTIF_015`) is nearly absent — just 3
instances in the whole proposition graph. Each is falsified the same way: it mixes
relation types and weak edges, and is not a strict-order cycle. The near-absence of
small directed cycles is itself evidence of local ordering consistency.

---

## 5. Local vs global consistency

- **Local:** every triad realises exactly one motif class — no triad is
  simultaneously two incompatible patterns. No motif collisions exist.
- **Global:** the only candidate global inconsistency (cyclic strict precedence)
  does not occur. The 9 weak cycles reflect tendency, not order.

---

## 6. Verdict

> **0 genuine motif/order contradictions.** 9 weak `PRECEDES` cycles and 3
> directed-3-cycle motif instances were surfaced and correctly excluded — they are
> non-strict statistical tendencies, not strict-order violations.

---

## 7. Reproduce

```bash
python3 scripts/build_consistency.py
python3 scripts/validate_consistency.py --rebuild
```

Source: `generated/consistency/motif_conflicts.json`.
