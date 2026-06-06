# Database Schema

**File:** `generated/monad.db` (SQLite 3)  
**Built by:** `scripts/build_database.py`  
**Validated by:** `scripts/validate_database.py`  
**Built:** 2026-06-06

---

## Overview

The Monad database is a normalized relational store of the Quranic corpus. It provides a single source of truth for all downstream analysis phases.

```
surahs (114)
  └── ayahs (6,236)
        └── words (77,429)          — one row per word position in morphology
              └── morphology (128,219)  — one row per token (prefix/stem/suffix)
                    ├── roots (1,642)
                    └── lemmas (4,832)
                          └── roots

pages (604)
```

Every word in the database is traceable back to its surah, ayah, and position within the ayah via the `(surah_number, ayah_number, word_position)` coordinate.

---

## Tables

### `surahs`

One row per surah (chapter). 114 rows.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| `surah_number` | INTEGER | PRIMARY KEY | Canonical surah number 1–114 |
| `name_arabic` | TEXT | NOT NULL | Surah name without diacritics (normalized) |
| `name_arabic_diacritics` | TEXT | | Full diacritics name from quran.csv |
| `ayah_count` | INTEGER | NOT NULL | Total ayahs (authoritative: from qurantexttanzil.csv) |
| `revelation_type` | TEXT | `'meccan'` or `'medinan'` | Place of revelation |
| `start_page` | INTEGER | | Mushaf page where this surah begins |
| `source_id_fahras` | INTEGER | | Raw col[0] value from fahras.csv (internal ID, not surah number) |

**Sample:**
```sql
SELECT surah_number, name_arabic, ayah_count, revelation_type, start_page
FROM surahs LIMIT 3;
-- 1 | الفاتحة | 7  | meccan  | 1
-- 2 | البقرة  | 286| medinan | 2
-- 3 | ال عمران| 200| medinan | 50
```

---

### `ayahs`

One row per canonical ayah. 6,236 rows.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| `surah_number` | INTEGER | PK, FK → surahs | |
| `ayah_number` | INTEGER | PK | 1-based within surah |
| `text_hafs` | TEXT | NOT NULL | Hafs An-Asim text from qurantexttanzil.csv |
| `text_uthmani` | TEXT | | Uthmani script from quranuthmanitanzil.csv |
| `text_diacritics` | TEXT | | Full diacritics from quran.csv col[2] |
| `text_normalized` | TEXT | | Normalized (no diacritics) from quran.csv col[3] |
| `text_hash` | TEXT | | SHA-256 of the text (from quran.csv) |
| `ayah_sequential` | INTEGER | | Global sequence number 1–6236 |

**Primary key:** `(surah_number, ayah_number)`

**Sample:**
```sql
SELECT surah_number, ayah_number, text_hafs
FROM ayahs WHERE surah_number = 1;
```

---

### `roots`

One row per unique Arabic root extracted from the morphology corpus. 1,642 rows.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| `root_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | |
| `root_buckwalter` | TEXT | UNIQUE NOT NULL | Root in Buckwalter transliteration |
| `root_arabic` | TEXT | NOT NULL | Root in Arabic Unicode |
| `token_count` | INTEGER | DEFAULT 0 | Number of morphology tokens with this root |

**Sample:**
```sql
SELECT root_arabic, root_buckwalter, token_count
FROM roots ORDER BY token_count DESC LIMIT 5;
-- اله | Alh | 2851
-- قول | qwl | 1722
-- كون | kwn | 1390
-- ربب | rbb |  980
-- امن | Amn |  879
```

---

### `lemmas`

One row per unique lemma (canonical lexical form) from the morphology corpus. 4,832 rows.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| `lemma_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | |
| `lemma_buckwalter` | TEXT | UNIQUE NOT NULL | Lemma in Buckwalter transliteration |
| `lemma_arabic` | TEXT | NOT NULL | Lemma in Arabic Unicode |
| `root_id` | INTEGER | FK → roots | Root this lemma belongs to (NULL for particles/proper nouns) |

**Note:** 175 lemmas have `root_id = NULL`. These are particles (حروف), proper nouns, and borrowed words that do not have a trilateral Arabic root.

---

### `words`

One row per word occurrence — one entry per `(surah_number, ayah_number, word_position)` triple. 77,429 rows.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| `word_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | |
| `surah_number` | INTEGER | FK → ayahs | |
| `ayah_number` | INTEGER | FK → ayahs | |
| `word_position` | INTEGER | | 1-based position within ayah |
| `form_buckwalter` | TEXT | NOT NULL | STEM token form in Buckwalter |
| `form_arabic` | TEXT | NOT NULL | STEM token form in Arabic Unicode |
| `lemma_id` | INTEGER | FK → lemmas | NULL if STEM has no LEM: feature |
| `root_id` | INTEGER | FK → roots | NULL if STEM has no ROOT: feature |

**Unique constraint:** `(surah_number, ayah_number, word_position)`

**Coverage note:**
- 3,307 words (4.3%) have no `lemma_id` — typically prefixes used as standalone words, particles
- 27,470 words (35.5%) have no `root_id` — particles, proper nouns, prepositions, conjunctions

**Sample — tracing word 1:1:2:**
```sql
SELECT w.surah_number, w.ayah_number, w.word_position,
       w.form_arabic, r.root_arabic, l.lemma_arabic,
       s.name_arabic, a.text_hafs
