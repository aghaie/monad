# Lemma Analysis Report — Phase 2 (Quran Internal Lexicon)

**Scope.** Distributional behaviour of the **4,831 lemmas** attested in
`generated/monad.db`. Derived solely from Quran-internal usage; no external
lexical resource is consulted. Reproducible via `scripts/build_lexicon.py`.

**Layer.** Strictly lexical and statistical. No definitions, no interpretation,
no claims about meaning or origin.

Data products: `lemma_profiles.json`, `cooccurrence_graph.json`,
`semantic_neighbors.json`.

---

## 1. Corpus shape

| Measure | Value |
|---|---|
| Distinct lemmas (attested in `words`) | 4,831 |
| Word tokens carrying a lemma | 74,122 / 77,429 (95.7%) |
| Lemmas with a parent root | most content lemmas |
| Lemmas **without** a root | function words (مِن, مَا, فِى, لَا, …) |
| Distinct co-occurring lemma pairs | 182,148 |

Lemma coverage (95.7%) is far higher than root coverage (64.5%) because
function words receive a lemma but no root. This makes the lemma layer the
**complete** token-level view and the root layer the **content-only** view.

---

## 2. Highest-frequency lemmas

| Lemma | Root | Occurrences |
|---|---|---:|
| مِن | — | 3,067 |
| ٱللَّه | اله | 2,699 |
| مَا | — | 2,565 |
| لَا | — | 1,738 |
| فِى | — | 1,675 |
| قَالَ | قول | 1,618 |
| إِنّ | — | 1,536 |
| ٱلَّذِى | — | 1,464 |
| عَلَىٰ | — | 1,445 |
| كَانَ | كون | 1,358 |

**Pattern — the frequency ceiling is held by function words.** Eight of the top
ten lemmas carry no root. The two content lemmas that break in — ٱللَّه and
قَالَ — are exactly the divine name and the speech-frame verb, the two pillars
of Quranic narrative syntax. The single most frequent token in the entire corpus
is the preposition مِن.

---

## 3. Most connected lemmas (graph degree)

Degree in the lemma co-occurrence graph (≤ 12 retained partners per node, so
high degree = repeatedly a strongest partner of others).

| Lemma | Root | Degree |
|---|---|---:|
| مِن | — | 838 |
| ٱللَّه | اله | 631 |
| مَا | — | 590 |
| فِى | — | 544 |
| لَا | — | 444 |
| عَلَىٰ | — | 431 |
| قَالَ | قول | 411 |
| ٱلَّذِى | — | 389 |
| كَانَ | كون | 359 |
| إِنّ | — | 347 |

**Pattern — function words are the graph's hubs.** The lemma graph is organised
around grammatical connectors: مِن alone is a top partner to 838 other lemmas.
This is the lemma-level counterpart to the root finding that اله dominates the
*content* graph. The two graphs have different hubs because they describe
different layers — syntax (lemmas) vs. content (roots).

**Most connected *content* lemma:** ٱللَّه (degree 631), followed at a distance
by قَالَ (411), كَانَ (359), and رَبّ (237). Content cohesion in the Quran is
anchored on the divine name, the verb of speech, the verb of being, and the
Lord-root — the same quartet that dominates the root graph, confirmed
independently at the lemma layer.

---

## 4. Unusually behaved lemmas

**Many lemmas per root.** A handful of roots fan out into large lemma families
(قوم → 22 lemmas, امن → 17, علم → 14, كفر → 14, بين → 13). Each member lemma has
its own co-occurrence signature, so a single root can host lemmas that behave
quite differently — e.g. the noun vs. verbal members of قوم occupy different
co-occurrence neighbourhoods even though they share a root.

**Function-word similarity.** Because semantic similarity is computed from
shared contexts, the rootless function lemmas form their own tight cluster
(مِن, فِى, عَلَىٰ, إِلَىٰ pattern together): they share contexts with almost
everything, so they are distributionally similar to one another and weakly
similar to content lemmas. This is the expected "stop-word" geometry, surfaced
here purely from internal evidence.

---

## 5. Per-lemma profile contents

Each entry in `lemma_profiles.json` answers the Phase-2 success criteria for a
lemma:

- **lemma / root / occurrence_count**
- **top_neighbor_lemmas** — PPMI-ranked co-occurring lemmas (support-floored)
- **top_neighbor_roots** — most associated roots
- **representative_contexts** — verbatim verse snippets
- **surah_distribution** — per-surah token counts
- **distribution_statistics** — coverage, evenness, concentration

Behaviourally similar lemmas (the "which other lemmas behave like this one"
criterion) are answered by `semantic_neighbors.json → lemmas`, which stores the
top-20 distributional neighbours with confidence scores.

---

## 6. Limitations

- Function lemmas dominate frequency and centrality; for content-level study,
  filter to lemmas with a non-null root.
- A lemma's neighbour evidence thins out in the long tail: the lemma inventory
  (4,831) is ~3× the root inventory, so the average lemma has fewer occurrences
  and noisier statistics than the average root.
- PPMI rare-pair inflation is mitigated by the support floor but not eliminated.
- All statements are distributional. No meaning is asserted.
