# Phase 15 — Final Report: Consistency Propagation Engine

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase15-consistency-propagation-1.0`.

Phase 15 investigates **how** the discovered consistency is maintained — with an
explicit mandate to **destroy** it. Consistency was not assumed, not protected, and
not assumed special or meaningful. No theology, tafsir, translation, external logic,
or imported explanation. All prior phases are read and hashed but never rebuilt.
Deterministic, byte-identically reproducible (`validate_consistency_propagation.py
--rebuild`, **81 checks pass**).

> **Immutability note:** the Phase-15 spec lists a generic `redundancy-report.md`,
> which already belongs to Phase 14. The Phase-15 redundancy report is named
> `consistency-redundancy-report.md` to keep Phase 14 immutable.

---

## 1. Method

Consistency is recomputed directly from the activation matrix M as a contradiction
count (exclusion∧positive, C2 necessity, C4 strict-order). The phase maps
consistency support, challenges the hub, searches for a core and pathways, ablates
motifs and SCCs, tests redundancy, and runs the decisive **counterfactual
destruction** (structural removal + null model + data corruption), the generative
test, and hypothesis falsification (H1–H7). Statistics include null-model CIs and a
corruption curve.

---

## 2. Primary research question

> *What structural mechanisms maintain consistency?*

**Answer: none.** No structure maintains consistency. It survives the removal of the
hub, the size-9 SCC, the top-10 concepts, every motif, every SCC, and the largest
region — always with **0 contradictions**. It also survives 30 null-model shuffles
(0 contradictions, generic). It is destroyed **only** by directly corrupting the
data. The one survivor is **H7 — consistency is irreducible**: a property of the
activation matrix's internal coherence, partly tautological and partly generic, not
carried by any removable structure.

---

## 3. Success-criteria answers

| Question | Answer |
|---|---|
| What structures support consistency? | **None** — every consistency-support weight is 0 |
| How dependent is consistency on CONCEPT_007? | **Not dependent** — survives hub removal; the hub only *mediates* 96% of necessity |
| Does a consistency core exist? | **No** — every subset (down to 10%) is consistent |
| Can consistency survive hub removal? | **Yes** (0 contradictions) |
| Can consistency survive SCC removal? | **Yes** (0 contradictions, no SCC self-negating) |
| Can consistency survive motif removal? | **Yes** (0 contradictions) |
| Can the Phase-12 grammar generate consistency? | **No** — grammar is topology-only; consistency is matrix-level |
| Is consistency local / distributed / redundant / emergent / irreducible? | **local & irreducible** — a per-pair property of the matrix; not redundant-by-mechanism, not specially emergent |
| Which hypotheses survive? | **only H7** |

---

## 4. Support rankings, core, hub, motif, SCC, redundancy

- **Support rankings:** max consistency-support weight = 0; the only structural
  signal is necessity-mediation (hub 96% of REQUIRES). No structure ranks as a
  maintainer.
- **Core:** none — consistency holds in every subset.
- **Hub:** mediator, not maintainer — survives full hub removal.
- **Motifs / SCCs:** no contribution — removal creates 0 contradictions; no SCC is
  self-negating.
- **Redundancy:** ubiquity of a local property, not a duplicated mechanism — both
  halves of every random split are independently consistent.

## 5. Counterfactual destruction & generative analysis

| Attack | Result |
|---|---|
| Remove strongest structures (hub, SCC-9, top-10, largest region) | 0 contradictions |
| Null model (30 marginal-preserving shuffles) | 0 contradictions, CI [0, 0] — **generic** |
| Direct corruption (inject positive into exclusion pairs) | breaks linearly: 5%→20, 50%→200, 100%→401 |
| Phase-12 grammar | cannot generate/test consistency (topology-only) |

The corruption curve is the only thing that breaks consistency, and it does so
proportionally — confirming consistency is a property of the data's internal
coherence, destroyable only by falsifying the data.

## 6. Hypothesis survival table

H1 hub — **falsified** (mediator) · H2 core — **falsified** · H3 SCCs —
**falsified** · H4 motifs — **falsified** · H5 redundancy — **falsified** (ubiquity)
· H6 emergent — **falsified** (nulls equally consistent) · **H7 irreducible —
SURVIVES**.

---

## 7. The deflationary conclusion (honest, unprotected)

Per the explicit prohibition against assuming consistency is meaningful or special,
the honest verdict is **deflationary**: the discovered "consistency" is **not a
maintained structural achievement**. It is an irreducible property of deriving every
relation from one coherent measurement matrix — **partly tautological** (a pair
cannot simultaneously have co = 0 and co ≥ 5) and **partly generic** (hub-dominated
sparse co-occurrence makes necessity conflict-free, and random nulls reproduce it).
No mechanism maintains it; no structure is required for it; a shuffled version of the
same data is equally consistent. We report this rather than narrate a mechanism that
does not exist.

---

## 8. Synthesis across phases

| Phase | Question | Verdict |
|---|---|---|
| 10 | Is the structure contradictory? | No — 0 contradictions |
| 11 | Is consistency robust? | Yes — SURVIVES STRONGLY |
| 12 | Can the grammar generate consistency? | No — out of scope |
| 14 | Is consistency localized? | No — present in every region |
| **15** | **How is consistency maintained?** | **It isn't — it is irreducible, not carried by any structure, generic, and destroyable only by corrupting the data** |

---

## 9. Outputs

`generated/consistency_propagation/`: `consistency_support.json`,
`hub_dependence.json`, `consistency_core.json`, `consistency_pathways.json`,
`motif_contribution.json`, `recursive_stability.json`, `redundancy_contribution.json`,
`counterfactual_destruction.json`, `generative_consistency.json`,
`hypothesis_falsification.json`, `consistency_propagation_manifest.json`. Tooling:
`scripts/build_consistency_propagation.py`,
`scripts/validate_consistency_propagation.py`. Reports:
`consistency-support-report.md`, `hub-dependence-report.md`,
`consistency-core-report.md`, `consistency-pathways-report.md`,
`motif-contribution-report.md`, `recursive-stability-report.md`,
`consistency-redundancy-report.md`, `counterfactual-destruction-report.md`,
`generative-consistency-report.md`, `hypothesis-falsification-report.md`, this report.

---

## 10. Limitations

- **Consistency is defined as the Phase-10 contradiction count** (exclusion∧positive,
  C2, C4). A different contradiction definition could behave differently; the
  partly-tautological component (exclusion∧positive) is definitional regardless.
- **Null model** is a single marginal-preserving shuffle family; other nulls
  (e.g. preserving the dyad census) might behave differently, though the genericity
  conclusion is robust to the tested family.
- The deflationary conclusion is about *this* discovered structure under *these*
  definitions; it makes no claim beyond the measured matrix.

## 11. Open questions (for any future phase — not started)

1. Whether a stricter contradiction definition (beyond pairwise) finds any
   non-generic consistency signal.
2. Whether a dyad-census-preserving null also yields 0 contradictions.
3. Whether the hub's necessity-mediation has any consequence the null does not
   reproduce.

---

## 12. Prohibitions observed

`no theology · no tafsir · no translation · no external logic · no imported
explanations · consistency not protected · consistency not assumed meaningful ·
consistency not assumed special · no explanation without evidence · did not start
from conclusions · prior phases never rebuilt.`

---

## 13. Reproduce

```bash
python3 scripts/build_consistency_propagation.py
python3 scripts/validate_consistency_propagation.py --rebuild
```

**Phase 15 complete. No Phase 16 started.**
