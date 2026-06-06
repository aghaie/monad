# Phase 17 — Frequency Null Model Engine: Design Spec

**Date:** 2026-06-06  
**Version:** phase17-frequency-null-1.0  
**Status:** approved

---

## 1. Mission

Phase 16 established that CONCEPT_007's hub dominance reduces entirely to lexical
frequency (Spearman 0.998 with corpus root count). Phase 17 extends this question to
every major Monad discovery: how much survives after controlling for lexical
frequency?

No discovery is protected. Any finding may fail. Any finding may survive. Report both.

---

## 2. Inputs

All Phase 1–16 outputs, read-only, hashed at load time. Never rebuilt.

Key inputs:

| Source | File | Used for |
|---|---|---|
| Phase 3 | `generated/concepts/concept_memberships.json` | concept→root mapping |
| Phase 3 | `generated/concepts/concept_statistics.json` | observed concept stats |
| Phase 4 | `generated/propositions/proposition_graph.json` | observed edge count, bridges |
| Phase 4 | `generated/propositions/proposition_manifest.json` | rule thresholds (constants) |
| Phase 7 | `generated/identification/concept_profiles.json` | identity distinctiveness |
| Phase 9 | `generated/motifs/motif_catalog.json` | observed motif frequencies |
| Phase 10 | `generated/consistency/consistency_scores.json` | observed consistency |
| Phase 10 | `generated/consistency/contradiction_candidates.json` | observed contradiction count |
| Phase 12 | `generated/grammar/rule_candidates.json` | observed grammar rule support |
| Phase 12 | `generated/grammar/rule_statistics.json` | rule fit values |
| Phase 15 | `generated/consistency_propagation/consistency_propagation_manifest.json` | Phase 15 consistency findings |
| Phase 16 | `generated/hub_origin/hub_origin_manifest.json` | frequency-dominance evidence |
| DB | `generated/monad.db` | word tokens with root_id, ayah assignments |

---

## 3. Outputs

### JSON (generated/frequency_null/)

| File | Content |
|---|---|
| `null_corpora.json` | Parameters, seeds, per-null metadata (not raw corpora) |
| `concept_survival.json` | Phase B: concept activation z-scores, effect sizes |
| `proposition_survival.json` | Phase C: edge/bridge/dependency z-scores |
| `motif_survival.json` | Phase D: per-motif-type z-scores |
| `consistency_survival.json` | Phase E: contradiction count null distribution |
| `identity_survival.json` | Phase F: concept distinctiveness z-scores |
| `scc_survival.json` | Phase G: SCC size/count z-scores |
| `grammar_survival.json` | Phase H: grammar rule support z-scores |
| `information_decomposition.json` | Phase I: frequency % and structure % per discovery |
| `survivor_analysis.json` | Phase J: survival classification per discovery |
| `frequency_falsification.json` | Phase K: H1–H7 falsification results |
| `frequency_null_manifest.json` | Method, constants, input hashes, output bytes |

### Markdown (docs/)

- `docs/frequency-null-model-report.md` — overall null model design and results
- `docs/concept-survival-report.md` — Phase B
- `docs/proposition-survival-report.md` — Phase C
- `docs/motif-survival-report.md` — Phase D
- `docs/consistency-survival-report.md` — Phase E
- `docs/identity-survival-report.md` — Phase F
- `docs/scc-survival-report.md` — Phase G
- `docs/grammar-survival-report.md` — Phase H
- `docs/information-decomposition-report.md` — Phase I
- `docs/survivor-analysis-report.md` — Phase J
- `docs/phase17-final-report.md` — final synthesis

---

## 4. Architecture

Single `scripts/build_frequency_null.py` (pure Python stdlib, ~1,100 lines) following
the established Monad pattern. Single `scripts/validate_frequency_null.py` for
reproducibility verification (checks output files and hashes).

```
build_frequency_null.py
  load_inputs()             — read + hash all Phase 1–16 files
  build_null_corpus()       — 1000 realizations (500 perm + 500 multinom)
  phase_b_concepts()        — activation frequencies vs null
  phase_c_propositions()    — edge/bridge/requires counts vs null
  phase_d_motifs()          — motif type frequencies vs null
  phase_e_consistency()     — contradiction counts vs null
  phase_f_identity()        — concept distinctiveness vs null
  phase_g_sccs()            — SCC sizes/counts vs null
  phase_h_grammar()         — rule support values vs null
  phase_i_decompose()       — information decomposition
  phase_j_classify()        — survival classification
  phase_k_falsify()         — H1–H7 hypothesis falsification
  phase_l_robustness()      — bootstrap, subsampling, threshold sweeps
  write_outputs()           — 12 JSON + 11 markdown reports
```

---

## 5. Null model (Phase A)

### 5.1 Corpus representation

Load all words with non-NULL root_id from the DB (49,959 tokens):

```python
tokens = [(surah, ayah, root_id), ...]  # 49,959 entries
```

