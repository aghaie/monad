# Phase 4 — Final Report: Proposition Discovery Engine

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase4-propositions-1.0`.

Phase 4 built the **Proposition Discovery Engine**: it discovers recurring
*relational* structures between Phase-3 concept candidates that emerge from
Quran-internal usage. A proposition here is **not** a word, root, lemma, or
concept — it is an emergent statistical relation among concepts. Propositions
are **discovered, not invented**, carry **opaque relation types** over opaque
concept ids, and are never named, translated, interpreted, or explained.

The Quran remains the only semantic universe. No external dictionary, tafsir,
translation, theology, or pre-trained embedding was used. The Phase 1/2/3
outputs are read and hashed but never rebuilt.

---

## 1. Statistics

| Quantity | Value |
|---|---:|
| Active ayahs (≥ 1 concept) | 6,101 / 6,236 (97.84%) |
| Concepts | 103 |
| Total candidate relations | **6,832** |
| CO_OCCURS | 1,215 |
| ASSOCIATES_WITH | 170 |
| DEPENDS_ON | 184 |
| REQUIRES | 100 |
| PRECEDES / FOLLOWS | 303 / 303 |
| PREDICTS (windows 1/2/3) | 182 / 193 / 172 |
| MEDIATES (triples) | 2,347 |
| CONDITIONAL_EMERGES (synergy triples) | 1,663 |
| Proposition graph: nodes / directed edges | 103 / 1,474 |
| Pairwise density (undirected projection) | 14.0 % |
| Isolated concepts | 3 |
| Bridges (top decile betweenness) | 10 |
| Hierarchical chains (depth-3 `REQUIRES → REQUIRES`) | 4 |
| Potential causal pairs (`PRECEDES ∧ DEPENDS_ON`) | 28 |
| Potential recursive cycles (≤ length 4) | 2,570 |
| Global relations (evidence in ≥ 50% of surahs) | 59 |
| Localized relations (evidence in ≤ 3 surahs) | 65 |

---

## 2. Method (all Quran-internal, deterministic)

1. **Concept-activation matrix** per ayah from Phase-3 root- and
   lemma-membership union; earliest word position retained for ordering.
2. **Pair + (filtered) triple ayah-joint counts** over the 103 concepts.
3. **CO_OCCURS** (support ≥ 5) and **ASSOCIATES_WITH** (NPMI ≥ 0.20).
4. **DEPENDS_ON** (conditional probability + lift) and **REQUIRES**
   (P(B|A) ≥ 0.90).
5. **PRECEDES / FOLLOWS** from intra-ayah word-position asymmetry
   (≥ 0.30 over support ≥ 10).
6. **PREDICTS** over sequence windows `w ∈ {1, 2, 3}` within the same surah
   (conf ≥ 0.20 ∧ lift ≥ 1.5 ∧ support ≥ 5).
7. **MEDIATES** triadic: P(M | A∧D) ≥ 0.70 ∧ isolation share ≥ 0.50.
8. **CONDITIONAL_EMERGES** synergy: `P(E|A,B) − max(P(E|A), P(E|B)) ≥ 0.15`.
9. **Proposition graph** + per-node unweighted Brandes betweenness, top-10
   in/out partners, and BRIDGES = top decile by betweenness.
10. **Stability** under `SUPPORT_MIN ± 1` perturbation.
11. **Classifications**: hubs, bridges, dependency hubs, rare /
    stable / global / localized edges, hierarchical chains, causal pairs,
    recursive cycles.

All constants are fixed and documented in `proposition_manifest.json`. The
build is byte-identically reproducible — verified by
`scripts/validate_propositions.py --rebuild` (99 checks, all pass).

---

## 3. Data products

`generated/propositions/`:

| File | Contents |
|---|---|
| `proposition_candidates.json` | every candidate relation, grouped by type; statistics + classifications |
| `proposition_graph.json` | typed directed multigraph + per-node topology metrics |
| `dependency_candidates.json` | DEPENDS_ON + REQUIRES + hierarchical chains |
| `implication_candidates.json` | PREDICTS by window |
| `conditional_patterns.json` | synergy triples |
| `bridge_patterns.json` | MEDIATES triples + BRIDGES list |
| `proposition_manifest.json` | constants, input SHA-256, totals, prohibitions, output bytes |

Tooling: `scripts/build_propositions.py` (≈0.7 s, pure stdlib),
`scripts/validate_propositions.py`. Reports:
`proposition-discovery-report.md`, `dependency-analysis-report.md`,
`implication-analysis-report.md`, `proposition-topology-report.md`,
`phase4-final-report.md`.

---

## 4. Discoveries (structural only — no interpretation)

1. **6,832 candidate relations emerge** across nine relation types from the
   103 Phase-3 concepts. Most directional edges have `stability_score = 1.0`
   under support ± 1 perturbation.
2. **One dominant requirement target.** 96 of 100 `REQUIRES` edges point at
   `CONCEPT_007`. Its (in + out)-degree is 185 — 2.8× the second highest. It
   is also the highest-betweenness node by a 7× margin.
3. **A secondary hierarchy exists.** Exactly four depth-3 `REQUIRES`
   chains were discovered — three pass through `CONCEPT_002`/`CONCEPT_081`,
   all four terminate at `CONCEPT_007`. The macro-structure is "outer
   periphery requires an intermediate concept requires the dominant target."
4. **A tight high-NPMI sub-cluster.** Six concept pairs exceed NPMI 0.70
   (`CONCEPT_073 ↔ CONCEPT_074` at 0.864, support 28; `CONCEPT_039` /
   `CONCEPT_048` / `CONCEPT_076` / `CONCEPT_089` recur repeatedly). This
   sub-cluster also dominates the high-lift `PREDICTS` edges at every
   window.
5. **Bimodal distribution of evidence reach.** 59 relations are evidenced
   across ≥ 57 surahs; 65 relations are confined to ≤ 3 surahs. Few sit in
   between.
6. **Bridge / hub identity overlap.** The top-10 betweenness set largely
   coincides with the top-10 degree set (8 of 10). High betweenness ≠ low
   degree here — the concept hubs *are* the structural bridges.
7. **Mediation is concentrated.** 2,347 mediation triples exist but the
   mediator is repeatedly a small set of high-marginal concepts. This is a
   distributional artefact of activation density — flagged as a limitation.
8. **Three isolated concepts** (`CONCEPT_086`, `CONCEPT_100`, `CONCEPT_102`)
   never produce a joint co-activation with another concept above support 5.
9. **2,570 directed cycles** of length ≤ 4 exist over the union
   `DEPENDS_ON ∪ REQUIRES ∪ PRECEDES`. The graph is recursive in the
   directional sense, dominated by short cycles through `CONCEPT_007`.

---

## 5. Success criteria — answered

| Question | Answer source |
|---|---|
| Which concepts are structurally related? | `proposition_candidates.json :: relations.*` |
| Which concepts appear dependent? | `dependency_candidates.json` |
| Which concepts act as bridges? | `bridge_patterns.json :: bridges` (top decile betweenness) |
| Which concepts appear foundational? | `REQUIRES` in-degree leaderboard (dominated by `CONCEPT_007`) |
| Which concepts appear derivative? | `REQUIRES` out-degree leaderboard + `dependency_hubs` |
| Which structures are stable across the Quran? | `classifications.highly_stable_edge_count`, `global_relations` |

All answered **without assigning meanings**.

---

## 6. Limitations

- **No meaning is claimed.** Concept ids and relation types are opaque
  throughout. `REQUIRES`, `PRECEDES`, `PREDICTS` etc. are structural labels
  on statistical regularities, not semantic or causal assertions.
- **`CONCEPT_007` saturation.** The dominant requirement target makes the
  directed projection appear hub-and-spoke. The structural fact is real;
  the interpretive weight is small. A masked-out re-run is recommended as
  a future open question.
- **Threshold dependence.** All thresholds are fixed (NPMI 0.20, support 5,
  lift 2.0, requires conf 0.90, asymmetry 0.30, synergy 0.15, predict conf
  0.20 / lift 1.5). Local robustness is bounded by `stability_score` only.
- **Triple pre-filter.** Triples are restricted to those whose three
  pairwise counts each meet `≥ 3`. Some weak-pair / strong-triple structures
  will be missed.
- **Activation rule.** Concept activation in an ayah is the **union** over
  word-level root and lemma memberships. Alternative rules would redraw
  every count.
- **Betweenness uses unweighted projection.** Weighted shortest paths
  collapsed onto one node because several confidences saturate at 1.0;
  unweighted is more informative but ignores edge strength.
- **Mediation depends on marginal density.** A concept active in a
  majority of ayahs trivially mediates many pairs.
- **`PREDICTS` is not causal.** It is a sequence-conditional probability
  within a surah only.

---

## 7. Recommendations for Phase 5 — NOT started

Scoping notes only. Any future phase must preserve the firewall: no external
meaning, no ontology, no axiom engine, no contradiction engine, no theology,
no interpretation, no doctrine, no origin claims, and no labels unless
explicitly instructed.

1. **Stability sweep across thresholds.** Build a persistence diagram per
   edge by sweeping `NPMI_MIN`, `SUPPORT_MIN`, `REQUIRES_CONF_MIN`,
   `ORDER_ASYM_MIN`. Edges surviving the widest range are the most robust
   propositions.
2. **`CONCEPT_007`-masked re-run.** Re-run the engine with the dominant
   concept removed from the activation matrix to expose the secondary
   structure.
3. **Triadic structure beyond marginals.** Score mediators by their lift
   *above* what marginal probability would predict, not absolute mediation
   probability — this would highlight mediators that genuinely concentrate
   joint activation rather than simply being everywhere.
4. **Hierarchical exploration.** Sweep `REQUIRES_CONF_MIN ∈ {0.85, 0.95}`
   to expose deeper chains.
5. **Recursive sub-graphs.** Catalogue cycles excluding the dominant hub
   and check whether any non-trivial recursive sub-structures emerge.
6. **Cross-phase reconciliation.** Compare dependency hubs and bridges
   with Phase-3 concept hubs / bridges; surface the alignment.

These are recommendations only. The phase did not start them.

---

## 8. Prohibitions observed

`no ontology · no axioms · no contradiction engine · no theology · no
interpretation · no doctrine · no origin claims · no concept translation · no
proposition naming · no semantic labels · no external knowledge · propositions
discovered not invented.`

---

## 9. Reproduce

```bash
python3 scripts/build_propositions.py                        # ≈0.7 s
python3 scripts/validate_propositions.py --rebuild           # 99 checks, byte-identical rebuild
```

**Phase 4 complete. Phase 5 not started.**
