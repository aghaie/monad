# Discovery Log

This log records decisions, findings, and amendments that affect the structure or direction of the Monad project. Entries are chronological and permanent — existing entries are never deleted, only annotated.

---

## 2026-06-06 — Repository Initialization

**Type:** Architecture decision

**Summary:**
Initial repository structure established. Ten source data files inventoried from `data/`. Files classified and organized into `corpus/quran/` subdirectories by function:

- `source/` — four Quranic text variants
- `morphology/` — Quranic Arabic Corpus v0.4
- `lexical/` — stemming and word frequency tables
- `metadata/` — sura index, page mapping, unicode character table

**Key findings from data inspection:**

1. `quran.csv` contains 6,461 rows against 6,236 canonical ayat. The 225-row surplus consists of sura header rows (aya index = 0) and additional basmala entries. These are not duplicates but structural rows.

2. `qurantexttanzil.csv` and `quranuthmanitanzil.csv` each have a trailing empty 5th column. This is a consistent trailing-comma artifact from export, not missing data.

3. `unicode.csv` contains whitespace and control characters (space U+0020, carriage return U+000D, line feed U+000A, vertical tab U+000B, form feed U+000C) as data rows. These are valid entries documenting the character inventory of the corpus, not encoding errors.

4. `words.csv` row 3 has an empty first column. This is the empty-string token (null word boundary marker used in the source export).

5. Morphological corpus (v0.4) encodes positions as `(S:A:W:T)` — sura, ayah, word, token. Contains 128,219 annotated tokens across 1,642 unique roots. Uses Buckwalter transliteration throughout.

6. `fahras.csv` contains all 114 suras, unique sura numbers, no duplicates.

**Decision:** Original files in `data/` are retained in place. Copies placed in `corpus/quran/` subdirectories. Corpus copies are the canonical reference; `data/` originals kept for provenance.

**Constitution status:** v1 adopted. See `constitution/monad-constitution.md`.

---
