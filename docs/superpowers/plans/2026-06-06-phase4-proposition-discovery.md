# Phase 4 — Proposition Discovery Engine — Implementation Plan

> **For agentic workers:** This plan is to be executed inline by the same session.
> The deliverable is a single deterministic builder + validator pair plus five
> markdown reports, mirroring Phase 3's pattern. Steps use checkbox (`- [ ]`)
> syntax for tracking.

**Goal:** Build the Proposition Discovery Engine — discover recurring
*relational* structures between Phase-3 concepts (association, dependency,
ordering, mediation, implication, conditional emergence) from Quran-internal
evidence only, with opaque ids and no interpretation.

**Architecture:** One Python-3 stdlib script (`build_propositions.py`) reads
`monad.db` + `lexicon/*` + `concepts/*` and writes seven deterministic JSON
products to `generated/propositions/`. A second script
(`validate_propositions.py`) performs structural checks and a byte-identical
rebuild. Five markdown reports document statistics, evidence, limitations and
open questions. Same firewall as Phase 3.

**Tech stack:** Python 3 stdlib only (json, sqlite3, math, hashlib,
collections, itertools). Deterministic: sorted iteration, fixed thresholds, no
randomness, JSON `sort_keys=True`.

---

## File Structure

| File | Responsibility |
|---|---|
| `scripts/build_propositions.py` | Single-pass deterministic builder. Stages: (1) load inputs, (2) per-ayah concept activation matrix, (3) co-occurrence & marginals, (4) ASSOCIATES_WITH / CO_OCCURS edges (PMI/NPMI), (5) DEPENDS_ON / REQUIRES (conditional probability + lift), (6) PRECEDES / FOLLOWS (intra-ayah word-position + inter-ayah sequence), (7) PREDICTS (sequence-window implication), (8) MEDIATES / BRIDGES (triadic mediation + graph betweenness), (9) conditional emergence (synergy triples A∧B→E), (10) proposition graph assembly, (11) stability under threshold perturbation, (12) statistics + classifications, (13) write seven JSON files with sorted keys. |
| `scripts/validate_propositions.py` | File presence, schema, referential integrity (concept ids ⊆ Phase-3), input SHA-256 match, edge invariants, byte-identical rebuild (`--rebuild`). |
| `generated/propositions/proposition_candidates.json` | All discovered candidate relations with attributes. |
| `generated/propositions/proposition_graph.json` | Directed concept→concept relation graph with edge attributes and node-level topology metrics. |
| `generated/propositions/dependency_candidates.json` | DEPENDS_ON / REQUIRES subset, ranked. |
| `generated/propositions/implication_candidates.json` | PREDICTS subset (sequence-window). |
| `generated/propositions/conditional_patterns.json` | Synergy triples (A∧B → E). |
| `generated/propositions/bridge_patterns.json` | MEDIATES triples + graph-betweenness BRIDGES. |
| `generated/propositions/proposition_manifest.json` | Constants, input SHA-256, totals, prohibitions observed. |
| `docs/proposition-discovery-report.md` | Method + overall statistics. |
| `docs/dependency-analysis-report.md` | DEPENDS_ON / REQUIRES findings. |
| `docs/implication-analysis-report.md` | PREDICTS findings. |
| `docs/proposition-topology-report.md` | Graph topology. |
| `docs/phase4-final-report.md` | Final summary in Phase-3 style. |
| `docs/project-status.md` | Updated to reflect Phase 4 complete. |

---

## Design — concrete algorithms

### Concept activation per ayah

For each ayah, the set of *active concepts* is the union of all concepts to
which any word's root or lemma belongs (via Phase-3
`concept_memberships.json`).  Encode as `dict[int ayah_seq → frozenset[int
concept_index]]`.  This is the only primitive used by all downstream stages.

Also retain, per (ayah_seq, concept_index): the **earliest word position** at
which any member of the concept is active. Used for intra-ayah ordering.

### Marginal & joint counts

- `n_ayah` = 6236.
- `cnt[A]` = #ayahs where A active.
- `cnt[A,B]` = #ayahs where both A and B active (A < B).
- `cnt[A,B,C]` = #ayahs where all three active (sorted triple).
- Only triples with at least `MIN_TRIPLE_SUPPORT` are retained (memory bound).