FROM words w
JOIN surahs  s ON s.surah_number = w.surah_number
JOIN ayahs   a ON a.surah_number = w.surah_number AND a.ayah_number = w.ayah_number
LEFT JOIN roots  r ON r.root_id  = w.root_id
LEFT JOIN lemmas l ON l.lemma_id = w.lemma_id
WHERE w.surah_number = 1 AND w.ayah_number = 1 AND w.word_position = 2;
-- 1 | 1 | 2 | الله | اله | الله | الفاتحة | بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ
```

---

### `morphology`

One row per morphological token. 128,219 rows. Tokens are prefixes, stems, or suffixes within a word.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| `token_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | |
| `surah_number` | INTEGER | FK → ayahs | |
| `ayah_number` | INTEGER | FK → ayahs | |
| `word_position` | INTEGER | | 1-based word position within ayah |
| `token_position` | INTEGER | | 1-based token position within word |
| `form_buckwalter` | TEXT | NOT NULL | Token form (Buckwalter) |
| `tag` | TEXT | NOT NULL | Grammatical tag (N, V, P, PN, ADJ, ...) |
| `features_raw` | TEXT | NOT NULL | Full raw FEATURES string from corpus |
| `segment_type` | TEXT | | `STEM` \| `PREFIX` \| `SUFFIX` |
| `pos` | TEXT | | Part of speech |
| `lemma_id` | INTEGER | FK → lemmas | |
| `root_id` | INTEGER | FK → roots | |
| `gender` | TEXT | | `M` \| `F` |
| `number_feature` | TEXT | | `S` \| `D` \| `P` (singular/dual/plural) |
| `case_feature` | TEXT | | `NOM` \| `ACC` \| `GEN` |
| `state` | TEXT | | `DEF` \| `INDEF` \| `NA` |
| `aspect` | TEXT | | `PERF` \| `IMPF` \| `IMPV` (verb aspect) |
| `voice` | TEXT | | `ACT` \| `PASS` |
| `mood` | TEXT | | `IND` \| `JUSS` \| `SUBJ` |
| `person` | TEXT | | `1` \| `2` \| `3` |

**Source:** Quranic Arabic Corpus v0.4 (Kais Dukes, 2011). License: GNU GPL.

**Unique key:** `(surah_number, ayah_number, word_position, token_position)`

**Sample — all tokens of word 1:1:1 (بِسْمِ):**
```sql
SELECT token_position, form_buckwalter, tag, segment_type, pos, root_id
FROM morphology
WHERE surah_number = 1 AND ayah_number = 1 AND word_position = 1
ORDER BY token_position;
-- 1 | bi   | P | PREFIX | null  | null
-- 2 | somi | N | STEM   | N     | (root: smw)
```

---

### `pages`

One row per mushaf page. 604 rows.

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| `page_number` | INTEGER | PRIMARY KEY | 1–604 |
| `ayah_count_on_page` | INTEGER | NOT NULL | Count of ayahs on this page |

**Note:** `SUM(ayah_count_on_page)` = 6,236 (verified). The surah for each page is not stored directly; it can be computed by joining with the `ayahs` table using cumulative ayah counts.

---

## Indexes

| Index | Table | Columns | Purpose |
|-------|-------|---------|---------|
| `idx_ayahs_surah` | ayahs | surah_number | Surah → ayah lookup |
| `idx_words_position` | words | surah_number, ayah_number, word_position | Position-based lookup |
| `idx_words_lemma` | words | lemma_id | Lemma → word occurrence lookup |
| `idx_words_root` | words | root_id | Root → word occurrence lookup |
| `idx_morphology_position` | morphology | surah_number, ayah_number, word_position, token_position | Full coordinate lookup |
| `idx_morphology_lemma` | morphology | lemma_id | Lemma → token lookup |
| `idx_morphology_root` | morphology | root_id | Root → token lookup |
| `idx_lemmas_root` | lemmas | root_id | Root → lemma lookup |

---

## Coordinate System

Every token in the database is addressable by a four-part coordinate:

```
(S, A, W, T) = (surah_number, ayah_number, word_position, token_position)
```

Abbreviated coordinates:
- `1:1` — Surah 1, Ayah 1 (ayah level)
- `1:1:2` — Surah 1, Ayah 1, Word 2 (word level)
- `1:1:1:2` — Surah 1, Ayah 1, Word 1, Token 2 (token level)

This system matches the coordinate notation in the Quranic Arabic Corpus (`(1:1:1:1)` format).

---

## Rebuild

To rebuild the database from scratch:

```bash
python3 scripts/build_database.py --force
python3 scripts/validate_database.py
```

The database is fully deterministic from the corpus files. No external dependencies.
