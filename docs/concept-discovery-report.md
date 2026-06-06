# Concept Discovery Report — Phase 3 (Monad Concept Discovery Engine)

**Scope.** Discovery of recurring conceptual structures that emerge from
Quran-internal usage. A concept here is **not** a word, root, or lemma; it is an
emergent cluster of statistically coherent lexical behaviour, discovered from the
Phase-2 lexicon and given an **opaque id** (`CONCEPT_001` …). No meaning,
translation, name, or label is assigned. Reproducible via
`scripts/build_concepts.py`.

**Layer.** Strictly structural and statistical. Member roots are shown in Arabic
as **raw evidence** (they are the clustered data); this report does **not**
interpret, translate, name, or explain any concept. All prose is metric.

Data products: `concept_candidates.json`, `concept_memberships.json`,
`concept_statistics.json`.

---

## 1. Method (all Quran-internal)

Concepts are discovered, not invented, by overlapping community detection on the
Phase-2 root semantic-similarity graph:

1. **Mutual-kNN root graph** — an edge connects two roots iff each lists the
   other among its semantic neighbours with confidence ≥ `MIN_EDGE = 0.30`;
   edge weight = the smaller of the two confidences. Mutuality removes hub
   artefacts.
2. **k = 4 clique percolation** — communities are unions of 4-cliques that share
   3 nodes. This is an *overlapping* community method: a root in two
   non-merging cliques belongs to two concepts → **multi-membership** is native.
3. **Recursive splitting** — any community larger than `MAX_SIZE = 40` is
   re-percolated on its induced subgraph at a raised threshold (`+0.03` per
   level, up to `0.60`). This dissolves single-linkage "chaining" through the
   dense backbone while leaving tight clusters intact.
4. **Lemma attachment** — a lemma joins a concept when its associated roots
   (Phase-2 `top_neighbor_roots`) and its parent root fall inside the concept's
   root set, with confidence ≥ `LEMMA_THR = 0.30`.

Every parameter is recorded in `concept_manifest.json`. The build is
deterministic and byte-identically reproducible.

---

## 2. How many concept candidates exist?

| Quantity | Value |
|---|---:|
| **Concept candidates** | **103** |
| Roots clustered | 735 / 1,633 (45.0%) |
| Lemmas attached | 2,264 / 4,831 |
| Concept size (roots) — max / mean / min | 34 / 9.0 / 4 |
| Roots in **multiple** concepts | 159 |
| Lemmas in **multiple** concepts | 536 |

45% of roots enter a concept; the remaining roots are distributionally too
peripheral to form a 4-clique community and are left unclustered (honest
abstention rather than forced assignment). Multi-membership is substantial — 159
roots and 536 lemmas behave as part of more than one concept.

### Size distribution (roots per concept)

A handful of large concepts (34, 33, 32, 31, 26 …) sit atop a long tail of small
tight cliques (size 4–8). The mean concept holds 9 roots.

---

## 3. Aggregate quality of the discovered concepts

| Metric (mean over 103 concepts) | Value | Meaning |
|---|---:|---|
| `internal_density` | 0.813 | fraction of within-concept root pairs that are connected |
| `cohesion_score` | 0.406 | mean internal edge confidence |
| `external_separation` | 0.369 | internal weight ÷ (internal + boundary) weight |
| `cluster_stability` | 0.778 | recovery under threshold perturbation (±0.02) |

Concepts are **internally dense** (0.81) by construction (clique-based) and
**stable** (0.78) — the same members re-cluster together when the similarity
threshold is perturbed. External separation is moderate (0.37) because concepts
deliberately **overlap**, so they share boundary mass with their neighbours.

---

## 4. Representative concept candidates (evidence)

Center roots (highest internal strength) shown as raw Arabic evidence; **no
glosses are given**. Metrics from `concept_candidates.json`.

| Concept | Size | Center roots (evidence) | cohesion | separation | stability | surah cov |
|---|---:|---|---:|---:|---:|---:|
| CONCEPT_001 | 34 | رفث فدي خيط صوم حجج | 0.408 | 0.381 | 0.971 | 0.70 |
| CONCEPT_002 | 33 | نصف نكح وصي فرض سدس | 0.410 | 0.409 | 0.777 | 0.72 |
| CONCEPT_003 | 32 | جنف ذكو خنزر زلم خنق | 0.534 | 0.798 | 0.953 | 0.89 |
| CONCEPT_007 | 24 | علم اله اتي امن بين | 0.386 | 0.366 | 0.396 | 0.97 |
| CONCEPT_016 | 16 | خلد نهر جنن تحت جري | 0.378 | 0.324 | 0.906 | 0.86 |
| CONCEPT_036 | 8 | اسن عسل معي لذذ لبن | 0.539 | 0.545 | 0.864 | 0.24 |
| CONCEPT_039 | 7 | قدد قمص سجن خبز بضع | 0.446 | 0.196 | 0.248 | 0.06 |
| CONCEPT_052 | 6 | اثل عرم خمط سدر سيل | 0.574 | 0.692 | 1.000 | 0.04 |
| CONCEPT_064 | 5 | وزع بسم عفر نمل هدهد | — | — | — | 0.03 |
| CONCEPT_089 | 4 | خبز عصر سجن خمر | 0.465 | 0.128 | 1.000 | 0.08 |

These rows illustrate the spectrum the engine recovers: large pervasive concepts
(CONCEPT_007, coverage 0.97) at one end and tiny perfectly-stable cliques
(CONCEPT_052, CONCEPT_089, stability 1.0, coverage < 0.1) at the other. The raw
member roots are presented as evidence only.

---

## 5. Multi-membership

Membership is non-exclusive and confidence-scored. `concept_memberships.json`
stores, per entity, every concept it belongs to with a confidence:

- **Root membership confidence** = the share of a root's total similarity mass
  that lies inside the concept (in [0,1]). A root split across concepts has a
  confidence per concept reflecting how much of its behaviour each captures.
- **Lemma membership confidence** = `0.5·(neighbour-root alignment) + 0.5·(parent
  root inside concept)`.

159 roots and 536 lemmas are multi-member, confirming the engine models concepts
as overlapping rather than partitioned structures.

---

## 6. Limitations

- **No meaning is claimed.** Member roots are evidence; the engine locates
  *behavioural* clusters, not semantic categories.
- **Coverage is partial by design** (45% of roots). Peripheral vocabulary that
  never forms a dense clique is left unclustered.
- **Threshold dependence.** `MIN_EDGE`, `MAX_SIZE`, and the split schedule are
  fixed, documented choices; other settings would shift boundaries. Stability
  (0.78) measures robustness to small perturbations of exactly these.
- **Lemma attachment is downstream** of root clustering, so lemma membership
  inherits the root concept structure.
- All figures are structural/statistical and assign no interpretation.