### Constants (all fixed, documented)

```
NPMI_MIN          = 0.20    # ASSOCIATES_WITH threshold
SUPPORT_MIN       = 5       # min #ayahs supporting an edge
DEPENDS_LIFT_MIN  = 2.0     # P(A|B)/P(A) >= 2
DEPENDS_CONF_MIN  = 0.30    # P(A|B)
REQUIRES_CONF_MIN = 0.90    # P(B|A) for REQUIRES
ORDER_ASYM_MIN    = 0.30    # |precedes - follows| / (precedes + follows)
ORDER_SUPPORT_MIN = 10
PREDICT_WINDOWS   = (1, 2, 3)
PREDICT_LIFT_MIN  = 1.5
PREDICT_CONF_MIN  = 0.20
PREDICT_SUPPORT_MIN = 5
MED_LIFT_MIN      = 2.0     # mediation strength
MED_SUPPORT_MIN   = 5
SYNERGY_MIN       = 0.15    # P(E|A,B) - max(P(E|A), P(E|B))
SYNERGY_SUPPORT_MIN = 5
TRIPLE_PREFILTER  = 3       # joint marginal cutoff for triples
EVIDENCE_TOP      = 5       # ayah evidence kept per relation
PERTURB           = (-1, +1)  # support-threshold perturbations for stability
ROUND             = 6
```

### Relation types

| Type | Directional | Formula | Confidence |
|---|---|---|---|
| `CO_OCCURS` | no | support ≥ SUPPORT_MIN | min(P(A\|B), P(B\|A)) |
| `ASSOCIATES_WITH` | no | NPMI ≥ NPMI_MIN ∧ support ≥ SUPPORT_MIN | NPMI |
| `DEPENDS_ON` (A→B) | yes | P(A\|B) ≥ DEPENDS_CONF_MIN ∧ lift ≥ DEPENDS_LIFT_MIN ∧ support | P(A\|B) |
| `REQUIRES` (A→B) | yes | P(B\|A) ≥ REQUIRES_CONF_MIN ∧ support | P(B\|A) |
| `PRECEDES` (A→B) | yes | intra-ayah asymmetry score ≥ ORDER_ASYM_MIN | asymmetry |
| `FOLLOWS` (A→B) | yes | reverse of PRECEDES | asymmetry |
| `PREDICTS` (A→B, window w) | yes | P(B@i+w \| A@i) ≥ PREDICT_CONF_MIN ∧ lift ≥ PREDICT_LIFT_MIN | conditional prob |
| `MEDIATES` (M; A,D) | yes (triadic) | P(M\| A∧D) ≥ 0.7 ∧ removing M-bearing ayahs drops support(A,D) ≥ 50% | combined |
| `BRIDGES` | per-node | top betweenness in proposition graph | betweenness |

Each edge stores: `confidence`, `support_count`, `stability_score`,
`evidence_paths` (up to EVIDENCE_TOP `(surah, ayah)` tuples).

### Stability score

For each edge, recompute existence with support threshold perturbed by ±1.
`stability = (kept_at_lower + kept_at_higher) / 2` where each indicator is
1 if the edge survives the perturbed test, else 0. Range [0, 1].

### Proposition graph

Directed multigraph: nodes = 103 Phase-3 concept ids, edges = candidate
relations with their type. Compute per-node:
- `in_degree`, `out_degree` (sum of edges, all relation types)
- `relation_diversity` (number of distinct relation types touching the node)
- `betweenness_centrality` (Brandes on undirected projection, distance = 1/weight)
- top-10 outgoing and incoming partner concepts.

BRIDGES = top 10% nodes by betweenness centrality.

### Classifications (final statistics)

