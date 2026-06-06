# Monad

A research repository for systematic, corpus-driven study of the Quran — from raw text through morphology, lexical structure, and semantic analysis.

## Overview

Monad is built on the principle that rigorous analysis of the Quranic corpus requires a clearly separated stack: immutable source data, reproducible transformations, and transparent reasoning. Nothing is invented; everything is derived from or traceable to primary sources.

## Repository Structure

```
monad/
├── constitution/          # Governing principles, methodology, constraints
├── corpus/                # All primary source material (read-only)
│   └── quran/
│       ├── source/        # Quranic text in multiple encodings
│       ├── metadata/      # Sura index, page layout, character tables
│       ├── morphology/    # Word-level morphological annotation
│       └── lexical/       # Stemming, word frequency tables
├── data/                  # Derived structured data (output of analysis phases)
│   ├── roots/             # Arabic root extractions
│   ├── lemmas/            # Lemma normalizations
│   ├── concepts/          # Semantic concept definitions
│   ├── propositions/      # Propositional claims extracted from text
│   ├── dependencies/      # Inter-concept and inter-ayah dependencies
│   ├── contradictions/    # Flagged tensions for analysis
│   ├── hypotheses/        # Research hypotheses under investigation
│   └── reports/           # Analysis outputs and summaries
├── docs/                  # Architecture and inventory documentation
├── generated/             # Machine-generated artifacts (derived, not committed as source)
├── graph/                 # Graph data structures (nodes, edges, adjacency)
├── journal/               # Discovery log and research notes
├── prompts/               # Prompt templates for AI-assisted analysis
├── scripts/               # Data processing and transformation scripts
└── experiments/           # Exploratory notebooks and one-off analyses
```

## Corpus Sources

| File | Description |
|------|-------------|
| `corpus/quran/source/quran.csv` | Primary annotated text with diacritics, normalized form, and hash |
| `corpus/quran/source/qurantexttanzil.csv` | Tanzil standard text (hafs, simple) |
| `corpus/quran/source/quranuthmanitanzil.csv` | Tanzil Uthmani script |
| `corpus/quran/source/quranbylines.csv` | Text organized by printed lines |
| `corpus/quran/morphology/quranic-corpus-morphology-0.4.txt` | Quranic Arabic Corpus v0.4 morphology |
| `corpus/quran/lexical/stemming.csv` | Root-to-surface-form stemming table |
| `corpus/quran/lexical/words.csv` | Word frequency table |
| `corpus/quran/metadata/fahras.csv` | Sura index (number, name, page, ayah count, revelation type) |
| `corpus/quran/metadata/pages.csv` | Mushaf page-to-sura/ayah mapping |
| `corpus/quran/metadata/unicode.csv` | Unicode character inventory |

## Phases

1. **Corpus** — source ingestion, quality verification, canonical reference selection
2. **Lexical** — roots, lemmas, morphological feature extraction
3. **Propositional** — sentence-level and ayah-level proposition extraction
4. **Semantic** — concept identification, relation mapping
5. **Graph** — knowledge graph construction over concepts and propositions
6. **Analysis** — dependency, contradiction, and hypothesis evaluation

## Constraints

- Corpus files are never modified.
- All derived data is traceable to a corpus position (sura:ayah[:word]).
- No data is invented. See `constitution/methodology.md`.

## License

Research use. Quran text sourced from Tanzil (tanzil.net) and the Quranic Arabic Corpus (quran.kais.net). See individual corpus files for their respective licenses.
