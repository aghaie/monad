# Proposition Topology Report — Phase 4

**Date:** 2026-06-06. **Source:** `generated/propositions/proposition_graph.json`,
`bridge_patterns.json`, `proposition_candidates.json`.

This report describes the structure of the proposition graph — the directed
multigraph whose nodes are the 103 Phase-3 concept candidates and whose edges
are the candidate relations discovered in Phase 4. No interpretation; topology
only.

---

## 1. Construction

- **Nodes** — 103 (all Phase-3 concept ids; isolated nodes retained).
- **Edges** — every directional candidate (`DEPENDS_ON`, `REQUIRES`,
  `PRECEDES`, `PREDICTS_W{1,2,3}`) plus `ASSOCIATES_WITH` materialised in
  both directions. Each edge stores `type`, `weight = confidence`,
  `support`, `stability`.
- **Undirected projection** — for topology metrics, the directed multigraph
  is collapsed to a simple undirected graph (edge iff any directional edge
  exists between the pair). Unweighted Brandes betweenness is computed on
  this projection.

Choice of unweighted betweenness is documented in
`proposition-discovery-report.md §6` — weighted betweenness collapsed onto a
single node because several `REQUIRES / PRECEDES` confidences saturate at
`1.0`.

---

## 2. Aggregate topology

| Quantity | Value |
|---|---:|
| Nodes | 103 |
| Directed edges | 1,474 |
| Unique unordered pairs with ≥ 1 edge | 735 |
| Pairwise density | 735 / 5,253 ≈ 14.0 % |
| Mean (in + out) degree | 28.6 |
| Max (in + out) degree | 185 (`CONCEPT_007`) |
| Median degree | 21 |
| Mean relation diversity per node | 5.48 / 9 |
| Mean betweenness | 40.92 |
| Isolated nodes (no edges) | **3** (`CONCEPT_086`, `CONCEPT_100`, `CONCEPT_102`) |
| Bridges (top decile by betweenness) | 10 |

The graph is sparse-to-moderately dense (≈ 14 % pair coverage), and the
degree distribution is heavy-tailed.

---

## 3. Hubs — top 15 by betweenness centrality

| concept | betweenness | out | in | relation diversity |
|---|---:|---:|---:|---:|
| `CONCEPT_007` | 2006.57 | 89 |  96 | 2 |
| `CONCEPT_016` |  289.43 | 29 |  56 | 7 |
| `CONCEPT_061` |  254.98 | 27 |  43 | 7 |
| `CONCEPT_004` |  223.88 | 51 |  93 | 7 |
| `CONCEPT_085` |  205.17 | 39 |  64 | 7 |
| `CONCEPT_034` |  200.11 | 17 |  84 | 7 |
| `CONCEPT_081` |  123.25 | 21 |  67 | 7 |
| `CONCEPT_084` |  122.11 | 17 |  47 | 7 |
| `CONCEPT_053` |  104.37 | 17 |  39 | 7 |
| `CONCEPT_088` |   96.88 | 28 |  51 | 7 |
| `CONCEPT_003` |   87.10 | 16 |  52 | 7 |
| `CONCEPT_008` |   72.77 | 21 |  15 | 7 |
| `CONCEPT_002` |   69.35 | 46 |  56 | 7 |
| `CONCEPT_060` |   51.67 | 18 |  23 | 7 |
| `CONCEPT_001` |   24.68 | 32 |  33 | 7 |

**`CONCEPT_007` is an extreme outlier** — its betweenness is ~7× the second
node. Its relation diversity is only 2 (presumably it participates strongly
in only a couple of relation types as source), yet its connectivity touches
99 / 102 other concepts.

---

## 4. Bridges (`top_decile_betweenness`)

`bridge_patterns.json` records the top 10 bridges (10 % of 103, rounded):

```
CONCEPT_007, CONCEPT_016, CONCEPT_061, CONCEPT_004, CONCEPT_085,
CONCEPT_034, CONCEPT_081, CONCEPT_084, CONCEPT_053, CONCEPT_088
```

Removing any of these would disproportionately fragment shortest paths in
the unweighted projection.

---

## 5. Mediators (MEDIATES)

| Quantity | Value |
|---|---:|
| MEDIATES triples | 2,347 |
| Unique mediators | small (concentrated on a handful) |
| Mean isolation share | 0.84 |

The triadic mediation analysis is highly concentrated: a few high-marginal
concepts appear as the mediator for the majority of `(A, D)` base pairs that
admit any mediator at all. This concentration is a consequence of marginal
activation: a concept active in a majority of ayahs will almost
automatically appear in any joint co-activation set with high probability.
The result is structurally faithful but interpretively weak — see
`proposition-discovery-report.md §6`.

---

## 6. Cycles (potential recursion)

| Length | Count |
|---|---:|
| 2 (mutual `A ↔ B`) | included |
| 3 | included |
| 4 | included |
| **Total cycles ≤ 4 (over `DEPENDS_ON ∪ REQUIRES ∪ PRECEDES`)** | **2,570** |

Recurring cycles are abundant. Most include `CONCEPT_007` because almost
every directional edge originates or terminates at it. Cycles excluding
`CONCEPT_007` are markedly fewer and are interesting candidates for
follow-up sweeps.

---

## 7. Hierarchy (potential)

Only **4** depth-3 `REQUIRES → REQUIRES` chains exist. All terminate at
`CONCEPT_007`. See `dependency-analysis-report.md §7`.

---

## 8. Causal pairs (potential)

28 ordered pairs satisfy `PRECEDES` *and* `DEPENDS_ON` simultaneously. The
label remains structural — an ordering plus a dependency, not a causal
claim. Sample:

```
CONCEPT_001 -> CONCEPT_055, CONCEPT_001 -> CONCEPT_090,
CONCEPT_001 -> CONCEPT_091, CONCEPT_002 -> CONCEPT_019,
CONCEPT_002 -> CONCEPT_035, ...
```

Full list in `proposition_candidates.json :: classifications.potential_causal_pairs`.

---

## 9. Distribution: global vs localized

- **Global relations** (evidence covers ≥ 57 of 114 surahs): 59.
- **Localized relations** (evidence confined to ≤ 3 surahs): 65.

The global tier is dominated by `REQUIRES` edges into `CONCEPT_007`. The
localized tier is dominated by `DEPENDS_ON` edges between low-support,
high-lift concept pairs that happen to share a single chapter.

---

## 10. Isolated nodes

`CONCEPT_086`, `CONCEPT_100`, `CONCEPT_102` participate in zero candidate
relations. These are Phase-3 concept candidates whose root/lemma membership
never produces a joint co-activation with another concept above
`SUPPORT_MIN = 5`. Their members may still be active in ayahs, but never
alongside members of any other concept frequently enough to clear threshold.

---

## 11. Limitations

- Unweighted betweenness ignores edge confidence. A weighted projection
  reorders mid-rank nodes but degenerates at the top — both views are
  recorded indirectly (per-node `top_in/out_partners` carry the weights).
- Mediation results are dominated by marginal-frequency effects.
- "Potential recursive" cycles are a graph-theoretic count; they do not
  imply semantic recursion.
- Degree counts double-count multi-typed pairs (e.g., a pair connected via
  both `PRECEDES` and `PREDICTS_W1` contributes 2 to each endpoint's
  degree).

---

## 12. Open questions

- What does the topology look like if `CONCEPT_007` is masked out?
- Does the bridge set change under support-threshold perturbation (`± 2`,
  `± 5`)?
- Are the 4-cycles dominated by `(A, B, A, B)` mutual-edge artefacts?
