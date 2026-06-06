# Data Quality Report

Assessment of all primary source files as of 2026-06-06. Each file inspected for missing values, duplicate records, encoding issues, and consistency against known Quranic structural invariants.

**Invariants used for validation:**
- 114 suras
- 6,236 canonical ayat (standard Hafs count)
- 128,219 morphological tokens (Quranic Arabic Corpus v0.4)
- Morphology coordinate system: (sura:ayah:word:token)

---

## 1. `quran.csv`

**Status: ACCEPTABLE — structural rows present, requires disambiguation**

### Missing Values
- 2 empty cells detected across 83,993 total cells
- Both empties are in columns that carry metadata redundantly
- No missing values in primary text columns (col[2], col[3])

### Duplicate Records
- 110 duplicate (sura, aya) key pairs detected
- **Root cause:** 225 rows have `aya_index = 0` (sura title/header rows). These are structural display rows, not ayat. The actual Quranic ayat rows are unique by (sura, aya) when restricted to `aya_index >= 1`.
- Additional source: basmala appears as aya 0 and aya 1 in some suras
- **Resolution:** Filter `aya_index > 0` to isolate canonical ayat before any analysis

### Encoding Issues
- None detected. UTF-8 throughout. Arabic script renders correctly.
- SHA-256 column (col[4]) confirmed to be 64-character hex strings

### Consistency Issues
- Column 5 (float) is uniformly `0.25` across all 6,461 rows — purpose unknown
- Columns 0 and 6 are identical (duplicate sura number) — redundant, not an error
- Column 8 appears to be a global display-line counter, not an aya number — requires clarification before use as a key
- `fahras.csv` col[0] values (e.g., 230, 231) do not match `quran.csv` col[0] values (1–114) — these are different identifier spaces; joining requires name-based matching

---

## 2. `qurantexttanzil.csv`

**Status: CLEAN — recommended primary text source**

### Missing Values
- 6,236 empty cells in col[4] — but col[4] is a trailing comma artifact (empty 5th column), confirmed uniform across all rows
- No missing values in cols [0]–[3]

### Duplicate Records
- 0 duplicate (sura, aya) pairs
- Row count (6,236) exactly matches canonical ayah count — no structural rows

### Encoding Issues
- None. UTF-8, standard hafs diacritics

### Consistency Issues
- None identified. Clean file. Recommended as the canonical text source for processing.

---

## 3. `quranuthmanitanzil.csv`

**Status: CLEAN — valid Uthmani variant**

### Missing Values
- Same trailing comma artifact as `qurantexttanzil.csv` — 6,236 empty col[4] values
- No missing values in cols [0]–[3]

### Duplicate Records
- 0 duplicate (sura, aya) pairs

### Encoding Issues
- None. UTF-8. Uthmani orthographic conventions confirmed by visual inspection (e.g., `رَّحمٰنِ` vs hafs `رَّحْمَنِ`).

### Consistency Issues
- Orthographic differences from `qurantexttanzil.csv` are expected (Uthmani vs. hafs conventions), not errors
- Cannot be used interchangeably with hafs text in character-level analysis without normalization

---

## 4. `quranbylines.csv`

**Status: ACCEPTABLE — valid for layout analysis; not for ayah-level text extraction**

### Missing Values
- 0 empty cells across 72,368 total cells

### Duplicate Records
- Not applicable — rows represent printed lines, not ayat. Lines are globally unique by col[0].

### Encoding Issues
- None detected

### Consistency Issues
- 9,046 rows vs. expected ~9,060 (604 pages × 15 lines): delta likely due to sura title pages and partial pages
- Column 4 (`first_aya_on_line`) uses 0-indexed aya counting — differs from `qurantexttanzil.csv` 1-based indexing. Join requires offset correction.
- Column 5 (float `0.25`) is the same unknown uniform value seen in `quran.csv`. Likely an export artifact.
- A single line may span partial ayat — this file is not suitable as a primary text source for ayah-level extraction

---

## 5. `quranic-corpus-morphology-0.4.txt`

**Status: AUTHORITATIVE — production quality, GPL-licensed**

### Missing Values
- Header comment block (57 lines) must be skipped; not a data issue
- FEATURES column is always populated for STEM rows; PREFIX/SUFFIX rows have compact feature strings

### Duplicate Records
- No duplicate LOCATION tuples (each token position is unique by design)

### Encoding Issues
- File uses Buckwalter transliteration (ASCII) for Arabic text — intentional design choice, not an encoding error
- Arabic glyphs do not appear in data columns; all Arabic is transliterated
- UTF-8 file encoding confirmed

### Consistency Issues
- Root notation: `ROOT:` field uses Buckwalter. Must be converted to Arabic for display.
- Lemma notation: `LEM:` uses Buckwalter with prefixes (`{` = ا, `}` = ء)
- Some tokens (prefixes, suffixes) do not have ROOT fields — this is structurally correct
- Version is 0.4 (2011). A newer version of the corpus may exist. Verify before extending.

### Quality Assessment
- Regarded as the gold standard for Quranic morphological annotation
- Peer-reviewed and used in academic literature
- 1,642 unique roots across 128,219 tokens is consistent with published corpus statistics

---

## 6. `stemming.csv`

**Status: ACCEPTABLE — useful for cross-reference; not authoritative on its own**

### Missing Values
- 0 empty cells

