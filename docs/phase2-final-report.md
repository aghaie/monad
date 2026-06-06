# Phase 2 — Final Report: Quran Internal Lexicon Engine

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase2-lexicon-1.0`.

Phase 2 built a complete **internal lexical layer** over the Canonical Quran
Database. It discovers how words derive meaning **from their usage inside the
Quran itself**, treating the Quran as the sole semantic universe. No external
dictionary, tafsir, translation, theological source, or pre-trained embedding
was consulted at any point.

The database from Phase 1 was **not** rebuilt, its schema **not** modified, and
the source datasets **not** touched. Phase 2 reads `generated/monad.db` and
writes only into `generated/lexicon/` and `docs/`.

---

## 1. Statistics

### Corpus (inputs, read-only)

| Entity | Count |
|---|---:|
| Surahs | 114 |
| Ayahs (co-occurrence unit) | 6,236 |
| Word tokens | 77,429 |
| Tokens carrying a root | 49,959 (64.5%) |
| Tokens carrying a lemma | 74,122 (95.7%) |
| Distinct roots | 1,642 |
| Distinct lemmas | 4,831 |

### Lexicon (outputs)

| Quantity | Value |
|---|---:|
| Root profiles | 1,642 |
| Lemma profiles | 4,831 |
| Context-window records (one per token) | 77,429 |
| Co-occurrence graph nodes | 6,473 |
| Co-occurrence graph edges | 28,968 |
| Roots with semantic neighbours | 1,633 / 1,642 |
| Lemmas with semantic neighbours | 4,791 / 4,831 |
| Distinct root co-occurrence pairs | 74,167 |
| Distinct lemma co-occurrence pairs | 182,148 |

(The handful of entities with no semantic neighbours are hapax/near-hapax roots
that never co-occur with anything sharing a context dimension.)

---

## 2. Method (all Quran-internal)

| Decision | Choice | Rationale |
|---|---|---|
| Co-occurrence unit | the **ayah** | the natural Quranic semantic envelope |
| Context windows | positional, within-ayah, sizes **3 / 5 / 10** | never cross ayah bounds |
| Association weight | **PPMI** over ayah co-occurrence | standard internal-evidence measure |
| Semantic similarity | `0.70·cosine(PPMI vectors) + 0.30·cosine(surah vectors)` | blends shared-context and chapter-distribution signals into a confidence ∈ [0,1] |
| Profile neighbours | PPMI-ranked with a frequency-scaled support floor | suppresses rare-pair artefacts |
| Determinism | sorted iteration, `sort_keys`, fixed rounding, no RNG | byte-identical rebuilds |

All tunable constants are recorded in `lexicon_summary.json → constants`.

---

## 3. Data products

`generated/lexicon/` (≈ 131 MB total, all deterministic JSON):

| File | Size | Contents |
|---|---:|---|
| `root_profiles.json` | 7.8 MB | per-root: occurrences, lemmas, surah spread, first/last, neighbour roots & lemmas, contexts, dispersion |
| `lemma_profiles.json` | 19.5 MB | per-lemma: occurrences, root, neighbour lemmas & roots, contexts, surah distribution |
| `context_windows.json` | 75.6 MB | per-token prev/next forms + neighbour roots/lemmas at windows 3/5/10 |
| `cooccurrence_graph.json` | 5.6 MB | weighted root+lemma graph (cooccurrence, ppmi, semantic_proximity) |
| `semantic_neighbors.json` | 20.7 MB | top-20 internal semantic neighbours + confidence for every root & lemma |
| `distribution_profiles.json` | 2.1 MB | surah / Meccan-Medinan / dispersion statistics |
| `lexicon_summary.json` | 1.1 KB | global totals + reproducibility manifest |

Tooling and reports:

- `scripts/build_lexicon.py` — deterministic builder (full rebuild ≈ 21 s, pure
  Python stdlib, no third-party dependencies).
- `scripts/validate_lexicon.py` — 26 integrity checks incl. a `--rebuild`
  byte-identity assertion. **All checks pass.**
- `docs/root-analysis-report.md`, `docs/lemma-analysis-report.md`,
  `docs/semantic-neighborhood-report.md`, `docs/distribution-analysis-report.md`.

---

## 4. Discoveries

1. **The model rediscovers Quranic verse-clusters with zero external input.**
   Highest-confidence root pairs reconstruct whole thematic units: the
   forbidden-meat list (وقذ·نطح·خنق·ذكو, ≈0.95), the demanded foods
   (قثا·فوم·عدس·بقل·بصل, ≈0.94), the healing miracles (برص·كمه, ≈0.94). These
   clusters were never specified; they emerge purely from shared usage.

2. **A pervasive core vs. tight peripheral cliques.** The semantic graph has a
   dense backbone of text-wide roots (اله, ربب, علم, كون, قول — ربب reaches
   94/114 surahs, the broadest in the corpus) surrounded by many small closed
   cliques of rare co-topical roots. High confidence and low connectivity
   coincide at the periphery.

3. **Two hub systems for two layers.** The **root** graph is hubbed on content
   (اله, degree 300); the **lemma** graph is hubbed on function words (مِن,
   degree 838). Content cohesion anchors on the quartet اللّٰه · قَالَ · كَانَ
   · رَبّ at both layers independently.

4. **Coherent high-frequency fields.** رحم↔غفر (0.56), the mutual صلو↔زكو
   (0.48), and جنن pulling in نهر·خلد·جري·تحت·ثمر·اكل (the "gardens beneath which
   rivers flow" formula) all surface from distribution alone.

5. **Sharp Meccan/Medinan vocabulary regimes.** Against the database's
   `revelation_type` label, regulation vocabulary (نفق, نسو, قتل, حلل, توب, جهد,
   اثم) skews ~75–88% Medinan while proclamation vocabulary (نذر, وحي, قرا, سحر,
   ملا) skews ~87–95% Meccan — a measured association, no causal claim.

6. **Frequency, morphology, and reach are independent axes.** اله is loud but
   morphologically narrow (3 lemmas); قوم is mid-frequency but prolific (22
   lemmas); جعل is low-frequency yet highly central. No single metric ranks the
   lexicon.

---

## 5. Limitations

- **Distributional ≠ semantic.** Neighbours share *environments*; antonyms
  (امن/كفر) and co-topical opposites appear as neighbours. The engine measures
  usage similarity, never meaning.
- **Root sparsity.** 35.5% of tokens (function words) carry no root; root-level
  co-occurrence is content-only.
- **PPMI rare-pair inflation.** Mitigated by a support floor in the profiles but
  not in the raw similarity model; the very high cluster scores rest on one or
  two ayahs.
- **Inherited labels.** Meccan/Medinan figures are only as reliable as
  `surahs.revelation_type` in the source data.
- **Window scope.** Context windows never cross ayah boundaries; cross-ayah and
  cross-surah discourse effects are out of scope by design.
- **Fixed weights.** The 0.70/0.30 similarity blend is a documented, frozen
  choice for reproducibility; other weightings would reshape common-entity
  neighbourhoods.

---

## 6. What Monad can now answer

For any **root**: where it appears, how often, with which neighbouring roots and
lemmas, in which semantic environments, and how it is distributed across surahs
and revelation type. For any **lemma**: its surrounding contexts, which other
lemmas behave similarly (top-20 with confidence), and its most strongly
associated roots. All from a single deterministic, fully rebuildable pipeline.

---

## 7. Recommendations for Phase 3

These are scoping notes only — **Phase 3 is not started.**

1. **Sense disambiguation within a root.** Several roots host lemmas with
   divergent neighbourhoods (قوم → 22 lemmas). Cluster a root's *occurrences* by
   their context vectors to surface usage-senses — still purely internal.
2. **Cross-ayah windows.** Add optional sentence/passage-level co-occurrence to
   capture discourse-scale association beyond the single ayah.
3. **Graph analytics.** Run community detection / centrality (betweenness,
   PageRank) on `cooccurrence_graph.json` to map the macro-structure
   quantitatively.
4. **Collocation significance testing.** Complement PPMI with log-likelihood or
   permutation tests to put confidence intervals on rare-pair clusters.
5. **Temporal/positional profiles.** Use `ayah_sequential` and Meccan/Medinan to
   model how a root's neighbourhood shifts across the mushaf — distributional,
   not chronological-causal.
6. **Whatever is built next must preserve the Phase-2 firewall:** no external
   meaning, no concepts/ontology/propositions/axioms, no interpretation, no
   origin claims. Phase 2 stops exactly at the lexical/statistical layer, as
   required.

---

### Reproduce

```bash
python3 scripts/build_lexicon.py        # writes generated/lexicon/*.json (~21 s)
python3 scripts/validate_lexicon.py --rebuild   # 26 checks, byte-identical rebuild
```
