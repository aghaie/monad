# Self-Interpreting Quran — Architecture & Phasing (Monad v2)

- **Date:** 2026-06-20
- **Status:** Adopted. Supersedes the prior 30-engine track for new work.
- **Governing operating constitution:** [researcher-agent-charter.md](../../../constitution/researcher-agent-charter.md)
- **Technical charter:** [self-interpretation-charter.md](../../../constitution/self-interpretation-charter.md)

## 1. Premise & Thesis

- **Premise (axiom, not under test):** the Quran is the speech of God.
- **Thesis (the falsifiable engine of the project):** the Quran is
  self-interpreting — the relational network among its verses suffices to
  interpret and self-translate it, with no external semantic reference. Meaning
  is anchored in the divine names attested within the text.

## 2. The Central Falsifiable Claim

- **H0 (null):** organizing Quranic meaning around the divine-name anchors does
  not predict held-out content better than name-agnostic baselines.
- **H1 (thesis):** a name-anchored, internally-induced semantic model recovers
  masked content (roots, words, links) better than (a) a frequency baseline and
  (b) a name-agnostic distributional baseline.

Every layer reports its self-prediction score and a falsification verdict. A
negative result is recorded honestly, never hidden.

## 3. What "Meaning" Is (internal, intensional)

No external glosses. The meaning of a unit `U` is represented by:

- **relational fingerprint** — co-occurrence, grammatical frames, contrast /
  substitution set;
- **selectional preferences** — what subjects/objects/frames `U` takes;
- **anchor profile** — coordinates over the divine-name axes (how `U` coheres
  with each name);
- **defining ayat** — the occurrences that most constrain `U`;
- **induced vector** — trained only on the corpus; no pretrained embeddings.

"Understanding `U`" = the degree `U` is predictable-from / predictive-of the
rest of the corpus. A word's meaning is extracted **first from its uses across
the whole Quran** (Researcher-Agent Charter §8).

## 4. Unifying Mechanism — Masked Recovery

