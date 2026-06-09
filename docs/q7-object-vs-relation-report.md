# Q7 — Object vs Relation Priority Report (Phase ΩΣ)

**Method:** `foundational-questions-1.0` · corpus-only · deterministic.

## 1. Objective
Does the Quran allocate more information to **entities** (objects) or to **relations**?

## 2. Method
Two structural views: (a) token mass by POS class — object/entity nominal (N, PN, PRON, DEM, ADJ) vs
relational/structural (V, P, REL, CONJ, SUB, COND, ACC, LOC, T); (b) co-occurrence graph density —
nodes (distinct roots) vs edges (distinct co-occurring root pairs).

## 3. Results
| measure | value |
|---|--:|
| object tokens | 35,368 (48.7%) |
| relation tokens | 37,217 (51.3%) |
| graph nodes (roots) | 1,642 |
| graph edges (pairs) | 74,185 |
| edges per node | **45.2** |

## 4. Interpretation
Relations dominate **both** the surface (51.3% of token mass) and the structure (a strongly edge-dense graph,
45 edges per node). Entities are not the organizing principle; the text is relationally saturated — most
information lives in how roots co-occur, not in the roots themselves.

## 5. Falsification Attempts
Token mass is an exact census. The edge density is far above any tree-like (1 edge/node) baseline; the
co-occurrence structure beyond frequency was separately confirmed (coherence-beyond-null, Phase 17 / Q9).

## 6. Limitations
POS-class assignment to object/relation is a defensible but not unique partition; verbs are counted as
relational. The edge-density conclusion is robust to this choice.

## 7. Conclusion
**RELATIONS are more fundamental** — more token mass (51%) and a strongly edge-dense graph (45 edges/node).
Objects dominate neither the surface nor the structure.
