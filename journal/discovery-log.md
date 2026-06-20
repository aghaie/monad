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

## 2026-06-20 — Architecture Reset: Self-Interpretation Track (Monad v2)

**Type:** Constitution amendment + architecture decision

**Directive (user):** Start anew with a new phasing. Build, from the ground up
(letters → roots → words → phrases → ayat → suras → whole), the most correct
possible understanding of the Quran. Thesis: the Quran needs no external
reference; the network of relations among all verses can interpret and
translate itself, and this network must be discovered. Premise (axiom): God
exists and is the Author; the names/attributes of God are inscribed in the
text, and all concepts cohere with the names — this coherence is the law of
interpretation. Existing human interpretations may err; no mistake shall occur.

**Locked decisions:**

1. Validation = internal self-prediction (masked recovery) as primary, plus a
   single held-out external scorecard at the end (demonstration only, never
   input).
2. Letters = phonological / structural only; semantic induction begins at the
   root level.
3. Divine names = discovered from the text (attributes predicated of God),
   established as the semantic anchors / axes; the traditional 99-name list is
   quarantined for final cross-check only.
4. "No mistake" = abstention over error: the system marks `UNKNOWN` /
   low-confidence rather than asserting beyond evidence; confidence tiers,
   provenance, falsification, and determinism are mandatory.
5. Human interpretations are never ground truth; on divergence, the text's
   internal evidence governs and the divergence is flagged.

**Constitution amendments (per Article VII):** Article VI's exclusion of
"translation" is amended — self-derived (internal) translation/understanding is
now the goal; external translation remains excluded as input (held-out
scorecard only). New governing charter adopted:
`constitution/self-interpretation-charter.md`. Articles II–IV and VII retained.

**Phasing (supersedes Article V list for this track):**
L0 substrate → L1 letters → L2 names → L3 roots → L4 words → L5 phrases →
L6 ayat → L7 sura/whole → L8 self-translation + scorecard.

**Design spec:** `docs/superpowers/specs/2026-06-20-self-interpreting-quran-design.md`.

**Legacy:** Prior `generated/*` discovery engines (≈30) and their reports are
retained for provenance (Constitution III.4) but are superseded; new work uses
the L-layer namespace. The canonical substrate `generated/monad.db` (built by
`scripts/build_database.py`) is reused as L0 — pure structure (no semantics),
already validated.

---

## 2026-06-20 — Adoption of the Researcher-Agent Charter

**Type:** Constitution amendment (governing principles)

**Summary:** The user issued the *Researcher-Agent Charter*
(منشور عامل پژوهشگر قرآن) — 22 principles plus a final principle defining the
agent's purpose, methodology, epistemics, and output discipline. Adopted
verbatim as the **governing operating constitution**:
`constitution/researcher-agent-charter.md`. It sits above the technical
`self-interpretation-charter.md` and the design spec, which implement it.

**Reconciliations applied:**

1. **Confidence tiers** unified to the charter's four named tiers:
   صریح/explicit (C1) → قوی/strong (C2) → محتمل/probable (C3) →
   نامشخص/unclear (C4 = abstain). Replaces the prior generic C1–C4 labels in the
   technical charter and the spec.
2. **Muḥkam → mutashābih** (charter §5) adopted as a **second anchoring axis**
   alongside the divine names: interpretation propagates from high-clarity
   (muḥkam) verses to low-clarity (mutashābih) ones. "Clarity" is an internal,
   measured quantity (attestation, recovery score, construction commonness), so
   it respects the no-external-reference boundary. Added as Article B-2 of the
   technical charter and §7.1 of the spec. Affects L6–L8.
3. **Analysis & output protocol** (gather all related verses; never interpret
   in isolation; list all candidate interpretations with tiers; apparent-
   contradiction protocol; accept Quranic silence) bound to L6–L8 and to all
   interpretive output (spec §7.1).

**Governing principle (overrides all):** «قرآن معیار است؛ برداشت تو از قرآن
معیار نیست.» — the Quran is the criterion; the agent's understanding is not.

---

## 2026-06-20 — Guidance Principle (Purpose-Coherence Re-Test)

**Type:** Constitution amendment (governing principle)

**Principle (user, verbatim):** «هدف قرآن هدایت انسان به سوی حق، عدالت، رحمت،
آگاهی و مسئولیت‌پذیری است؛ هر برداشتی که به نفی این اصول منجر شود باید دوباره با
کل قرآن آزموده شود.»

