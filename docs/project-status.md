# Monad — Project Status

**Last updated:** 2026-06-06. **Current phase complete:** Phase 7 (Semantic
Revelation Engine). **Next phase:** Phase 8 — *not started*.

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
| 5 | Dependency Compression Engine | ✅ complete | `generated/compression/*.json` |
| 6 | Concept Identification Engine | ✅ complete | `generated/identification/*.json` |
| 7 | Semantic Revelation Engine | ✅ complete | `generated/revelation/*.json` |
| 8 | (future) | ⛔ not started | — |

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

## Phase 5 — Dependency Compression Engine

Measures whether the Phase-4 proposition structure compresses into a smaller set
of foundational structures. **Not** an axiom / ontology / theology engine.
Concept ids and relation types stay opaque; no meaning, ontology, axiom, or
origin claim is produced. Reconstruction = full set membership (a relation is
recovered iff every participating concept is retained).

- 8 data products in `generated/compression/` (foundationality, reconstruction
  sets, dependency layers, irreducible structures, statistics, curve, hub
  removal, manifest)
- **Primary finding:** only *partially* compressible — 80% of structure needs
  **59 / 103 concepts** (ratio 0.573); 50% needs 39; 95% needs 76. Convex
  compression curve (knee at k ≈ 66 → 88%); greedy AUC 0.612
- **Single dominant core:** `CONCEPT_007` (composite 1.000 vs 0.402 next; 22.2%
  of relations incident; sole fragmenting node). 15 concepts each destroy ≥ 5%
  alone; 27 above mean necessity
- **Hub removal → reorganize, not collapse:** 77.8% of relations survive,
  `CONCEPT_016` + a size-9 SCC become the new core; all 4 hierarchical chains
  (hub-terminated) vanish; short cycles fall 2,570 → 219
- **8 dependency layers** (0–7, wide base / thin spire) · **7 irreducible
  dependency cores** (largest size 9, all hub-independent) · one 94-node
  directional SCC (ordering is globally cyclic)
- Method: set-coverage reconstruction; six-metric composite foundationality;
  greedy maximum-coverage; Tarjan SCC condensation + longest-path layering;
  Brandes betweenness (Phase-4-consistent) on the hub-removed induced subgraph
- Builder: `scripts/build_compression.py`; Validator:
  `scripts/validate_compression.py` (byte-identical rebuild, all checks pass)
- Reports: `foundationality-report.md`, `compression-analysis-report.md`,
  `hub-removal-report.md`, `dependency-layer-report.md`,
  `irreducibility-report.md`, `phase5-final-report.md`

---

## Phase 6 — Concept Identification Engine

Reveals *what Quran-internal evidence defines each discovered concept* — dominant
roots, dominant lemmas, activating ayahs, carrying surahs, and surrounding
structures. **Not** a meaning, ontology, or theology engine. Concept ids and
relation types stay opaque; **no meaning, name, translation, or interpretation is
assigned.** Activation reuses the Phase-4 membership-union rule exactly.

- 8 data products in `generated/identification/` (concept profiles, dominant
  roots, dominant lemmas, ayah signatures, surah signatures, concept atlas, core
  investigation, manifest)
- **All 103 concepts profiled.** Activation cross-checks Phase 4 exactly: 6,101
  active ayahs; `CONCEPT_081` activates 2,553 ayahs (= its Phase-4 `REQUIRES`
  support). Activation skew: min 3 · median 53 · **max 5,906** (`CONCEPT_007`,
  96.8% of active ayahs)
- **Dominant evidence (no meaning):** strongest single activation = ayah 2:282
  (`CONCEPT_007`); 2:282 and 47:15 each head 3 concepts; surah 2 carries the most
  activity (top for 35 concepts); uniqueness peaks in short surahs
  (`CONCEPT_102` lift 346 in surah 49); `CONCEPT_007` alone has no distinctive
  surah
- **Core investigation:** deep evidence dossiers for the dominant hub
  (`CONCEPT_007`, layer 0, requires-in only), the secondary core (`CONCEPT_016`,
  layer 7, depends-out, relation-diversity 7/9), the top-20 foundational
  concepts, and the size-9 irreducible core (`003 004 034 053 060 061 084 085
  088`, all layer 6)
- Method: Phase-4-consistent per-ayah activation + summed-membership-confidence
  strength; activation-weight ranking of members; neighbourhood/graph influence
  from Phase-2 semantic neighbours; incident-relation indexing; Phase-5
  SCC/layer reuse
- Builder: `scripts/build_identification.py`; Validator:
  `scripts/validate_identification.py` (18,839 checks, byte-identical rebuild)