- `highly_connected_propositions` — concepts with highest total edge count
- `highly_stable_propositions` — edges with `stability_score == 1.0`
- `rare_propositions` — edges with support in lowest quartile (still passing min)
- `global_propositions` — relations whose evidence spans ≥ 50% of surahs
- `localized_propositions` — relations whose evidence is confined to ≤ 3 surahs
- `concept_hubs` — top-degree concepts
- `dependency_hubs` — concepts with most outgoing DEPENDS_ON / REQUIRES
- `bridge_propositions` — top betweenness
- `potential_hierarchical_structures` — chains A→B→C of REQUIRES edges
- `potential_causal_structures` — PRECEDES edges that are also DEPENDS_ON
- `potential_recursive_structures` — cycles in directed projection (≤ length 4)

All classifications are sets of opaque ids — never named.

---

## Tasks

### Task 1: Inspect Phase-3 outputs, decide membership semantics, freeze inputs

**Files:**
- Read: `generated/concepts/concept_memberships.json`
- Read: `generated/concepts/concept_candidates.json`
- Read: `generated/lexicon/distribution_profiles.json`

- [ ] **Step 1:** Inspect `concept_memberships.json` to confirm both
  `root_memberships` (root_id → list of concept_ids) and `lemma_memberships`
  (lemma_id → list of concept_ids) exist. Confirm the concept-id format and
  total count is 103.
- [ ] **Step 2:** Inspect a concept's `member_roots` to confirm we can map
  root_id → list of concept_ids (multi-membership preserved).
- [ ] **Step 3:** Decide activation rule: a concept C is active in ayah `a`
  iff any word in `a` has a `root_id` whose `root_memberships[root_id]`
  contains C **or** a `lemma_id` whose `lemma_memberships[lemma_id]` contains
  C. (Union of both.) Document in the script header.

### Task 2: Skeleton — `scripts/build_propositions.py`

**Files:**
- Create: `scripts/build_propositions.py`

- [ ] **Step 1:** Write the file header (docstring, mission statement, mirror
  Phase-3 style, list inputs/outputs/method/prohibitions).
- [ ] **Step 2:** Add CLI (`argparse`) with `--db`, `--lex`, `--concepts`,
  `--out` flags defaulting to `generated/{monad.db, lexicon, concepts,
  propositions}`.
- [ ] **Step 3:** Add constants block (all values from "Constants" section
  above).
- [ ] **Step 4:** Implement `_sha256(path)` and `_write_json(path, obj)`
  helpers (UTF-8, `sort_keys=True`, `separators=(",", ":")`, no trailing
  newline — match Phase-3 byte-identical convention. Confirm by reading
  `build_concepts.py` how it writes.) Then run a quick sanity build to ensure
  the script imports.

### Task 3: Load Phase-3 inputs + build activation matrix

- [ ] **Step 1:** Load `concept_memberships.json`. Build
  `root_to_concepts: dict[int, frozenset[str]]` and
  `lemma_to_concepts: dict[int, frozenset[str]]`.
- [ ] **Step 2:** Load `concept_candidates.json` to get sorted concept-id
  list and per-concept surah distribution (used later for evidence).
- [ ] **Step 3:** Open `monad.db`. For each ayah (`ayah_sequential`), collect
  the union of concepts active via roots and via lemmas. Also retain
  earliest word position per (ayah, concept).
- [ ] **Step 4:** Build `ayah_concepts: dict[int, frozenset[str]]` and
  `ayah_concept_pos: dict[int, dict[str, int]]`.
- [ ] **Step 5:** Compute `cnt[A]` and pairwise `cnt[A,B]` (sorted lex pairs).
  Confirm `cnt[A]` totals match concept-level surah evidence approximately.

### Task 4: ASSOCIATES_WITH / CO_OCCURS

- [ ] **Step 1:** For every pair with `cnt[A,B] >= SUPPORT_MIN`, compute
  `pA`, `pB`, `pAB`, `pmi`, `npmi`. Save pairs with `npmi >= NPMI_MIN`.
- [ ] **Step 2:** Compute symmetric `co_occurs` confidence `min(pA|B, pB|A)`
  for those passing SUPPORT_MIN.
- [ ] **Step 3:** Sample `EVIDENCE_TOP` `(surah, ayah)` tuples of joint
  activation, deterministically ordered by `ayah_sequential`.

### Task 5: DEPENDS_ON / REQUIRES

