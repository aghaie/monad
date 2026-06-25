# Control corpora — provenance (QUARANTINED)

> Per the charter, these external Arabic texts are a **final, quarantined
> scorecard** for L11 stylometry. They are NEVER input to any self-interpretation
> derivation — only used to ask: does the Quran's measured structure sit apart
> from human Arabic writing? Downloaded 2026-06-25.

## 1. `bible_ar_vandyke.json` — Arabic prose (translation) control
- **Source:** Smith & Van Dyke Arabic Bible (1865), via getbible API v2.
- **URL:** https://api.getbible.net/v2/arabicsv.json
- **Content:** 66 books, 1,189 chapters, 31,102 verses. Fully diacritized.
- **Role:** non-rhymed prose translation — the low-rhyme floor.
- **Compact form:** verses grouped by book/chapter (metadata stripped).

## 2. `poetry_ashaar_classical.json` — classical Arabic verse control
- **Source:** ARBML *Ashaar* dataset (scraped from aldiwan.net), via the
  HuggingFace datasets-server rows API.
- **URL:** https://huggingface.co/datasets/arbml/ashaar
- **Content:** 391 classical qaṣīdas (poet era = العصر العباسي / Abbasid),
  ≥6 hemistichs each, ~6,300 bayts. Each poem is a monorhyme qaṣīda.
- **Role:** native Arabic monorhyme verse — the high-rhyme reference.
- **Note on era:** the dataset is ordered by poet, and its strictly pre-Islamic
  (جاهلي) subset is sparse (~0.4%) and could not be sampled reliably through the
  rate-limited API. Abbasid poetry follows the **identical qaṣīda monorhyme
  convention** inherited from the Jāhilī ode, so it validly represents the
  poetic genre's rhyme structure. A strictly-Jāhilī replication is left for a
  later pass.
- **Licence:** released for research/fair-use only (ARBML). Not redistributed
  for commercial use.

## Reproduction
Both files are compact extractions of the above public sources; the build script
`scripts/build_L11b_controls.py` consumes them as-is (seeded, byte-identical).
