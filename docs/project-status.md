# Monad — Project Status

**Last updated:** 2026-06-06. **Current phase complete:** Phase 4 (Proposition
Discovery Engine). **Next phase:** Phase 5 — *not started*.

Monad derives everything from the Quranic corpus itself. No external dictionary,
tafsir, translation, theology, or pre-trained embedding is used at any layer. Each
phase reads the previous phase's outputs and never rebuilds them.

---

## Phase ledger

| Phase | Title | Status | Primary outputs |
|---|---|---|---|
| 1 | Canonical Quran Database | ✅ complete | `generated/monad.db` |
| 2 | Quran Internal Lexicon Engine | ✅ complete | `generated/lexicon/*.json` |
| 3 | Concept Discovery Engine | ✅ complete | `generated/concepts/*.json` |
| 4 | Proposition Discovery Engine | ✅ complete | `generated/propositions/*.json` |
| 5 | (future) | ⛔ not started | — |

---

## Phase 1 — Canonical Quran Database

Immutable, reproducible SQLite database from the read-only corpus.

- 114 surahs · 6,236 ayahs · 77,429 word tokens · 128,219 morphology tokens
- 1,642 roots · 4,831 lemmas
- Builder: `scripts/build_database.py`; Validator: `scripts/validate_database.py`
- Docs: `database-schema.md`, `data-inventory.md`, `import-report.md`,
  `source-priority.md`, `data-quality-report.md`

---

## Phase 2 — Quran Internal Lexicon Engine

Complete internal lexical layer: how words derive meaning from Quran-internal
usage. PPMI over ayah-level co-occurrence; composite distributional + chapter
similarity.

- 7 data products in `generated/lexicon/` (root/lemma profiles, context windows,
  co-occurrence graph, semantic neighbors, distribution profiles, summary)
- 1,642 root profiles · 4,831 lemma profiles · 77,429 context-window records ·
  6,473-node / 28,968-edge co-occurrence graph · top-20 semantic neighbors per
  entity
- Builder: `scripts/build_lexicon.py`; Validator: `scripts/validate_lexicon.py`
  (26 checks, byte-identical rebuild)
- Reports: `root-analysis-report.md`, `lemma-analysis-report.md`,
  `semantic-neighborhood-report.md`, `distribution-analysis-report.md`,
  `phase2-final-report.md`

---

## Phase 3 — Concept Discovery Engine

Discovery of emergent conceptual structures (clusters of co-behaving roots and
lemmas) from the Phase-2 lexicon. Concepts carry opaque ids; **no meaning,
name, translation, or interpretation is assigned.**

- 7 data products in `generated/concepts/` (candidates, memberships, graph,
  centers, statistics, relationships, manifest)
- **103 concept candidates** · 735/1,633 roots clustered · 2,264 lemmas attached
- Multi-membership: 159 roots, 536 lemmas in >1 concept
- Concept graph: 103 nodes / 329 edges / 42 meta-communities / 8 isolated
- Mean internal density 0.81 · cohesion 0.41 · separation 0.37 · stability 0.78
- Method: mutual-kNN + recursive k=4 clique percolation; degree / betweenness /
  eigenvector centrality; deterministic label-propagation communities
- Builder: `scripts/build_concepts.py`; Validator: `scripts/validate_concepts.py`
  (30 checks, byte-identical rebuild)
- Reports: `concept-discovery-report.md`, `concept-topology-report.md`,
  `concept-centrality-report.md`, `concept-cluster-report.md`,
  `phase3-final-report.md`

---

## Phase 4 — Proposition Discovery Engine

Discovery of emergent *relational* structures between Phase-3 concepts.
Propositions carry opaque relation types over opaque concept ids; **no meaning,
name, theology, or interpretation is assigned.**

- 7 data products in `generated/propositions/` (candidates, graph, dependency,
  implication, conditional, bridge, manifest)
- **6,832 candidate relations** across 9 relation types over 103 concepts
- ASSOCIATES_WITH 170 · CO_OCCURS 1,215 · DEPENDS_ON 184 · REQUIRES 100 ·
  PRECEDES / FOLLOWS 303 / 303 · PREDICTS 547 (windows 1/2/3) · MEDIATES 2,347
  · CONDITIONAL_EMERGES 1,663
- Proposition graph: 103 nodes / 1,474 directed edges / 14.0 % pairwise density
  / 3 isolated / 10 bridges (top-decile betweenness)
- Mean (in + out) degree 28.6 · max 185 · mean relation diversity 5.48 / 9 ·
  mean unweighted betweenness 40.92
- 4 depth-3 hierarchical chains · 28 potential causal pairs · 2,570 directed
  cycles of length ≤ 4 · 59 global / 65 localized relations
- Method: per-ayah concept-activation matrix → marginal / pair / triple counts;
  PMI / NPMI; conditional probability + lift; intra-ayah positional asymmetry;
  sequence-window conditional probability; triadic mediation; synergy triples;
  unweighted Brandes betweenness on the undirected projection
- Builder: `scripts/build_propositions.py`; Validator:
  `scripts/validate_propositions.py` (99 checks, byte-identical rebuild)
- Reports: `proposition-discovery-report.md`, `dependency-analysis-report.md`,
  `implication-analysis-report.md`, `proposition-topology-report.md`,
  `phase4-final-report.md`

Monad can now answer, without assigning meanings: which concepts are
structurally related, which appear dependent, which act as bridges, which
appear foundational, which appear derivative, and which structures are stable
across the Quran.

---

## Invariants held across all phases

- The Quran is the only semantic universe; no external knowledge is imported.
- Source datasets, the database schema, and prior-phase outputs are never
  modified or rebuilt by a later phase.
- Every engine is deterministic, reproducible, and byte-identically rebuildable,
  with a dedicated validator.
- No ontology, contradiction engine, axioms, theology, interpretation, doctrine,
  or origin claims have been produced. Work remains at the lexical /
  statistical / structural layer. Concept ids and relation types are opaque
  throughout.

---

## Reproduce the full stack

```bash
python3 scripts/build_database.py     && python3 scripts/validate_database.py
python3 scripts/build_lexicon.py      && python3 scripts/validate_lexicon.py     --rebuild
python3 scripts/build_concepts.py     && python3 scripts/validate_concepts.py    --rebuild
python3 scripts/build_propositions.py && python3 scripts/validate_propositions.py --rebuild
```

---

## Next

Phase 5 is **not started** by design. Recommendations are recorded in
`phase4-final-report.md §7`. Awaiting explicit instruction to proceed.