Build a flat list of `root_ids` (length 49,959) and a parallel list of `ayah_keys`
(length 49,959). The `ayah_keys` list is the real corpus assignment.

### 5.2 Permutation null (500 realizations)

Fisher-Yates shuffle the `root_ids` list in place, keeping `ayah_keys` fixed.
Regroup into `null_ayah_roots: dict[ayah_key → set(root_ids)]`.

Preserves exactly:
- Total corpus count of every root
- Exact word count per ayah (verse lengths)

Destroys:
- All root co-occurrence within verses
- Verse-level concept activation patterns
- All proposition, motif, dependency, SCC structure

### 5.3 Multinomial null (500 realizations)

For each root r with corpus count n_r, independently sample n_r ayah_keys from
`Uniform(all 6236 ayahs)` with replacement. Merge into `null_ayah_roots`.

Preserves exactly:
- Total corpus count of every root

Destroys:
- Verse lengths (Poisson-like variation)
- All co-occurrence and structural patterns

### 5.4 Per-realization statistics (stored in memory)

For each of 1000 realizations, compute and store:

```python
{
  "activation_freqs":      {concept_id: int},      # ayahs where ≥1 member root present
  "activation_variance":   float,                   # variance across concepts
  "cooccur_count":         int,                     # concept pairs with support ≥ 5
  "requires_count":        int,                     # pairs with CONF ≥ 0.9, support ≥ 5
  "bridge_count":          int,                     # articulation points in null graph
  "scc_count":             int,                     # strongly connected components
  "scc_max_size":          int,                     # largest SCC node count
  "contradiction_count":   int,                     # C2 necessity exclusion violations
  "motif_freqs":           {motif_type: int},       # 15 triad/dyad type counts
  "concept_entropy":       {concept_id: float},     # surah-level entropy per concept
  "grammar_rule_hits":     {rule_id: float},        # rule support in null graph
  "distinctiveness_index": float,                   # mean concept separability
}
```

`null_corpora.json` stores these aggregate statistics, not the 1000 raw root-to-ayah
assignments.

---

## 6. Per-phase survival testing (Phases B–H)

### Common pattern

For each observed statistic O and null distribution N = [n_1, ..., n_1000]:

```
null_mean  = mean(N)
null_std   = std(N)
z_score    = (O - null_mean) / null_std   (if null_std > 0, else 0)
p_value    = rank of O in N / 1000        (empirical, two-tailed)
effect_size = z_score                     (standardized)
```

### Phase B — Concept survival

Observed: per-concept activation frequency, activation variance across concepts,
average concept cohesion score (0.406), average cluster stability (0.778).

Null test: do the 103 fixed concept clusters (by their member roots) produce
activation patterns that differ from random co-occurrence?

Key statistics:
- activation_freq per concept (103 z-scores)
- activation_variance (1 z-score)
- CONCEPT_007 relative dominance (observed 96.8% vs null distribution)

### Phase C — Proposition survival

Observed: 1,474 graph edges, 100 REQUIRES edges, 10 bridges, 4 hierarchical chains.

Null test: recompute REQUIRES (CONF ≥ 0.9, support ≥ 5) and co-occurrence edges
(support ≥ 5) from null activation. Count bridges and hierarchical chains.

Key statistics:
- requires_count z-score
- cooccur_count z-score
- bridge_count z-score

### Phase D — Motif survival

Observed: 15 motif types; MOTIF_001 = 4,092 instances, significance z = 9.60.

Null test: for each null graph (built from null REQUIRES + co-occurrence edges),
run triad census on the 103-node graph, count each of 15 motif types.

Key statistics:
- per-motif z-score (15 values)
- motif type diversity z-score

### Phase E — Consistency survival

Observed: 0 genuine contradictions, global_consistency_index = 0.955.
Phase 15 already showed 30 null shuffles → 0 contradictions.

Null test: reapply the C2 contradiction rule (REQUIRES + EXCLUSION) to each null's
activation-derived REQUIRES set. Count violations.

Expected outcome: 0 contradictions in null too (confirming consistency is generic
not structural). The 1000-null distribution will quantify this precisely.

### Phase F — Identity survival

Observed: per-concept surah signature distinctiveness (from Phase 7 concept_profiles).

Null test: in each null, compute each concept's surah-level activation profile.
Measure inter-concept separability (mean pairwise cosine distance of profiles).
Compare to observed separability.

Key statistics: distinctiveness_index z-score.

### Phase G — SCC survival

Observed: one size-9 SCC, 74 trivial SCCs (from Phase 5/8/9).

Null test: build null directed graph (REQUIRES edges from null activations), run
Tarjan's SCC algorithm on 103 nodes, record scc_max_size and scc_count.

Key statistics:
- scc_max_size z-score
- scc_count z-score

### Phase H — Grammar survival

Observed: Phase 12 fitted grammar parameters (transitivity, reciprocity, gamma fit).

