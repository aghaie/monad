# Phase 6 — Final Report: Concept Identification Engine

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase6-identification-1.0`.

Phase 6 built the **Concept Identification Engine**. It is **not** a meaning
engine, **not** an ontology engine, **not** a theology engine. Its sole purpose
is to reveal *what Quran-internal evidence defines each discovered concept* — its
dominant roots and lemmas, the ayahs that most strongly activate it, the surahs
that carry it, and the structures that surround and depend on it. **It assigns no
meaning.** No concept, root, lemma, ayah, surah, or structure is renamed,
labelled, translated, or interpreted. Concept ids and relation types stay opaque
exactly as in Phases 3–5. The Quran is the only semantic universe; no
dictionary, tafsir, translation, theology, ontology, embedding, or interpretation
is used. Phases 1–5 are read and hashed but never rebuilt or modified.

---

## 1. Method

**Concept activation** reuses the Phase-4 rule exactly: an ayah activates a
concept iff any word token carries a member `root_id` or `lemma_id`. On top of
that, an evidence-weighted **activation strength** per `(concept, ayah)` is the
summed Phase-3 membership confidence of the firing member tokens. Cross-checks
confirm consistency with prior phases: the active-ayah population is **6,101**
(identical to Phase 4), and `CONCEPT_081` activates exactly **2,553** ayahs
(matching its Phase-4 `REQUIRES → CONCEPT_007` support).

Seven evidence layers (A–G) are produced, all deterministic, pure-stdlib, and
byte-identically reproducible — verified by `validate_identification.py
--rebuild` (**18,839 checks pass**).

---

## 2. Primary question

> *What evidence defines each discovered concept, and what Quranic regions
> activate it — without assigning meaning?*

**Answer:** for all 103 concepts, Monad now exposes — as pure evidence — the
dominant roots, dominant lemmas, the top-25/50/100 activating ayahs, the
highest-activation / highest-density / highest-uniqueness surahs, the closest
concepts, and the dependencies, propositions, bridges, and cycles each concept
participates in. No concept was named or interpreted to do so.

---

## 3. Dominant concepts (evidence)

| Concept | Act. ayahs | Roots | Found. rank | Role (Phase-5, structural) |
|---|---:|---:|---:|---|
| `CONCEPT_007` | 5,906 | 24 | 1 | dominant hub (layer 0, requires-in only) |
| `CONCEPT_081` | 2,553 | 4 | 2 | hub partner (CO_OCCURS/REQUIRES) |
| `CONCEPT_003` | 1,628 | 32 | 4 | size-9 irreducible core |
| `CONCEPT_053` | 1,265 | 6 | 7 | size-9 irreducible core |
| `CONCEPT_016` | 1,199 | 16 | 6 | secondary core (emerges on hub removal) |
| `CONCEPT_061` | 1,194 | 5 | 11 | size-9 irreducible core |
| `CONCEPT_084` | 1,175 | 4 | 12 | size-9 irreducible core |
| `CONCEPT_088` | 1,126 | 4 | 5 | size-9 irreducible core |

Activation is extremely skewed (min 3, **max 5,906**, median 53). One concept,
`CONCEPT_007`, activates 96.8% of all active ayahs. Member size and reach are
decoupled: the largest concept by roots (`CONCEPT_001`, 34) ranks only 13th by
activation, while a 4-root concept (`CONCEPT_081`) ranks 2nd.

---

## 4. Dominant roots & lemmas (evidence)

The single highest-`activation_weight` roots/lemmas per leading concept (raw, no
gloss):

| Concept | Top roots (activation weight) | Top lemmas |
|---|---|---|
| `CONCEPT_007` | `اله` · `كون` · `قول` · `علم` · `امن` | `ٱللَّه` · `قَالَ` · `مِن` · `كَانَ` · `مَا` |
| `CONCEPT_081` | `اله` · `يوم` · `كفر` · `بين` | `ٱللَّه` · `يَوْم` · `كَفَرَ` · `بَيْن` |
| `CONCEPT_016` | `جنن` · `وعد` · `نور` · `وقي` | `جَنَّة` · `ٱتَّقَىٰ` · `نَار` · `خَٰلِد` |
| `CONCEPT_053` | `عذب` · `كفر` · `يوم` · `اخر` | — |
| `CONCEPT_088` | `رسل` · `كفر` · `عذب` · `صوب` | — |

The root `رسل` is a dominant root of three size-9-core members; `رحم`, `عذب`,
`كفر` recur across the core. These are co-occurrence facts stated without
interpretation.

---

## 5. Dominant ayahs (evidence)

- **Strongest single activation:** ayah **2:282** (`CONCEPT_007`, strength 48.5,
  48 member tokens) — the strongest concept activation in the corpus.
- **Most-shared #1 ayahs:** **2:282** and **47:15** each head three different
  concepts.
- Signature ayahs are dense, multi-root ayahs (e.g. 47:15 fires 11 distinct
  member roots of `CONCEPT_016`).

---

## 6. Dominant surahs (evidence)

| Surah | Concept activations (top-axis sum) | Top-activation #1 for N concepts |
|---:|---:|---:|
| 2 | 1,883 | 35 |
| 4 | 1,238 | 10 |
| 3 | 1,157 | 6 |
| 7 | 1,039 | — |
| 9 | 839 | 5 |

Concept activity is front-loaded into the long Medinan surahs; **uniqueness**
peaks in short surahs (`CONCEPT_102` lift 346 in surah 49). `CONCEPT_007` alone
has no distinctive surah (flat lift ≈ 1.06) — the hub's structural signature.

---

## 7. Dominant structures (evidence)

- **One dominant core** `CONCEPT_007`: removal destroys 22.2% of relations and is
  the only single concept that fragments the proposition graph; corpus-wide
  activation; layer 0; receives 96 `REQUIRES`, emits 0 `DEPENDS_ON`.
- **Secondary core** `CONCEPT_016`: top-betweenness on hub removal; layer 7;
  relation-diversity 7/9; surah-distinctive; emits `DEPENDS_ON` — the structural
  opposite of the hub.
- **Size-9 irreducible core** (`003 · 004 · 034 · 053 · 060 · 061 · 084 · 085 ·
  088`), all in layer 6 — eight of them in the top-20 foundational set.
- **94-concept directional core** — ordering is globally cyclic; no global
  precedence hierarchy.

---

## 8. Outputs

`generated/identification/`:

| File | Bytes | Phase | Contents |
|---|---:|:--:|---|
| `concept_profiles.json` | 667,273 | A | full per-concept evidence profile |
| `dominant_roots.json` | 349,567 | B | ranked member roots per concept |
| `dominant_lemmas.json` | 894,361 | C | ranked member lemmas per concept |
| `ayah_signatures.json` | 5,787,884 | D | top 25/50/100 activating ayahs |
| `surah_signatures.json` | 558,057 | E | surah activation/density/uniqueness |
| `concept_atlas.json` | 506,637 | F | neighbours, deps, propositions, bridges, cycles |
| `core_investigation.json` | 1,146,133 | G | deep dossiers (core/secondary/top-20/SCCs) |
| `identification_manifest.json` | 2,713 | — | constants, input SHA-256, output bytes, prohibitions, totals |

Tooling: `scripts/build_identification.py` (≈ 0.6 s, pure stdlib),
`scripts/validate_identification.py`. Reports: `concept-identification-report.md`,
`core-investigation-report.md`, `ayah-signature-report.md`,
`surah-signature-report.md`, this report.

---

## 9. Limitations

- **Inherited activation rule.** Activation is the Phase-4 membership-union rule;
  a different rule (confidence-thresholded, positional, etc.) would re-weight
  every ranking.
- **One deterministic strength weighting** (summed membership confidence); raw
  token counts and confidences are published for independent re-ranking.
- **Multi-membership** is not partitioned: roots/lemmas in several concepts
  contribute to each.
- **Inherited population.** All structure rests on the Phase-3 concept set and
  the Phase-4 relation set with their fixed thresholds.
- **No meaning.** Every root, lemma, ayah, surah, and concept id is raw evidence.
  This engine exposes evidence; it does not explain it.

---

## 10. Open questions (for any future phase — not started)

1. Whether a confidence-thresholded activation rule sharpens or blurs the
   dominant-root rankings.
2. Whether the size-9 irreducible core's shared roots (`رسل`, `رحم`, `عذب`,
   `كفر`) reflect overlapping membership or genuine co-activation.
3. Exclusive (partitioned) vs shared multi-membership attribution of
   activation weight.
4. Stability of ayah/surah signatures under a Phase-3/4 threshold sweep.

---

## 11. Prohibitions observed

`no concept renaming · no concept labels · no assigned meanings · no root
translation · no lemma translation · no ontology · no axioms · no contradiction
engine · no theology · no doctrine · no divine origin claim · no human origin
claim · no interpretation · no external knowledge · concepts remain opaque ·
prior phases never rebuilt.`

---

## 12. Reproduce

```bash
python3 scripts/build_identification.py
python3 scripts/validate_identification.py --rebuild
```

**Phase 6 complete. No future phase started.**
