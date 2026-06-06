# Data Inventory

Inventory of all primary source files as of 2026-06-06. Files are located in `corpus/quran/` subdirectories (canonical copies) with originals retained in `data/` for provenance.

---

## 1. `corpus/quran/source/quran.csv`

**Original path:** `data/quran.csv`  
**Format:** CSV, no header row, UTF-8  
**File size:** ~3.0 MB  
**Rows:** 6,461 (6,236 ayat + 225 structural rows)  
**Columns:** 13

| Col | Index | Inferred Name | Example | Notes |
|-----|-------|--------------|---------|-------|
| 0 | 0 | sura_number | `1` | Integer, 1–114 |
| 1 | 1 | aya_index | `1` | 0 = sura header row; 1+ = ayah |
| 2 | 2 | text_diacritics | `بِسۡمِ ٱللَّهِ...` | Full diacritics, Uthmani-like script |
| 3 | 3 | text_normalized | `بسم الله الرحمٰن الرحيم` | Stripped diacritics, normalized |
| 4 | 4 | sha256 | `803dee27b5a9...` | SHA-256 hash of the text |
| 5 | 5 | unknown_float | `0.25` | Constant 0.25 across all rows — likely juz fraction or source version |
| 6 | 6 | sura_number_dup | `1` | Duplicate of col[0] |
| 7 | 7 | sura_number_arabic | `١` | Arabic-Indic numeral |
| 8 | 8 | display_line | `2` | Sequential line number within display |
| 9 | 9 | sura_name_diacritics | `سُورَةُ الفَاتِحَةِ` | Full diacritics |
| 10 | 10 | sura_name_normalized | `سورة الفاتحة` | Normalized |
| 11 | 11 | unknown_flag_a | `1` | Binary-like; possibly is_meccan |
| 12 | 12 | unknown_flag_b | `0` | Binary-like; possibly is_start_of_sura |

**Estimated purpose:** Main annotated text database used for display and text processing. Contains redundant metadata columns alongside the primary text.

**Key notes:**
- 225 rows have `aya_index = 0` (sura header rows) — not canonical ayat
- 114 rows have `aya_index = 1` — first ayat of each sura
- Column 5 (float `0.25`) is uniform across the entire file; purpose unclear
- SHA-256 per ayah enables integrity checking

---

## 2. `corpus/quran/source/qurantexttanzil.csv`

**Original path:** `data/qurantexttanzil.csv`  
**Format:** CSV, no header row, UTF-8  
**File size:** ~1.3 MB  
**Rows:** 6,236 (exactly matches canonical ayah count)  
**Columns:** 5 (col[4] is always empty — trailing comma artifact)

| Col | Index | Inferred Name | Example | Notes |
|-----|-------|--------------|---------|-------|
| 0 | 0 | sura_number | `1` | 1–114 |
| 1 | 1 | aya_number | `1` | 1-based |
| 2 | 2 | text | `بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ` | Standard hafs diacritics |
| 3 | 3 | aya_sequential | `1` | Global ayah sequence number (1–6236) |
| 4 | 4 | empty | `` | Trailing comma artifact, always empty |

**Estimated purpose:** Tanzil hafs canonical text. Standard reference for Quranic text in most digital applications. Clean (sura, aya) primary key with no structural rows.

**Key notes:**
- Cleanest text representation for processing
- The 5th column is always empty — confirmed across all 6,236 rows
- Uses standard hafs reading with full diacritics

---

## 3. `corpus/quran/source/quranuthmanitanzil.csv`

**Original path:** `data/quranuthmanitanzil.csv`  
**Format:** CSV, no header row, UTF-8  
**File size:** ~1.2 MB  
**Rows:** 6,236  
**Columns:** 5 (col[4] always empty)

| Col | Index | Inferred Name | Example | Notes |
|-----|-------|--------------|---------|-------|
| 0 | 0 | sura_number | `1` | 1–114 |
| 1 | 1 | aya_number | `1` | 1-based |
| 2 | 2 | text_uthmani | `بِسمِ اللَّهِ الرَّحمٰنِ الرَّحيمِ` | Uthmani orthography |
| 3 | 3 | aya_sequential | `1` | Global sequence number |
| 4 | 4 | empty | `` | Trailing comma artifact |