Null test: in the null proposition graph, measure the same structural properties
(transitivity fraction, reciprocity fraction, degree distribution fit). Compare
parameter values to those fitted from the null graphs.

Key statistics: per-rule z-score.

---

## 7. Information decomposition (Phase I)

For each discovery D with observed value O and null mean N:

```
frequency_contribution_pct = (N / O) × 100      if O > 0 and N ≤ O
structure_contribution_pct = ((O - N) / O) × 100 if O > 0
```

Edge cases:
- N > O (observed below null expectation): frequency_contribution > 100%, structure
  contribution negative — indicates structural suppression
- O = 0: skip (no information to decompose)
- null_std = 0: structure contribution = 100% if O > 0, else 0%

---

## 8. Survival classification (Phase J)

| Category | z-score | Interpretation |
|---|---|---|
| FREQUENCY ONLY | \|z\| < 1 | indistinguishable from frequency artifact |
| MOSTLY FREQUENCY | 1 ≤ \|z\| < 2 | weak structural signal |
| MIXED | 2 ≤ \|z\| < 3 | moderate structural signal |
| MOSTLY STRUCTURE | 3 ≤ \|z\| < 5 | strong structural signal |
| STRUCTURE ONLY | \|z\| ≥ 5 | cannot be explained by frequency |

Classification applied to every named discovery (103 concept activation frequencies,
9 proposition statistics, 15 motif z-scores, 3 consistency statistics, 1
distinctiveness index, 2 SCC statistics, N grammar rule statistics).

---

## 9. Falsification (Phase K)

Seven hypotheses tested. Falsification criterion: p_value ≥ 0.05 (observed not
distinguishable from null).

| # | Hypothesis | Test statistic |
|---|---|---|
| H1 | Concept structure exceeds frequency | activation_variance z-score |
| H2 | Proposition structure exceeds frequency | requires_count z-score |
| H3 | Motif vocabulary exceeds frequency | motif diversity z-score |
| H4 | Consistency exceeds frequency | contradiction_count empirical p |
| H5 | Identity exceeds frequency | distinctiveness_index z-score |
| H6 | Grammar exceeds frequency | grammar_rule_hits z-scores |
| H7 | Irreducible structure remains | composite: count of |z| ≥ 5 discoveries |

Outcomes: SURVIVES, FALSIFIED, or INCONCLUSIVE (0.05 ≤ p ≤ 0.10).

---

## 10. Robustness (Phase L)

### Bootstrap (100 outer × 100 inner = 10,000 total)

For each bootstrap run: resample 49,959 tokens with replacement, then apply the
permutation null 100 times. Record survival classification per discovery. Report
how often classification changes across bootstraps.

### Subsampling

Run the full 1000-null procedure on 50% and 75% random samples of the corpus.
Do survival rankings change? Report instability.

### Threshold sweeps

For REQUIRES_CONF_MIN ∈ {0.7, 0.8, 0.9, 0.95}:
- Recompute null requires_count at each threshold
- Test whether Phase C survival changes

Only findings robust across all three robustness tests are classified as
**fully surviving**.

---

## 11. Constants

```python
METHOD            = "phase17-frequency-null-1.0"
SEED              = 20261717
N_PERM            = 500
N_MULTI           = 500
N_BOOT            = 100
N_BOOT_INNER      = 100
SUBSAMPLE_FRACS   = [0.50, 0.75]
THRESH_SWEEP      = [0.70, 0.80, 0.90, 0.95]
REQUIRES_CONF_MIN = 0.90
SUPPORT_MIN       = 5
P_THRESHOLD       = 0.05
Z_FREQ_ONLY       = 1.0
Z_MOSTLY_FREQ     = 2.0
Z_MIXED           = 3.0
Z_MOSTLY_STRUCT   = 5.0
ROUND             = 6
```

---

## 12. Prohibitions

- No theology, tafsir, translation, meaning, interpretation
- No protection of previous discoveries
- No modifying prior phase outputs
- Any discovery may fail; report it
- All results must be reproducible byte-identically

---

## 13. Estimated runtime

| Phase | Time estimate |
|---|---|
| Load inputs | < 5s |
| 1000 null activations (Phases A–E,G) | ~2–4 min |
| Motif census per null (Phase D) | ~1–2 min additional |
| Robustness bootstrap (10,000 inner) | ~10–15 min |
| Write outputs | < 5s |
| **Total** | **~15–25 min** |

---

## 14. Spec self-review

- No TBDs or placeholders
- Constants section is complete and internally consistent
- Phase I edge cases are handled (N > O, O = 0, null_std = 0)
- Phase L test counts (10,000 bootstrap inner realizations) are feasible given
  ~0.13s per null → 22 minutes worst case; acceptable
- All 12 JSON outputs and 11 markdown reports are listed
- Prohibitions are copied from the Phase 17 mission spec
- All prior-phase inputs are explicitly listed with file paths
