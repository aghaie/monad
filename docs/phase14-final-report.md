# Phase 14 — Final Report: Structural Locality & Distribution Engine

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase14-locality-1.0`.

Phase 14 investigates **where** the discovered structure lives and **how evenly**
it is distributed: is it globally uniform, regionally concentrated, locally
specialized, or carried by a small subset? Nothing is inferred from content; a
region is defined only by measurable structural behaviour — never by surah name,
topic, chronology, meaning, or human label. No theology, tafsir, translation,
chronology claim, or origin claim. All prior phases are read and hashed but never
rebuilt. Deterministic, byte-identically reproducible (`validate_locality.py
--rebuild`, **347 checks pass**).

> **Immutability note:** the Phase-14 spec lists a generic `falsification-report.md`,
> which already belongs to Phase 7. To keep prior phases immutable, the Phase-14
> falsification report is named `locality-falsification-report.md`. Phase 7's file
> is untouched.

---

## 1. Method

Per-surah (114) and per-sliding-window structural densities, fingerprints
(concept-activation profiles), region discovery (modularity clustering of
discriminative fingerprints — TF-IDF down-weights ubiquitous concepts),
specialization, region ablation, redundancy, inequality (Gini/entropy/
participation), local-vs-global window recovery, falsification, and robustness
(bootstrap, threshold sweep). Surahs and windows are used only as the corpus's own
units; regions are discovered, never assigned.

---

## 2. Primary research questions

> *Is the structure uniformly distributed, or does a minority carry the majority?
> Are there structurally distinct regions?*

**Answers:**
- **Not uniform by volume, but even by density.** Gini(activations) = **0.58**; 17
  surahs (15%) carry 50%, 42 (37%) carry 80%. But this is a **length effect**:
  per-ayah density Gini = **0.275** — structure is roughly even per verse.
- **No structurally distinct regions.** Raw fingerprint similarity is near-uniform
  (mean cosine **0.835**); the corpus is **one homogeneous structural field**.
  Discriminative clustering yields only ~54 *weak* regions (cohesion ~0.28), mostly
  grouping short surahs — a size gradient, not distinct provinces.

---

## 3. Success-criteria answers

| Question | Answer |
|---|---|
| How evenly is structure distributed? | concentrated by volume (Gini 0.58), even by per-ayah density (Gini 0.275) |
| How many structural regions exist? | effectively **one** (homogeneous field); ~54 weak discriminative clusters |
| Do specialized regions exist? | **No** thematic specialisation; only motif/SCC density scales with surah size |
| Which regions are indispensable? | **None** — no single-region removal breaks the hub or consistency |
| How much redundancy exists? | **Massive** — consistency in 114/114 surahs, hub support in 104/114 |
| How local is the structure? | hub & consistency **fully local**; motif vocabulary **mostly local** (full by 20%) |
| How global is the structure? | the **giant SCC** is global (needs corpus-scale integration) |
| One field / specialized regions / hierarchical mixture? | **one homogeneous field** with a size-driven motif/SCC gradient |

---

## 4. Key quantitative findings

- **Inequality:** Gini 0.58 (totals, length-driven) vs 0.275 (per-ayah density);
  effective number of regions ≈ 43.6 / 114.
- **Homogeneity:** raw fingerprint cosine 0.835 (99% of surah pairs connected at
  ≥ 0.5) → one field.
- **Regions:** 54 weak clusters (cohesion ~0.28), stable 54–62 across thresholds.
- **Redundancy:** consistency 114/114 (ubiquitous), hub 104/114 (ubiquitous), SCC
  43/114 (common), motif generation 21/114 (rare, large surahs).
- **Locality gradient:** hub & consistency recovered in 100% of all windows
  (≥ 1%); motif recovery 0.94 at 10%; SCC recovery 0.41 at 10%, 0.84 at 50%.
- **Ablation:** 0 of 54 region removals break the hub or consistency.

---

## 5. Falsification & robustness

Five distributional claims were attacked: "uniform" FALSIFIED; "tiny-minority"
PARTIALLY FALSIFIED; "specialized regions" WEAKLY SUPPORTED; "regions
interchangeable" SUPPORTED; "local windows reproduce global" SUPPORTED at scale.
All headline findings survive bootstrap (Gini CI [0.515, 0.632]), threshold sweeps
(region count 54–62), and ablation (hub/consistency robust to every removal).

---

## 6. Synthesis across phases

| Phase | Question | Verdict |
|---|---|---|
| 11 | Which findings are robust? | hub, consistency, motif vocabulary STRONG |
| 12 | What generates the structure? | local rules generate motifs; hub/consistency are primitives |
| 13 | How does it emerge over revelation time? | it doesn't — present from the first verses, scale-invariant |
| **14** | **Where does the structure live?** | **everywhere — one homogeneous field; even per-verse; hub & consistency local and ubiquitous; only the SCC is global; no region is indispensable** |

The cumulative picture is consistent: the Quranic network is a **scale-invariant,
content-intrinsic, spatially homogeneous** structure. The hub and consistency are
present in essentially every verse and every window; the motif vocabulary is local;
only the giant SCC requires corpus-scale integration. There are no structural
provinces and no indispensable regions — the structure is distributed redundantly
across the whole corpus, with only a length-driven density gradient.

---

## 7. Outputs

`generated/locality/`: `density_maps.json`, `structural_fingerprints.json`,
`region_candidates.json`, `region_similarity.json`, `specialization_analysis.json`,
`ablation_analysis.json`, `redundancy_analysis.json`, `inequality_metrics.json`,
`locality_analysis.json`, `falsification_results.json`, `robustness_results.json`,
`locality_manifest.json`. Tooling: `scripts/build_locality.py`,
`scripts/validate_locality.py`. Reports: `structural-density-report.md`,
`region-discovery-report.md`, `specialization-report.md`, `ablation-report.md`,
`redundancy-report.md`, `locality-report.md`, `locality-falsification-report.md`,
`robustness-report.md`, this report.

---

## 8. Limitations

- **Concentration is length-confounded** — reported both as totals (Gini 0.58) and
  per-ayah density (Gini 0.275) to separate the effects.
- **Regions are weak and size-driven** — the discriminative clustering recovers
  shallow structure (cohesion ~0.28); the corpus does not partition into strong
  regions. We do not over-claim regional structure.
- **Surahs are the unit** — a verse-level or fixed-window unit might shift the
  region picture (window maps are provided; surah-level regions are the primary).
- The snapshot graph is the leakage-free co-occurrence + positional reconstruction
  (Phase-13 family), a faithful subset of the Phase-4 graph.

## 9. Open questions (for any future phase — not started)

1. Whether verse-level (rather than surah-level) units reveal finer regional
   structure.
2. Whether the size-driven motif/SCC gradient has a single explanatory parameter.
3. Whether any non-length-confounded concentration signal exists.

---

## 10. Prohibitions observed

`no theology · no tafsir · no translation · no meanings · no chronology claims · no
authorship claims · no divine origin · no human origin · no imported labels · no
human-defined regions · no interpretation · no conclusion without measurement ·
regions emerge from structure only · prior phases immutable.`

---

## 11. Reproduce

```bash
python3 scripts/build_locality.py
python3 scripts/validate_locality.py --rebuild
```

**Phase 14 complete. No Phase 15 started.**