**Estimated purpose:** Uthmani script (رسم عثماني) reference. Orthographic differences from hafs include elongated alef maqsura, special hamza forms, and variant spelling conventions.

**Key notes:**
- Structurally identical to `qurantexttanzil.csv`
- Text differs in orthographic conventions (Uthmani vs. standard modern)
- Same (sura, aya) key space

---

## 4. `corpus/quran/source/quranbylines.csv`

**Original path:** `data/quranbylines.csv`  
**Format:** CSV, no header row, UTF-8  
**File size:** ~2.6 MB  
**Rows:** 9,046  
**Columns:** 8

| Col | Index | Inferred Name | Example | Notes |
|-----|-------|--------------|---------|-------|
| 0 | 0 | line_global | `1` | Global line number |
| 1 | 1 | page_number | `1` | Mushaf page number |
| 2 | 2 | sura_number | `1` | Sura number |
| 3 | 3 | line_text_diacritics | `سُورَةُ الفَاتِحَةِ` | Text of this line with diacritics |
| 4 | 4 | first_aya_on_line | `0` | Index of first ayah starting on this line |
| 5 | 5 | unknown_float | `0.25` | Uniform value — same artifact as quran.csv col[5] |
| 6 | 6 | sura_name_diacritics | `سُورَةُ الفَاتِحَةِ` | Sura name |
| 7 | 7 | line_text_normalized | `سورة الفاتحة` | Normalized line text |

**Estimated purpose:** Text organized by physical mushaf printed lines (15 lines per page, 604 pages = ~9,060 lines). Used for page-faithful display rendering.

**Key notes:**
- 9,046 rows ≈ 604 pages × 15 lines/page (minus page breaks and sura headers)
- No empty cells confirmed
- Useful for reconstructing visual layout but not for ayah-level analysis

---

## 5. `corpus/quran/morphology/quranic-corpus-morphology-0.4.txt`

**Original path:** `data/quranic-corpus-morphology-0.4.txt`  
**Format:** TSV with header, UTF-8, GPL-licensed  
**File size:** ~6.1 MB  
**Rows:** 128,219 data rows (plus 57 comment/header lines)  
**Columns:** 4

| Col | Name | Example | Notes |
|-----|------|---------|-------|
| LOCATION | Token position | `(1:1:1:1)` | (sura:ayah:word:token) |
| FORM | Buckwalter form | `bi` | Transliterated token form |
| TAG | Part-of-speech tag | `P` | Grammar category abbreviation |
| FEATURES | Morphological features | `PREFIX\|bi+` | Pipe-delimited feature set |

**Feature keys include:** `POS`, `LEM` (lemma), `ROOT`, `M/F` (gender), `NOM/ACC/GEN` (case), `STEM/PREFIX/SUFFIX`, verb features (aspect, voice, mood), etc.

**Estimated purpose:** Primary morphological analysis layer. Enables root extraction, lemma identification, part-of-speech analysis, and grammatical parsing of every token in the Quran.

**Key statistics:**
- 128,219 annotated tokens
- 1,642 unique roots
- Source: Quranic Arabic Corpus v0.4, Kais Dukes, University of Leeds, 2011
- License: GNU GPL

---

## 6. `corpus/quran/lexical/stemming.csv`

**Original path:** `data/stemming.csv`  
**Format:** CSV, no header row, UTF-8  
**File size:** ~112 KB  
**Rows:** 2,186  
**Columns:** 3

| Col | Index | Inferred Name | Example | Notes |
|-----|-------|--------------|---------|-------|
| 0 | 0 | root_or_lemma | `أله` | Arabic root or lemma form |
| 1 | 1 | surface_form_count | `11` | Number of distinct surface forms |
| 2 | 2 | surface_forms | `"الهتنا,الهة,..."` | Comma-separated surface forms (quoted if multiple) |

**Estimated purpose:** Root/lemma → surface form expansion table. Enables reverse lookup from surface form to root. Cross-reference layer between morphology corpus and the text.

**Key notes:**
- 2,186 unique root/lemma entries
- Some entries have only 1 surface form; many have 5–20+
- Root `أله` (deity/God root) has 11 surface forms, confirming expected high-frequency theological vocabulary

