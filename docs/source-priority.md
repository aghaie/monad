# Source Priority

Defines the source-of-truth hierarchy for every data field in `generated/monad.db`.
When two sources conflict, the higher-priority source wins. Conflicts are logged in
`docs/import-report.md`.

---

## Hierarchy Summary

```
Tier 1 — Authoritative (never overridden)
  qurantexttanzil.csv             canonical Hafs text, ayah count, sequential numbering
  quranic-corpus-morphology-0.4.txt  all morphological annotation (roots, lemmas, tokens)

Tier 2 — Primary supplementary
  quranuthmanitanzil.csv          Uthmani text (fills text_uthmani column only)
  quran.csv                       diacritics text, normalized text, SHA-256 hash

Tier 3 — Metadata
  fahras.csv                      revelation type, start page, surah names
  pages.csv                       page layout (ayah count per mushaf page)

Skipped / Not imported
  quranbylines.csv                printed-line layout (no schema table)
  unicode.csv                     character inventory (informational)
  stemming.csv                    root→surface forms (superseded by morphology corpus)
  words.csv                       word-type frequency (computable from morphology table)
```

---

## Field-Level Priority

### `surahs` table

| Field | Source (priority order) | Rationale |
|-------|------------------------|-----------|
| `surah_number` | Derived (1–114 ordinal) | Canonical Uthmani ordering is not ambiguous; surah numbers are universally agreed |
| `name_arabic` | quran.csv (sura header rows, col[10]) | Normalized Arabic name without diacritics |
| `name_arabic_diacritics` | quran.csv (sura header rows, col[9]) | Full diacritics form with "سورة" prefix stripped |
| `ayah_count` | **qurantexttanzil.csv** (counted directly) | Most reliable: row count per surah in the authoritative text file. Overrides fahras.csv when they conflict (surah 9: 129 vs 128). |
| `revelation_type` | fahras.csv (col[4]) | Only source for this field. Normalised: مكيه→meccan, مدنيه→medinan. |
| `start_page` | fahras.csv (col[2]) | Only source for mushaf start-page per surah. |
| `source_id_fahras` | fahras.csv (col[0]) | Stored verbatim for traceability; NOT a surah number. |

### `ayahs` table

| Field | Source (priority order) | Rationale |
|-------|------------------------|-----------|
| `text_hafs` | **qurantexttanzil.csv** (col[2]) | Tanzil hafs text is the most widely used, validated, and consistent source. Used as the primary text for all analysis. |
| `text_uthmani` | quranuthmanitanzil.csv (col[2]) | Tanzil Uthmani variant. Stored as supplementary; not used in analysis by default. |
| `text_diacritics` | quran.csv (col[2]) | Secondary diacritics form. May differ from hafs in presentation style. |
| `text_normalized` | quran.csv (col[3]) | Stripped-diacritics form from quran.csv. |
| `text_hash` | quran.csv (col[4]) | SHA-256 per ayah; useful for integrity checking. |
| `ayah_sequential` | qurantexttanzil.csv (col[3]) | Global sequence 1–6236; Tanzil project's numbering. |

### `roots` table

| Field | Source | Rationale |
|-------|--------|-----------|
| All fields | **quranic-corpus-morphology-0.4.txt** (`ROOT:` feature) | The Quranic Arabic Corpus is peer-reviewed and the gold standard for morphological annotation. stemming.csv is not used for roots. |

### `lemmas` table

| Field | Source | Rationale |
|-------|--------|-----------|
| All fields | **quranic-corpus-morphology-0.4.txt** (`LEM:` feature) | Same rationale as roots. |

### `words` table

| Field | Source | Rationale |
|-------|--------|-----------|
| `form_buckwalter` / `form_arabic` | **quranic-corpus-morphology-0.4.txt** (STEM token FORM) | The STEM token represents the lexical core of the word. |
| `lemma_id` / `root_id` | morphology corpus (STEM token LEM:/ROOT: features) | Inherited from the STEM token. NULL where the morphology corpus does not annotate. |

### `morphology` table

| Field | Source | Rationale |
|-------|--------|-----------|
| All fields | **quranic-corpus-morphology-0.4.txt** | Verbatim from the corpus. No override. |

### `pages` table

| Field | Source | Rationale |
|-------|--------|-----------|
| `page_number` | pages.csv (row index) | col[0] equals row index; used as the page number. |
| `ayah_count_on_page` | pages.csv (col[1]) | Only source. Verified: sum = 6,236. |

---

## Conflict Resolution Log

| Table | Field | Conflict | Resolution |
|-------|-------|---------|-----------|
| surahs | ayah_count | Surah 9: fahras=128, tanzil=129 | Tanzil used (Tier 1 wins). Difference reflects a known scholarly counting variant (At-Tawbah). |
| surahs | name_arabic | quran.csv "ال عمران" (split) vs fahras "آلِعِمۡرَانَ" | quran.csv used; fahras name stored in source_id_fahras for reference |

No conflicts in text fields (each text column has exactly one source).

---

## Why Tanzil is Tier 1 for Text

1. Tanzil (tanzil.net) is the most widely adopted digital Quran text project, used as the base for hundreds of Quran apps and research tools.
2. The hafs text in `qurantexttanzil.csv` is the standard Hafs An-Asim recitation encoding used in the majority of printed masahif worldwide.
3. Row counts in the Tanzil file directly provide authoritative ayah counts (no counting ambiguity).
4. The file is clean: exactly 6,236 rows, no structural rows, no duplicates.

## Why the Morphology Corpus is Tier 1 for Lexical Data

1. The Quranic Arabic Corpus (v0.4, Kais Dukes, University of Leeds, 2011) is the de facto standard for Quranic morphological annotation.
2. It has been validated by Arabic linguists and used extensively in academic literature.
3. It is the only source in this corpus that provides token-level annotations (as opposed to word-level or ayah-level).
4. `stemming.csv` and `words.csv` are derivative or supplementary; the morphology corpus is the primary lexical authority.

## Sources Not Imported

| File | Reason |
|------|--------|
| `quranbylines.csv` | Layout data (printed lines) — relevant for display rendering, not for canonical analysis. A separate `lines` table could be added in a future schema version. |
| `unicode.csv` | Character inventory — informational. No corresponding schema need. |
| `stemming.csv` | Root-to-surface-form mapping — superseded by the morphology corpus, which provides the same data with full provenance coordinates. |
| `words.csv` | Word-type frequency table — fully reproducible from `SELECT form_arabic, COUNT(*) FROM words GROUP BY form_arabic`. Not needed as a separate table. |
