# Hub Robustness Report — Phase 16 (J)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase16-hub-origin-1.0`.

Phase J repeats the frequency-origin findings under bootstrap so that only robust
results survive.

---

## 1. Bootstrap (200 runs)

The ayahs were resampled with replacement 200 times (`SEED = 20261616`):

| Quantity | Value |
|---|---|
| Bootstrap runs | 200 |
| Hub remains the top concept | **100%** (probability 1.00) |
| Spearman(frequency, degree) — bootstrap mean | ~0.97 |
| Spearman bootstrap CI | tight |

The hub is the top concept in **every** bootstrap, and the frequency→degree
correlation is stable across resamples. The frequency-origin findings are not
sampling artifacts.

---

## 2. Corroboration from prior phases

The frequency-origin conclusion is reinforced by independent robustness results
established earlier:

| Phase | Finding | Bearing on Phase 16 |
|---|---|---|
| 11 | Hub SURVIVES STRONGLY (rank-1 in 1,500 resamples, share CI [0.963, 0.972]) | hub identity is robust |
| 12 | Topology grammar cannot generate the hub (~3.4%) | confirms non-topological origin |
| 13 | Hub present from the first verses under any order | confirms sampling/frequency origin |
| 14 | Hub support ubiquitous (104/114 surahs) | confirms frequency, not localization |

Every prior robustness result is consistent with — and now explained by — the
lexical-frequency origin.

---

## 3. Robust findings

| Finding | Robust? | Evidence |
|---|:--:|---|
| Hub is the highest-frequency concept | **Yes** | rank-1 in 100% of bootstraps |
| Frequency predicts degree | **Yes** | Spearman ~0.97, stable under bootstrap |
| Hub reconstructible from lexical frequency | **Yes** | deterministic (lexical rank-1 = CONCEPT_007) |
| Hub requires the Zipfian lexical tail | **Yes** | uniform-frequency simulation produces no hub |
| Hub generable from frequency, not topology | **Yes** | 0.88 vs 0.034, stable across 20 sim runs |

---

## 4. Verdict

> **The frequency-origin findings are robust.** The hub is the top concept in 100%
> of bootstraps, the frequency→degree correlation is stable, and the
> lexical-reconstruction and frequency-simulation results are deterministic. The
> conclusion — hub dominance is frequency-driven and reduces to the corpus's lexical
> frequency distribution — survives resampling and is corroborated by every prior
> robustness phase.

---

## 5. Reproduce

```bash
python3 scripts/build_hub_origin.py
python3 scripts/validate_hub_origin.py --rebuild
```

Source: `generated/hub_origin/hub_robustness.json`.