---

## 7. `corpus/quran/lexical/words.csv`

**Original path:** `data/words.csv`  
**Format:** CSV, no header row, UTF-8  
**File size:** ~204 KB  
**Rows:** 14,978  
**Columns:** 2

| Col | Index | Inferred Name | Example | Notes |
|-----|-------|--------------|---------|-------|
| 0 | 0 | word_form | `سورة` | Arabic surface word form |
| 1 | 1 | frequency | `121` | Occurrence count in corpus |

**Estimated purpose:** Word-type frequency table. Maps every distinct orthographic form to its corpus frequency. Useful for term weighting and vocabulary analysis.

**Key notes:**
- 14,978 distinct word types
- Row 3 has an empty word form (col[0] = `""`) with frequency 227 — represents null/boundary tokens from the export process
- Top frequency: `الله` appears 2,265 times (confirmed cross-check with morphology data)

---

## 8. `corpus/quran/metadata/fahras.csv`

**Original path:** `data/fahras.csv`  
**Format:** CSV, no header row, UTF-8  
**File size:** ~4.5 KB  
**Rows:** 114 (one per sura)  
**Columns:** 5

| Col | Index | Inferred Name | Example | Notes |
|-----|-------|--------------|---------|-------|
| 0 | 0 | sura_number | `230` | WARNING: these are NOT 1–114 sequential |
| 1 | 1 | sura_name | `النِّسَاءِ` | Arabic name with diacritics |
| 2 | 2 | start_page | `77` | Mushaf page where sura begins |
| 3 | 3 | ayah_count | `176` | Total ayat in sura |
| 4 | 4 | revelation_type | `مدنيه` | Meccan (مكيه) or Medinan (مدنيه) |

**Estimated purpose:** Sura index / table of contents. Maps sura metadata including revelation provenance and physical layout.

**Key notes:**
- Column 0 contains values like 230, 231, 303 — these appear to be internal identifiers, NOT sura ordinal numbers (1–114). All 114 suras present, unique, no duplicates.
- Revelation type encoding: `مدنيه` = Medinan, `مكيه` = Meccan
- Must join to other tables using sura name match rather than col[0] value directly

---

## 9. `corpus/quran/metadata/pages.csv`

**Original path:** `data/pages.csv`  
**Format:** CSV, no header row, UTF-8  
**File size:** ~3.6 KB  
**Rows:** 604  
**Columns:** 2

| Col | Index | Inferred Name | Example | Notes |
|-----|-------|--------------|---------|-------|
| 0 | 0 | sura_number | `1` | 1–114 |
| 1 | 1 | ayah_count_on_page | `7` | Number of ayat on this mushaf page |

**Estimated purpose:** Page-level layout index. Maps each mushaf page to the sura it belongs to and how many ayat appear on that page. Enables page-number-to-ayah navigation.

**Key notes:**
- 604 rows matches standard 604-page mushaf
- Column 0 appears to reset per page (not globally sequential) — reflects sura context per page
- No missing values, no duplicates

---

## 10. `corpus/quran/metadata/unicode.csv`

**Original path:** `data/unicode.csv`  
**Format:** CSV, no header row, UTF-8  
**File size:** ~1.1 KB  
**Rows:** 86 (including control character rows)  
**Columns:** 3

| Col | Index | Inferred Name | Example | Notes |
|-----|-------|--------------|---------|-------|
| 0 | 0 | character | `س` | The Unicode character (may be control) |
| 1 | 1 | frequency | `6249` | Occurrence count in corpus |
| 2 | 2 | code_point | `0633` | Hexadecimal Unicode code point |

**Estimated purpose:** Complete Unicode character inventory of the corpus. Documents every character used, including whitespace and control characters, with frequencies. Used for encoding validation and character normalization.

**Key notes:**
- Includes 5 rows with whitespace/control characters: space (U+0020), CR (U+000D), LF (U+000A), vertical tab (U+000B), form feed (U+000C) — these are valid entries, not errors
- Arabic diacritic fatha (U+064E) is the most frequent character at 123,495 occurrences
- 86 unique characters document the full orthographic range of the corpus