### Duplicate Records
- No duplicate root/lemma entries in col[0]

### Encoding Issues
- None. UTF-8, Arabic script.

### Consistency Issues
- Source provenance of this stemming table is unknown — no header, no license, no attribution
- Root forms may not use a consistent normalization scheme (some entries appear to be lemmas, not strict 3-letter roots)
- Cross-validation against morphology corpus `ROOT:` fields is required before treating this as authoritative
- Recommended use: cross-reference only, not primary root source

---

## 7. `words.csv`

**Status: ACCEPTABLE — useful for frequency analysis; one anomalous row**

### Missing Values
- 1 row with empty col[0] (word form): row 3, frequency = 227
- This represents the empty-string token — a null/boundary marker from the export tool
- Not a data error, but must be excluded from word-type analysis

### Duplicate Records
- No duplicate word forms (each surface form appears once with its aggregate frequency)

### Encoding Issues
- None. UTF-8, Arabic script.

### Consistency Issues
- Source and provenance unknown (no header, no attribution)
- Frequency counts should be validated against a direct count from `qurantexttanzil.csv`
- Top token `الله` = 2,265 is consistent with published Quranic word frequency data

---

## 8. `fahras.csv`

**Status: ACCEPTABLE — critical join key issue identified**

### Missing Values
- 0 empty cells

### Duplicate Records
- 0 duplicate entries in col[0] (internal identifier)
- All 114 suras present

### Encoding Issues
- None. UTF-8, Arabic with diacritics.

### Consistency Issues
- **Critical:** col[0] contains values like 230, 231, 303 — NOT the standard sura ordinal (1–114). These appear to be a different internal numbering system. This means `fahras.csv` cannot be directly joined to other files using col[0] as a sura number.
- To join `fahras.csv` to other tables, use sura name (col[1]) as the join key, matched against sura name columns in `quran.csv` (col[9] or col[10])
- Revelation type strings use `مكيه` / `مدنيه` — these are colloquial Arabic spellings (missing final alef), not standard `مكية` / `مدنية`. Acceptable, but normalize before display.

---

## 9. `pages.csv`

**Status: CLEAN — simple layout table**

### Missing Values
- 0 empty cells

### Duplicate Records
- 604 rows, one per mushaf page — no structural duplicates expected or found

### Encoding Issues
- None

### Consistency Issues
- Column 0 resets per page (not globally sequential) and reflects the sura present on that page — interpretation requires understanding that multiple rows can share the same col[0] value (when a sura spans multiple pages)
- No explicit page number column; row index (1-based) is the implicit page number

---

## 10. `unicode.csv`

**Status: ACCEPTABLE — control character rows are valid data**

### Missing Values
- 5 rows where col[0] contains non-printable characters (space, CR, LF, vertical tab, form feed)
- These cells are not "missing" — they contain the actual control characters being inventoried
- Technically: col[0] appears empty when printed but contains the character

### Duplicate Records
- 0 duplicate code points

### Encoding Issues
- Control character rows (U+000D, U+000A, U+000B, U+000C) will cause issues in CSV parsers that treat these as record terminators
- Recommend reading this file with a robust CSV parser that handles embedded control characters, or pre-processing to escape them
- Otherwise clean UTF-8

### Consistency Issues
- Total character count derivable from frequency sum should match total character count in `qurantexttanzil.csv` — not yet validated
- Code points cover Arabic letters (U+0600–U+06FF), Arabic presentation forms, diacritics, and Latin/ASCII characters (digits, space) used in some variants

---

## Summary Table

| File | Missing Values | Duplicates | Encoding Issues | Consistency Issues | Overall |
|------|--------------|------------|-----------------|-------------------|---------|
| `quran.csv` | Minimal (2 cells) | 110 structural rows (expected) | None | Unknown col[5], col[8] ambiguity | Acceptable |
| `qurantexttanzil.csv` | Trailing comma (artifact) | None | None | None | **Clean** |
| `quranuthmanitanzil.csv` | Trailing comma (artifact) | None | None | Orthographic variant (expected) | **Clean** |
| `quranbylines.csv` | None | N/A | None | Line vs. ayah alignment | Acceptable |
| `quranic-corpus-morphology-0.4.txt` | None | None | Buckwalter (intentional) | Version may be dated | **Authoritative** |
| `stemming.csv` | None | None | None | Unknown provenance | Cross-ref only |
| `words.csv` | 1 empty-form row | None | None | Unknown provenance | Acceptable |
| `fahras.csv` | None | None | None | **col[0] not sura ordinal** | Acceptable (see note) |
| `pages.csv` | None | None | None | Implicit page number | Clean |
| `unicode.csv` | 5 control chars (valid) | None | Control chars in CSV | None | Acceptable |

---

## Recommended Primary Sources by Use Case

| Use Case | Recommended File |
|----------|-----------------|
| Canonical Arabic text | `qurantexttanzil.csv` |
| Uthmani script | `quranuthmanitanzil.csv` |
| Morphological analysis | `quranic-corpus-morphology-0.4.txt` |
| Root/lemma lookup | `quranic-corpus-morphology-0.4.txt` (primary), `stemming.csv` (cross-ref) |
| Sura metadata | `fahras.csv` (join by name) |
| Word frequency | `words.csv` |
| Page layout | `quranbylines.csv`, `pages.csv` |
| Full annotated text | `quran.csv` (filter `aya_index > 0`) |
