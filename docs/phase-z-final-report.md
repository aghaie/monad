# Phase Z — Final Report: Quran Self-Method Discovery Engine (Falsification Study)

**Method version:** `self-methodology-1.0` · **Date:** 2026-06-07 · **Verdict:** `PARTIAL`
(weak — bordering NO). Deterministic, byte-identical (`validate_self_methodology.py
--rebuild`). Rebuilt from the corpus only; **no Phase-Q or Phase-X output was read**;
their conclusions were treated as hypotheses.

## 1. Objective

Test — not confirm — whether the Quran describes within itself a **stable internal method**
for reaching knowledge, and whether that conclusion survives the rigorous controls Phases Q
and X never applied (frequency, surah-length, and mushaf-order nulls; bootstrap;
subsampling). The phase may not say "the Quran is true," "from God," or "the method is
correct." It may only answer: does the Quran describe a specific, stable method for reaching
knowledge — **YES / NO / PARTIAL** — with statistical evidence.

## 2. Method (summary)

16 epistemic nodes (the spec's vocabulary, mapped to corpus roots) → directed graph from
within-ayah word order + cross-ayah adjacency → 85 candidate edges (support ≥ 8). Each edge
faced: a **frequency** configuration null (exists beyond marginals?), a **mushaf-order** null
(directional beyond text order?), a **surah-length** split (length-stable?), a **bootstrap**
(direction CI excludes 0.5?), and a **subsampling** battery (persists ≥ 90%?). A *full
survivor* passes all. The verdict is computed from pre-registered thresholds (NO if < 10% of
edges exist beyond frequency; YES if ≥ 50% are directionally robust **and** a ≥ 6-node
connected backbone survives; PARTIAL otherwise).

## 3. Results

| metric | value |
|---|--:|
| ayahs containing method vocabulary | 2,678 (≈ 43% of corpus) |
| candidate edges (support ≥ 8) | 85 |
| exist beyond the **frequency** null | **10 / 85 (11.8%)** |
| directional beyond the **order** null | 15 / 85 |
| directionally **stable** (bootstrap+subsample) | 10 / 85 |
| **full survivors (all controls)** | **2 / 85** — `ask → knowledge`, `observe → misguidance` |
| largest connected survivor backbone | **2 nodes** (no chain, no cycle) |

Raw graph (pre-control) net-outflow: sources observe/read/listen/ask; deepest sink
knowledge (−79) — i.e. the raw data **reproduces the Q/X pipeline**.

## 4. The verdict

# `PARTIAL` (weak — bordering NO)

Pre-registered logic: existence-survivor fraction = 0.118 is just above the NO cutoff (0.10),
so **not NO**; directionality-survivor fraction = 0.082 (≪ 0.50) with a 2-node backbone, so
**not YES** → **PARTIAL**.

**What PARTIAL means here, precisely:** a *small minority* of the Quran's epistemic
associations are real beyond word frequency (≈ 12%), and **two** directional regularities
survive every control — so it is not *nothing* (not NO). But the **directional method /
pipeline** that Phases Q and X reported **does not survive**: 88% of associations are
frequency artifacts, the sequence dissolves under order-shuffling, and the two survivors are
isolated (`ask → knowledge`, `observe → misguidance`) and form no connected method. The
Quran has a real *epistemic vocabulary field* but, under controls, **not a stable directional
method.**

## 5. Explicit comparison with Phases Q, X, and P

| | Claim | Controls applied | Phase Z verdict on it |
|---|---|---|---|
| **Q** (methodology-1.0) | integrative method (observe signs → reason → remember) | raw token counts; **no** frequency/order/length nulls | **not supported as a controlled structure** — the vocabulary is real but ≈ 88% of its associations are frequency artifacts |
| **X** (epistemology-1.0) | directed pipeline (perceive → reflect → know → certainty); perception bivalent | reverse-sequence + Meccan/Medinan split only; **no** frequency/length/mushaf-order nulls | **directionality does not survive** the order null; only 2 isolated edges remain. The bivalent-perception finding **is** echoed — the surviving perception edge is `observe → misguidance` |
| **P** (predictivity-1.0) | the structure is real but **non-predictive** beyond frequency; directional (S2) model weakest | held-out prediction, frequency null | **Phase Z is fully consistent with P** — the directional method is both non-predictive (P) and non-robust to nulls (Z) |

Phase Z is the controlled re-test that Q and X lacked, and it **converges with Phase P**:
the discovered epistemic structure is real in a thin residue but is overwhelmingly frequency-
and order-driven; the "Quran describes its own method" conclusion **does not survive rigorous
controls** as a directional method — it survives only as (a) a real vocabulary field and (b)
two isolated directional regularities.

## 6. Interpretation

What does *survive* is worth stating exactly, without inflation:
- **`ask → knowledge`** (سؤال precedes علم): asking robustly precedes knowing — a single
  genuine methodological regularity.
- **`observe → misguidance`** (نظر/بصر precedes ضلال): the one surviving perception edge
  points to *misguidance*, not knowledge — anti-confirmatory for a clean method and
  consistent with Phase X's structural finding that perception is bivalent.

Two isolated edges are not a method. The dense "pipeline" and "cycle" structures of the raw
graph are artifacts of orienting frequency-driven co-occurrences; they vanish under controls
(no surviving cycle; backbone of 2).

## 7. What Phase Z does NOT claim

It does not say the Quran is true, divine, or its method correct. It says only: **subjected
to frequency, surah-length, and mushaf-order nulls plus bootstrap and subsampling, the
Quran's own text does not robustly encode a connected, directional method for reaching
knowledge** — only a real vocabulary field and two isolated directional regularities. The
strong "internal methodology" reading of Phases Q and X is, under controls, **not supported**.

## 8. Limitations

- Node vocabulary is the spec's 16-node list; which 2 edges survive could shift with a
  different vocabulary, but the collapse pattern (≈ 12% existence, 2 full survivors) is the
  result.
- Nulls are node-level / median-split; stronger (root-level, syntactic) nulls would be
  stricter, not more lenient.
- "Method" is operationalised as directional regularities among epistemic nodes; a method
  expressed through structures outside this vocabulary is not tested.

## 9. Conclusion

**`PARTIAL`, leaning NO.** The Quran contains a real epistemic-vocabulary field and two
isolated directional regularities (`ask → knowledge`, `observe → misguidance`), but the
**stable, connected, directional method** asserted by Phases Q and X **does not survive**
frequency, order, and length controls. Consistent with Phase P, the structure is real only
in a thin residue and is overwhelmingly frequency- and order-driven. The Quran does not, by
this controlled test, describe a robust internal method for reaching knowledge.

---

### Outputs
`generated/self_methodology/`: 8 data products + `methodology_manifest.json`. Tooling:
`scripts/build_self_methodology.py`, `scripts/validate_self_methodology.py`. Reports:
`methodology-discovery-report.md`, `methodology-chain-report.md`,
`methodology-obstacle-report.md`, `methodology-outcome-report.md`,
`methodology-cycle-report.md`, `methodology-stability-report.md`,
`self-methodology-falsification-report.md`, this report.

### Reproduce
```bash
python3 scripts/build_self_methodology.py
python3 scripts/validate_self_methodology.py --rebuild
```

**Phase Z complete. No further phase started automatically.**
