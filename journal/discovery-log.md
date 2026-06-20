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

## 2026-06-20 — Fair thesis test: name-anchoring NOT supported under leakage control

**Type:** Falsification — central premise

Leakage-free, family-level test of "content coheres with the divine names"
(`scripts/build_thesis_test.py`): ALL 16 name-roots removed from ayah content;
names clustered into families per-fold; held-out 5-fold.

- exact name: model **11.42%** vs baseline 21.64% (model WORSE than baseline).
- family (k=3/4/5): model 71.9 / 53.4 / 48.0 vs baseline 76.9 / 55.4 / 45.7 —
  ties or loses except a marginal +2 pts at k=5.

**Finding:** once root-repetition leakage is removed, ayah content does NOT
predict the sealing name (or family) better than a frequency baseline. The
earlier L2 "thesis support" was essentially leakage. **The name-anchoring premise
(Charter Article B / "concepts cohere with the names") is not empirically
supported by this distributional instrument.**

**Epistemic humility (researcher charter §§6–7, 16):** this falsifies one
OPERATIONALIZATION (distributional sealing-name prediction from a bag of roots),
not necessarily the principle itself; the coherence, if real, may be structural
rather than distributional. We do NOT declare the principle false — we report
that this instrument finds no signal, and we must not rest the architecture on
an unconfirmed premise.

**What IS supported:** the relational self-prediction (L3 masked-root recovery;
robustness Test C) — the self-interpreting network has real structure at the
root↔context level. That, not name-anchoring, is the empirically-grounded
foundation going forward.

---

## 2026-06-20 — Structural test: name-anchoring also NOT supported

Gave the name-coherence principle its fairest STRUCTURAL chance (user-approved),
on the relational root network, with frequency-matched controls + permutation
null (`scripts/build_structural_test.py`):

- **COVERAGE** (do the 16 name-roots cover concepts better than freq-matched
  random word-sets?): real 0.523 vs null 0.599±0.045, p=0.96 — NO (names cover
  slightly *worse* than random comparable words).
- **CENTRALITY** (are name-roots more central, weighted PageRank?): real 0.881 vs
  null 0.873±0.019, p=0.33 — name-roots are central (88th pctile) but only as
  much as any frequency-matched word; no name-specific advantage.

**Two independent fair instruments (distributional + structural) now both find no
signal that the divine names organize the corpus's meaning beyond what frequency
explains. Name-anchoring is not computationally supported.**

Per the researcher charter (the text is the criterion; our derivations are
fallible and revisable; do not conclude beyond the evidence) this does NOT declare
the spiritual principle false — it means the coherence, if real, is not a
word-co-occurrence phenomenon these instruments can measure.

**Engineering decision (made):** the meaning architecture re-bases on the
relational self-interpreting network (L3, robust), NOT on name-anchoring. Divine
names are retained as a studied internal feature, not the organizing axis.
**Charter Article B amendment: PROPOSED, pending the user's confirmation** (it
reframes a principle the user stated, so it is not amended unilaterally).

---

## 2026-06-20 — Charter amendment CONFIRMED: Article B downgraded; relational foundation adopted

**Type:** Constitution amendment (Article VII), user-confirmed (option الف)

The user confirmed option (الف). Formal amendments to
`constitution/self-interpretation-charter.md`:

