# Motif Coverage Report — Phase 9 (C, G)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase9-motifs-1.0`.

How pervasive are the discovered motifs? Phase C measures the share of concepts,
propositions, dependencies, and principles each motif touches; Phase G measures
motif persistence inside the irreducible SCCs. Structural counts only; no meaning.

---

## 1. Phase C — coverage per motif (pervasiveness)

The frequent path motifs span almost the entire network:

| Motif | Descriptor | Concept cov. | Proposition cov. | Dependency cov. | Principle cov. |
|---|---|---:|---:|---:|---:|
| `MOTIF_002` | in-merge | 96.1% | 94.3% | 93.0% | 93.8% |
| `MOTIF_005` | out-fork | 91.3% | 92.9% | 95.4% | 93.8% |
| `MOTIF_001` | mutual-path | 88.3% | 60.6% | 85.2% | 93.8% |
| `MOTIF_004` | chain | high | high | high | 93.8% |
| `MOTIF_003` | in-merge | high | high | high | 93.8% |

The top five triad motifs each touch **88–96% of concepts**, **60–94% of
propositions**, **85–95% of dependencies**, and **15 of 16 principles (93.8%)**.
Motifs are not localised features — they recur across essentially the whole
network. Collectively the motifs touch **100% of the connected concepts**.

**Answer — how pervasive are motifs?** Maximally: a single motif class
(`MOTIF_002`, convergence) already appears among 96% of concepts and 94% of
propositions. The motif vocabulary is woven through the entire structure.

---

## 2. Phase G — SCC persistence

Restricting the triad census to the irreducible SCC node sets discovered in
Phases 5 and 8:

| SCC scope | Size | Connected triads | Triad classes present |
|---|---:|---:|---:|
| Largest concept dependency SCC (Phase 5) | 9 | 33 | **5 / 13** |
| Directional SCC (Phase 5) | 94 | 16,725 | **13 / 13** |
| Principle SCC concepts (Phase 8) | 61 | 6,552 | **13 / 13** |

- The **94-node directional SCC contains 16,725 of the 17,345 triads (96.4%)** in
  **all 13 classes** — the motif vocabulary lives almost entirely inside the
  globally-cyclic core.
- The **61 concepts of the size-11 principle SCC** also realise **all 13 classes**
  (6,552 triads) — motifs persist fully through the principle-level irreducible
  structure.
- Even the tight **size-9 concept core** realises **5 of the 13 classes** in just
  33 triads — the dominant path/convergence motifs are present even there.

**Answer — do motifs survive SCC decomposition? Yes.** Every motif class that
matters recurs inside the large irreducible SCCs; motifs are an intrinsic property
of the irreducible core, not an artefact of the periphery.

---

## 3. Coverage vs Phase-8 principles

| | Phase 8 principles | Phase 9 motifs |
|---|---|---|
| Unit | structural module (partition block) | recurring subgraph pattern |
| Self-contained structure | **9.9%** (internal ceiling) | n/a (motifs are patterns, not containers) |
| Pervasiveness | each module holds ≤ 12.6% of concepts | each top motif touches ≥ 88% of concepts |
| Presence in irreducible core | split across 5 modules | all 13 classes present |

Where principles *partitioned* the network and left 90% of structure between
blocks, motifs *describe* the connection patterns that fill that between-block
space — and a handful of them cover almost everything (see
`motif-compression-report.md`).

---

## 4. Limitations

- Coverage counts a concept/edge as "touched" if it participates in ≥ 1 instance
  of the motif; it does not weight by instance count.
- Dependency coverage uses `DEPENDS_ON ∪ REQUIRES` edges only.

---

## 5. Reproduce

```bash
python3 scripts/build_motifs.py
python3 scripts/validate_motifs.py --rebuild
```
