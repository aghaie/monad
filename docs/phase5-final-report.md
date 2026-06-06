# Phase 5 — Final Report: Dependency Compression Engine

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase5-compression-1.0`.

Phase 5 built the **Dependency Compression Engine**. It is **not** an axiom
engine, **not** an ontology engine, **not** a theology engine. Its sole purpose
is to measure whether the Phase-4 proposition structure can be compressed into a
substantially smaller set of foundational structures, and to characterise that
structure. Every output is combinatorial / graph-theoretic. Concept ids and
relation types stay opaque. No meaning, name, translation, interpretation,
ontology, axiom, doctrine, or origin claim is produced. The Quran remains the
only semantic universe; Phases 1–4 are read and hashed but never rebuilt.

---

## 1. Method

A concept set **reconstructs** a relation iff every participating concept is in
the set (binary relations need both endpoints; triadic relations need all
three). Recovered structure = fraction of the 6,832 Phase-4 relations so
covered. From this single rule:

- **A — Foundationality.** Per concept: removal impact, support-weighted loss,
  dependency impact, reach reduction, fragmentation effect, information loss.
  Composite necessity rank (mean of six min-max-normalised metrics).
- **B — Removal experiments.** Remove top-{1,3,5,10,20,30,50} foundational
  concepts; measure proposition / dependency retention, graph integrity,
  connectivity, recoverability.
- **C — Dominant-hub elimination.** Delete `CONCEPT_007`; recompute the induced
  graph, betweenness, bridges, chains, cycles, SCCs.
- **D — Minimum reconstruction sets.** Deterministic greedy maximum-coverage
  for {50,60,70,80,90,95}%.
- **E — Dependency layers.** SCC-condense `DEPENDS_ON ∪ REQUIRES`; longest-path
  structural layering.
- **F — Irreducible structures.** Strongly-connected components (size ≥ 2).
- **G — Compression curve.** Concept count vs recovered structure; AUC; knee.

Deterministic, pure-stdlib, byte-identically reproducible — verified by
`validate_compression.py --rebuild` (all checks pass).

---

## 2. Primary research question

> *Can the proposition graph be reconstructed from a substantially smaller
> subset of concepts? If yes, how small? If no, why not?*

**Answer: only partially. The system is compressible at the margin but not
reducible to a small foundational kernel.**

| Recovered structure | Concepts | Compression ratio |
|---:|---:|---:|
| 50% | 39 | 0.379 |
| 80% | **59** | **0.573** |
| 95% | 76 | 0.738 |

**Why not.** The structure is a dense relational web, not a star. Because every
relation needs *all* its endpoints present, concepts pay off only once their
partners exist — the compression curve is **convex early** (10 concepts recover
< 5%; the knee sits at k ≈ 66, 88%). Seven **irreducible** strongly-connected
cores (largest size 9) place a hard floor under any hierarchy-preserving
reduction. **Compression ratio ≈ 0.57 for 80% of structure.**

---

## 3. Secondary research questions

| Question | Answer |
|---|---|
| Core–periphery structure? | **Yes** — a ~15–20 concept core, long periphery. |
| Multiple independent cores? | **No** — one dominant node + one secondary band. |
| Single dominant core? | **Yes** — `CONCEPT_007`. |
| Hierarchical dependency layers? | **Yes** — 8 levels (0–7), wide base / thin spire. |
| Recursive dependency layers? | **Yes** — 7 irreducible cycles. |
| Irreducible subgraphs? | **Yes** — SCCs up to size 9 (dependency); one 94-node directional SCC. |
| Can a small subset explain most structure? | **No** — 80% needs 57% of concepts. |

---

## 4. Key structural discoveries (no interpretation)

1. **One dominant core.** `CONCEPT_007` scores the normalised maximum on every
   foundationality metric (composite 1.000 vs 0.402 next); it alone is incident
   to 22.2% of relations and is the only single concept that fragments the
   graph.
2. **A foundational band, not an axis.** 15 concepts each destroy ≥ 5% of
   structure alone; 27 sit above mean necessity. Necessity is concentrated but
   distributed across ~15–20 concepts.
3. **The hub masks a secondary core.** Removing `CONCEPT_007` **reorganizes**
   rather than collapses the structure: 77.8% of relations and a 94-node
   component survive; `CONCEPT_016` + a size-9 SCC become the new centre.
4. **Clean hierarchy was hub-induced.** All 4 depth-3 `REQUIRES` chains
   terminated at the hub; without it, 0 remain. Short cycles fall 2,570 → 219.
5. **One large irreducible core, hub-independent.** The 9-concept SCC
   (`003, 004, 034, 053, 060, 061, 084, 085, 088`) is identified independently
   by foundationality, dependency layering, and hub removal; all 7 dependency
   SCCs survive hub removal intact.
6. **Ordering is globally cyclic.** Adding `PRECEDES`/`PREDICTS` collapses the
   directional graph into a single 94-node SCC — no global precedence hierarchy
   exists.

---

## 5. Compression ratios, core size, dominant & irreducible structures

| Metric | Value |
|---|---|
| Compression ratio @ 50% / 80% / 95% | 0.379 / 0.573 / 0.738 |
| Greedy-coverage AUC | 0.612 |
| Knee (greedy) | k = 66 → 88.1% |
| Core-size estimate (≥ 5% impact alone) | 15 concepts |
| Concepts above mean foundationality | 27 |
| Dominant core | `CONCEPT_007` (single) |
| Hub-removal verdict | reorganize (77.8% retained) |
| Irreducible dependency cores (SCC ≥ 2) | 7 (largest size 9) |
| Directional irreducible core | 1 (size 94) |

---

## 6. Outputs

`generated/compression/`:

| File | Contents |
|---|---|
| `foundationality_scores.json` | per-concept necessity metrics + composite rank |
| `reconstruction_sets.json` | greedy minimum sets per recovery threshold |
| `dependency_layers.json` | SCC-condensed structural layers |
| `irreducible_structures.json` | strongly-connected cores (± hub) |
| `compression_statistics.json` | ratios, removal experiments, summary answers |
| `compression_curve.json` | concept-count vs recovered-structure curves, AUC, knee |
| `hub_removal_analysis.json` | `CONCEPT_007` elimination recomputation |
| `compression_manifest.json` | constants, input SHA-256, output bytes, prohibitions |

Tooling: `scripts/build_compression.py` (≈ 0.6 s, pure stdlib),
`scripts/validate_compression.py`. Reports: `foundationality-report.md`,
`compression-analysis-report.md`, `hub-removal-report.md`,
`dependency-layer-report.md`, `irreducibility-report.md`, this report.

---

## 7. Limitations

- **Strict reconstruction.** Full-membership coverage is conservative; partial,
  weighted, or approximate recovery would report higher compressibility. The
  qualitative verdict (not reducible to a small kernel) is robust to this.
- **Greedy ≈ optimum.** Greedy maximum-coverage is a (1−1/e) approximation;
  reported set sizes are deterministic upper bounds on the true minimum.
- **Inherited population.** All analysis runs on the Phase-4 relation set with
  its fixed thresholds and per-ayah activation-union rule. A different relation
  population would redraw every curve.
- **Hub removal is induced-subgraph only.** Statistical relations are not
  re-derived from the corpus after deleting the hub.
- **Composite weighting is uniform**, a deterministic choice; raw per-metric
  columns are published for independent re-ranking.
- **No meaning.** Concept ids and relation types are opaque structural labels
  throughout.

---

## 8. Open questions (for any future phase — not started)

1. A genuine `CONCEPT_007`-masked **re-derivation** of the Phase-4 activation
   matrix (vs the induced-subgraph recomputation done here).
2. Threshold-persistence of the 7 irreducible cores under a Phase-4 threshold
   sweep.
3. Exact (vs greedy) minimum reconstruction sets via ILP for the headline
   thresholds.
4. Whether a partial-recovery reconstruction rule changes the compression-ratio
   floor.

---

## 9. Prohibitions observed

`not an axiom engine · not an ontology engine · not a theology engine · no
concept naming · no concept translation · no interpretation · no inferred
meanings · no ontology · no theology · no axioms · no contradiction engine · no
doctrine · no divine origin claim · no human origin claim · no philosophical
conclusions · no semantic labels · no external knowledge · prior phases never
rebuilt.`

---

## 10. Reproduce

```bash
python3 scripts/build_compression.py
python3 scripts/validate_compression.py --rebuild
```

**Phase 5 complete. No future phase started.**
