# Motif Discovery Report — Phase 9

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase9-motifs-1.0`.

Phase 9 built the **Structural Motif Discovery Engine**. Its purpose is to test —
never assume — whether the Quranic relational network is organised around
recurring *structural motifs*: recurring directed subgraph patterns. The goal is
not concepts, not principles, not meanings — only recurring relational structures.
Motifs carry opaque ids `MOTIF_001…`; none is named, translated, or interpreted.
A neutral *structural descriptor* (graph-theoretic, e.g. "triad:path:chain") is
attached as classification, never as meaning. No theology, doctrine, ontology,
apologetics, intention, authorship, or origin claim is produced; significance is
never asserted without evidence. Phases 1–8 are read and hashed but never rebuilt.

---

## 1. Method

Motifs are **isomorphism classes of small connected directed subgraphs** over the
Phase-4 proposition graph (the discovered relational network, 100 connected nodes,
1,059 directed pairs), collapsed to a simple directed graph (A→B iff any directed
relation A→B exists; symmetric relations such as `ASSOCIATES_WITH` yield mutual
edges). Two sizes are catalogued:

- **dyads (2 nodes):** mutual (A↔B), asymmetric (A→B).
- **triads (3 nodes):** the connected directed 3-node classes, classified by a
  canonical minimum-permutation adjacency code.

Per motif: frequency, structural signature, stability (deterministic
edge-subsampling perturbation), significance (z-score vs a fixed-seed
degree-preserving directed null, 20 samples), participating concepts /
propositions / principles, example instances. Deterministic, pure-stdlib,
byte-identically reproducible (`validate_motifs.py --rebuild`, **299 checks
pass**).

---

## 2. Result: recurring motifs exist — 15 classes

**Do recurring structural motifs exist? Yes.** The 17,345 connected triads of the
network fall into exactly the **13 canonical directed triad classes**; with the 2
dyad classes, **15 motifs** are catalogued. The distribution is highly
concentrated — a handful of patterns dominate.

| Motif | Size | Structural descriptor | Freq | % triads | z-score | Stability | Hub | Survives |
|---|---:|---|---:|---:|---:|---:|:--:|:--:|
| `MOTIF_001` | 3 | path : mutual | 4,092 | 23.6% | +9.6 | 1.00 | weakened | ✗ |
| `MOTIF_002` | 3 | path : in-merge | 3,315 | 19.1% | +5.7 | 1.19 | survives | ✓ |
| `MOTIF_003` | 3 | path : in-merge | 3,127 | 18.0% | −5.1 | 1.12 | survives | ✓ |
| `MOTIF_004` | 3 | path : chain | 2,253 | 13.0% | −11.3 | 1.25 | survives | ✓ |
| `MOTIF_005` | 3 | path : out-fork | 1,930 | 11.1% | +9.2 | 1.32 | survives | ✓ |
| `MOTIF_006` | 3 | path : out-fork | 863 | 5.0% | −11.0 | 1.20 | survives | ✓ |
| `MOTIF_007` | 3 | triangle : cyclic-mixed | 675 | 3.9% | −8.0 | 1.28 | weakened | ✗ |
| `MOTIF_008` | 2 | dyad : asymmetric | 411 | — | — | — | — | ✓ |
| `MOTIF_009` | 3 | triangle : fully-mutual | 387 | 2.2% | **+29.2** | 0.91 | weakened | ✗ |
| `MOTIF_010` | 2 | dyad : mutual | 324 | — | — | — | — | ✓ |
| `MOTIF_011` | 3 | triangle : transitive | 249 | 1.4% | +4.4 | 1.25 | survives | ✓ |
| `MOTIF_012` | 3 | triangle : transitive | 240 | 1.4% | −3.3 | 1.33 | survives | ✓ |
| `MOTIF_013` | 3 | triangle : cyclic-mixed | 125 | 0.7% | −11.9 | 1.85 | survives | ✓ |
| `MOTIF_014` | 3 | triangle : transitive | 86 | 0.5% | −15.0 | 1.78 | survives | ✗ |
| `MOTIF_015` | 3 | triangle : 3-cycle | 3 | 0.0% | −7.5 | 2.00 | survives | ✗ |

("path" = open triad / 2 adjacent pairs; "triangle" = closed / 3 adjacent pairs.
Descriptors are structural classifications, not names.)

---

## 3. Which motifs are most common / most significant

- **Most common:** `MOTIF_001` (mutual-path, 23.6%), `MOTIF_002`/`MOTIF_003`
  (in-merge / convergence, 19.1% + 18.0%), `MOTIF_004` (chain, 13.0%),
  `MOTIF_005` (out-fork / divergence, 11.1%). **Five motifs carry ~85% of all
  triads.**
- **Most over-represented vs random** (positive z): the **fully-mutual triangle**
  `MOTIF_009` (z = +29.2), the **mutual-path** `MOTIF_001` (+9.6), the **out-fork**
  `MOTIF_005` (+9.2), the **in-merge** `MOTIF_002` (+5.7), transitive triangle
  `MOTIF_011` (+4.4). Reciprocity and convergence recur **far more than chance**.
- **Under-represented vs random** (negative z): chains (`MOTIF_004`, −11.3),
  certain forks and cyclic triangles. Open directed chains are *less* common than
  a degree-preserving null predicts.

The over-representation of mutual and convergent structures, and
under-representation of long directed chains, is genuine network-motif evidence —
the network is locally reciprocal and convergent, not chain-like.

---

## 4. Most stable motifs

Under edge-subsampling perturbation, every triad motif retains at least as many
instances as an independent-edge model predicts (stability ≥ 0.91; most > 1.2,
indicating clustered robustness). The rarer triangle motifs (`MOTIF_013/014/015`)
score highest (1.8–2.0) — when present they are perturbation-robust — but they are
infrequent. The frequent path motifs are stable at 1.0–1.3.

---

## 5. Outputs

`generated/motifs/`: `motif_catalog.json`, `motif_statistics.json`,
`motif_coverage.json`, `motif_compression.json`, `motif_replacement.json`,
`motif_survival.json`, `motif_scc_analysis.json`, `motif_falsification.json`,
`motif_manifest.json`.

Tooling: `scripts/build_motifs.py` (≈ 2 s, pure stdlib),
`scripts/validate_motifs.py` (299 checks, `--rebuild` byte-identical). Reports:
this one, `motif-coverage-report.md`, `motif-compression-report.md`,
`motif-survival-report.md`, `motif-falsification-report.md`,
`phase9-final-report.md`.

---

## 6. Limitations

- Motifs are dyad/triad classes over the Phase-4 directed proposition graph;
  4-node motifs and typed-edge motifs are out of scope (open questions).
- The null model preserves in/out degree but not the dyad (reciprocity) census;
  z-scores are indicative, not definitive. Stability and the
  observed-frequency findings do not depend on the null.
- "Motif" is a graph isomorphism class; the structural descriptor is not a
  meaning.

---

## 7. Prohibitions observed

`no meanings · no motif names · no translation · no theology · no doctrine · no
ontology · no apologetics · no divine origin · no human origin · no intention · no
authorship · no significance without evidence · motifs are opaque structural
patterns only · prior phases never rebuilt.`

---

## 8. Reproduce

```bash
python3 scripts/build_motifs.py
python3 scripts/validate_motifs.py --rebuild
```