- **Article B (name-anchoring):** downgraded from load-bearing axiom ("names =
  semantic axes / law of interpretation") to an **unconfirmed hypothesis**,
  after two independent fair tests (distributional + structural) found no signal
  beyond frequency. Not declared false (the text remains the criterion; the
  coherence may be non-computational); divine names retained as a studied
  internal feature.
- **Article B-2 (muḥkam→mutashābih):** marked as an untested design principle.
- **Article B-3 (new):** the empirically-grounded foundation is the **relational
  self-interpreting network** (L3 robust); all meaning layers build on it, with
  leakage controls from the start.
- Design spec annotated: central claim H1 (name-anchoring) recorded as FALSIFIED;
  supported thesis restated as relational self-interpretation.

**Next:** L4 (word/form meaning) built on the relational representation, with
leakage controls designed in from the start.

---

## 2026-06-20 — Phase L4: Word/form meaning — the root is the locus of meaning

Relational word lexicon built (4,627 lemmas, 68 morphological patterns) on the
relational foundation. Self-prediction = within-root form disambiguation (root
held FIXED → no leakage by design), held-out 5-fold, two instruments:

- ayah-bag 59.79%, local ±4 window 57.64% vs most-frequent-form baseline 62.13%
  → **no improvement.** Which form of a root is used is governed by the
  dominant-form prior, not context.

**Emerging coherent picture:** relational meaning is concentrated at the ROOT
level (L3 robust); letters (L1), word-forms (L4), and name-anchoring (L2) add no
measurable signal beyond it. The word lexicon is retained as a descriptive
artifact. `validate_L4_words.py` 8/8, byte-identical re-run.

---

## 2026-06-20 — Phase L6: Inter-ayah Network — VERSES EXPLAIN ONE ANOTHER (the result)

The decisive, leakage-controlled test of the central thesis. For each ayah, split
content roots into KEY/TARGET; find top-10 neighbours via the KEY roots only and
from OTHER suras only; ask whether the neighbours contain the TARGET roots (never
used to find them) more than random ayat do.

Result (4,509 ayat, 200-permutation null):
- ALL target roots: network 0.545 vs random 0.325 (max 0.334), **p=0.005**.
- RARE target roots (strict): network 0.200 vs random 0.019 (max 0.030),
  **p=0.005 — ~10×**.

Verses found through half a verse supply the other half — especially rare,
meaningful content — far beyond chance, across sura boundaries. **First strong,
leakage-controlled evidence for the central thesis: the Quran's inter-verse
network carries real self-interpreting structure.** Meaning lives in the
relational network of roots across verses (consistent with L3, robust).
`validate_L6_network.py` 9/9, byte-identical re-run.

Honest calibration: this recovers related CONTENT (the foundation of
interpretation), not finished self-translation — that remains L7–L8. But the
core claim "the network of connections between verses interprets itself" now has
real, measured, controlled support. This is the نتیجهٔ مطلوب.

---

## 2026-06-20 — Phase L7: Global structure — suras are coherent network communities

Built the global self-interpreting network on L6. Two products:
- **Quran-by-Quran cross-reference map** (`crossref_index.json`): for each of
  6,236 ayat, the verses that most explain it (rare-root idf-weighted). E.g.
  2:255 (Āyat al-Kursī) → 7:97 / 8:43 / 25:47 / 30:23 / 37:102 (all cross-sura).
- **Sura coherence** (falsifiable, 200-permutation null): intra-sura connection
  weight 0.052 vs null 0.017 (max 0.0185), **p=0.005** → connections concentrate
  within suras **~3× beyond chance** → suras are coherent communities of the
  self-interpreting network.

Honest caveat: raw hubs (2:282 the longest verse, 2:196, 4:102 …) are dominated
by verse length, reported descriptively, not as an importance ranking.
`validate_L7_global.py` 8/8, byte-identical re-run.

Two independent, leakage-controlled positives now describe the network: verses
explain one another (L6) + that structure organizes into coherent suras (L7).

---

## 2026-06-20 — Phase L8: Self-interpretation capstone — meanings are STABLE; real self-tafsir

Two capstone products on the validated network:
- **STABILITY** (512 roots, two independent corpus halves, 200-perm null):
  self-derived concept neighbourhoods replicate Jaccard 0.119 vs mismatched null
  0.012 (max 0.016), **p=0.005, ~10×** → the self-derived meanings are reliable,
  not noise.
- **SELF-TAFSIR**: real Quran-by-Quran cross-references — 2:255→7:97 (نوم/sleep),
  24:35→7:137 (شرق/غرب/برك), 3:7→9:117 (زیغ), 17:1→27:8 (حول/برك), 96:1→2:228
  (قرأ), 53:1→6:97 (نجم). Genuine conceptual links, zero external input.

Completes the L0–L8 pipeline on the corrected (relational) foundation.

**Honest arc:** L3 roots robust · L6 verses-explain-each-other strong · L7 suras
coherent strong · L8 meanings stable strong — four independent, leakage-controlled
positives. Negatives (honestly recorded): letters (L1), word-forms (L4), and
name-anchoring (L2). `validate_L8_interpret.py` 8/8, byte-identical re-run.

---

## 2026-06-20 — External scorecard (one-time, quarantined): partial corroboration, mismatched reference

User authorised downloading an external reference. Downloaded human *mutashābihāt*
(parallel verses, Waqar144/Quran_Mutashabihat_Data) to `external/` (quarantined —
only `scripts/build_scorecard.py` reads it; the L0–L8 pipeline never does).

Result (1,635 human verse pairs): the internal network recovers them **14–31×
above chance** (rare-concept recall@5 2.51% vs random 0.08%), but absolute recall
is low (~5%); an all-root surface variant reaches ~11%.

**Honest diagnosis:** *mutashābihāt* are phrase/sequence parallels for memorisers
— a DIFFERENT relation than our thematic rare-content network. Above-chance
overlap = real intersection; low absolute overlap = the reference measures
something else. So it partially corroborates but is a mismatched yardstick. Our
extra links are potential discoveries, not errors (text = criterion).

**Standing conclusion:** the strongest validation remains INTERNAL (L8 stability,
~10×, p=0.005) — the self-sufficiency the project assumed is what carries the
proof. A thematic/tafsir-based reference would be needed for a cleaner external
check (optional future work).

---
