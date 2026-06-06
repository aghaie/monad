# Entity Model Report — Phase Ω (A)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`omega-world-model-1.0`.

Phase Ω asks not what structures exist but what *model* generates them. The Quran
must explain itself: no external definitions, ontology, theology, tafsir,
philosophy, science, or imported categories. The model must emerge, or fail to
emerge. No religion is proved or disproved; no divinity or humanity is assumed.
Deterministic, byte-identically reproducible (`validate_world_model.py --rebuild`,
**87 checks pass**).

This report covers Phase A — entity discovery.

---

## 1. How entities are discovered (no imported category)

An "entity" cannot be defined by meaning without importing a category. The only
Quran-internal signal distinguishing a thing-referent from an action is the
**morphology POS** (Phase-1 corpus annotation). An **entity-class concept** is a
concept whose member roots are dominantly **nominal** (POS N / PN). This is a
grammatical fact in the corpus, not an external ontology. Concepts stay opaque;
their Arabic anchors are evidence, never glossed.

---

## 2. Result

| Quantity | Value |
|---|---|
| Entity-class (nominal-dominant) concepts | **83 / 103** |
| Transformation-class (verbal) | 20 |
| State-class (adjectival) | 0 |

**83 of 103 concepts are entity-class.** The Quranic concept system is dominated by
nominal referents — recurring "things" — over actions.

---

## 3. Recurring entities (evidence only)

The highest-activation entity-class concepts (anchors are raw Arabic evidence, no
gloss):

| Concept | Anchor | Activation |
|---|---|---:|
| `CONCEPT_007` | `اله` | 5,906 |
| `CONCEPT_081` | `اله` | 2,553 |
| `CONCEPT_003` | `غفر` | 1,628 |
| `CONCEPT_053` | `عذب` | 1,265 |
| `CONCEPT_016` | `جنن` | 1,199 |

(Full list in `entity_model.json`.) These are reported as opaque entity-class
concepts with their dominant nominal anchors — what *kinds* of things they are is
**not** recoverable structurally.

---

## 4. What emerges and what does not

| Question | Answer |
|---|---|
| Do recurring entities emerge? | **Yes (structurally)** — 83 nominal-dominant concepts |
| What KINDS of things exist? | **Does not emerge** — kind requires interpretation, which is forbidden |
| How many entity-classes exist? | one grammatical class (nominal); no finer typology emerges structurally |

The entity *layer* emerges; the entity *taxonomy* (what each entity is) does not.

---

## 5. Verdict

> **Entity structure emerges.** 83 of 103 concepts are entity-class (nominal
> referents). They are reported as opaque concepts with Arabic anchors as evidence.
> What kinds of things they represent cannot be established structurally and is not
> claimed.

---

## 6. Reproduce

```bash
python3 scripts/build_world_model.py
python3 scripts/validate_world_model.py --rebuild
```

Source: `generated/world_model/entity_model.json`.
