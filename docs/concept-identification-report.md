# Concept Identification Report — Phase 6

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase6-identification-1.0`.

Phase 6 built the **Concept Identification Engine**. Its sole purpose is to
reveal *what Quran-internal evidence defines each discovered concept* — its
dominant roots, dominant lemmas, most strongly activating ayahs, carrying
surahs, and surrounding structures. It assigns **no meaning**. No concept is
renamed, labelled, translated, or interpreted. Concept ids and relation types
stay opaque exactly as in Phases 3–5. The Quran is the only semantic universe;
no dictionary, tafsir, translation, theology, ontology, embedding, or
interpretation is used. Phases 1–5 are read and hashed but never rebuilt.

---

## 1. Method

**Concept activation** reuses the Phase-4 rule exactly: an ayah *activates* a
concept iff any of its word tokens carries a `root_id` or `lemma_id` that is a
member of that concept. On top of this binary rule the engine computes an
evidence-weighted **activation strength** per `(concept, ayah)`: the summed
Phase-3 membership confidence of the member tokens that fire in the ayah, each
word counted once at its strongest membership.

Cross-check: 6,101 ayahs carry at least one concept — **byte-for-byte the same
active-ayah population Phase 4 reported**. `CONCEPT_081` activates exactly 2,553
ayahs, matching its Phase-4 `REQUIRES → CONCEPT_007` support count. Activation is
therefore consistent with all prior phases, not a fresh re-derivation.

From activation plus the Phase-3/4/5 products, seven evidence layers are
produced:

| Phase | Product | Evidence exposed (no meaning) |
|---|---|---|
| A | `concept_profiles.json` | size, members, activation, distribution, centrality, compression, dependency metrics |
| B | `dominant_roots.json` | per concept: roots ranked by activation weight, neighbourhood influence, stability |
| C | `dominant_lemmas.json` | per concept: lemmas ranked by activation weight, graph influence |
| D | `ayah_signatures.json` | per concept: top-25 / 50 / 100 most strongly activating ayahs + firing members |
| E | `surah_signatures.json` | per concept: highest-activation / highest-density / highest-uniqueness surahs |
| F | `concept_atlas.json` | per concept: closest concepts, strongest dependencies, propositions, bridges, cycles |
| G | `core_investigation.json` | deep evidence dossiers for the dominant core, secondary core, top-20, largest SCCs |

Everything is deterministic, pure-stdlib, byte-identically reproducible —
verified by `validate_identification.py --rebuild` (**18,839 checks pass**).

---

## 2. Metric definitions (evidence only)

| Metric | Definition |
|---|---|
| `activation_count` | distinct ayahs that activate the concept |
| `activation_strength` (ayah) | summed Phase-3 membership confidence of the member tokens firing in the ayah |
| `confidence` (ayah) | `activation_strength` / the concept's maximum `activation_strength` |
| `activation_weight` (root/lemma) | `in_concept_token_count × membership_confidence` |
| `activation_share` | `activation_weight` normalised to sum 1 across the concept's members |
| `neighborhood_influence` / `graph_influence` | summed Phase-2 semantic-neighbour confidence from the entity to its concept co-members |
| `stability_contribution` | Phase-3 `membership_confidence` (perturbation-survival fraction) |
| `density` (surah) | `activating_ayahs / surah_ayah_count` |
| `uniqueness_lift` (surah) | surah density ÷ the concept's corpus-wide activation rate; `>1` = over-represented |

No metric encodes meaning, valuation, or interpretation. All are corpus counts
or prior-phase graph quantities.

---

## 3. Aggregate findings (no interpretation)

- **103 concepts, all active.** Every concept activates ≥ 3 ayahs. Activation is
  extremely skewed: min 3, **max 5,906**, median 53, mean 256.
- **One concept dominates activation.** `CONCEPT_007` activates **5,906 / 6,101**
  active ayahs (96.8%) — it is the Phase-5 dominant hub and Phase-1 foundationality
  rank 1. The next, `CONCEPT_081`, activates 2,553.
- **Activation rank tracks foundationality rank loosely but not exactly.** The
  ten most-activating concepts all sit in the top-15 foundationality ranks; but
  small high-confidence concepts (e.g. `CONCEPT_081`, 4 roots / 2,553 ayahs) can
  out-activate large diffuse ones.
- **Member size and activation are decoupled.** The largest concept by roots
  (`CONCEPT_001`, 34 roots) activates only 429 ayahs; the second-most-activating
  (`CONCEPT_081`) has just 4 roots. Concept extent ≠ concept reach.
- **Distinct surah signatures.** Concepts localise sharply: `CONCEPT_102`
  (3 ayahs) is confined to surah 49; `CONCEPT_007` is spread across all surahs
  with near-flat uniqueness lift (≈ 1.06 everywhere) — it is the only concept
  with no distinctive surah, consistent with its hub role.

---

## 4. Per-concept evidence table (all 103)

Dominant roots are the top-4 by `activation_weight`. "Top ayah" is the single
most strongly activating ayah. "Top surah" is the surah with the most activating
ayahs. Foundationality rank is Phase-5. **Roots/ayahs shown as raw evidence only
— no gloss is attached to any of them.**

| Concept | Act. ayahs | Roots | Lemmas | Found. rank | Dominant roots (top 4) | Top ayah | Top surah |
|---|---:|---:|---:|---:|---|---|---:|
| `CONCEPT_001` | 429 | 34 | 135 | 13 | يسر عدد حجج حدد | 2:196 | 2 |
| `CONCEPT_002` | 550 | 33 | 123 | 8 | ولد عرف قرب نسو | 4:12 | 2 |
| `CONCEPT_003` | 1628 | 32 | 162 | 4 | غفر رحم موت سلم | 5:3 | 2 |
| `CONCEPT_004` | 1005 | 31 | 124 | 3 | رود احد صلو وجد | 5:6 | 4 |
| `CONCEPT_005` | 135 | 26 | 62 | 38 | نشا ركب نخل ثمر | 6:99 | 6 |
| `CONCEPT_006` | 131 | 25 | 53 | 42 | طلع فرر شمل شمس | 18:18 | 18 |
| `CONCEPT_007` | 5906 | 24 | 326 | 1 | اله كون قول علم | 2:282 | 2 |
| `CONCEPT_008` | 690 | 21 | 95 | 15 | خلق بلغ بعث اجل | 22:5 | 2 |
| `CONCEPT_009` | 61 | 21 | 28 | 41 | كفي ميل وفق سلح | 4:102 | 4 |
| `CONCEPT_010` | 136 | 18 | 39 | 19 | رضو جهد نفر حلف | 9:109 | 9 |
| `CONCEPT_011` | 51 | 18 | 30 | 66 | نصح لوح غضب اسف | 7:150 | 7 |
| `CONCEPT_012` | 71 | 18 | 38 | 52 | نقم عون صيد دوم | 5:95 | 5 |
| `CONCEPT_013` | 195 | 17 | 46 | 17 | قسط ملل حضر بيع | 2:282 | 2 |
| `CONCEPT_014` | 106 | 16 | 28 | 61 | حين شعر خفف جلد | 16:80 | 16 |
| `CONCEPT_015` | 326 | 16 | 59 | 26 | سال عدو بدل عصي | 2:61 | 2 |
| `CONCEPT_016` | 1199 | 16 | 90 | 6 | جنن وعد نور وقي | 47:15 | 2 |
| `CONCEPT_017` | 16 | 15 | 16 | 78 | خبت بهم ذبب عتق | 22:73 | 22 |
| `CONCEPT_018` | 221 | 15 | 53 | 44 | روح سحر طير برا | 5:110 | 26 |
| `CONCEPT_019` | 99 | 14 | 29 | 43 | شفع حوط نوم وسع | 2:255 | 2 |
| `CONCEPT_020` | 175 | 14 | 38 | 31 | شكر بحر فلك لبس | 35:12 | 2 |
| `CONCEPT_021` | 140 | 14 | 29 | 49 | ابو كيل سرق بضع | 12:65 | 12 |
| `CONCEPT_022` | 143 | 13 | 46 | 30 | لعن وثق وضع خون | 5:13 | 2 |
| `CONCEPT_023` | 94 | 13 | 27 | 64 | غرر لهو لعب لبب | 57:20 | 3 |
| `CONCEPT_024` | 127 | 12 | 38 | 48 | شجر برك شرق غرب | 24:35 | 2 |
| `CONCEPT_025` | 152 | 12 | 44 | 18 | ظلل منن حجر عشر | 7:160 | 2 |
| `CONCEPT_026` | 104 | 12 | 30 | 60 | صرف كود سنو خلل | 24:43 | 17 |
| `CONCEPT_027` | 52 | 11 | 27 | 34 | ربو وبل صفو بيع | 2:275 | 2 |
| `CONCEPT_028` | 168 | 11 | 42 | 39 | صدر خفي طوف جهل | 3:154 | 7 |
| `CONCEPT_029` | 14 | 10 | 11 | 65 | قنطر قرح بهل رمز | 3:140 | 3 |
| `CONCEPT_030` | 94 | 10 | 27 | 28 | حفظ فرج بدو بعل | 24:31 | 12 |
| `CONCEPT_031` | 12 | 10 | 12 | 82 | رفت بذر نغض هجد | 17:26 | 17 |
| `CONCEPT_032` | 98 | 9 | 27 | 46 | عرب حول مدن ضيع | 9:120 | 9 |
| `CONCEPT_033` | 65 | 9 | 30 | 57 | سبع فتي عبر سنبل | 12:43 | 12 |
| `CONCEPT_034` | 893 | 8 | 48 | 10 | رحم بعض صلح عظم | 48:29 | 2 |
| `CONCEPT_035` | 58 | 8 | 17 | 21 | فقر يتم نكح دفع | 4:6 | 2 |
| `CONCEPT_036` | 44 | 8 | 15 | 29 | حمم صفو لذذ خمر | 47:15 | 2 |
| `CONCEPT_037` | 105 | 8 | 20 | 59 | قمر عرش برك نجم | 7:54 | 6 |
| `CONCEPT_038` | 53 | 8 | 13 | 45 | لبث ماي حمر عوم | 2:259 | 18 |
| `CONCEPT_039` | 26 | 7 | 12 | 55 | سجن قمص قدد لفو | 12:25 | 12 |
| `CONCEPT_040` | 54 | 7 | 17 | 53 | عتد حوط مهل غوث | 18:29 | 4 |
| `CONCEPT_041` | 6 | 7 | 7 | 99 | حدب فتق رتق فهم | 21:30 | 21 |
| `CONCEPT_042` | 37 | 7 | 19 | 68 | ودي مكث وقد زبد | 13:17 | 28 |
| `CONCEPT_043` | 7 | 7 | 9 | 97 | رفد سعد حنذ روع | 11:44 | 11 |
| `CONCEPT_044` | 59 | 7 | 18 | 40 | بسط غلل حرب فوه | 5:64 | 5 |
| `CONCEPT_045` | 32 | 7 | 15 | 76 | سقط نخل جذع جني | 19:25 | 6 |
| `CONCEPT_046` | 24 | 6 | 15 | 72 | غنم خلط بقر حوي | 6:146 | 2 |
| `CONCEPT_047` | 47 | 6 | 19 | 47 | ركع غلظ سوم غيظ | 48:29 | 3 |
| `CONCEPT_048` | 10 | 6 | 7 | 75 | قمص قدد غلق هيت | 12:25 | 12 |
| `CONCEPT_049` | 202 | 6 | 17 | 23 | ليل نهر شمس قمر | 31:29 | 2 |
| `CONCEPT_050` | 29 | 6 | 12 | 50 | خول عرج شتت حرج | 24:61 | 33 |
| `CONCEPT_051` | 7 | 6 | 6 | 95 | سرمد نوا بقع جذو | 28:71 | 28 |
| `CONCEPT_052` | 7 | 6 | 9 | 98 | سدر سيل اثل عرم | 34:16 | 34 |
| `CONCEPT_053` | 1265 | 6 | 35 | 7 | عذب كفر يوم اخر | 57:20 | 2 |
| `CONCEPT_054` | 81 | 6 | 12 | 70 | عقل عمي صمم بكم | 2:171 | 2 |
| `CONCEPT_055` | 44 | 6 | 24 | 22 | لغو حرر وسط عقد | 5:89 | 2 |
| `CONCEPT_056` | 80 | 6 | 25 | 36 | هون مطر ودد حذر | 4:102 | 4 |
| `CONCEPT_057` | 5 | 5 | 5 | 100 | حتم ضدد حنن شعل | 19:71 | 19 |
| `CONCEPT_058` | 23 | 5 | 11 | 63 | عصم حبل نقذ حفر | 3:103 | 3 |
| `CONCEPT_059` | 17 | 5 | 12 | 67 | قصر عطل شيد خوي | 22:45 | 4 |
| `CONCEPT_060` | 621 | 5 | 39 | 14 | سوا حسن صلح اهل | 17:7 | 4 |
| `CONCEPT_061` | 1194 | 5 | 33 | 11 | رسل امر رحم جيا | 4:83 | 7 |
| `CONCEPT_062` | 16 | 5 | 10 | 92 | ضيق رحب لجا جمح | 9:118 | 9 |
| `CONCEPT_063` | 70 | 5 | 12 | 62 | سحر عصو لقف ثعب | 20:69 | 26 |
| `CONCEPT_064` | 9 | 5 | 8 | 93 | وزع نمل عفر بسم | 27:18 | 27 |
| `CONCEPT_065` | 10 | 5 | 7 | 96 | نسف سمر زهر عنو | 20:97 | 20 |
| `CONCEPT_066` | 15 | 5 | 13 | 90 | صفف بدن قنع عرر | 22:36 | 37 |
| `CONCEPT_067` | 53 | 5 | 6 | 33 | كفي يتم حوب بدر | 4:6 | 4 |
| `CONCEPT_068` | 5 | 5 | 5 | 89 | وطر نحب عوق جوف | 33:37 | 33 |
| `CONCEPT_069` | 16 | 5 | 8 | 81 | صعق صبع رعد برق | 2:19 | 2 |
| `CONCEPT_070` | 15 | 5 | 11 | 84 | خيل مرح فخر خدد | 31:18 | 17 |
| `CONCEPT_071` | 57 | 5 | 12 | 37 | جهد ربص تجر قرف | 9:24 | 9 |
| `CONCEPT_072` | 69 | 4 | 18 | 25 | شرب ثمر صفو لبن | 47:15 | 2 |
| `CONCEPT_073` | 48 | 4 | 6 | 32 | كتم شري ادي سبط | 2:283 | 2 |
| `CONCEPT_074` | 34 | 4 | 9 | 35 | شري ادي زلل زحزح | 3:187 | 2 |
| `CONCEPT_075` | 16 | 4 | 11 | 74 | عزم لين شور فظظ | 3:159 | 2 |
| `CONCEPT_076` | 12 | 4 | 4 | 83 | قمص ذاب جبب طرح | 12:18 | 12 |
| `CONCEPT_077` | 7 | 4 | 8 | 88 | نقذ طلب ذبب سلب | 22:73 | 36 |
| `CONCEPT_078` | 107 | 4 | 11 | 27 | زوج قنت اذي سرح | 33:37 | 2 |
| `CONCEPT_079` | 11 | 4 | 8 | 73 | زلل اصر طوق غمض | 2:286 | 2 |
| `CONCEPT_080` | 56 | 4 | 14 | 71 | غلب الف ماي فاي | 8:66 | 8 |
| `CONCEPT_081` | 2553 | 4 | 31 | 2 | اله يوم كفر بين | 2:282 | 2 |
| `CONCEPT_082` | 50 | 4 | 12 | 86 | الو قصر نحت سهل | 7:74 | 55 |
| `CONCEPT_083` | 46 | 4 | 11 | 51 | انث ثني ضان معز | 6:143 | 4 |
| `CONCEPT_084` | 1175 | 4 | 47 | 12 | قوم اخذ ظلم بعد | 7:150 | 2 |
| `CONCEPT_085` | 889 | 4 | 26 | 9 | رسل اخذ بني سبل | 7:146 | 4 |
| `CONCEPT_086` | 4 | 4 | 4 | 101 | حيف لوذ ايم زجج | 24:35 | 24 |
| `CONCEPT_087` | 20 | 4 | 6 | 80 | برهن بيض ضمم جيب | 28:32 | 2 |
| `CONCEPT_088` | 1126 | 4 | 32 | 5 | رسل كفر عذب صوب | 35:39 | 2 |
| `CONCEPT_089` | 21 | 4 | 11 | 56 | عصر سجن خمر خبز | 12:36 | 12 |
| `CONCEPT_090` | 84 | 4 | 21 | 16 | حلل عفو صوم عقد | 2:237 | 2 |
| `CONCEPT_091` | 79 | 4 | 16 | 20 | عرف فقر حصر لحف | 2:273 | 2 |
| `CONCEPT_092` | 8 | 4 | 4 | 91 | نحت عثو فره سهل | 7:74 | 26 |
| `CONCEPT_093` | 12 | 4 | 8 | 58 | عوم نسا وطا نجس | 9:37 | 9 |
| `CONCEPT_094` | 30 | 4 | 10 | 79 | بغت وقت جلو حفو | 7:187 | 7 |
| `CONCEPT_095` | 14 | 4 | 4 | 87 | صيح جسم سند خشب | 63:4 | 36 |
| `CONCEPT_096` | 12 | 4 | 7 | 94 | دلل ورق طفق خصف | 7:22 | 20 |
| `CONCEPT_097` | 113 | 4 | 23 | 24 | جري تحت ثوب طهر | 18:31 | 3 |
| `CONCEPT_098` | 20 | 4 | 10 | 77 | غرف جوز فاي طوق | 2:249 | 8 |
| `CONCEPT_099` | 23 | 4 | 8 | 54 | درج فسح نشز جلس | 58:11 | 4 |
| `CONCEPT_100` | 4 | 4 | 5 | 102 | كدح هلع كبد كند | 84:6 | 70 |
| `CONCEPT_101` | 12 | 4 | 8 | 69 | كهف رفق هيا سردق | 18:16 | 18 |
| `CONCEPT_102` | 3 | 4 | 4 | 103 | جسس ليت لقب نبز | 49:11 | 49 |
| `CONCEPT_103` | 42 | 4 | 17 | 85 | مري رجم خمس كلب | 18:22 | 3 |

---

## 5. Raw-evidence dossiers (special requirement)

Below, six representative concepts are shown with full raw evidence — roots,
lemmas, ayahs, surahs, and graph metrics — and **no interpretation whatsoever**.
The deep dossiers for the dominant core, secondary core, top-20 foundational
concepts, and the largest SCC structures are in `core-investigation-report.md`.

### `CONCEPT_081` — 2nd most activating, 4 roots

- **Dominant roots (activation weight):** `اله` , `يوم` , `كفر` , `بين`
- **Dominant lemmas:** `ٱللَّه` , `يَوْم` , `كَفَرَ` , `بَيْن`
- **Activation:** 2,553 ayahs · top ayah **2:282** · top surah **2** (285 ayahs)
- **Compression:** foundationality rank **2**, removal destroys a large support mass
- **Atlas:** closest concept `CONCEPT_007`; dependency layer / SCC: shares the
  hub's lowest layer; proposition bridge.

### `CONCEPT_053` — 6 roots / 1,265 ayahs

- **Dominant roots:** `عذب` , `كفر` , `يوم` , `اخر`
- **Top ayah 57:20**, top surah **2**; member of the 9-concept dependency SCC.

### `CONCEPT_049` — 6 roots / 202 ayahs

- **Dominant roots:** `ليل` , `نهر` , `شمس` , `قمر`
- **Top ayah 31:29**, top surah **2**; highly cohesive (Phase-3), localised
  uniqueness peaks in short surahs.

### `CONCEPT_021` — 14 roots / 140 ayahs

- **Dominant roots:** `ابو` , `كيل` , `سرق` , `بضع`
- **Top ayah 12:65**, top surah **12** — strongly surah-localised (uniqueness
  concentrated in one surah).

### `CONCEPT_018` — 15 roots / 221 ayahs

- **Dominant roots:** `روح` , `سحر` , `طير` , `برا`
- **Top ayah 5:110**, top surah **26**.

### `CONCEPT_102` — 4 roots / 3 ayahs (rarest)

- **Dominant roots:** `جسس` , `ليت` , `لقب` , `نبز`
- **All 3 activating ayahs in surah 49**; foundationality rank **103** (last).

---

## 6. Outputs

`generated/identification/`:

| File | Bytes | Contents |
|---|---:|---|
| `concept_profiles.json` | 667,273 | Phase A — full per-concept evidence profile |
| `dominant_roots.json` | 349,567 | Phase B — ranked member roots per concept |
| `dominant_lemmas.json` | 894,361 | Phase C — ranked member lemmas per concept |
| `ayah_signatures.json` | 5,787,884 | Phase D — top 25/50/100 activating ayahs per concept |
| `surah_signatures.json` | 558,057 | Phase E — surah activation/density/uniqueness per concept |
| `concept_atlas.json` | 506,637 | Phase F — neighbours, dependencies, propositions, bridges, cycles |
| `core_investigation.json` | 1,146,133 | Phase G — deep dossiers for core/secondary/top-20/SCCs |
| `identification_manifest.json` | 2,713 | constants, input SHA-256, output bytes, prohibitions, totals |

Tooling: `scripts/build_identification.py` (≈ 0.6 s, pure stdlib),
`scripts/validate_identification.py` (18,839 checks, `--rebuild` byte-identical).

---

## 7. Limitations

- **Inherited activation rule.** Activation is the Phase-4 membership-union rule;
  a different rule (e.g. confidence-thresholded) would re-weight every ranking.
- **Strength weighting is one deterministic choice** (summed membership
  confidence); raw token counts and confidences are published for re-ranking.
- **Multi-membership.** Roots/lemmas in several concepts contribute to each; the
  per-concept shares are not partitioned exclusively.
- **No meaning.** Every root, lemma, ayah, surah, and concept id is raw
  evidence. This engine exposes evidence; it does not explain it.

---

## 8. Prohibitions observed

`no concept renaming · no concept labels · no assigned meanings · no root
translation · no lemma translation · no ontology · no axioms · no contradiction
engine · no theology · no doctrine · no divine origin claim · no human origin
claim · no interpretation · no external knowledge · concepts remain opaque ·
prior phases never rebuilt.`

---

## 9. Reproduce

```bash
python3 scripts/build_identification.py
python3 scripts/validate_identification.py --rebuild
```
