# Structural Density Report — Phase 14 (A, G)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase14-locality-1.0`.

Phase 14 investigates **where** the discovered structure lives in the corpus and
**how evenly** it is distributed. Nothing is inferred from content; a region is
defined only by measurable structural behaviour. No theology, tafsir, translation,
meaning, chronology, or imported label. All prior phases are read and hashed but
never rebuilt. Deterministic, byte-identically reproducible (`validate_locality.py
--rebuild`, **347 checks pass**).

This report covers Phase A (density mapping) and Phase G (distribution inequality).

---

## 1. Density mapping (Phase A)

Per-surah structural densities were computed (114 surahs) plus sliding 50-ayah
windows. Key per-surah signals: activation density (activations/ayah), concept
density, hub participation, SCC participation, identity recognizability.

| Top surahs by total activation | Activations | Share | Cumulative | Ayahs |
|---|---:|---:|---:|---:|
| 2 | 1,887 | 7.2% | 7.2% | 285 |
| 4 | 1,260 | 4.8% | 11.9% | 176 |
| 3 | 1,185 | 4.5% | 16.4% | 199 |
| 7 | 1,054 | 4.0% | 20.4% | 205 |
| 9 | 908 | 3.4% | 23.9% | 129 |

**Concentration:** **17 surahs (15%) carry 50%** of all activations; **42 surahs
(37%) carry 80%.** No single surah dominates (the largest is 7.2%).

---

## 2. Distribution inequality (Phase G)

| Quantity | Gini | Entropy (bits) | Max entropy | Effective number |
|---|---:|---:|---:|---:|
| Activations (totals) | **0.580** | high | 6.83 (log₂114) | **43.6** |
| Hub support (totals) | ~0.58 | — | — | — |
| Ayahs (surah lengths) | ~0.57 | — | — | — |
| **Activation density (per-ayah)** | **0.275** | — | — | — |

**The decisive finding:** total-activation inequality (Gini 0.58) is **almost
entirely a surah-length effect** — the Gini of surah lengths is ~0.57. When
normalised to **per-ayah density**, the Gini drops to **0.275** — structure is
roughly *even per unit of text*. Big surahs carry more structure because they
contain more verses, not because they are structurally denser.

- **Effective number of regions ≈ 43.6** (participation ratio of activations) — out
  of 114 surahs, structure is effectively spread across ~44, not concentrated in a
  handful.

---

## 3. Answering the questions

| Question | Answer |
|---|---|
| Is structure uniformly distributed? | **No** by totals (Gini 0.58); **roughly yes** by per-ayah density (Gini 0.28) |
| Does a minority carry a majority? | **Yes** — 15% of surahs carry 50%, 37% carry 80% (a length effect) |
| Where is structure concentrated? | in the long surahs (2, 3, 4, 7, 9 …) — by volume, not density |
| Where is structure sparse? | the short surahs — fewer verses, similar per-ayah density |

---

## 4. Robustness (Phase J)

Gini of activations is bootstrap-stable: **0.577 [0.515, 0.632]** (100 surah
bootstraps). The concentration finding survives resampling.

---

## 5. Verdict

> Structure is **moderately concentrated by volume (Gini 0.58) but roughly even by
> per-ayah density (Gini 0.275)**. The concentration is a length effect, not a
> structural specialisation: every verse carries comparable structure; longer
> surahs simply contain more verses.

---

## 6. Reproduce

```bash
python3 scripts/build_locality.py
python3 scripts/validate_locality.py --rebuild
```

Source: `generated/locality/density_maps.json`, `inequality_metrics.json`.