- [ ] **Step 1:** For each ordered pair (A, B) with `cnt[A,B] >= SUPPORT_MIN`,
  compute `P(A|B) = cnt[A,B]/cnt[B]`, `P(B|A)`, `lift = P(A|B)/pA`.
- [ ] **Step 2:** Emit DEPENDS_ON(A→B) if `P(A|B) >= DEPENDS_CONF_MIN ∧ lift
  >= DEPENDS_LIFT_MIN`.
- [ ] **Step 3:** Emit REQUIRES(A→B) if `P(B|A) >= REQUIRES_CONF_MIN`.
- [ ] **Step 4:** Attach evidence (top-K joint ayahs), confidence,
  support_count.

### Task 6: PRECEDES / FOLLOWS

- [ ] **Step 1:** For each pair (A,B) co-occurring in `>= ORDER_SUPPORT_MIN`
  ayahs, count `precedes(A,B)` = #ayahs where `pos_A < pos_B` and
  `follows(A,B)` = #ayahs where `pos_A > pos_B`.
- [ ] **Step 2:** Compute `asymmetry = (precedes - follows) / (precedes +
  follows)`.
- [ ] **Step 3:** Emit PRECEDES(A→B) if `asymmetry >= ORDER_ASYM_MIN` and
  FOLLOWS(A→B) symmetrically.
- [ ] **Step 4:** Evidence = top ayahs by clearest positional gap.

### Task 7: PREDICTS (sequence-window)

