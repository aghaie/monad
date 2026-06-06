# Foundationality Report — Phase 5 (A)

**Date:** 2026-06-06. **Method version:** `phase5-compression-1.0`. **Status:**
complete.

Phase 5 (A) ranks every Phase-3 concept by **structural necessity** to the
Phase-4 proposition structure — *what happens to the discovered structure if
this concept disappears*. Every quantity is combinatorial / graph-theoretic.
Concept ids stay opaque (`CONCEPT_001…`). No meaning, name, translation, or
interpretation is assigned. The Quran remains the only semantic universe; prior
phases are read but never rebuilt.

---

## 1. Population

| Quantity | Value |
|---|---:|
| Concepts | 103 |
| Relations (full Phase-4 population) | 6,832 |
| Dependency relations (`DEPENDS_ON ∪ REQUIRES`) | 284 |
| Directed proposition-graph edges | 1,474 |
| Total relation incidence (Σ members) | (see `foundationality_scores.json`) |
| Baseline undirected components / largest | 4 / 100 |
| Baseline graph entropy | 5.760 bits |
| Baseline reachable ordered pairs (directed) | 9,306 |

A relation is **destroyed** when any participating concept is removed (binary
relations need both endpoints; triadic `MEDIATES` / `CONDITIONAL_EMERGES` need
all three). This single set-membership rule defines every removal metric.

---

## 2. Metrics (per concept)

| Metric | Definition |
|---|---|
| `removal_impact_count` | relations destroyed if the concept is removed |
| `support_weighted_loss` | summed Phase-4 `support_count` of destroyed relations |
| `dependency_impact` | incident `DEPENDS_ON + REQUIRES` relations |
| `reach_reduction` | lost reachable ordered pairs among surviving nodes in the directed graph |
| `fragmentation_components_added` | increase in undirected component count on deletion |
| `information_loss_bits` | frequency-code bits carried by the concept = `inc · −log₂(inc/total)` |

Composite structural-necessity score = mean of the six metrics after per-metric
min-max normalisation to `[0,1]`. Higher = more necessary. Ties broken by
concept id.

---

## 3. Leaderboard (top 12 of 103)

| Rank | Concept | Composite | Relations destroyed | (frac) | Dep. impact | Reach reduction | Frag. | Info bits |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | `CONCEPT_007` | **1.000** | 1,519 | 22.2% | 96 | 741 | +5 | 5,378 |
| 2 | `CONCEPT_081` | 0.402 | 1,112 | 16.3% | 5 | 98 | 0 | 4,437 |
| 3 | `CONCEPT_004` | 0.314 | 788 | 11.5% | 31 | 0 | 0 | 3,536 |
| 4 | `CONCEPT_003` | 0.284 | 717 | 10.5% | 9 | 0 | 0 | 3,315 |
| 5 | `CONCEPT_088` | 0.258 | 553 | 8.1% | 15 | 0 | 0 | 2,764 |
| 6 | `CONCEPT_016` | 0.252 | 566 | 8.3% | 12 | 98 | 0 | 2,810 |
| 7 | `CONCEPT_053` | 0.251 | 605 | 8.9% | 9 | 0 | 0 | 2,945 |
| 8 | `CONCEPT_002` | 0.237 | 604 | 8.8% | 17 | 0 | 0 | 2,942 |
| 9 | `CONCEPT_085` | 0.237 | 540 | 7.9% | 16 | 0 | 0 | 2,718 |
| 10 | `CONCEPT_034` | 0.226 | 520 | 7.6% | 13 | 0 | 0 | 2,645 |
| 11 | `CONCEPT_061` | 0.222 | 496 | 7.3% | 12 | 0 | 0 | 2,557 |
| 12 | `CONCEPT_084` | 0.196 | 460 | 6.7% | 9 | 0 | 0 | 2,421 |

Full table: `generated/compression/foundationality_scores.json`.

---

## 4. Structural findings (no interpretation)

1. **A single concept dominates necessity.** `CONCEPT_007` scores the
   normalised maximum on every component metric: composite **1.000** versus
   0.402 for the second-ranked concept — a 2.5× gap. Removing it alone destroys
   **22.2%** of all relations.
2. **It is the only fragmenting node.** `CONCEPT_007` is the sole concept whose
   removal raises the connected-component count (+5). No other single concept
   fragments the undirected projection at all. Its `reach_reduction` (741) is
   7.6× the next value (98). Structural connectivity is concentrated in one node.
3. **The necessity distribution is heavy-tailed but not a single spike.**
   Below the dominant node, a band of ~10 concepts (`CONCEPT_004 / 003 / 088 /
   016 / 053 / 002 / 085 / 034 / 061 / 084`) each destroy 6.7–11.5% of
   structure. **15** concepts destroy ≥ 5% alone; **27** sit above mean
   composite score.
4. **Two distinct roles among high scorers.** `CONCEPT_081` ranks #2 by raw
   relations-destroyed (1,112) yet carries almost no dependency edges
   (`dependency_impact = 5`) — it is a high-frequency co-activator, not a
   dependency target. By contrast `CONCEPT_004` (dep 31) and `CONCEPT_002`
   (dep 17) carry the dependency load. Necessity is multi-dimensional.

---

## 5. Limitations

- **Reconstruction = full set membership.** A relation is recoverable from a
  concept set only if *every* participating concept is retained. This is a
  strict, conservative definition; a looser one (e.g. approximate / partial
  recovery) would raise apparent compressibility.
- **Composite weighting is uniform.** Equal weights on six normalised metrics
  is a deterministic choice, not a derived optimum. The raw per-metric columns
  are published so any reader can re-rank.
- **Directed-graph metrics use the Phase-4 projection** (`proposition_graph`
  edges), inheriting its activation-union and threshold choices.
- **Information-loss uses a frequency code**, monotone in incidence by
  construction; it is a description-length proxy, not an inference.
- **No meaning.** All ids and relation types remain opaque structural labels.

---

## 6. Reproduce

```bash
python3 scripts/build_compression.py
python3 scripts/validate_compression.py --rebuild
```
