# Validation Overview Report — Phase 11

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase11-validation-1.0`.

Phase 11 is a **validation phase**, not a discovery phase. It discovers nothing.
It attempts to **destroy** the prior discoveries through systematic methodological
perturbation and reports only what survives. The burden of proof is reversed:
every discovery is assumed fragile until proven robust; failures are documented,
never hidden; prior conclusions are not protected. No new concept, principle,
motif, identity, or theory is created; no result is reinterpreted; no run is
cherry-picked. Every perturbation regime is fixed-seed deterministic
(`SEED = 20261111`) and byte-identically reproducible (`validate_validation.py
--rebuild`, **112 checks pass**).

---

## 1. Method

Most downstream findings derive from one per-ayah concept-activation matrix M
(reconstructed by the exact Phase-4/6 rule; **6,101 active ayahs**). M is resampled
(subsampling, bootstrap) and the affected statistics recomputed. The concept
partition is re-derived by **5 alternative clustering families** (ARI/NMI). The
proposition graph is **noise-injected** (edge removal / degree-preserving
rewiring) and its motif census, hub degree, and largest SCC recomputed.
Thresholds are swept low/medium/high/extreme. Reproducibility is audited by
rebuilding 7 engines to temp dirs and hashing against canonical.

| Phase | Test | Scale |
|---|---|---|
| A | threshold sweeps | 3 thresholds × 4 levels |
| B | concept-discovery stability | 5 clustering families, ARI/NMI |
| C | subsampling | 5 levels × 100 = 500 resamples |
| D | bootstrap | 1,000 runs |
| E/G | noise injection + motif validation | 5 regimes × 20 trials |
| F | hub validation | aggregate of C/D/E |
| H | consistency validation | sweeps + bootstrap |
| I | reproducibility audit | 7 engines rebuilt to temp |
| J | survivor analysis | 8 discoveries classified |

---

## 2. Headline result

| Discovery | Verdict | Key statistic |
|---|---|---|
| **CONCEPT_007 dominance** | **SURVIVES STRONGLY** | top-1 prob **1.000** (1000 bootstraps + 500 subsamples); share CI [0.963, 0.972] |
| **Phase-9 motif vocabulary** | **SURVIVES STRONGLY** | 13 classes at every noise level; 5-motifs-for-80% invariant |
| **Phase-10 consistency** | **SURVIVES STRONGLY** | 0 contradictions under every regime; exclusion/positive overlap 0 at all thresholds |
| **Phase-5 compression** | **SURVIVES STRONGLY** | byte-identical reproducible; threshold-robust qualitative verdict |
| **Size-9 irreducible SCC** | **SURVIVES MODERATELY** | a large SCC (~92) persists under 20% edge perturbation |
| **Phase-7 identity anchors** | **SURVIVES MODERATELY** | top-10 concept Jaccard 0.92 under bootstrap |
| **103-concept structure** | **SURVIVES WEAKLY** | NMI 0.74 (shared structure) but ARI 0.22 (method-sensitive boundaries) |
| **Phase-8 principle structure** | **SURVIVES WEAKLY** | 90%-inter-module verdict robust; exact 16 modules not |

**Tally: 4 SURVIVES STRONGLY · 2 SURVIVES MODERATELY · 2 SURVIVES WEAKLY · 0 FAILS.**

No discovery failed outright, but **two findings (the exact 103-concept partition
and the 16-principle decomposition) are method-sensitive** and must be used with
caution in any future phase.

---

## 3. Reproducibility

All **7 `--out`-capable engines** (concepts, propositions, identification,
revelation, principles, motifs, consistency) rebuild **byte-identically** to temp
dirs. Compression (no `--out` flag) is covered by its dedicated Phase-5 validator.
The pipeline is deterministic; the only seeded component (Phase-9 significance
z-scores) is seed-robust in its qualitative signs.

---

## 4. What earned its place

- **Use freely:** CONCEPT_007 dominance, Phase-5 compression, Phase-9 motif
  vocabulary, Phase-10 consistency.
- **Use with caution:** size-9 SCC, Phase-7 identity anchors, 103-concept
  structure, Phase-8 principles.
- **Do not rely on:** (none — but the exact concept/principle *boundaries* are
  fragile even where the *existence* of structure is not).

---

## 5. Outputs

`generated/validation/`: `threshold_sweeps.json`, `bootstrap_results.json`,
`subsampling_results.json`, `noise_results.json`, `hub_validation.json`,
`motif_validation.json`, `consistency_validation.json`,
`reproducibility_audit.json`, `survivor_analysis.json`, `validation_manifest.json`.
Tooling: `scripts/build_validation.py`, `scripts/validate_validation.py`. Reports:
this one plus nine companions (threshold-sweep, bootstrap, subsampling,
hub-validation, motif-validation, consistency-validation, reproducibility,
survivor-analysis, phase11-final).

---

## 6. Reproduce

```bash
python3 scripts/build_validation.py
python3 scripts/validate_validation.py --rebuild
```
