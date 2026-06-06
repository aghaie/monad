# Semantic Neighborhood Report — Phase 2 (Quran Internal Lexicon)

**Scope.** The internal semantic-similarity model over the 1,642 roots and 4,831
lemmas of `generated/monad.db`. Every neighbour relation is derived **only** from
Quran-internal distributional evidence — co-occurrence, shared contexts, shared
neighbours, and chapter distribution. No external embeddings, dictionaries, or
corpora are used. Reproducible via `scripts/build_lexicon.py`.

**Layer.** Strictly statistical. "Semantic neighbour" is a name for
*distributional similarity*, i.e. two roots/lemmas that tend to occur in similar
Quranic environments. It is **not** a synonym, a gloss, or a meaning. No
interpretation, theology, or origin claim is made anywhere below.

Data product: `semantic_neighbors.json`.

---

## 1. The model

For each entity (root or lemma) the engine builds a **PPMI context vector** over
its ayah-level co-occurrence partners (Positive Pointwise Mutual Information,
truncated to the strongest 100 dimensions). Similarity between two entities is a
composite **confidence** score in [0, 1]:

```
confidence = 0.70 · cosine(PPMI context vectors)      # shared contexts + shared neighbours
           + 0.30 · cosine(surah distribution vectors) # chapter-level affinity
```

The distributional cosine simultaneously captures the spec's "shared contexts"
and "shared neighbours" signals (two words are close if they keep the same
company); the chapter term adds macro-distribution agreement. Pairs below
`MIN_SIM = 0.05` are discarded; the top 20 per entity are stored.

This is a classic **distributional-semantics** construction (Harris's
distributional hypothesis) restricted entirely to the Quran as its universe.

---

## 2. The clearest validation: the model rediscovers Quranic verse-clusters

With no external knowledge, the highest-confidence root pairs reconstruct whole
thematic units of the text:

| Discovered cluster | Roots (confidence ≈) | What the verses are |
|---|---|---|
| **Forbidden-meat list** | وقذ · نطح · خنق · ذكو (0.95) | the beaten / gored / strangled animals and ritual slaughter (cf. 5:3) |
| **The demanded foods** | قثا · فوم · عدس · بقل · بصل (0.94) | cucumber · garlic · lentils · herbs · onions (cf. 2:61) |
| **Healing miracles** | برص · كمه (0.94) | the leper and the man born blind (cf. 3:49, 5:110) |

These clusters were **not** told to the engine. They emerge because these rare
roots occur almost only in each other's company, in the same one or two ayahs,
in the same surah — so their PPMI vectors and chapter vectors nearly coincide.
This is the strongest internal evidence that the method is tracking real usage
structure rather than noise.

---

## 3. High-frequency semantic fields

For common roots the neighbourhoods are softer but strikingly coherent:

| Root | Top distributional neighbours (confidence) |
|---|---|
| **رحم** mercy | **غفر** 0.56 · سلم · اجر · حرم |
| **صلو** prayer | **زكو** 0.48 · طهر · قرب · توب |
| **زكو** alms | **صلو** 0.48 · توب · نكح · فحش |
| **جنن** garden | **نهر** 0.44 · خلد · جري · تحت · ثمر · اكل |
| **كفر** disbelief | **امن** 0.45 · قتل · دين · عذب · موت |
| **امن** belief | **اله** 0.48 · كفر · عمل · رسل |
| **علم** knowledge | **اله** 0.49 · بين · حكم |

Three patterns stand out:

1. **رحم ↔ غفر (0.56)** is the single strongest high-frequency pairing — mercy
   and forgiveness keep almost identical company throughout the corpus.
2. **صلو ↔ زكو (0.48)** is mutual and symmetric: prayer and almsgiving are each
   other's top neighbour, an internally-measured collocational bond.
3. **جنن** ("garden") pulls in نهر · خلد · جري · تحت · ثمر · اكل — i.e. the exact
   recurring vocabulary of the *"gardens beneath which rivers flow, abiding
   eternally"* formula, reconstructed from distribution alone.

Note also the **antonym-as-neighbour** effect: كفر's top neighbour is امن and
vice-versa. Distributional similarity measures *shared environment*, and
opposites are debated in the same verses — so belief and disbelief sit close in
this geometry. This is expected behaviour for a distributional model and must
not be read as synonymy.

---

## 4. Two similarity signals, two behaviours

The confidence score blends a **distributional** and a **chapter** component,
and they tell different stories:

- **Rare roots** score high on *both* (≈0.91 distributional, ≈1.00 chapter):
  they live in one shared verse, so they share contexts *and* chapters almost
  perfectly → confidence ≈ 0.95.
- **Common roots** score modestly on distributional (0.20–0.35) but very high on
  chapter (0.82–0.92): pervasive vocabulary co-occurs with everything, so its
  *contexts* are diffuse but its *chapter spread* is similar to other pervasive
  vocabulary. The chapter term is what keeps the common-root neighbourhoods
  populated and ranked.

This separation is visible in every `neighbors` entry via the explicit
`distributional` and `chapter` fields.

---

## 5. Unusually connected / unusually isolated entities

- **Most semantically central roots** (broad, high-confidence neighbourhoods)
  are the pervasive backbone roots — اله, علم, امن, ربب — whose chapter spread
  matches many others.
- **Most semantically isolated roots** are the rare cluster-roots of §2: their
  *only* strong neighbours are their 3–4 cluster siblings, with effectively no
  ties to the rest of the lexicon. They are simultaneously the **highest
  confidence** and the **lowest connectivity** — tight, closed cliques.

This dichotomy (a dense pervasive core + many tight peripheral cliques) is the
dominant macro-structure of the Quran-internal semantic graph.

---

## 6. Limitations

- **Distributional ≠ synonymous.** Neighbours share *environments*; antonyms and
  co-topical opposites (belief/disbelief, conceal/reveal) appear as neighbours.
- **Rare-pair inflation.** The very high scores in §2 rest on one or two ayahs;
  they are robust as *cluster detection* but say nothing about frequency.
- **Function lemmas** form a degenerate cluster (they co-occur with everything);
  for content study, restrict to rooted lemmas.
- The chapter weight (0.30) is a deliberate, documented choice; changing it
  reweights the common-root neighbourhoods. It is fixed for reproducibility.
- Nothing here is an interpretation. The model locates usage similarity; it does
  not assign meaning.
