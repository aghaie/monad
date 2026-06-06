# Motif Falsification Report — Phase 9 (H)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase9-motifs-1.0`.

Phase H attacks every motif candidate. A motif claims to be a *genuine recurring
structural pattern*; the test asks whether it actually recurs, broadly, stably,
independently of the hub and of specific concepts. Structural only; no meaning.

---

## 1. Falsification criteria

A motif is falsified if it fails **any** of:

| Criterion | Threshold |
|---|---|
| recurrence | frequency ≥ 30 instances |
| broad concept support | ≥ 10 distinct participating concepts |
| stability | perturbation retention ≥ 0.50 |
| hub-removal survival | retains ≥ 10% of instances without `CONCEPT_007` |
| concept replaceability | recurs across many concepts, no single one ≥ 50% |

---

## 2. Result: 10 of 15 motifs survive

| Motif | Descriptor | Failures |
|---|---|---|
| `MOTIF_001` | mutual-path | `concept_bound` (74% via hub) |
| `MOTIF_002` | in-merge | — survives |
| `MOTIF_003` | in-merge | — survives |
| `MOTIF_004` | chain | — survives |
| `MOTIF_005` | out-fork | — survives |
| `MOTIF_006` | out-fork | — survives |
| `MOTIF_007` | cyclic-mixed triangle | `concept_bound` |
| `MOTIF_008` | dyad: asymmetric | — survives |
| `MOTIF_009` | fully-mutual triangle | `concept_bound` |
| `MOTIF_010` | dyad: mutual | — survives |
| `MOTIF_011` | transitive triangle | — survives |
| `MOTIF_012` | transitive triangle | — survives |
| `MOTIF_013` | cyclic-mixed triangle | — survives |
| `MOTIF_014` | transitive triangle | `concept_bound` |
| `MOTIF_015` | 3-cycle | `non_recurrence`, `narrow_concept_support`, `concept_bound` |

**10 survive, 5 fail.** Unlike Phase 8 (where 0 of 16 principles survived), the
majority of motifs withstand falsification: they recur thousands of times, across
90+ concepts, stably, and survive hub removal.

---

## 3. The five failures (what they reveal)

1. **`MOTIF_001` (mutual-path)** — the *most frequent* motif, yet **concept-bound**:
   74% of its instances pass through the hub. The dominance of reciprocal paths is
   largely a hub effect.
2. **`MOTIF_007` / `MOTIF_009` (cyclic-mixed / fully-mutual triangles)** —
   also hub-concentrated; the fully-mutual triangle is the most over-represented
   motif (z = +29) but is driven by the hub's reciprocal `ASSOCIATES_WITH` edges.
3. **`MOTIF_014` (transitive triangle)** — concept-bound at low frequency.
4. **`MOTIF_015` (directed 3-cycle)** — occurs only **3 times**: a genuine
   non-recurrence. Directed 3-cycles are essentially absent from the network — a
   notable structural fact (the network avoids small directed cycles locally even
   though it is globally cyclic).

The failures are informative, not noise: they isolate exactly the patterns that
depend on the hub or barely occur, leaving a robust core of **10 genuinely
recurring, concept-independent, hub-independent motifs** — the open path patterns
(in-merge, out-fork, chain), the transitive and mixed triangles, and both dyads.

---

## 4. Honesty of the test

The most common motif **failing** falsification is the key honesty check: high
frequency alone does not certify a structural pattern. `MOTIF_001` is frequent but
hub-bound; `MOTIF_002` (in-merge) is frequent *and* distributed, and survives. The
test separates genuine recurrence from hub amplification.

---

## 5. Reproduce

```bash
python3 scripts/build_motifs.py
python3 scripts/validate_motifs.py --rebuild
```

**No meaning, intention, authorship, or origin is claimed. Motifs are opaque
structural patterns.**
