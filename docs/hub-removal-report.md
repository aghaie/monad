# Hub-Removal Report — Phase 5 (C)

**Date:** 2026-06-06. **Method version:** `phase5-compression-1.0`. **Status:**
complete.

Special experiment: remove the dominant hub `CONCEPT_007` completely, then
recompute the induced structure. This addresses the Phase-4 open question —
*is there a sub-graph (mod the dominant requirement target) with cleaner
structure?* — and the Phase-5 success criterion *what survives after removal of
the dominant hub?*

**Scope note.** This recomputes graph-theoretic structure over the **induced
subgraph** of the existing Phase-4 relations after deleting the hub and every
relation that touches it. It does **not** regenerate statistical relations from
the corpus (prior phases are never rebuilt). Concept ids stay opaque; nothing is
named or interpreted.

---

## 1. What the hub carried

`CONCEPT_007` is the Phase-4 dominant requirement target (96 of 100 `REQUIRES`
edges point at it) and the top concept on every Phase-5 foundationality metric
(composite 1.000; 22.2% of all relations incident; sole fragmenting node).

---

## 2. Structure surviving its removal

| Quantity | With hub | Without hub | Survives |
|---|---:|---:|:--|
| Propositions | 6,832 | 5,310 | **77.8%** |
| Dependency relations | 284 | 188 | **66.2%** |
| Directed edges | 1,474 | — | reduced |
| Largest undirected component | 100 / 103 | 94 / 102 | **92.2%** |
| Undirected components | 4 | 9 | +5 |
| Depth-3 `REQUIRES` chains | 4 | **0** | none |
| Directed cycles (≤ len 4) | 2,570 | **219** | 8.5% |
| Irreducible dependency cores (SCC ≥ 2) | 7 | **7** | all |

Source: `hub_removal_analysis.json`.

---

## 3. Verdict — the structure **reorganizes**

Classification: **reorganize** (largest component fraction 0.922 ≥ 0.80;
proposition retention 0.778). The graph neither collapses nor merely loses a
node — a new core takes over:

- **New top by betweenness:** `CONCEPT_016` (655.7), followed by `CONCEPT_061`
  (510.3), `CONCEPT_085` (437.6), `CONCEPT_004` (377.9), `CONCEPT_034` (352.0).
- **New top by degree:** `CONCEPT_004` (total degree 142).
- **New bridge set:** `CONCEPT_016, 061, 085, 004, 034, 081, 084, 053, 088,
  003` — almost exactly the members of the largest irreducible dependency core
  (§ irreducibility report), promoted from "behind the hub" to structurally
  central.

So the dominant hub **masks** a secondary core; with the hub gone, that core
(`CONCEPT_016` + the size-9 dependency SCC) becomes the structural centre.

---

## 4. What depended on the hub specifically

- **All hierarchical chains were hub-terminated.** Every one of the 4 Phase-4
  depth-3 `REQUIRES` chains passed through `CONCEPT_007`; with it removed, the
  count drops to **0**. The clean hierarchy was an artefact of the dominant
  requirement target.
- **Most recursion routed through the hub.** Directed cycles (≤ len 4) fall
  from 2,570 to **219** (−91.5%). The graph stays recursive, but the vast bulk
  of short cycles passed through one node.
- **The irreducible cores did not.** All 7 strongly-connected dependency cores
  survive intact (largest still size 9). They are **independent of the dominant
  hub** — genuinely recursive sub-structure, not hub-induced.

---

## 5. Answers to the experiment's questions

| Question | Answer |
|---|---|
| Does another core emerge? | **Yes** — `CONCEPT_016` + the size-9 dependency SCC. |
| Does the structure collapse? | **No** — 77.8% of relations and a 94-node component survive. |
| Does the structure reorganize? | **Yes** — bridges and centrality re-rank onto the former secondary core. |

---

## 6. Limitations

- Induced-subgraph recomputation only; statistical relations are **not**
  re-derived from the corpus. A genuine `CONCEPT_007`-masked re-run of the
  Phase-4 activation matrix (recommended in `phase4-final-report.md §7.2`) could
  shift counts further and is left as an open question.
- Betweenness uses the unweighted undirected projection, matching Phase 4.
- No meaning is assigned to `CONCEPT_007`, `CONCEPT_016`, or any successor.

---

## 7. Reproduce

```bash
python3 scripts/build_compression.py
python3 scripts/validate_compression.py --rebuild
```
