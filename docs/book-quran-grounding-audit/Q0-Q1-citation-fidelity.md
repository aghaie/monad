# Book Quran-Grounding Audit — Phases Q0–Q1

**Subject:** Mohammadali Jannatkhahdoost, *نظریهٔ آزادی، ایران و دین* (817-page Persian
edition, `azadi din iran _ Jannatkhah.pdf`).
**Claim under test:** the book asserts its *اصول موضوعه* (postulates/axioms) are written
"based on Quran reference" (بر اساس رفرنس قرآن).
**Method:** internal, mechanical, reproducible. Ground truth = the Tanzil Quran text in
this repo (`corpus/quran/source/qurantexttanzil.csv`, 114 surahs / 6236 verses). No human
tafsir is used as an input.

---

## Q0 — Reference extraction

`scripts/book_audit_q0_extract.py` parses the layout-preserving `pdftotext` output and
extracts every Quran reference. Four citation shapes occur in the book; all are handled,
including pdftotext's bidi reordering of ornamental verse markers (`﴿N﴾` → `﴿ ﴾Nسوره X`):

| pattern | example | count |
|---|---|---|
| `bracket` (`﴿ ﴾N سوره X`) | `…عَلِيم ﴿ ﴾۲۵۶ سوره البقرة` | 25 |
| `ayah_first` (`آیه N سوره X`) | `آیه ۲۵۶ سوره بقره` | 16 |
| `surah_only` (`سوره X`, no ayah) | `سوره الرحمن` | 19 |
| `surah_first` (`سوره X آیه N`) | `سوره فرقان آیه ۶۳` | 1 |

- **61 references** extracted, across **25 distinct surahs**.
- **42** carry a specific `surah:ayah`; **19** are surah-level only.
- **0** had an unresolvable surah name (full 114-name normalization map).
- Most-cited surahs: al-Baqara (13), al-Nisāʾ (9), Āl ʿImrān (6), al-Nūr (5), al-Māʾida (5).

Output: `generated/book-quran-audit/q0_references.jsonl`.

## Q1 — Citation fidelity

`scripts/book_audit_q1_fidelity.py` checks each `surah:ayah` against the corpus for
(a) **existence** and (b) **quote-match** (recall of canonical Arabic content-words inside
a ±300-char window around the citation).

| metric | result |
|---|---|
| citations resolving to a **real verse** (existence) | **42 / 42 = 100 %** |
| fabricated / out-of-range citations | **0** |
| canonical **Arabic** text quoted faithfully near citation | 29 / 42 (69 %) |
| Arabic recall low (`reference_only`) | 13 / 42 |

**Every verse the book cites exists. No fabricated or out-of-range references.**

### The 13 low-Arabic-recall cases are not errors

The recall metric scores *Arabic* overlap only. Manual review of all 13 confirms each is a
**correct attribution** where the book quotes the verse's **Persian translation** or
discusses its actual content — e.g.:

- R-0027 → 2:216: book quotes it in Persian, «چه بسا چیزی را خوش نداشته باشید…» (exact).
- R-0011 → 25:63: about «عباد الرحمن» who answer the ignorant with «سلام» — correct.
- R-0023 → 9:5: discussed as the "sword verse" re مشرکین and treaty-violation — correct.
- R-0033/34 → 24:33: discussed re کنیز / sexual exploitation — correct.

So fidelity is **higher** than the 69 % mechanical figure; **0 misattributions detected**.
(The corpus has no aligned Persian translation, so Persian-quote matches cannot be scored
automatically; this is a stated limitation, not a finding against the book.)

---

## Verdict so far

On the **citation layer**, the book's claim holds: its Quran references are real,
correctly numbered, and faithfully reproduced. Integrity at this level is **clean**.

This does **not** yet test the substantive claim — that the *axioms* are *grounded in* the
Quran (vs. merely decorated with verses), nor whether verses are read in context. Those are
phases **Q2** (grounding coverage) and **Q3** (contextual fidelity via the self-interpreting
relational network).

**Reproduce:**
```
pdftotext -enc UTF-8 -layout "<book>.pdf" generated/book-quran-audit/raw/book_fa.txt
python3 scripts/book_audit_q0_extract.py
python3 scripts/book_audit_q1_fidelity.py
```
