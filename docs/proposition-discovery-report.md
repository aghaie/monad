# Proposition Discovery Report — Phase 4

**Date:** 2026-06-06. **Method version:** `phase4-propositions-1.0`. **Status:**
complete.

Phase 4 discovers **proposition candidates** — recurring relational structures
between Phase-3 concept candidates. A proposition here is *not* a word, root,
lemma, or concept; it is an emergent statistical regularity in how concepts
co-activate, order, depend, mediate, or jointly enable a third inside the
Quran. Concept ids remain opaque (`CONCEPT_001`…); no meaning, translation,
name, theology, or interpretation is assigned at any layer.

The Quran is the only semantic universe. Phase 1/2/3 outputs are read and
hashed but never rebuilt. The build is byte-identically reproducible.

---

## 1. Inputs

| Source | Use |
|---|---|
| `monad.db` (Phase 1) | per-ayah words → root_id, lemma_id, position |
| `lexicon/{root,lemma,distribution,semantic_neighbors}.json` (Phase 2) | indirect — hashed for reproducibility |
| `concepts/concept_memberships.json` (Phase 3) | root_id → concept ids; lemma_id → concept ids |
| `concepts/concept_candidates.json` (Phase 3) | canonical concept id set |
| `concepts/concept_graph.json` + `concept_manifest.json` (Phase 3) | hashed for reproducibility |

A concept is *active* in an ayah iff any word in the ayah carries a root or
lemma membership for it. Earliest word position is retained for intra-ayah
ordering.

| Quantity | Value |
|---|---:|
| Ayahs (total) | 6,236 |
| Ayahs with ≥ 1 active concept | **6,101** (97.84%) |
| Concepts | 103 |
| Pair counts (≥ 1 joint ayah) | 2,698 |
| Triple counts (≥ 3 joint ayahs, pair-prefiltered) | 7,633 |

---

## 2. Method (deterministic, Quran-internal)

1. **Concept-activation matrix** `ayah_seq → frozenset(concept_id)`.
2. **Joint counts** `cnt[A]`, `cnt[A,B]`, `cnt[A,B,C]` (triple pre-filtered by
   all three pair counts ≥ 3, support ≥ 3).
3. **CO_OCCURS** — symmetric. Edge iff `cnt[A,B] ≥ 5`. Confidence
   `min(P(A|B), P(B|A))`.
4. **ASSOCIATES_WITH** — symmetric. NPMI ≥ 0.20 ∧ support ≥ 5.
5. **DEPENDS_ON** — directional. `P(A|B) ≥ 0.30 ∧ lift = P(A|B)/P(A) ≥ 2.0`.
6. **REQUIRES** — directional. `P(B|A) ≥ 0.90` (A nearly never appears
   without B).
7. **PRECEDES / FOLLOWS** — directional. Within an ayah, compare earliest
   word position of A vs B. Asymmetry score ≥ 0.30, support ≥ 10 ayahs.
8. **PREDICTS** — directional, sequence-window `w ∈ {1, 2, 3}` within the
   same surah. `P(B@i+w | A@i) ≥ 0.20 ∧ lift ≥ 1.5 ∧ support ≥ 5`.
9. **MEDIATES** — triadic `(M; A, D)`. `P(M | A∧D) ≥ 0.70`, isolation
   `cnt[A,M,D]/cnt[A,D] ≥ 0.50`, support ≥ 5.
10. **CONDITIONAL_EMERGES** — triadic `A∧B → E`. Synergy
    `P(E|A,B) − max(P(E|A), P(E|B)) ≥ 0.15`, support ≥ 5.
11. **Proposition graph** — directed multigraph over 103 concept nodes,
    edges typed by relation. Per node: in/out degree, relation diversity,
    unweighted betweenness centrality on the undirected projection.
12. **Stability score** — for each candidate edge, recompute survival at
    `support_threshold ± 1` and store `(kept_low + kept_high)/2 ∈ {0, 0.5, 1}`.

All edge attributes: `confidence`, `support_count`, `stability_score`,
`evidence_paths` (up to 5 `(surah, ayah)` tuples per pair, sampled in
sequential order).

---

## 3. Statistics

### 3.1 Edge counts per relation type

| Relation | Count |
|---|---:|
| CO_OCCURS | **1,215** |
| ASSOCIATES_WITH | **170** |
| DEPENDS_ON | **184** |
| REQUIRES | **100** |
| PRECEDES | **303** |
| FOLLOWS | **303** |
| PREDICTS (all windows) | **547** |
| PREDICTS w=1 / w=2 / w=3 | 182 / 193 / 172 |
| MEDIATES (triples) | **2,347** |
| CONDITIONAL_EMERGES (triples) | **1,663** |
| **Total candidate relations** | **6,832** |

### 3.2 Graph

| Quantity | Value |
|---|---:|
| Nodes | 103 |
| Directed graph edges (incl. duplicate-typed) | 1,474 |
| Mean out-degree | 14.31 |
| Mean relation diversity per node | 5.48 |
| Mean unweighted betweenness | 40.92 |
| Bridges (top decile betweenness) | 10 |

### 3.3 Stability and rarity

