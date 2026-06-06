# Phase 11 — Final Report: Discovery Stability & Robustness Engine

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase11-validation-1.0`.

Phase 11 is a **validation** phase. It discovered nothing. It attempted to
**destroy** the prior discoveries through systematic methodological perturbation
and reports only what survived. The burden of proof was reversed: every discovery
was assumed fragile until proven robust; failures are documented, not hidden;
prior conclusions were not protected. No new concept, principle, motif, identity,
or theory was created; no result was reinterpreted; no run was cherry-picked.
Every regime is fixed-seed deterministic and byte-identically reproducible
(`validate_validation.py --rebuild`, **112 checks pass**).

---

## 1. Method

The per-ayah concept-activation matrix M (6,101 active ayahs, reconstructed by the
exact Phase-4/6 rule) was resampled (1,000 bootstraps; 500 subsamples at
5–40% removal). The concept partition was re-derived by 5 alternative clustering
families (ARI/NMI). The proposition graph was noise-injected (edge removal /
degree-preserving rewiring). Every major threshold was swept low→extreme.
Reproducibility was audited by rebuilding 7 engines to temp dirs and hashing.
Statistics are reported as means / medians / std / 95% CIs — never point estimates
alone.

---

## 2. Primary research question

> *Which discoveries survive systematic methodological perturbation?*

**Answer:** 4 of 8 major discoveries survive **strongly** (invariant under all
perturbation), 2 survive **moderately**, 2 survive **weakly** (real structure,
method-sensitive specifics), and **0 fail**. The robust findings are the hub, the
consistency, the compression verdict, and the motif vocabulary. The fragile
specifics are the **exact 103-concept partition** and the **exact 16-principle
decomposition**.

---

## 3. Surviving discoveries

| Discovery | Verdict | Evidence |
|---|---|---|
| CONCEPT_007 dominance | **STRONG** | rank-1 in 1,500/1,500 resamples; share CI [0.963, 0.972]; max-degree at all thresholds |
| Phase-10 consistency | **STRONG** | 0 contradictions under all regimes; exclusion/positive overlap 0 at all thresholds |
| Phase-9 motif vocabulary | **STRONG** | 13 classes + 5-for-80% invariant under all noise; giant SCC persists |
| Phase-5 compression | **STRONG** | byte-identical; threshold-robust verdict |
| Size-9 irreducible SCC | **MODERATE** | large SCC (~92) persists under 20% edge perturbation |
| Phase-7 identity anchors | **MODERATE** | top-10 concept Jaccard 0.92 under bootstrap |

## 4. Failed / fragile discoveries

| Discovery | Verdict | Why fragile |
|---|---|---|
| 103-concept structure | **WEAK** | NMI 0.74 (shared structure) but ARI 0.22; cluster counts 38–471 across methods; threshold-sensitive (giant blob → 141 components) |
| Phase-8 principle structure | **WEAK** | modularity modules method/resolution-dependent; verdict robust, exact 16 modules not |
| (dominant motif `MOTIF_001`) | **fragile sub-finding** | #1 ranking flips under 10% noise (hub-driven; already caveated in Phase 9) |

**No discovery failed outright (0 FAILS),** but the *exact counts and boundaries*
of the concept and principle partitions are method-relative, not absolute facts.

---

## 5. Stability rankings, CIs, robustness

- **Most robust:** CONCEPT_007 dominance (share std 0.0023, rank-1 prob 1.000).
- **Consistency:** 0 contradictions across 800-fold threshold variation + 1,700
  resamples.
- **Motif vocabulary:** 13/13 classes at every noise level; 5-for-80% invariant.
- **Identity anchors:** top-10 Jaccard 0.92 (strong-tier robust; weak-tier not).
- **Least robust:** exact concept/principle partition (ARI ~0.22).

## 6. Reproducibility

7/7 `--out`-capable engines rebuild **byte-identically** to temp dirs;
`build_validation` is itself deterministic; the pipeline is effectively seed-free
(one seeded component, seed-robust in conclusions). Compression covered by its
Phase-5 validator.

---

## 7. Methodological risks (documented)

1. **Concept/principle counts are method artifacts.** The "103 concepts" and "16
   principles" are specific cuts of a real but boundary-ambiguous similarity
   structure. Future phases must not treat the exact counts as canonical.
2. **Hub-leaning findings inherit the hub.** The dominant motif, the strongest
   reciprocal triangle, and the clean Phase-4 hierarchy are CONCEPT_007 effects,
   not independent structure.
3. **Everything is conditional on the inherited Phase-4 relation population** and
   its fixed thresholds; the validation tests robustness *within* that population,
   not the population itself.
4. **The null model** (Phase 9) preserves degree but not the dyad census; its
   z-scores are indicative.

## 8. Recommendations for future phases

- **Use freely:** CONCEPT_007 dominance, Phase-5 compression verdict, Phase-9
  motif vocabulary, Phase-10 consistency. These are robust corpus properties.
- **Use with caution:** size-9 SCC and identity anchors (robust in aggregate,
  member-specifics inherit thresholds).
- **Treat as method-relative:** the exact 103-concept and 16-principle partitions
  — cite the *existence* of cohesive clusters / modular structure, not the precise
  counts.
- **Do not build on:** the dominant-motif ranking or any single hub-dependent
  artifact.

---

## 9. Success-criteria answers

| Question | Answer |
|---|---|
| Which discoveries are robust? | hub, consistency, compression, motif vocabulary |
| Which are fragile? | exact concept count, exact principle count, dominant-motif ranking |
| Which survive nearly all perturbations? | hub (1.000), consistency (0 contradictions), motif vocabulary (13/13) |
| Which depend on methodological choices? | concept/principle partition boundaries |
| What confidence per finding? | see survivor-analysis (very high → low, with CIs) |
| Which deserve use in future phases? | the 4 STRONG findings; others with caveats |

---

## 10. Outputs

`generated/validation/`: `threshold_sweeps.json`, `bootstrap_results.json`,
`subsampling_results.json`, `noise_results.json`, `hub_validation.json`,
`motif_validation.json`, `consistency_validation.json`,
`reproducibility_audit.json`, `survivor_analysis.json`, `validation_manifest.json`.
Tooling: `scripts/build_validation.py`, `scripts/validate_validation.py`. Reports:
`validation-overview-report.md`, `threshold-sweep-report.md`, `bootstrap-report.md`,
`subsampling-report.md`, `hub-validation-report.md`, `motif-validation-report.md`,
`consistency-validation-report.md`, `reproducibility-report.md`,
`survivor-analysis-report.md`, this report.

---

## 11. Limitations

- Validation is **within** the inherited Phase-4 relation population; it does not
  re-derive that population.
- Subsampling/bootstrap recompute lightweight derived statistics (marginals,
  co-occurrence, motif census), not a full Phase-2→10 pipeline per sample —
  faithful to the affected findings but a proxy for the full pipeline.
- Alternative clustering (Phase B) runs on the root semantic graph; two of five
  methods are known-degenerate baselines, transparently reported.

## 12. Open questions (for any future phase — not started)

1. A full pipeline re-run per subsample (vs the lightweight proxy used here).
2. Whether a principled resolution/threshold selection stabilises the concept and
   principle counts.
3. Robustness of the size-9 SCC's exact membership under a Phase-4 threshold sweep.

---

## 13. Prohibitions observed

`no new concepts · no new principles · no new motifs · no new identities · no new
theories · no reinterpretation · prior conclusions not protected · failures
documented · no cherry-picking · every regime fixed-seed deterministic.`

---

## 14. Reproduce

```bash
python3 scripts/build_validation.py
python3 scripts/validate_validation.py --rebuild
```

**Phase 11 complete. No Phase 12 started. No new discovery performed.**
