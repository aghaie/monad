# Survivor Analysis Report — Phase 11 (J)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase11-validation-1.0`.

Every major discovery is classified **SURVIVES STRONGLY / MODERATELY / WEAKLY /
FAILS** with explicit evidence, statistics, and confidence. Prior conclusions are
not protected; failures and fragilities are documented.

---

## 1. Classification scale

| Class | Criterion |
|---|---|
| SURVIVES STRONGLY | survival probability ≥ 0.999 / invariant under all perturbation |
| SURVIVES MODERATELY | ≥ 0.95 / robust with bounded variation |
| SURVIVES WEAKLY | ≥ 0.6 / shared structure but method-sensitive specifics |
| FAILS | < 0.6 / artifact of methodological choice |

---

## 2. The eight discoveries

### CONCEPT_007 dominance — **SURVIVES STRONGLY**
- Remains the rank-1 concept in **100.0%** of 1,000 bootstraps and all 500
  subsamples. Bootstrap share mean 0.968, **95% CI [0.963, 0.972]**, min ever
  observed **0.961**. Is the max-degree node at every co-occurrence threshold
  (2/5/10/20). No alternative hub ever replaces it; dominance neither disappears
  nor strengthens — it is simply invariant.
- **Confidence: very high.**

### Phase-9 motif vocabulary — **SURVIVES STRONGLY**
- All **13 triad classes** present at every edge-removal / rewiring level (mean
  13.0). The **5-motifs-for-80%** compression is invariant (mean 5.0). The
  giant directional SCC persists (~92–93 nodes).
- **Caveat (documented):** the single *most-frequent* motif is **not** stable —
  `top_motif_unchanged_probability` falls from 0.5 (5% removal) to 0.0 (10–20%).
  This confirms Phase 9/10: the dominant motif `MOTIF_001` is hub-bound. The
  *vocabulary* is strong; the *ranking of #1* is fragile.
- **Confidence: high (vocabulary), low (dominant-motif identity).**

### Phase-10 consistency — **SURVIVES STRONGLY**
- **0 surviving contradictions under every regime.** Exclusion/positive-relation
  overlap is **0 at every marginal threshold** (10/30/50/100 → 1593/401/181/2
  exclusion pairs, all disjoint from positive relations). Disjointness holds in
  100% of bootstrap co-occurrence runs and all subsamples.
- **Confidence: very high.**

### Phase-5 compression — **SURVIVES STRONGLY**
- Byte-identical reproducible (Phase-5 validator). Deterministic given the
  inherited Phase-4 relation population; the qualitative verdict ("not reducible
  to a small core") is threshold-robust.
- **Confidence: high.**

### Size-9 irreducible SCC — **SURVIVES MODERATELY**
- A large strongly-connected core (~92 nodes in the full directional graph)
  persists under 20% edge perturbation (min largest-SCC stays large). The specific
  9-concept dependency core is a deterministic property of the inherited relations.
- **Confidence: high that a large irreducible core exists; the exact 9 members
  inherit Phase-4/5 thresholds.**

### Phase-7 identity anchors — **SURVIVES MODERATELY**
- Anchors are dominant member roots; dominance is bootstrap-stable (top-10 concept
  Jaccard **0.92**, top-5 **0.82**). Strong-tier anchors are robust; weak/diffuse
  anchors (and the 6 resist-identification concepts) are method-sensitive.
- **Confidence: strong-tier high, weak-tier low.**

### 103-concept structure — **SURVIVES WEAKLY**
- Five alternative clustering families share information with the canonical
  partition (**NMI 0.74** on non-degenerate methods) but disagree on exact
  assignment (**ARI 0.22**). Connected-components degenerates to a 1,350-root
  giant blob; k-core to singletons; cluster counts range 38–471 vs canonical 103.
- The *existence* of cohesive concept clusters is robust; the *precise count and
  boundaries* are method-dependent.
- **Confidence: moderate for existence, low for the exact 103.**

### Phase-8 principle structure — **SURVIVES WEAKLY**
- Reproducible, but the modularity modules are method/resolution-dependent (same
  ARI fragility as concepts). The **qualitative verdict** (90% of structure is
  inter-module; not reducible to principles) is robust; the **exact 16 modules**
  are not.
- **Confidence: high for the verdict, low for the specific partition.**

---

## 3. Tally and recommendations

| Class | Count | Discoveries |
|---|---:|---|
| SURVIVES STRONGLY | 4 | CONCEPT_007, motif vocabulary, consistency, compression |
| SURVIVES MODERATELY | 2 | size-9 SCC, identity anchors |
| SURVIVES WEAKLY | 2 | 103-concept structure, principle structure |
| FAILS | 0 | — |

**Use freely (future phases):** CONCEPT_007 dominance, Phase-5 compression,
Phase-9 motif vocabulary, Phase-10 consistency.

**Use with caution:** size-9 SCC and identity anchors (robust in aggregate,
member-specifics inherit thresholds); 103-concept partition and 16-principle
decomposition (treat counts/boundaries as method-relative, not absolute).

**Do not rely on:** the *exact* concept count (103) or principle count (16) as
canonical facts — they are method-sensitive cuts of a real but boundary-ambiguous
structure.

---

## 4. Reproduce

```bash
python3 scripts/build_validation.py
python3 scripts/validate_validation.py --rebuild
```

Source: `generated/validation/survivor_analysis.json`.