- Edges with `stability_score == 1.0`: **1,459** (out of 1,710 directional +
  symmetric pairs counted across DEPENDS_ON / REQUIRES / PRECEDES / FOLLOWS /
  PREDICTS / ASSOCIATES_WITH; CO_OCCURS / MEDIATES / CONDITIONAL excluded
  from this aggregate).
- Rare edges (support ≤ 1st quartile = 11): **411**.

### 3.4 Distribution

- **Global relations** (evidence spans ≥ 50% of 114 surahs): **59**.
- **Localized relations** (evidence confined to ≤ 3 surahs): **65**.
- Several `REQUIRES` edges show evidence in 91–99 surahs — pervasive
  structural dependence.

---

## 4. Structural findings (no interpretation)

These observations describe the graph; no claim is made about what any
concept *means*.

1. **One concept dominates the requirement graph.** `CONCEPT_007` is the
   target of the strongest `REQUIRES` edges (confidence 1.0 at support 2,553)
   and the source of the strongest `PRECEDES` edges. It also tops degree and
   betweenness rankings. Its membership covers 99 of 103 other concepts as
   immediate partners.
2. **Mediation is concentrated.** Of 2,347 `MEDIATES` triples, the vast
   majority list a small set of high-coverage concepts as mediator. This is
   a property of the activation distribution, not an interpretation.
3. **A small cluster of high-NPMI symmetric pairs.** Six pairs exceed NPMI
   0.70, with the strongest at 0.864 (support 28 ayahs). These are
   semantically narrow but statistically tight.
4. **Bimodal distribution.** As in Phase 3, relations split into a pervasive
   tier (59 global) and a long tail (65 localized to ≤ 3 surahs).
5. **Few clean hierarchical chains.** Only **4** depth-3 chains of
   `REQUIRES → REQUIRES` survive — all terminate at `CONCEPT_007`. Most
   chains are "absorbed" by the dominant requirement target.
6. **Recursion is abundant in the directional projection.** **2,570**
   directed cycles of length ≤ 4 exist over the union of `DEPENDS_ON ∪
   REQUIRES ∪ PRECEDES`. This includes many short cycles through
   `CONCEPT_007`.
7. **28 "potential causal" pairs** — `PRECEDES` edges that also pass the
   `DEPENDS_ON` thresholds. The label remains structural: an ordering plus a
   dependency, not a causal claim.

---

## 5. Outputs

`generated/propositions/`:

| File | Contents |
|---|---|
| `proposition_candidates.json` | every candidate relation, grouped by type; statistics + classifications |
| `proposition_graph.json` | nodes (degree, diversity, betweenness, top partners) + typed edges + bridges |
| `dependency_candidates.json` | DEPENDS_ON + REQUIRES + hierarchical chains |
| `implication_candidates.json` | PREDICTS per window |
| `conditional_patterns.json` | synergy triples (A∧B → E) |
| `bridge_patterns.json` | MEDIATES triples + BRIDGES list |
| `proposition_manifest.json` | constants, input SHA-256, totals, prohibitions, output bytes |

Tooling: `scripts/build_propositions.py` (~0.7 s, stdlib only),
`scripts/validate_propositions.py` (99 checks, byte-identical rebuild).

---

## 6. Limitations

- **No meaning claimed.** All ids stay opaque; the graph describes structural
  regularity in the activation matrix only.
- **Activation rule.** Concept activation in an ayah is the *union* over
  word-level root and lemma memberships. A different rule (intersection,
  weighted, per-token instead of per-ayah) would redraw counts and therefore
  edges.
- **Threshold dependence.** Every relation is gated by fixed thresholds
  (NPMI, lift, confidence, support, asymmetry, synergy). Stability score
  bounds local robustness only; sweeping the schedule would expose a
  persistence diagram and is left for a future phase.
- **Triple pre-filter.** Triples are pre-filtered by pair support ≥ 3. Some
  weak-pair / strong-triple cases will be missed.
- **`PREDICTS` is non-causal.** It captures conditional probability of a
  concept activating w ayahs later within the same surah. No causal
  inference is claimed.
- **Betweenness uses unweighted projection.** A weighted (1/weight)
  formulation collapsed onto a single hub because several `REQUIRES /
  PRECEDES` confidences saturate at 1.0; unweighted shortest paths give a
  more informative distribution. Different choices reorder mid-rank nodes.
- **Mediation is statistical.** A high mediator score means M almost always
  appears whenever A and D do; it does not imply M causes their
  co-activation.

---

## 7. Open questions (for future phases, not this one)

- Does a sweep over `(NPMI_MIN, SUPPORT_MIN, REQUIRES_CONF_MIN)` produce a
  persistence diagram per edge?
- If concept activation is restricted to lemmas with `membership_confidence
  ≥ 0.5`, how do the counts shift?
- Are the `MEDIATES` triples carrying real triadic structure or just
  marginal-density bias from one dominant concept?
- Is there a sub-graph (mod the dominant requirement target) that exhibits
  cleaner hierarchical structure?

---

## 8. Prohibitions observed

`no ontology · no axioms · no contradiction engine · no theology · no
interpretation · no doctrine · no origin claims · no concept translation · no
proposition naming · no semantic labels · no external knowledge · propositions
discovered not invented.`

---

## 9. Reproduce

```bash
python3 scripts/build_propositions.py
python3 scripts/validate_propositions.py --rebuild
```
