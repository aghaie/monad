# Methodology

## Guiding Principles

### 1. Corpus-First

All analysis begins from attested text. The Quranic Arabic Corpus morphological annotation (v0.4, Kais Dukes, 2011) is used as the reference morphological layer. Tanzil text (hafs, Uthmani) is used as the reference textual layer.

### 2. Layered Representation

Analysis proceeds in layers, each building on the previous:

```
Layer 0  — Raw text (source CSVs)
Layer 1  — Morphological tokens (morphology corpus)
Layer 2  — Lemma/root normalizations
Layer 3  — Propositional units (ayah-level or sub-ayah)
Layer 4  — Concept nodes (named entities, predicates, relations)
Layer 5  — Dependency and contradiction maps
Layer 6  — Hypothesis graph
```

### 3. Coordinate System

Every datum is anchored by a four-part coordinate:

```
(S, A, W, T) = (sura, ayah, word_position, token_position)
```

Morphology corpus uses the same system: `(1:2:3:1)` = sura 1, ayah 2, word 3, token 1.

Short forms are acceptable when resolution is unambiguous:
- `1:1` = Sura 1, Ayah 1 (ayah-level)
- `1:1:1` = first word of 1:1

### 4. Canonical Text Selection

| Purpose | Source |
|---------|--------|
| Display / human reading | `qurantexttanzil.csv` (hafs, diacritics, standard encoding) |
| Uthmani script reference | `quranuthmanitanzil.csv` |
| Internal processing | `quran.csv` (normalized column, col[3]) |
| Morphological analysis | `quranic-corpus-morphology-0.4.txt` (Buckwalter transliteration) |

### 5. Root and Lemma Extraction

- Primary source: morphology corpus `ROOT:` and `LEM:` feature fields
- Cross-checked against `stemming.csv` where possible
- Buckwalter transliteration is used internally; Arabic is used in output artifacts

### 6. Uncertainty Marking

Any artifact that involves human or model judgment must be marked with a confidence tier:

| Tier | Meaning |
|------|---------|
| `C1` | Directly attested (text says exactly this) |
| `C2` | Morphologically derived (corpus annotation) |
| `C3` | Inferred from context (documented reasoning required) |
| `C4` | Hypothetical (recorded in `data/hypotheses/`) |

### 7. Reproducibility

All scripts in `scripts/` must:
- Accept input paths as arguments (no hardcoded paths)
- Emit output to stdout or a specified output path
- Log the corpus coordinate of every output datum
- Be runnable without internet access

### 8. Review Protocol

Before any derived dataset moves from `generated/` to `data/`:
1. A quality check script must run without errors
2. A human must review a sample of at least 50 records
3. The review outcome is logged in `journal/discovery-log.md`