- [ ] **Step 1:** For each window `w ∈ PREDICT_WINDOWS`, iterate over the
  global `ayah_sequential` ordering (skipping cross-surah pairs to avoid
  spurious chapter joins). For pairs (A, B), count
  `co_seq[w][A,B]` = #i where `A ∈ ayah_concepts[i]` and `B ∈
  ayah_concepts[i+w]`.
- [ ] **Step 2:** Pre-filter: only consider pairs with `co_seq[w][A,B] >=
  PREDICT_SUPPORT_MIN`.
- [ ] **Step 3:** Compute `P(B@i+w | A@i) = co_seq[w][A,B] / cnt_first[A]`
  where `cnt_first[A]` counts ayahs i where A active and i+w is in same
  surah. Lift = conditional / pB.
- [ ] **Step 4:** Emit PREDICTS(A→B, window=w) if both thresholds pass.

### Task 8: MEDIATES / BRIDGES (triadic)

- [ ] **Step 1:** For ordered pair (A, D) with `cnt[A,D] >= MED_SUPPORT_MIN`,
  enumerate candidate mediators M with `cnt[A,M,D] >= MED_SUPPORT_MIN`.
  Compute `P(M | A∧D) = cnt[A,M,D]/cnt[A,D]` and `coverage = cnt[A,M,D] /
  cnt[A,D]`.
- [ ] **Step 2:** Compute *isolation lift* — how much A∧D depends on M:
  `iso = 1 - (cnt[A,D] - cnt[A,M,D]) / cnt[A,D]` (fraction of A∧D
  evidence carried by M).
- [ ] **Step 3:** Emit MEDIATES(M; A,D) when `P(M|A∧D) >= 0.70 ∧ iso >=
  0.50`.
- [ ] **Step 4:** Cap to top-K triples per (A,D) to bound output size.

### Task 9: Conditional patterns (synergy triples A∧B → E)

- [ ] **Step 1:** Enumerate triples (A,B,E) where `cnt[A,B] >=
  SYNERGY_SUPPORT_MIN` and E ≠ A,B. Compute `P(E|A,B)`, `P(E|A)`, `P(E|B)`.
- [ ] **Step 2:** `synergy = P(E|A,B) - max(P(E|A), P(E|B))`. Emit if
  `synergy >= SYNERGY_MIN`.

### Task 10: Stability + Proposition graph + Topology

- [ ] **Step 1:** For each emitted edge, recompute survival when
  `SUPPORT_MIN` is shifted by ±1 (only affects edges near the boundary).
  `stability_score ∈ {0, 0.5, 1.0}`.
- [ ] **Step 2:** Build directed multigraph: nodes 103, edges = all candidate
  relations (with `relation_type` attribute).
- [ ] **Step 3:** Compute per-node `out_degree`, `in_degree`,
  `relation_diversity`, undirected betweenness (Brandes,
  `distance = 1/(weight + ε)`).
- [ ] **Step 4:** Compute classifications listed in design section.

### Task 11: Write seven JSON outputs (deterministic)

- [ ] **Step 1:** `proposition_candidates.json` — all edges grouped by
  relation_type, each with confidence, support_count, stability_score,
  evidence_paths.
- [ ] **Step 2:** `proposition_graph.json` — nodes (with metrics) + edges
  (with type, weight, confidence, support, stability).
- [ ] **Step 3:** `dependency_candidates.json` — DEPENDS_ON + REQUIRES.
- [ ] **Step 4:** `implication_candidates.json` — PREDICTS (by window).
- [ ] **Step 5:** `conditional_patterns.json` — synergy triples.
- [ ] **Step 6:** `bridge_patterns.json` — MEDIATES triples + BRIDGES list.
- [ ] **Step 7:** `proposition_manifest.json` — constants, input SHA-256,
  totals, prohibitions_observed, output bytes.
- [ ] **Step 8:** Run the builder; confirm files exist; record total byte
  sizes for the manifest.

### Task 12: `scripts/validate_propositions.py`

- [ ] **Step 1:** File presence check (seven files).
- [ ] **Step 2:** Schema check (top-level keys, edge attribute presence).
- [ ] **Step 3:** Concept-id referential integrity (all node ids ⊆ 103
  Phase-3 ids).
- [ ] **Step 4:** Threshold compliance (every edge meets its declared
  threshold).
- [ ] **Step 5:** Input SHA-256 match against `concept_manifest.json` +
  `lexicon` files + `monad.db`.
- [ ] **Step 6:** `--rebuild` flag: rebuild to a tmp dir and compare files
  byte-for-byte.

### Task 13: Run + verify byte-identical rebuild

- [ ] **Step 1:** `python3 scripts/build_propositions.py`.
- [ ] **Step 2:** `python3 scripts/validate_propositions.py --rebuild`.
- [ ] **Step 3:** Fix any nondeterminism (sort everything; never iterate
  unordered dicts when emitting JSON).

### Task 14: Reports

- [ ] **Step 1:** `docs/proposition-discovery-report.md` — method, stats per
  relation type, confidence/support/stability distributions, limitations,
  open questions.
- [ ] **Step 2:** `docs/dependency-analysis-report.md` — DEPENDS_ON /
  REQUIRES findings: top edges by confidence and by lift; dependency hubs;
  hierarchical chains; evidence samples (concept-id only).
- [ ] **Step 3:** `docs/implication-analysis-report.md` — PREDICTS findings
  per window, decay-of-prediction across windows, support distribution.
- [ ] **Step 4:** `docs/proposition-topology-report.md` — graph topology,
  betweenness, bridges, hubs, potential recursive cycles.
- [ ] **Step 5:** `docs/phase4-final-report.md` — Phase-3-style summary
  including limitations and reproduction commands.

### Task 15: Update `docs/project-status.md`

- [ ] **Step 1:** Add Phase-4 section mirroring Phase-3 style.

### Task 16: Commit

- [ ] **Step 1:** `git add` and `git commit` with message
  `Phase 4 complete`.

---

## Self-review checklist

1. Every output file from the spec is covered: ✓
2. Every relation type from the spec is covered: ✓
3. Each relation includes `confidence`, `support_count`, `stability_score`,
   `evidence_paths`: ✓
4. Discovery tasks (hubs, bridges, hierarchical, causal, recursive) covered
   in classifications: ✓
5. Five reports covered: ✓
6. Validator with byte-identical rebuild covered: ✓
7. No interpretation, no naming, no ontology, no theology: ✓ (concept ids
   remain opaque throughout)
8. Phase-3 / lexicon / DB are read but not modified: ✓

---

## Execution choice

Inline execution within this session (no subagent dispatch). Reasons:
deterministic data-processing script; algorithmic continuity is easier in one
context; Phase-3 used the same pattern.
