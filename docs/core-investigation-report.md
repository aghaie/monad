# Core Investigation Report — Phase 6

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase6-identification-1.0`.

This report is the Phase-6 deep-evidence dossier for the structures Phase 5
identified as central: the **dominant core** (`CONCEPT_007`), the **secondary
core** that emerges under hub removal (`CONCEPT_016`), the **top-20 foundational
concepts**, and the **largest strongly-connected (irreducible) structures**.

Every figure below is raw Quran-internal evidence or a prior-phase graph
quantity. **No meaning, label, translation, interpretation, theology, ontology,
or origin claim is assigned to any concept, root, lemma, ayah, surah, or
structure.** Concept ids stay opaque. Targets were selected purely by Phase-5
foundationality rank and Phase-5 core identity — not by content.

---

## 1. Dominant core — `CONCEPT_007`

`CONCEPT_007` is Phase-5 foundationality **rank 1** (composite 1.000 — the
normalised maximum on every metric) and the single dominant hub.

| Evidence axis | Value |
|---|---|
| Member roots / lemmas | 24 roots · 326 lemmas |
| Activation | **5,906 / 6,101** active ayahs (96.8%) |
| Activation strength (max / mean) | top ayah 2:282 |
| Dominant roots (activation weight) | `اله` (2054.6) · `كون` (898.3) · `قول` (847.9) · `علم` (659.3) · `امن` (578.5) · `اتي` · `بين` · `شيا` |
| Dominant lemmas | `ٱللَّه` · `قَالَ` · `مِن` · `كَانَ` · `مَا` · `لَا` · `فِى` · `عَلَىٰ` · `إِنّ` · `ٱلَّذِى` |
| Top ayahs | 2:282 · 3:154 · 73:20 · 2:102 · 4:92 · 2:213 · 5:48 · 4:12 · 5:41 · 74:31 |
| Top surahs (activating ayahs) | 2 (285) · 26 (210) · 7 (203) · 3 (199) · 4 (176) · 37 (166) |
| Uniqueness | **none** — near-flat lift ≈ 1.06 across all surahs (only concept with no distinctive surah) |
| Concept-graph centrality | degree 1.605 · betweenness 0.043 · eigenvector 0.003 · meta-community 0 |
| Proposition-graph | in-degree 96 · out-degree 89 · betweenness **2006.6** (highest) · relation-diversity 2 |
| Compression | removal destroys **1,519 relations (22.2%)** · support-weighted loss 127,496 · reach reduction 741 · **fragments graph (+5 components)** · 5,377.9 info-bits |
| Dependency | layer **0** · directional core member · incident `REQUIRES` 96 · `DEPENDS_ON` 0 |
| Strongest incident relations | `REQUIRES ← CONCEPT_081` (conf 1.0, support 2,553) · `CO_OCCURS CONCEPT_081` (2,553) · `FOLLOWS ← CONCEPT_081` (2,222) |

**Raw observations (no interpretation):** it carries no outgoing `DEPENDS_ON`
relations yet receives 96 `REQUIRES`; it is the only concept whose removal
fragments the proposition graph; its activation is corpus-wide and undistinctive
by surah; its top root by activation weight is `اله`.

---

## 2. Secondary core — `CONCEPT_016`

Under Phase-5 hub removal, `CONCEPT_016` becomes the new top-betweenness node.
It is foundationality **rank 6** while the hub is present.

| Evidence axis | Value |
|---|---|
| Member roots / lemmas | 16 roots · 90 lemmas |
| Activation | 1,199 ayahs · top ayah **47:15** |
| Dominant roots | `جنن` (149.7) · `وعد` (103.5) · `نور` (88.8) · `وقي` (85.1) · `نهر` (79.6) · `خلد` (76.6) · `مثل` · `دخل` |
| Dominant lemmas | `جَنَّة` · `ٱتَّقَىٰ` · `نَار` · `خَٰلِد` · `مَثَل` · `دَخَلَ` · `وَعَدَ` · `جَرَيْ` · `مِثْل` · `نَهَر` |
| Top ayahs | 47:15 · 65:11 · 9:72 · 13:35 · 4:57 · 64:9 · 4:122 · 61:12 |
| Top surahs (activating) | 2 (85) · 3 (57) · 7 (54) · 5 (43) · 4 (36) · 6 (32) |
| Highest-uniqueness surahs (lift) | **65 (3.03)** · 13 (2.18) · 59 (2.17) · 66 (2.17) · 49 (2.02) — all Medinan |
| Concept-graph centrality | degree 1.472 · betweenness 0.111 · eigenvector 0.023 · meta-community 0 |
| Proposition-graph | in-degree 56 · out-degree 29 · betweenness 289.4 · relation-diversity **7** |
| Compression | removal destroys 566 relations (8.3%) · support-weighted loss 24,286 · **no fragmentation** · 2,810 info-bits |
| Dependency | layer **7** (top of spire) · directional core member · incident `DEPENDS_ON` 11 · `REQUIRES` 1 |
| Closest concepts | `CONCEPT_097` (0.301) · `CONCEPT_060` (0.224) · `CONCEPT_072` (0.222) · `CONCEPT_049` (0.174) · `CONCEPT_036` (0.139) · `CONCEPT_034` (0.123) |

**Raw observations:** unlike the hub, `CONCEPT_016` is surah-distinctive (lift up
to 3.0 in surah 65), has high relation-diversity (7/9 types), sits at the top
dependency layer (7), and carries outgoing `DEPENDS_ON` (11) — the structural
opposite profile to `CONCEPT_007`'s layer-0, requires-only profile.

---

## 3. Top-20 foundational concepts (evidence)

Ordered by Phase-5 foundationality rank. Roots are the top-3 by activation
weight; layer = dependency layer; SCC = dependency-component index. **All raw
evidence; no gloss.**

| Rank | Concept | Act. | Roots | Lemmas | Layer | SCC | Top-3 roots | Top ayah |
|---:|---|---:|---:|---:|---:|---:|---|---|
| 1 | `CONCEPT_007` | 5906 | 24 | 326 | 0 | 10 | اله كون قول | 2:282 |
| 2 | `CONCEPT_081` | 2553 | 4 | 31 | 1 | 5 | اله يوم كفر | 2:282 |
| 3 | `CONCEPT_004` | 1005 | 31 | 124 | 6 | 0 | رود احد صلو | 5:6 |
| 4 | `CONCEPT_003` | 1628 | 32 | 162 | 6 | 0 | غفر رحم موت | 5:3 |
| 5 | `CONCEPT_088` | 1126 | 4 | 32 | 6 | 0 | رسل كفر عذب | 35:39 |
| 6 | `CONCEPT_016` | 1199 | 16 | 90 | 7 | 18 | جنن وعد نور | 47:15 |
| 7 | `CONCEPT_053` | 1265 | 6 | 35 | 6 | 0 | عذب كفر يوم | 57:20 |
| 8 | `CONCEPT_002` | 550 | 33 | 123 | 4 | 2 | ولد عرف قرب | 4:12 |
| 9 | `CONCEPT_085` | 889 | 4 | 26 | 6 | 0 | رسل اخذ بني | 7:146 |
| 10 | `CONCEPT_034` | 893 | 8 | 48 | 6 | 0 | رحم بعض صلح | 48:29 |
| 11 | `CONCEPT_061` | 1194 | 5 | 33 | 6 | 0 | رسل امر رحم | 4:83 |
| 12 | `CONCEPT_084` | 1175 | 4 | 47 | 6 | 0 | قوم اخذ ظلم | 7:150 |
| 13 | `CONCEPT_001` | 429 | 34 | 135 | 5 | 7 | يسر عدد حجج | 2:196 |
| 14 | `CONCEPT_060` | 621 | 5 | 39 | 6 | 0 | سوا حسن صلح | 17:7 |
| 15 | `CONCEPT_008` | 690 | 21 | 95 | 3 | 11 | خلق بلغ بعث | 22:5 |
| 16 | `CONCEPT_090` | 84 | 4 | 21 | 4 | 2 | حلل عفو صوم | 2:237 |
| 17 | `CONCEPT_013` | 195 | 17 | 46 | 2 | 15 | قسط ملل حضر | 2:282 |
| 18 | `CONCEPT_025` | 152 | 12 | 44 | 3 | 27 | ظلل منن حجر | 7:160 |
| 19 | `CONCEPT_010` | 136 | 18 | 39 | 2 | 12 | رضو جهد نفر | 9:109 |
| 20 | `CONCEPT_091` | 79 | 4 | 16 | 4 | 2 | عرف فقر حصر | 2:273 |

**Raw observations:** eight of the top-20 (`003, 004, 034, 053, 060, 061, 084,
085`) share dependency SCC component 0 and layer 6 — the largest irreducible
core (§4). Foundationality rank is not monotone in activation count: rank 16
(`CONCEPT_090`, 84 ayahs) outranks many far larger concepts on the composite,
driven by its dependency incidence rather than its reach.

---

## 4. Largest strongly-connected (irreducible) structures

The Phase-5 `DEPENDS_ON ∪ REQUIRES` graph condenses to seven irreducible cores
(SCC size ≥ 2). Their per-member evidence (no meaning):

### 4.1 The size-9 core — component 0, layer 6

`CONCEPT_003 · 004 · 034 · 053 · 060 · 061 · 084 · 085 · 088`
(internal edges 20 · edge density 0.278). Independently surfaced by
foundationality, dependency layering, and hub removal.

| Concept | Found. rank | Act. | Layer | Top-3 roots |
|---|---:|---:|---:|---|
| `CONCEPT_003` | 4 | 1628 | 6 | غفر رحم موت |
| `CONCEPT_004` | 3 | 1005 | 6 | رود احد صلو |
| `CONCEPT_034` | 10 | 893 | 6 | رحم بعض صلح |
| `CONCEPT_053` | 7 | 1265 | 6 | عذب كفر يوم |
| `CONCEPT_060` | 14 | 621 | 6 | سوا حسن صلح |
| `CONCEPT_061` | 11 | 1194 | 6 | رسل امر رحم |
| `CONCEPT_084` | 12 | 1175 | 6 | قوم اخذ ظلم |
| `CONCEPT_085` | 9 | 889 | 6 | رسل اخذ بني |
| `CONCEPT_088` | 5 | 1126 | 6 | رسل كفر عذب |

**Raw observations:** all nine sit in layer 6; the root `رسل` is a dominant root
of three members (`061, 085, 088`), `رحم` of two (`003, 034, 061`), `عذب`/`كفر`
of two (`053, 088`). These are co-occurrence facts among member roots, stated
without interpretation.

### 4.2 Remaining irreducible cores (size desc)

| Size | Internal edges | Density | Concepts |
|---:|---:|---:|---|
| 4 | 7 | 0.583 | `CONCEPT_039 · 048 · 076 · 089` |
| 3 | 4 | 0.667 | `CONCEPT_002 · 090 · 091` |
| 3 | — | — | (further size-3 components) |
| 2 | — | — | (smallest cores) |

The single directional irreducible core (adding `PRECEDES`/`PREDICTS`) spans
**94 concepts** — there is no global precedence ordering; ordering is globally
cyclic, as Phase 5 reported. 102 of the 103 concepts (all but the hub-isolated
node) lie in the directional core.

---

## 5. Cross-core contrasts (evidence summary)

| Axis | `CONCEPT_007` (dominant) | `CONCEPT_016` (secondary) |
|---|---|---|
| Activation | 5,906 (corpus-wide) | 1,199 (clustered) |
| Surah uniqueness | none (lift ≈ 1.06) | high (lift up to 3.03, surah 65) |
| Dependency layer | 0 (base) | 7 (spire) |
| Dependency direction | `REQUIRES`-in only | `DEPENDS_ON`-out present |
| Relation diversity | 2 / 9 | 7 / 9 |
| Removal effect | fragments graph | reorganises, no fragmentation |

These are the structural signatures Phase 5 predicted (hub vs emergent core),
now grounded in Phase-6 root/lemma/ayah/surah evidence. No content claim is
made about either.

---

## 6. Outputs & reproduce

Source: `generated/identification/core_investigation.json` (1,146,133 bytes),
built by `scripts/build_identification.py`, validated by
`scripts/validate_identification.py --rebuild`.

```bash
python3 scripts/build_identification.py
python3 scripts/validate_identification.py --rebuild
```

**No meaning assigned. Concepts remain opaque.**