- Reports: `concept-identification-report.md`, `core-investigation-report.md`,
  `ayah-signature-report.md`, `surah-signature-report.md`,
  `phase6-final-report.md`

Monad can now answer, without assigning meanings: what evidence defines each
concept, which Quranic regions activate it, which roots and lemmas dominate it,
and which structures depend on and surround it.

---

## Phase 7 — Semantic Revelation Engine

The first phase permitted to investigate concept *identity* — but identity is
revealed, never imported. A concept's identity and candidate "names" are
expressed **only** as the concept's own dominant **Arabic** roots/lemmas and the
ayah / structural patterns they form. **No translation, gloss, dictionary,
tafsir, theology, or interpretation is used; no certainty or origin is claimed;
competing identities are preserved.** The validator enforces the core invariant:
every candidate name is a literal Quran-internal member token.

- 9 data products in `generated/revelation/` (concept dossiers, semantic fields,
  ayah identity profiles, root consistency, candidate names, core revelation,
  identity confidence, falsification results, manifest)
- **Identity tiers across 103 concepts:** 43 strong · 51 moderate · 3 weak · **6
  resist** (the most lexically diffuse: `001`–`004`, `013`, `017`). Verdicts: 15
  coherent_single · 55 coherent_dominant · 33 diffuse_unified · 0 fragmented
- **Flagship answers (evidence only):** `CONCEPT_007` → anchor `ٱللَّه`/`اله`
  (present in 96% of its signature ayahs, broad diffuse field); `CONCEPT_016` →
  `جَنَّة`/`جنن`; `CONCEPT_081` → `ٱللَّه`/`اله` (strongest single identity, conf
  0.629)
- **Ambiguity preserved:** 42 concepts carry competing anchors; 4 anchors head
  >1 concept (`اله`→`007/081`, `رسل`→`061/085/088`, `كفي`, `قمص`). Most
  structurally central concepts are the hardest to name
- **Falsification:** each identity attacked; 97 tested, **94 survive, 3
  falsified** (`011` `نصح`, `041` `حدب`, `043` `رفد` — fail to explain ≥78% of
  their own signature ayahs)
- Method: root-anchored naming over Phase-6 activation; semantic fields by intra-
  concept co-occurrence + Phase-2 neighbours; POS-based actors/actions (Phase-1
  morphology); HHI/entropy coherence; evidence-graph dossiers; self-falsification
- Builder: `scripts/build_revelation.py`; Validator:
  `scripts/validate_revelation.py` (3,299 checks incl. no-imported-meaning
  invariant, byte-identical rebuild)
- Reports: `semantic-revelation-report.md`, `concept-identity-report.md`,
  `core-revelation-report.md`, `identity-confidence-report.md`,
  `falsification-report.md`, `phase7-final-report.md`

Monad can now answer, using Quran-internal evidence only and without claiming
certainty: what each concept is most likely anchored on, which identities are
strongly supported, which remain ambiguous, which concepts resist identification,
and what competing explanations coexist.

---

## Invariants held across all phases

- The Quran is the only semantic universe; no external knowledge is imported.
- Source datasets, the database schema, and prior-phase outputs are never
  modified or rebuilt by a later phase.
- Every engine is deterministic, reproducible, and byte-identically rebuildable,
  with a dedicated validator.
- No ontology, contradiction engine, axioms, theology, interpretation, doctrine,
  or origin claims have been produced. Work remains at the lexical /
  statistical / structural layer. Relation types stay opaque throughout. From
  Phase 7, a concept's *identity* may be revealed — but only as its own dominant
  Quran-internal Arabic roots/lemmas and ayah/structure patterns; never as a
  translation, gloss, meaning, or origin claim, and never with claimed certainty.

---

## Reproduce the full stack

```bash
python3 scripts/build_database.py     && python3 scripts/validate_database.py
python3 scripts/build_lexicon.py      && python3 scripts/validate_lexicon.py     --rebuild
python3 scripts/build_concepts.py     && python3 scripts/validate_concepts.py    --rebuild
python3 scripts/build_propositions.py && python3 scripts/validate_propositions.py --rebuild
python3 scripts/build_compression.py  && python3 scripts/validate_compression.py  --rebuild
python3 scripts/build_identification.py && python3 scripts/validate_identification.py --rebuild
python3 scripts/build_revelation.py     && python3 scripts/validate_revelation.py     --rebuild
```

---

## Next

Phase 8 is **not started** by design. Open questions are recorded in
`phase7-final-report.md §9`. Awaiting explicit instruction to proceed.
