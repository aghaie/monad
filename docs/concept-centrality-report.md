# Concept Centrality Report — Phase 3

**Scope.** Centrality and role analysis over the concept graph (103 concept
candidates, 329 edges). Identifies central, bridge, and isolated concepts.
Strictly structural; concepts are referenced by opaque id with raw member roots
as evidence — none are named or interpreted. Reproducible via
`scripts/build_concepts.py`.

Data products: `concept_graph.json` (per-node centralities),
`concept_centers.json`, `concept_statistics.json`.

---

## 1. Centrality measures computed

| Measure | Definition (this build) |
|---|---|
| **Degree centrality** | weighted sum of incident concept-graph edge weights |
| **Betweenness centrality** | Brandes' algorithm, edge distance = 1 / weight, normalised |
| **Eigenvector centrality** | power iteration on the weighted adjacency (deterministic init, 200 iters) |
| **Meta-community** | deterministic synchronous label propagation |

All are deterministic and reproducible.

---

## 2. Which concepts are central? (degree)

| Rank | Concept | Degree | Size | Center roots (evidence) |
|---|---|---:|---:|---|
| 1 | CONCEPT_039 | 2.406 | 7 | قدد قمص سجن خبز بضع |
| 2 | CONCEPT_002 | 2.111 | 33 | نصف نكح وصي فرض سدس |
| 3 | CONCEPT_035 | 1.919 | 8 | عفف فقر بدر نكح يتم |
| 4 | CONCEPT_001 | 1.917 | 34 | رفث فدي خيط صوم حجج |
| 5 | CONCEPT_089 | 1.853 | 4 | خبز عصر سجن خمر |
| 6 | CONCEPT_027 | 1.766 | 11 | طلل صلد خبط وبل ربو |
| 7 | CONCEPT_004 | 1.697 | 31 | غوط مسح غسل سفر لمس |

**Observation.** High degree is **not** a function of size: the most connected
concept (CONCEPT_039) has only 7 roots, and a 4-root concept (CONCEPT_089) ranks
5th. Centrality here reflects how much a concept's roots co-occur with the roots
of *other* concepts, independent of the concept's own size.

---

## 3. Which concepts connect distant regions? (betweenness — bridge concepts)

| Rank | Concept | Betweenness | Size | Center roots (evidence) |
|---|---|---:|---:|---|
| 1 | CONCEPT_027 | 0.148 | 11 | طلل صلد خبط وبل ربو |
| 2 | CONCEPT_072 | 0.123 | 4 | شرب ثمر لبن صفو |
| 3 | CONCEPT_016 | 0.111 | 16 | خلد نهر جنن تحت جري |
| 4 | CONCEPT_036 | 0.109 | 8 | اسن عسل معي لذذ لبن |
| 5 | CONCEPT_001 | 0.108 | 34 | رفث فدي خيط صوم حجج |
| 6 | CONCEPT_005 | 0.097 | 26 | قنو ينع رمن عنب شبه |

**Bridge concepts** are those with high betweenness — they sit on many shortest
paths between otherwise distant concepts. Notably CONCEPT_072 (4 roots) and
CONCEPT_036 (8 roots) are small yet bridge heavily: small concepts can be
topological linchpins. The engine flags the top bridges in
`concept_statistics.json → classifications.bridge_concepts`.

---

## 4. Which concepts dominate the core? (eigenvector — hub concepts)

| Rank | Concept | Eigenvector | Size | Center roots (evidence) |
|---|---|---:|---:|---|
| 1 | CONCEPT_039 | 0.566 | 7 | قدد قمص سجن خبز بضع |
| 2 | CONCEPT_021 | 0.424 | 14 | بعر بضع مير رحل جهز |
| 3 | CONCEPT_048 | 0.421 | 6 | غلق هيت قدد قمص حصحص |
| 4 | CONCEPT_089 | 0.409 | 4 | خبز عصر سجن خمر |
| 5 | CONCEPT_076 | 0.332 | 4 | قمص ذاب جبب طرح |

**Observation.** Eigenvector centrality is sharply concentrated: five
small-to-mid concepts (CONCEPT_039/021/048/089/076) form a **mutually
reinforcing cluster** — each is a strong neighbour of the others — and together
they dominate the eigenvector ranking. This is a single dense knot of
inter-linked concepts within the large meta-community, distinct from the
betweenness leaders (which are spread-out bridges). Degree, betweenness, and
eigenvector therefore highlight **three different roles**, as intended.

---

## 5. Isolated concepts

8 concepts have degree 0 — no concept-graph edge above threshold. Examples
(evidence only):

| Concept | Size | Center roots |
|---|---:|---|
| CONCEPT_041 | 7 | فتق رتق فهم نون نفح |
| CONCEPT_043 | 7 | قلع بلع روع حنذ سعد |
| CONCEPT_064 | 5 | وزع بسم عفر نمل هدهد |
| CONCEPT_065 | 5 | سمر نسف زهر سحل عنو |
| CONCEPT_095 | 4 | سند خشب جسم صيح |

Isolated concepts combine **high internal separation** with **near-zero surah
coverage** — tight cliques of roots that co-occur only with one another and
nowhere else in the corpus. They are the topological opposite of the hub and
bridge concepts.

---

## 6. Role summary

| Role | Signal | Top example |
|---|---|---|
| Hub | high eigenvector | CONCEPT_039 |
| Connector | high degree | CONCEPT_039, CONCEPT_002 |
| Bridge | high betweenness, modest degree | CONCEPT_027, CONCEPT_072 |
| Isolated | degree 0 | CONCEPT_041, CONCEPT_064 |

All roles are derived from graph structure alone. No concept is assigned a
meaning, and the member roots are shown solely as evidence of what was
clustered.

---

## 7. Limitations

- Centralities depend on the concept-graph edge definition (§topology report);
  the three measures are stored per node for independent re-analysis.
- Eigenvector concentration on one dense knot is expected when a subgraph is
  near-clique; it indicates structure, not importance-of-meaning.
- Betweenness uses `distance = 1/weight`; an unweighted variant would reorder
  minor ranks but not the broad picture.
