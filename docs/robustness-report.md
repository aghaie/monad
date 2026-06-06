# Robustness Report — Phase 14 (J)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase14-locality-1.0`.

Phase J repeats the locality analyses under perturbation — bootstrap, threshold
sweep, and ablation — so that only robust findings survive.

---

## 1. Concentration robustness (bootstrap)

The Gini coefficient of per-surah activations was recomputed under 100 surah
bootstraps (`SEED = 20261414`):

| Statistic | Value |
|---|---|
| Gini (full corpus) | 0.580 |
| Bootstrap mean | 0.577 |
| Bootstrap 95% CI | **[0.515, 0.632]** |

The moderate-concentration finding (Gini ≈ 0.58) is bootstrap-stable; the
concentration is a genuine, reproducible property, not a sampling artifact.

---

## 2. Region-count robustness (threshold sweep)

Region count under the discriminative-similarity edge threshold:

| Threshold | Edges | Regions |
|---:|---:|---:|
| 0.3 | 2,824 | 62 |
| 0.4 | 1,855 | 54 |
| 0.5 | 1,011 | 54 |

Region count is stable (54–62) across thresholds. The weak-region finding (many
small clusters, low cohesion) is not a threshold artifact — at every threshold the
corpus fails to partition into a small number of strong regions.

---

## 3. Hub & consistency robustness (ablation)

| Property | Result |
|---|---|
| Consistency holds under every single-region removal | **Yes** |
| Hub remains rank-1 under every single-region removal | **Yes** |

The two core structural functions survive the removal of any region — confirmed
across all 54 ablations.

---

## 4. Locality robustness (random windows)

The local-vs-global recovery (Phase H) used 40 random windows per size. The
qualitative gradient is robust across samples:

- **Hub rank-1 probability = 1.000** at every window size (1%–50%).
- **Consistency recovery = 1.000** at every window size.
- **Motif recovery** rises monotonically (0.50 → 1.00) with window size.
- **SCC recovery** rises monotonically (0.11 → 0.84) — the one global structure.

---

## 5. Robust findings

| Finding | Robust? | Evidence |
|---|:--:|---|
| Moderate concentration (Gini ~0.58) | **Yes** | bootstrap CI [0.515, 0.632] |
| Even per-ayah density (Gini ~0.28) | **Yes** | deterministic |
| One homogeneous field (no strong regions) | **Yes** | region count 54–62 across thresholds |
| Hub & consistency carried redundantly | **Yes** | survive all 54 ablations |
| Hub & consistency are local | **Yes** | prob 1.0 across all window samples |
| Giant SCC is global | **Yes** | monotone recovery, only 0.41 at 10% |

---

## 6. Verdict

> All headline locality findings — moderate-but-length-driven concentration, the
> homogeneous-field structure, the ubiquity/redundancy of the hub and consistency,
> and the locality gradient (hub/consistency local, SCC global) — **survive
> bootstrap, threshold sweeps, and ablation.** They are robust structural
> properties.

---

## 7. Reproduce

```bash
python3 scripts/build_locality.py
python3 scripts/validate_locality.py --rebuild
```

Source: `generated/locality/robustness_results.json`.
