# Phase 3 — Final Report: Concept Discovery Engine

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase3-concepts-1.0`.

Phase 3 built the **Concept Discovery Engine**: it discovers recurring
conceptual *structures* that emerge from Quran-internal usage patterns. A concept
is **not** a word, root, or lemma — it is an emergent cluster of statistically
coherent lexical behaviour. Concepts are **discovered, not invented**, carry
**opaque ids** (`CONCEPT_001` …), and are never named, translated, interpreted,
or explained.

The Quran remains the only semantic universe. No external dictionary, tafsir,
translation, theology, or pre-trained embedding was used. The Phase-1 database
and Phase-2 lexicon were **read but not rebuilt**.

---

## 1. Statistics

| Quantity | Value |
|---|---:|
| Concept candidates | **103** |
| Roots clustered | 735 / 1,633 (45.0%) |
| Lemmas attached | 2,264 / 4,831 |
| Multi-membership roots | 159 |
| Multi-membership lemmas | 536 |
| Concept size (roots): max / mean / min | 34 / 9.0 / 4 |
| Concept graph: nodes / edges | 103 / 329 |
| Meta-communities | 42 (largest = 43 concepts) |
| Isolated concepts | 8 |
| Mean internal density | 0.813 |
| Mean cohesion | 0.406 |
| Mean external separation | 0.369 |
| Mean cluster stability | 0.778 |

---

## 2. Method (all Quran-internal, deterministic)

1. **Mutual-kNN root graph** from Phase-2 semantic confidence (edge iff both
   roots list each other, confidence ≥ 0.30; weight = min).
2. **k = 4 clique percolation** → overlapping communities (native
   multi-membership).
3. **Recursive splitting** of communities > 40 roots at raised thresholds —
   removes single-linkage chaining through the dense backbone.
4. **Lemma attachment** by distributional + parent-root alignment (confidence ≥
   0.30).
5. **Per-concept metrics** (cohesion, density, separation, stability) and surah
   distribution profile.
6. **Concept graph** (shared members + cross semantic overlap) with degree,
   betweenness, eigenvector centrality and label-propagation meta-communities.

All parameters are in `concept_manifest.json`. The build is byte-identically
reproducible (verified by `scripts/validate_concepts.py --rebuild`, 30 checks,
all pass).

---

## 3. Data products

`generated/concepts/`:

| File | Contents |
|---|---|
| `concept_candidates.json` | per concept: members, density, separation, stability, cohesion, centers, distribution |
| `concept_memberships.json` | per-concept member lists + inverse root→concepts & lemma→concepts indices (multi-membership) |
| `concept_graph.json` | weighted concept graph + per-node centralities + meta-community |
| `concept_centers.json` | most central member roots per concept + centralities |
| `concept_statistics.json` | global statistics + discovery classifications |
| `concept_relationships.json` | top related concepts + meta-community structure |
| `concept_manifest.json` | constants + input SHA-256 + totals (reproducibility) |

Tooling: `scripts/build_concepts.py` (≈0.7 s, pure stdlib),
`scripts/validate_concepts.py`. Reports: `concept-discovery-report.md`,
`concept-topology-report.md`, `concept-centrality-report.md`,
`concept-cluster-report.md`.

---

## 4. Discoveries (structural only — no interpretation)

1. **103 stable, internally dense concept candidates emerge** from the lexicon
   with mean internal density 0.81 and mean stability 0.78. The same members
   re-cluster under threshold perturbation — the structures are not artefacts of
   one threshold.

2. **Multi-membership is real and substantial** — 159 roots and 536 lemmas
   behave as part of more than one concept. Exclusive partitioning would have
   discarded this structure.

3. **A bimodal reach pattern.** Concepts split into a *pervasive* band touching
   85–97% of surahs and a *single-surah* band whose entire root set is confined
   to one chapter, with relatively few concepts in between.

4. **Three distinct centrality roles.** Degree, betweenness, and eigenvector
   centrality rank different concepts: connectors (high degree), bridges (high
   betweenness, often small — e.g. 4-root concepts on many shortest paths), and a
   single dense knot of mutually reinforcing concepts that dominates eigenvector
   centrality. Concept importance is multi-dimensional, not size-driven.

5. **Core/periphery topology one level up.** The concept graph is sparse (density
   0.06) with one dominant 43-concept meta-community plus a scatter of isolated
   small concepts — the same macro-shape Phase 2 found among roots, now among
   concepts.

6. **Unusually self-contained large structures exist.** At least one 32-root
   concept is simultaneously large, highly cohesive (0.53), highly separated
   (0.80), and pervasive (coverage 0.89) — rare to be all four at once.

---

## 5. Success criteria — answered

| Question | Answer source |
|---|---|
| How many concept candidates exist? | **103** (`concept_statistics.json`) |
| Which concepts are central? | degree / eigenvector leaders in `concept_graph.json`, `classifications.highly_connected` |
| Which concepts connect distant regions? | betweenness leaders, `classifications.bridge_concepts` |
| Which concepts are highly stable? | `cluster_stability`, `classifications.highly_stable` |
| Which concepts are highly specialized? | `classifications.localized_concepts` / `rare_concepts` |

All answered **without assigning meanings**.

---

## 6. Limitations

- **No meaning is claimed.** Member roots are evidence; concepts are behavioural
  clusters, not semantic categories. The engine refuses naming by design.
- **Partial coverage (45% of roots)** — peripheral vocabulary that forms no
  dense clique is left unclustered rather than force-assigned.
- **Parameter dependence.** `MIN_EDGE`, `MAX_SIZE`, the split schedule, and
  `LEMMA_THR` are fixed, documented choices; stability (0.78) bounds their
  local robustness but other regimes would redraw boundaries.
- **Lemma membership is downstream** of root clustering.
- **Centrality / meta-community definitions** are specific (Brandes with
  distance = 1/weight; deterministic label propagation); alternatives would
  reorder minor ranks.
- Built entirely on Phase-2 outputs — inherits their limitations (ayah-scoped
  co-occurrence, distributional ≠ semantic, PPMI rare-pair sensitivity).

---

## 7. Recommendations for Phase 4 (NOT started)

Scoping notes only. Any future phase must preserve the firewall: no external
meaning, no ontology/propositions/axioms/contradiction-engine, no theology,
interpretation, doctrine, or origin claims, and no labels unless a future phase
explicitly instructs it.

1. **Concept stability spectra** — sweep `MIN_EDGE`/`MAX_SIZE` to produce a
   persistence diagram per concept (which concepts survive across many regimes).
2. **Concept-to-lexicon round-trip** — index every ayah by the concepts active
   in it, enabling "which concepts co-activate in a verse" queries — still
   structural.
3. **Hierarchical concepts** — expose the recursive-split tree as an explicit
   concept hierarchy (parent/child), rather than a flat list.
4. **Concept dynamics across the mushaf** — use `ayah_sequential` and
   Meccan/Medinan to profile how concept activation shifts by position
   (distributional, not chronological-causal).
5. **Alternative community models** — compare CPM against deterministic
   modularity / link-clustering to bound method sensitivity.
6. **Only on explicit instruction**: a labelling phase that maps opaque concept
   ids to human-readable handles. Until then, ids remain opaque.

---

### Reproduce

```bash
python3 scripts/build_concepts.py              # writes generated/concepts/*.json (~0.7 s)
python3 scripts/validate_concepts.py --rebuild  # 30 checks, byte-identical rebuild
```

**Phase 3 complete. Phase 4 not started.**
