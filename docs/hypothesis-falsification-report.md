# Hypothesis Falsification Report — Phase 15 (J)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase15-consistency-propagation-1.0`.

Phase J attacks every explanatory hypothesis for consistency. Only hypotheses that
survive falsification are explanatory. Consistency was not protected.

---

## 1. Hypothesis survival table

| # | Hypothesis | Result | Evidence |
|---|---|---|---|
| **H1** | The hub maintains consistency | **FALSIFIED** (mediator, not maintainer) | survives full hub removal (0 contradictions); hub mediates 96% of REQUIRES but is not required |
| **H2** | A small core maintains consistency | **FALSIFIED** | no core exists; every subset down to 10% of ayahs is fully consistent |
| **H3** | SCCs maintain consistency | **FALSIFIED** | removing any SCC creates 0 contradictions; no SCC is self-negating |
| **H4** | Motifs maintain consistency | **FALSIFIED** | removing any motif's concepts creates 0 contradictions |
| **H5** | Redundancy maintains consistency | **FALSIFIED** (ubiquity, not redundancy) | holds independently in both halves of every random split — a local property, not a duplicated mechanism |
| **H6** | Consistency is emergent / special | **FALSIFIED** | shuffled null matrices are equally consistent (0 contradictions in 30 nulls) — consistency is generic |
| **H7** | Consistency is irreducible (a property of the matrix's internal coherence) | **SURVIVES** | survives every structural removal and every null shuffle; destroyed only by direct data corruption |

**Surviving hypotheses: H7 only.**

---

## 2. What survived and why

Only **H7** survives every attack. Consistency is:

- **Not maintained by the hub** (H1) — it survives hub removal; the hub only
  *mediates* necessity.
- **Not maintained by a core** (H2) — every subset is consistent; no core exists.
- **Not maintained by SCCs** (H3) or **motifs** (H4) — their removal changes
  nothing.
- **Not maintained by redundancy** (H5) — it is a local per-pair property, not a
  duplicated mechanism.
- **Not specially emergent** (H6) — random null matrices are equally consistent, so
  it is generic to hub-dominated sparse co-occurrence data and the contradiction
  definitions.
- **Irreducible** (H7) — it is a property of the activation matrix's internal
  coherence. It is partly **tautological** (a pair cannot have co = 0 and co ≥ 5
  simultaneously) and partly **structural-but-generic** (the hub's ubiquity makes
  necessity conflict-free, but nulls reproduce this). It can be destroyed *only* by
  directly corrupting the data.

---

## 3. The deflationary conclusion (no protection)

Per the prohibitions — *do not assume consistency is meaningful or special* — the
honest conclusion is **deflationary**: the discovered "consistency" is not a
maintained structural achievement. It is an irreducible property of how the data is
derived (one coherent measurement matrix), partly tautological and partly generic.
No structure maintains it, and a random rearrangement of the same data is equally
consistent. We report this plainly rather than narrate a mechanism that does not
exist.

---

## 4. Verdict

> **Only H7 survives.** Consistency is **irreducible** — not maintained by the hub,
> a core, SCCs, motifs, or redundancy, and not specially emergent. It is a property
> of the activation matrix's internal coherence, destroyable only by corrupting the
> data itself.

---

## 5. Reproduce

```bash
python3 scripts/build_consistency_propagation.py
python3 scripts/validate_consistency_propagation.py --rebuild
```

Source: `generated/consistency_propagation/hypothesis_falsification.json`.
