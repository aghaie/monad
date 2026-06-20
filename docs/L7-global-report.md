# L7 — Global Structure of the Self-Interpreting Network

- **Layer:** L7 (Monad v2), built on the validated inter-ayah network (L6).
- **Source:** `generated/monad.db`. Outputs: `generated/layers/L7_global/`.
- **Reproducibility:** `validate_L7_global.py` passes 8/8, byte-identical re-run.

## Products

### 1. The Quran-by-Quran cross-reference map (`crossref_index.json`)

For every one of the 6,236 ayat, the verses across the Quran that most explain it
— ranked by **rare-root, idf-weighted shared content** (so connections reflect
specific shared concepts, not ubiquitous function words). This is the
computational *tafsīr al-Qurʾān bi-l-Qurʾān* (Quran-by-Quran) map, built entirely
internally.

*Example* — verses linked to **2:255 (Āyat al-Kursī)**: 7:97, 8:43, 25:47, 30:23,
37:102 — all **cross-sura**, joined by a rare content root they share with it. The
links are concrete and sensible.

### 2. Suras are coherent communities (a falsifiable structural result)

Do connections concentrate *within* suras beyond chance? Test: intra-sura share
of total connection weight vs a **sura-label permutation null** (200×).

| | intra-sura weight fraction |
|---|---:|
| **Real** | **0.052** |
| Permuted-label null | 0.017 ± 0.0004 (max 0.0185) |

p = 0.005 (real beats every one of 200 permutations). Connections concentrate
within suras **~3× more than chance** — **suras are coherent communities of the
self-interpreting network**, not arbitrary groupings. This is new, independent,
leakage-controlled structural evidence on top of L6.

### 3. Network shape & hubs

Weighted pairs: 84,477. Degree: max 266, median 20 — a heavy-tailed network with
hub verses.

**Honest caveat on hubs:** the most-connecting verses (2:196, 4:102, 2:282 —
the longest verse in the Quran, …) are dominated by **verse length**: longer
verses have more rare roots and therefore more connections. So the raw hub list
reflects length, not a deep "centrality" claim. It is reported as descriptive
structure, not as an importance ranking.

## Where L7 sits

| Layer | Finding |
|-------|---------|
| **L3 roots** | robust relational meaning |
| **L6 inter-ayah** | verses explain one another (~10× rare content, p=0.005) |
| **L7 global** | suras are coherent network communities (~3×, p=0.005) + Quran-by-Quran map |

Two independent, leakage-controlled positives now describe the self-interpreting
network: verses explain each other (L6), and that explanation structure organizes
into coherent suras (L7).

## Prohibitions observed

No external glosses, dictionaries, tafsir, translations, or pretrained models —
the cross-reference map and community structure are derived entirely from the
corpus.
