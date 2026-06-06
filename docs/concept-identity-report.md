# Concept Identity Report — Phase 7

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase7-revelation-1.0`.

This report is the full Quran-internal identity catalogue for all 103 concepts.
Every "name" is a literal Arabic member token of the concept itself (the dominant
member lemma of its dominant member root) — **not a translation, gloss, or
meaning.** Anchors are the underlying roots. Confidence is the anchor root's
activation share; HHI is the concentration of root activation weight; competing
names are preserved. **No interpretation is supplied.** The reader supplies any
meaning; the engine supplies only the evidence.

---

## 1. How to read this catalogue

- **Top name** — the dominant member lemma (Arabic surface form) of the
  concept's dominant member root. It is an anchor, not a definition.
- **Anchor** — the dominant member root (Arabic).
- **Conf** — anchor root activation share (0–1).
- **HHI** — Herfindahl index of root activation weights (high = one root
  dominates → coherent; low = distributed identity).
- **Competing names** — all candidate anchors with share ≥ 0.15 (root-anchored,
  ≤ 5). Multiple entries = preserved competing identities.
- **Falsif.** — ✓ the single-anchor identity survives its falsification attack;
  ✗ it is falsified (does not explain a majority of its own evidence); — not
  tested (resists identification).

---

## 2. Identity tiers (summary)

| Tier | Count | Meaning (structural) |
|---|---:|---|
| strong | 43 | dominant anchor (conf ≥ 0.30, HHI ≥ 0.30) that survives falsification |
| moderate | 51 | clear anchor (conf ≥ 0.15) that survives falsification |
| weak | 3 | anchor exists but is falsified by its own evidence |
| resists | 6 | no member root reaches the dominance floor — distributed identity |

---

## 3. Full identity catalogue (all 103 concepts)

| Concept | Tier | Top name | Anchor | Conf | HHI | Competing names | Falsif. |
|---|---|---|---|---:|---:|---|:--:|
| `CONCEPT_001` | resists | — | — | 0.0 | 0.056 | — | — |
| `CONCEPT_002` | resists | — | — | 0.0 | 0.057 | — | — |
| `CONCEPT_003` | resists | — | — | 0.0 | 0.068 | — | — |
| `CONCEPT_004` | resists | — | — | 0.0 | 0.065 | — | — |
| `CONCEPT_005` | moderate | أَنشَأَ | نشا | 0.187 | 0.085 | أَنشَأَ | ✓ |
| `CONCEPT_006` | moderate | طَّلَعَ | طلع | 0.160 | 0.076 | طَّلَعَ | ✓ |
| `CONCEPT_007` | moderate | ٱللَّه | اله | 0.240 | 0.100 | ٱللَّه | ✓ |
| `CONCEPT_008` | moderate | خَلَقَ | خلق | 0.190 | 0.094 | خَلَقَ | ✓ |
| `CONCEPT_009` | moderate | كَفَىٰ | كفي | 0.320 | 0.140 | كَفَىٰ | ✓ |
| `CONCEPT_010` | moderate | رَّضِىَ | رضو | 0.342 | 0.185 | رَّضِىَ; جَٰهَدَ | ✓ |
| `CONCEPT_011` | weak | نَاصِح | نصح | 0.207 | 0.122 | نَاصِح; لَوْح | ✗ |
| `CONCEPT_012` | moderate | ٱنتَقَمْ | نقم | 0.243 | 0.111 | ٱنتَقَمْ | ✓ |
| `CONCEPT_013` | resists | — | — | 0.0 | 0.080 | — | — |
| `CONCEPT_014` | moderate | حِين | حين | 0.369 | 0.234 | حِين; يَشْعُرُ | ✓ |
| `CONCEPT_015` | moderate | سَأَلَ | سال | 0.323 | 0.192 | سَأَلَ; عَدُوّ | ✓ |
| `CONCEPT_016` | moderate | جَنَّة | جنن | 0.168 | 0.093 | جَنَّة | ✓ |
| `CONCEPT_017` | resists | — | — | 0.0 | 0.084 | — | — |
| `CONCEPT_018` | moderate | رِيح | روح | 0.194 | 0.122 | رِيح; سِحْر | ✓ |
| `CONCEPT_019` | moderate | شَفَٰعَة | شفع | 0.326 | 0.210 | شَفَٰعَة; أَحَاطَ; مَنَام | ✓ |
| `CONCEPT_020` | moderate | شَكَرَ | شكر | 0.331 | 0.199 | شَكَرَ; بَحْر | ✓ |
| `CONCEPT_021` | strong | ا^بَاء | ابو | 0.652 | 0.441 | ا^بَاء | ✓ |
| `CONCEPT_022` | moderate | لَعَنَ | لعن | 0.246 | 0.135 | لَعَنَ; مِّيثَٰق | ✓ |
| `CONCEPT_023` | moderate | غَرَّ | غرر | 0.244 | 0.131 | غَرَّ | ✓ |
| `CONCEPT_024` | moderate | شَجَرَة | شجر | 0.202 | 0.129 | شَجَرَة; تَبَارَكَ | ✓ |
| `CONCEPT_025` | moderate | ظِلّ | ظلل | 0.282 | 0.168 | ظِلّ; مَنَّ; حِجَارَة | ✓ |
| `CONCEPT_026` | moderate | صَرَفَ | صرف | 0.291 | 0.152 | صَرَفَ | ✓ |
| `CONCEPT_027` | moderate | رِّبَوٰا | ربو | 0.289 | 0.181 | رِّبَوٰا; وَبَال; ٱصْطَفَىٰ | ✓ |
| `CONCEPT_028` | moderate | صَدْر | صدر | 0.326 | 0.179 | صَدْر; أُخْفِىَ | ✓ |
| `CONCEPT_029` | moderate | قِنطَار | قنطر | 0.232 | 0.142 | قِنطَار; قَرْح | ✓ |
| `CONCEPT_030` | moderate | حَٰفِظ | حفظ | 0.393 | 0.209 | حَٰفِظ; فَرْج | ✓ |
| `CONCEPT_031` | moderate | رُفَٰت | رفت | 0.206 | 0.123 | رُفَٰت; تَبْذِير | ✓ |
| `CONCEPT_032` | moderate | عَرَبِيّ | عرب | 0.211 | 0.140 | عَرَبِيّ; حَوْل | ✓ |
| `CONCEPT_033` | moderate | سَبْع | سبع | 0.354 | 0.201 | سَبْع; يَسْتَفْتُ | ✓ |
| `CONCEPT_034` | moderate | رَّحِيم | رحم | 0.240 | 0.141 | رَّحِيم | ✓ |
| `CONCEPT_035` | moderate | فَقِير | فقر | 0.250 | 0.199 | فَقِير; يَتِيم; نَكَحَ; دَفَعْ | ✓ |
| `CONCEPT_036` | strong | حَمِيم | حمم | 0.533 | 0.337 | حَمِيم; ٱصْطَفَىٰ | ✓ |
| `CONCEPT_037` | moderate | قَمَر | قمر | 0.197 | 0.160 | قَمَر; عَرْش; تَبَارَكَ; نَّجْم | ✓ |
| `CONCEPT_038` | moderate | لَبِثَ | لبث | 0.454 | 0.265 | لَبِثَ; مِائَة | ✓ |
| `CONCEPT_039` | moderate | سِّجْن | سجن | 0.346 | 0.215 | سِّجْن; قَمِيص; قُدَّ; أَلْفَ | ✓ |
| `CONCEPT_040` | moderate | أَعْتَدَتْ | عتد | 0.364 | 0.268 | أَعْتَدَتْ; أَحَاطَ | ✓ |
| `CONCEPT_041` | weak | حَدَب | حدب | 0.169 | 0.144 | حَدَب | ✗ |
| `CONCEPT_042` | moderate | وَاد | ودي | 0.436 | 0.265 | وَاد; مَكَثَ | ✓ |
| `CONCEPT_043` | weak | مَرْفُود | رفد | 0.203 | 0.148 | مَرْفُود | ✗ |
| `CONCEPT_044` | moderate | بَسَطَ | بسط | 0.320 | 0.217 | بَسَطَ; غِلّ; حَرْب | ✓ |
| `CONCEPT_045` | moderate | سُقِطَ | سقط | 0.361 | 0.221 | سُقِطَ; نَخْل; جِذْع | ✓ |
| `CONCEPT_046` | moderate | مَغَانِم | غنم | 0.476 | 0.293 | مَغَانِم; ٱخْتَلَطَ | ✓ |
| `CONCEPT_047` | moderate | رَاكِع | ركع | 0.300 | 0.237 | رَاكِع; غَلِيظ; سِيمَٰ | ✓ |
| `CONCEPT_048` | moderate | قَمِيص | قمص | 0.357 | 0.258 | قَمِيص; قُدَّ | ✓ |
| `CONCEPT_049` | moderate | لَيْل | ليل | 0.450 | 0.269 | لَيْل | ✓ |
| `CONCEPT_050` | moderate | خَٰلَٰت | خول | 0.280 | 0.214 | خَٰلَٰت; يَعْرُجُ; شَتَّىٰ; حَرَج | ✓ |
| `CONCEPT_051` | moderate | سَرْمَد | سرمد | 0.356 | 0.213 | سَرْمَد; تَنُو^أُ | ✓ |
| `CONCEPT_052` | moderate | سِدْر | سدر | 0.391 | 0.238 | سِدْر; سَيْل | ✓ |
| `CONCEPT_053` | moderate | عَذَاب | عذب | 0.276 | 0.212 | عَذَاب; كَفَرَ; يَوْم; ا^خِر | ✓ |
| `CONCEPT_054` | strong | عَقَلُ | عقل | 0.411 | 0.317 | عَقَلُ; أَعْمَىٰ; أَصَمّ | ✓ |
| `CONCEPT_055` | moderate | لَغْو | لغو | 0.354 | 0.221 | لَغْو; تَحْرِير; أَوْسَط | ✓ |
| `CONCEPT_056` | moderate | مُّهِين | هون | 0.429 | 0.287 | مُّهِين; مَّطَر; وَدَّ | ✓ |
| `CONCEPT_057` | moderate | حَتْم | حتم | 0.288 | 0.222 | حَتْم; ضِدّ; حَنَان | ✓ |
| `CONCEPT_058` | strong | ٱعْتَصَمُ | عصم | 0.532 | 0.360 | ٱعْتَصَمُ; حَبْل | ✓ |
| `CONCEPT_059` | strong | قَصْر | قصر | 0.484 | 0.307 | قَصْر; مُّعَطَّلَة | ✓ |
| `CONCEPT_060` | moderate | سُو^ء | سوا | 0.450 | 0.280 | سُو^ء; مُحْسِن | ✓ |
| `CONCEPT_061` | moderate | رَسُول | رسل | 0.375 | 0.240 | رَسُول; أَمْر; رَحْمَة; جَا^ءَ | ✓ |
| `CONCEPT_062` | strong | ضَاقَ | ضيق | 0.631 | 0.452 | ضَاقَ; رَحُبَتْ | ✓ |
| `CONCEPT_063` | strong | سِحْر | سحر | 0.760 | 0.596 | سِحْر | ✓ |
| `CONCEPT_064` | strong | يُوزَعُ | وزع | 0.540 | 0.359 | يُوزَعُ; نَّمْل | ✓ |
| `CONCEPT_065` | strong | نُسِفَتْ | نسف | 0.385 | 0.315 | نُسِفَتْ; سَّامِرِىّ | ✓ |
| `CONCEPT_066` | strong | صَفّ | صفف | 0.726 | 0.549 | صَفّ | ✓ |
| `CONCEPT_067` | strong | كَفَىٰ | كفي | 0.566 | 0.460 | كَفَىٰ; يَتِيم | ✓ |
| `CONCEPT_068` | moderate | وَطَر | وطر | 0.311 | 0.222 | وَطَر; نَحْب; مُعَوِّقِين; جَوْف | ✓ |
| `CONCEPT_069` | strong | صَاعِقَة | صعق | 0.597 | 0.402 | صَاعِقَة | ✓ |
| `CONCEPT_070` | moderate | خَيْل | خيل | 0.452 | 0.289 | خَيْل; مَرَح; فَخُور | ✓ |
| `CONCEPT_071` | strong | جَٰهَدَ | جهد | 0.474 | 0.375 | جَٰهَدَ; تَرَبَّصْ | ✓ |
| `CONCEPT_072` | strong | شَرِبَ | شرب | 0.549 | 0.394 | شَرِبَ; ثَمَرَٰت; ٱصْطَفَىٰ | ✓ |
| `CONCEPT_073` | strong | كَتَمَ | كتم | 0.417 | 0.340 | كَتَمَ; ٱشْتَرَىٰ | ✓ |
| `CONCEPT_074` | strong | ٱشْتَرَىٰ | شري | 0.505 | 0.340 | ٱشْتَرَىٰ; يُؤَدِّ; زَلَلْ | ✓ |
| `CONCEPT_075` | strong | عَزْم | عزم | 0.438 | 0.351 | عَزْم; لِن; شَاوِرْ | ✓ |
| `CONCEPT_076` | strong | قَمِيص | قمص | 0.430 | 0.302 | قَمِيص; ذِّئْب; جُبّ | ✓ |
| `CONCEPT_077` | strong | أَنقَذَ | نقذ | 0.440 | 0.339 | أَنقَذَ; طَّالِب | ✓ |
| `CONCEPT_078` | strong | زَوْج | زوج | 0.641 | 0.463 | زَوْج; قَانِت | ✓ |
| `CONCEPT_079` | strong | زَلَلْ | زلل | 0.419 | 0.309 | زَلَلْ; إِصْر; طَاقَة | ✓ |
| `CONCEPT_080` | strong | غَلَبُ | غلب | 0.609 | 0.444 | غَلَبُ; أَلْف | ✓ |
| `CONCEPT_081` | strong | ٱللَّه | اله | 0.629 | 0.442 | ٱللَّه | ✓ |
| `CONCEPT_082` | strong | ءَالَا^ء | الو | 0.669 | 0.508 | ءَالَا^ء; قَصْر | ✓ |
| `CONCEPT_083` | strong | أُنثَىٰ | انث | 0.615 | 0.497 | أُنثَىٰ; ٱثْنَيْن | ✓ |
| `CONCEPT_084` | strong | قَوْم | قوم | 0.468 | 0.317 | قَوْم; أَخَذَ; ظَالِم | ✓ |
| `CONCEPT_085` | strong | رَسُول | رسل | 0.451 | 0.309 | رَسُول; أَخَذَ; بُنَىّ | ✓ |
| `CONCEPT_086` | strong | يَحِيفَ | حيف | 0.455 | 0.312 | يَحِيفَ; لِوَاذ; أَيَٰمَىٰ | ✓ |
| `CONCEPT_087` | strong | بُرْهَٰن | برهن | 0.422 | 0.340 | بُرْهَٰن; أَبْيَض | ✓ |
| `CONCEPT_088` | strong | رَسُول | رسل | 0.384 | 0.305 | رَسُول; كَفَرَ; عَذَاب | ✓ |
| `CONCEPT_089` | strong | يَعْصِرُ | عصر | 0.540 | 0.394 | يَعْصِرُ; سِّجْن; خَمْر | ✓ |
| `CONCEPT_090` | strong | أَحَلَّ | حلل | 0.511 | 0.366 | أَحَلَّ; عَفَا | ✓ |
| `CONCEPT_091` | strong | مَّعْرُوف | عرف | 0.724 | 0.566 | مَّعْرُوف; فَقِير | ✓ |
| `CONCEPT_092` | strong | يَنْحِتُ | نحت | 0.503 | 0.370 | يَنْحِتُ; تَعْثَ | ✓ |
| `CONCEPT_093` | strong | عَام | عوم | 0.429 | 0.321 | عَام; نَّسِى^ء; يَطَ_#ُ | ✓ |
| `CONCEPT_094` | strong | بَغْتَة | بغت | 0.390 | 0.308 | بَغْتَة; مِيقَٰت; جَلَّىٰ | ✓ |
| `CONCEPT_095` | strong | صَيْحَة | صيح | 0.805 | 0.662 | صَيْحَة | ✓ |
| `CONCEPT_096` | strong | دَلَّ | دلل | 0.493 | 0.342 | دَلَّ; وَرَق; طَفِقَ | ✓ |
| `CONCEPT_097` | moderate | جَرَيْ | جري | 0.377 | 0.293 | جَرَيْ; تَحْت; ثَوَاب | ✓ |
| `CONCEPT_098` | strong | غُرْفَة | غرف | 0.461 | 0.344 | غُرْفَة; جَاوَزَ | ✓ |
| `CONCEPT_099` | strong | دَرَجَة | درج | 0.612 | 0.437 | دَرَجَة; يَفْسَحِ | ✓ |
| `CONCEPT_100` | strong | كَادِح | كدح | 0.447 | 0.302 | كَادِح; هَلُوع; كَبَد; كَنُود | ✓ |
| `CONCEPT_101` | strong | كَهْف | كهف | 0.397 | 0.303 | كَهْف; مُرْتَفَق; يُهَيِّئْ | ✓ |
| `CONCEPT_102` | moderate | تَجَسَّسُ | جسس | 0.308 | 0.255 | تَجَسَّسُ; يَلِتْ; أَلْقَٰب; تَنَابَزُ | ✓ |
| `CONCEPT_103` | strong | يَمْتَرُ | مري | 0.516 | 0.407 | يَمْتَرُ; رَجِيم | ✓ |

---

## 4. Notable patterns (evidence only)

- **Shared anchors.** `اله` heads both `CONCEPT_007` and `CONCEPT_081`; `رسل`
  heads `CONCEPT_061`, `085`, `088` (three members of the size-9 dependency
  core); `كفي` heads `009` and `067`; `قمص` heads `048` and `076`. The shared
  anchor is reported, not resolved — the concepts differ in their remaining
  evidence.
- **Strongest single identities** (highest HHI): `CONCEPT_095` (`صَيْحَة`, 0.66),
  `063` (`سِحْر`, 0.60), `091` (`مَّعْرُوف`, 0.57), `066` (`صَفّ`, 0.55),
  `082` (`ءَالَا^ء`, 0.51) — small, lexically tight concepts.
- **Most distributed identities** (resist): the 15–34-root concepts `001`–`004`,
  `013`, `017`.
- **Strong vs reach.** The highest-activation concepts (`007`, `003`, `004` — the
  Phase-5 core) are precisely those with the *weakest* single identity: reach and
  lexical concentration are inversely related here.

---

## 5. Reproduce

```bash
python3 scripts/build_revelation.py
python3 scripts/validate_revelation.py --rebuild
```

**No meaning assigned. Names are Quran-internal Arabic tokens only.**