Hide `U`; recover it from everything else. This single mechanism both **induces**
meaning (`U`'s meaning is what makes it recoverable) and **validates** it
(claimed understanding must yield recovery above baseline). Held-out folds, no
leakage, deterministic.

## 5. The Boundary

- **Allowed (structure):** Tanzil text, QAC morphology (segmentation / root /
  grammar), Buckwalter map, sura metadata.
- **Forbidden (semantics, as input):** dictionaries, translations, tafsir,
  theology, pretrained models, external ontologies.
- **Quarantined (final scorecard only):** one external translation + the
  traditional 99-name list. Fallible; comparison only.

## 6. No-Mistake Discipline (abstention over error)

- Abstain (`UNKNOWN` / low-confidence) rather than assert beyond evidence.
- Confidence tiers **صریح/explicit (C1) → قوی/strong (C2) → محتمل/probable (C3)
  → نامشخص/unclear (C4 = abstain)** + provenance `(S:A:W:T)` on every datum.
- Falsification attempt + self-prediction score per layer.
- Determinism & reproducibility (seeds, pinned inputs, offline).
- Human references are never ground truth; divergence is flagged, the text
  governs.

## 7. Layers

| Layer | Name | Method (internal only) | Self-prediction test |
|------|------|------------------------|----------------------|
| **L0** | Substrate | **Reuse + verify** the canonical SQLite DB (surahs, ayahs, roots, lemmas, words, morphology, pages). Pure structure, no semantics. | Counts (114 / 6236 / 128219) + FK integrity. |
| **L1** | Letters / phonology | Letter inventory, positional distribution, root morpho-phonology (weak / hamzated / geminate letters & alternations), muqaṭṭaʿāt flagged. **No semantic claim.** | Predict morphological alternation from letter structure. |
| **L2** | Names (anchors) | Discover attributes predicated of God (epithet positions; predication of `{ll~ah` / `Huwa`; recurrent ayah-final pairs). Build each name's relational signature. Establish names as basis axes. | Do names span the high-frequency concept space; does a name-basis beat a name-agnostic basis at held-out recovery? |
| **L3** | Roots | For each ~1642 roots: relational fingerprint + selectional prefs + contrast set + **anchor profile (name coordinates)** + induced vector. | Masked root recovery vs. baselines; per-root confidence; abstain for under-attested roots. |
| **L4** | Words / forms | Compose root + pattern (wazn) + affixes → word meaning; derive pattern semantics internally. | Predict word behavior from root + pattern. |
| **L5** | Phrases / clauses | Intra-ayah composition via grammatical features, particles, government, adjacency (no full treebank in v0.4 → shallow syntax derived internally, flagged). | Masked slot recovery within the clause. |
| **L6** | Ayat | Per-ayah meaning = composition + connection network (shared roots, parallels, refrains, formulae — all internal). Interpretation = reading most coherent with invoked names, propagated from muḥkam verses. | Masked phrase recovery; inter-ayah link prediction. |
| **L7** | Sura / whole | Sura structure + global inter-ayah / inter-sura graph = the self-interpreting network. Hubs, most-constraining ayat, propagation paths. | Predict held-out links; community stability. |
| **L8** | Self-translation + scorecard | Propagate meaning to convergence; emit best internally-grounded interpretation per ayah with confidence + provenance path. **Then once:** held-out external scorecard (alignment %, divergences flagged, text governs). | Convergence stability + external alignment (demonstration only). |

## 7.1 Anchoring & Protocol (from the Researcher-Agent Charter)

**Dual anchoring.** Two internal anchor systems ground interpretation:

1. **Divine names** (Charter B) anchor the *semantic* space — concepts are
   located by their coherence with the names.
2. **Muḥkam → mutashābih** (Charter §5) anchors the *interpretive* space —
   interpretation propagates from high-clarity (muḥkam) verses to low-clarity
   (mutashābih) ones, never the reverse. Clarity is measured internally
   (attestation, recovery score, construction commonness).

**Analysis & output protocol** (Charter §§3–4, 6–7, 13, 18–22), binding on
L6–L8 and on every interpretive answer:

- Gather *all* related verses for a topic; never interpret a verse in isolation.
- Present evidence (verses) → then their connections → then a conclusion kept
  visibly separate from the evidence.
- List *all* plausible interpretations with their confidence tiers; do not force
  a single choice without sufficient evidence.
- On apparent contradiction: first suspect a gap in understanding, translation,
  context, categorization, or data — do not conclude real contradiction until
  all Quranic evidence is examined.
- Where the Quran is silent, accept the silence; do not fill the gap with guess.
- **Purpose-coherence re-test:** if a reading negates a well-attested
  guidance-aim (truth, justice, mercy, awareness, responsibility — all
  Quran-derived), re-test it against the whole Quran before keeping or
  discarding; the text remains the criterion.

## 8. Cycle 1 Scope

`L0 (reuse+verify) → L1 (letters/phonology) → L2 (names + anchors) → L3 (root lexicon in name-coordinates)`.

**Deliverable:** the first self-grounded, name-anchored root lexicon with
self-prediction scores — the first concrete test of the thesis. Each layer gets
a `build_*.py` + `validate_*.py` + a report, following existing repo
conventions.

## 9. Namespaces & Reuse

- `generated/monad.db` — substrate (reused as L0).
- `generated/layers/L1_letters`, `L2_names`, `L3_roots`, … — new pipeline outputs.
- Prior `generated/*` (≈30 engines): legacy, retained for provenance
  (Constitution III.4), superseded for new work.
- Scripts: `scripts/build_Lx_*.py` + `scripts/validate_Lx_*.py`.

## 10. Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Small corpus (~78k tokens) → leakage / overfit in self-prediction. | Held-out folds; conservative baselines; abstention for sparse units. |
| Circularity: names defined by contexts that names then "explain". | Discover names **structurally** (predication), then test against a name-agnostic baseline; falsification required. |
| v1 substrate parser under-captures gender/number on combined feature tokens (e.g. `MS`). | L1 re-derives morphological features rigorously from `features_raw`. |
| "Meaning" without glosses is hard to inspect. | Express meaning as defining-ayat + nearest names + contrast set (human-readable, internal). |
| Over-claiming. | Abstention + confidence tiers + the no-mistake discipline. |

## 11. Definition of Done (Cycle 1)

- `monad.db` rebuilt and validated (counts + FK integrity).
- L1, L2, L3 each: deterministic build, validation pass, report, and a
  self-prediction score beating baseline **or** an honest negative result.
- No external semantics used as input (verified by an input inventory).
