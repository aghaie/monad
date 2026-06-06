# Project Architecture

## Overview

Monad is organized as a layered research repository. The top-level structure separates immutable source material (corpus) from derived analysis products (data, generated), tooling (scripts), and documentation (docs, constitution, journal).

```
monad/
├── constitution/
├── corpus/
│   └── quran/
│       ├── source/
│       ├── metadata/
│       ├── morphology/
│       └── lexical/
├── data/
│   ├── roots/
│   ├── lemmas/
│   ├── concepts/
│   ├── propositions/
│   ├── dependencies/
│   ├── contradictions/
│   ├── hypotheses/
│   └── reports/
├── docs/
├── experiments/
├── generated/
├── graph/
├── journal/
├── prompts/
└── scripts/
```

---

## Directory Reference

### `constitution/`

Governing documents. These define the epistemological rules under which all other work operates.

| File | Purpose |
|------|---------|
| `monad-constitution.md` | Core principles: source supremacy, derivation discipline, scope |
| `methodology.md` | Operational methodology: coordinate system, text selection, confidence tiers |

Not versioned after adoption except via explicit amendment recorded in `journal/`.

---

### `corpus/`

**Read-only.** All primary source material lives here. Files in this directory are never modified by any script or analysis process.

#### `corpus/quran/source/`

Quranic text in multiple encodings and presentation formats.

| File | Rows | Purpose |
|------|------|---------|
| `quran.csv` | 6,461 | Primary annotated text: diacritics, normalized form, SHA-256 hash, sura metadata |
| `qurantexttanzil.csv` | 6,236 | Tanzil hafs text, standard diacritics, simple encoding |
| `quranuthmanitanzil.csv` | 6,236 | Tanzil Uthmani script (رسم عثماني) |
| `quranbylines.csv` | 9,046 | Text segmented by printed mushaf lines |

#### `corpus/quran/metadata/`

Structural and navigational metadata about the corpus.

| File | Rows | Purpose |
|------|------|---------|
| `fahras.csv` | 114 | Sura index: number, Arabic name, start page, ayah count, revelation type |
| `pages.csv` | 604 | Mushaf page layout: page number → sura/ayah count per page |
| `unicode.csv` | 86 | Unicode character inventory: character, frequency, code point |

#### `corpus/quran/morphology/`

| File | Rows (data) | Purpose |
|------|------------|---------|
| `quranic-corpus-morphology-0.4.txt` | 128,219 | Quranic Arabic Corpus v0.4. Token-level morphological annotation in Buckwalter transliteration. Fields: LOCATION, FORM, TAG, FEATURES |

#### `corpus/quran/lexical/`

| File | Rows | Purpose |
|------|------|---------|
| `stemming.csv` | 2,186 | Root → surface forms mapping |
| `words.csv` | 14,978 | Word type → frequency table |

---

### `data/`

Derived structured data. Every file here is the output of a documented process and carries provenance references to corpus positions.

| Subdirectory | Contents (future) |
|---|---|
| `roots/` | Extracted Arabic roots with morphology-corpus provenance |
| `lemmas/` | Canonical lemma forms, normalized from `LEM:` fields |
| `concepts/` | Named concept definitions with textual anchor |
| `propositions/` | Ayah-level or sub-ayah propositional units |
| `dependencies/` | Inter-proposition and inter-concept dependency edges |
| `contradictions/` | Flagged semantic or propositional tensions |
| `hypotheses/` | Formal research hypotheses with supporting evidence |
| `reports/` | Analysis summaries and phase completion reports |

All files in `data/` follow the naming convention: `<phase>_<descriptor>_<version>.{csv,json,jsonl}`.

---

### `generated/`

Ephemeral machine output. Scripts write here first; after human review, outputs are promoted to `data/`. Nothing in `generated/` is treated as authoritative. Not committed to git in normal workflow (add to `.gitignore` if needed).

---

### `graph/`

Graph-structured representations of the knowledge extracted from the corpus. Intended formats:

- Node lists: `nodes_<type>.csv` or `.jsonl`
- Edge lists: `edges_<relation>.csv` or `.jsonl`
- Adjacency snapshots for specific queries

Graph files are derived from `data/` and are regenerated from it; they are not primary artifacts.

---

### `scripts/`

Data processing, transformation, and validation scripts. Each script must:
- Accept input paths as CLI arguments
- Write output to stdout or a specified path
- Be self-documenting (usage in first comment block)
- Log corpus coordinate provenance for every output datum

Naming: `<phase>_<action>.py` (e.g., `lexical_extract_roots.py`, `morphology_parse.py`).

---

### `experiments/`

Exploratory analyses, Jupyter notebooks, and one-off scripts. Not held to the standards of `scripts/`. Findings worth retaining are documented in `journal/discovery-log.md` and promoted to `data/` or `scripts/` as appropriate.

---

### `prompts/`

Prompt templates for AI-assisted analysis steps. Templates use `{{placeholder}}` syntax for corpus-position injection. Stored here so prompts are versioned alongside the data they operate on.

---

### `journal/`

Permanent chronological log of decisions and discoveries. See `journal/discovery-log.md`. Entries are append-only.

---

### `docs/`

Architecture and inventory documentation (this directory).

| File | Contents |
|------|---------|
| `project-architecture.md` | This file — repository structure and purpose |
| `data-inventory.md` | Every source file: format, columns, estimated purpose, quality notes |
| `data-quality-report.md` | Per-file quality analysis: missing values, duplicates, encoding issues |

---

## Analysis Phases

### Phase 1 — Corpus Verification (current)

- Establish canonical source references
- Complete data inventory and quality report
- Verify row counts against known Quranic structure (114 suras, 6,236 ayat)
- Confirm morphology corpus alignment with text sources

Deliverables: `docs/data-inventory.md`, `docs/data-quality-report.md`

### Phase 2 — Lexical Extraction

- Extract all roots from morphology corpus
- Build lemma → root → surface-form table
- Cross-validate against `stemming.csv`
- Output to `data/roots/`, `data/lemmas/`

### Phase 3 — Propositional Decomposition

- Segment ayat into propositional units using morphological parse
- Classify by predicate type (assertion, command, prohibition, question, conditional)
- Annotate with grammatical subject and object where identifiable
- Output to `data/propositions/`

### Phase 4 — Concept Mapping

- Identify recurring named concepts (theological, cosmological, legal, historical)
- Anchor each concept to its first occurrence and high-frequency contexts
- Output to `data/concepts/`

### Phase 5 — Dependency and Relation Graph

- Map inter-proposition dependencies (explicit textual connectives: fa, thumma, wa, law, etc.)
- Map concept co-occurrence and reference networks
- Output to `data/dependencies/`, `graph/`

### Phase 6 — Tension and Hypothesis Analysis

- Flag structural tensions for review (not contradictions in text, but analytical tensions)
- Formalize research hypotheses with supporting ayah citations
- Output to `data/contradictions/`, `data/hypotheses/`

### Phase 7 — Reporting

- Generate structured reports per sura, per concept, per relation type
- Output to `data/reports/`

---

## Architectural Constraints

1. Data flows only forward: corpus → generated → data → graph → reports.
2. No file in `corpus/` is ever written by a script.
3. All cross-file joins use the `(sura, ayah)` or `(sura, ayah, word, token)` coordinate as the join key.
4. Arabic text in output files uses UTF-8 encoding exclusively.
5. Buckwalter transliteration is used only in internal processing; all human-facing outputs use Arabic script.