**Integration:** Recorded in the Researcher-Agent Charter (Guidance Principle)
and as Article H of the technical charter; bound into the analysis protocol
(spec §7.1). Framed as a *re-test trigger*, not a content filter, to preserve
falsifiability: the five guidance-aims are Quran-derived (not imported); a
reading that negates one triggers a re-test against the whole Quran; if the text
still supports it, the reading stands and our grasp of the aim is revised — the
Quran remains the criterion.

---

## 2026-06-20 — Phase L2: Divine Names / Anchors (keystone result)

**Type:** Layer build + first thesis test

**Method:** Names discovered PURELY internally (no 99-list — quarantined) via
three signals: predicate-of-Allah (INDEF NOM/ACC within 5 words of "Allah"),
name-community pairing (names sit beside names), and predicate-dominance
(seed/frequency). No syntactic treebank in QAC v0.4 → ranked candidates with
confidence tiers, not a closed list; confounds flagged honestly.

**Discovered:** 16 قوی/strong names — غفور علیم رحیم حکیم سمیع خبیر واسع قدیر
حلیم بصیر عفوّ رؤوف قوی محیط شهید وکیل. Famous but ambiguous names (عزیز، عظیم،
حمید) fall to محتمل due to substantial non-divine usage — an honest finding, not
an error. Confounds (شیء، قرض، ثمن) correctly kept out of قوی.

**THESIS TEST (keystone):** predict which divine name seals an ayah from the
ayah's content roots, held-out 5-fold. Model **30.91% top-1 / 68.55% top-3** vs
baseline 21.64% / 50.13% vs random 6.25%. **Model beats baseline and random →
first internal empirical support for "concepts cohere with the names" (Charter
Article B).** `validate_L2_names.py` 11/11, byte-identical re-run.

---

## 2026-06-20 — Phase L3: Self-grounded Root Lexicon (name-coordinates)

**Type:** Layer build — first full meaning layer

**Method:** For every root, "meaning" = internal relations + coordinates in the
L2 name-space (no external gloss). name_coordinates (PPMI vs the 16 anchor
names), relational_neighbors (root-root PPMI), field_neighbors (cosine over
name-profiles), defining_ayat, and an attestation tier (قوی 593 / محتمل 453 /
نامشخص-abstain 589). L2 outputs used as permitted source data.

**Meaningfulness (zero external input):** رحم → رحیم/رؤوف/غفور; علم →
علیم/واسع/سمیع/حکیم; کتب → شهید/وکیل. Each root sits next to the names it should.

**Self-prediction:** masked content-root recovery from ayah context, held-out
5-fold (35,596 instances, 1,635 roots). Model **9.70% top-1 / 17.73% top-3** vs
baseline 3.54% / 8.68% vs random 0.061%. **Model beats baseline and random ⇒ the
relational network recovers its own roots; self-interpretation works at the root
level.** Honest coverage: only 221 roots are directly name-anchored (co-occur
with a name ≥3×); the rest rely on relational fingerprint. `validate_L3_roots.py`
12/12, byte-identical re-run.

---

## 2026-06-20 — Robustness study + L2 correction (revisability in action)

**Type:** Falsification study + result revision (Charter Article D / §17)

Before building further layers, ran adversarial nulls on L2 and L3
(`scripts/build_robustness.py`, deterministic):

- **L2 permutation null:** real 31.18% vs null 4.10%±1.08% (p=0.020) → real
  content→name structure exists.
- **L2 leakage test:** removing the sealing name's OWN root from the ayah content
  drops accuracy to **16.13%, below the 21.64% frequency baseline**. ⇒ ~half the
  headline was root-repetition leakage (رحمة→رحیم).
- **L3 mismatched-context null:** real 4.93% vs null 0.18% (p=0.048) → masked-root
  recovery is genuinely contextual. **L3 robust.**

**Revision:** The earlier L2 claim "thesis supported at 30.9%" is **downgraded**.
L2 shows real but modest structure; the clean content→*exact*-name signal is weak
(≈ at/below baseline), partly because synonymous names are mutually confusable.
The thesis should be tested at the name-*family*/ayah level (L6) with leakage
controls built in. `docs/L2-names-report.md` annotated;
`docs/L2-L3-robustness-report.md` added. The discipline caught an inflated result
before it propagated — which is the point.

---
