# Concept Topology Report — Phase 3

**Scope.** The topology of the **concept graph** — how the 103 discovered concept
candidates connect to one another. Nodes are concepts; edges measure shared
members and cross semantic overlap. Strictly structural; no concept is named or
interpreted. Reproducible via `scripts/build_concepts.py`.

Data product: `concept_graph.json`, `concept_relationships.json`.

---

## 1. Graph construction

For every pair of concepts (A, B):

```
shared_members   = Jaccard(member_roots(A), member_roots(B))
semantic_overlap = (Σ root-graph edge weights between A-only and B-only roots)
                   / (#A-only roots + #B-only roots),  capped at 1
weight           = 0.5 · shared_members + 0.5 · semantic_overlap
```

Edges below `GRAPH_MIN_EDGE = 0.02` are dropped. The weight blends two
independent signals: overlap of membership (concepts literally sharing roots)
and proximity of behaviour (their distinct roots co-occurring in the Quran).

---

## 2. Global topology

| Measure | Value |
|---|---:|
| Nodes (concepts) | 103 |
| Edges | 329 |
| Graph density | 0.063 |
| Isolated concepts (degree 0) | 8 |
| Meta-communities (label propagation) | 42 |
| Edge weight — min / median / max | 0.020 / 0.081 / 0.667 |

The concept graph is **sparse** (density 0.06): most concepts connect to only a
few others, and 8 are fully isolated. Edge weights are mostly small (median
0.08) with a thin tail of strong links (max 0.67).

---

## 3. Meta-community structure

Deterministic label propagation yields **42 meta-communities** of concepts. Their
size distribution is extremely skewed:

| Meta-community | # concepts |
|---|---:|
| largest | 43 |
| 2nd | 9 |
| 3rd | 3 |
| remaining (≈39) | 1–2 each |

One **dominant meta-community of 43 concepts** absorbs the densely
inter-overlapping concepts; a second holds 9; the rest are isolated pairs or
singletons. The topology is therefore *one large connected mass of mutually
overlapping concepts + a scatter of detached small concepts* — the same
core/periphery shape seen at the lexical layer in Phase 2, now one level up.

---

## 4. Strongest concept-to-concept links (evidence)

Center roots shown as raw evidence only; no interpretation.

| Edge | weight | shared | sem. overlap | A centers · B centers |
|---|---:|---:|---:|---|
| CONCEPT_082 ~ CONCEPT_092 | 0.667 | 0.33 | 1.00 | سهل نحت قصر · سهل نحت فره |
| CONCEPT_039 ~ CONCEPT_048 | 0.650 | 0.30 | 1.00 | قدد قمص سجن · غلق هيت قدد |
| CONCEPT_073 ~ CONCEPT_074 | 0.620 | 0.33 | 0.91 | كتم شري سبط · شري زلل ادي |
| CONCEPT_040 ~ CONCEPT_101 | 0.603 | 0.22 | 0.98 | سردق شوي مهل · رفق سردق كهف |
| CONCEPT_036 ~ CONCEPT_072 | 0.600 | 0.20 | 1.00 | اسن عسل لذذ · شرب ثمر لبن |

The strongest edges pair concepts that share a few members **and** whose
remaining roots are near-maximally co-occurring (semantic_overlap ≈ 1.0). These
are tight neighbouring cliques in the lexical graph that the concept layer keeps
as distinct-but-linked nodes rather than merging — exactly the behaviour the
recursive-split design intends.

---

## 5. Connectivity profile

- **Hub region.** A small set of concepts carries most of the edge mass (see the
  centrality report); the 43-node meta-community is where they sit.
- **Bridges.** A few low-degree concepts have high betweenness, i.e. they lie on
  many shortest paths between otherwise distant concepts (see centrality report).
- **Isolated concepts (8).** Concepts whose member roots co-occur essentially
  only with each other and with nothing in other concepts — fully detached
  cliques. They have high internal separation and near-zero surah coverage.

---

## 6. Limitations

- Edge weight mixes membership overlap (a partly mechanical consequence of
  overlapping clustering) with semantic overlap; the two components are stored
  separately in `concept_graph.json` for independent inspection.
- Meta-communities depend on the (deterministic) label-propagation procedure;
  alternative community methods would redraw boundaries.
- Topology is reported without any claim about what the connected regions mean.
