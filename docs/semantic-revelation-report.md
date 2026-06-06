# Semantic Revelation Report — Phase 7

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase7-revelation-1.0`.

Phase 7 built the **Semantic Revelation Engine** — the first phase permitted to
investigate concept *identity*. Identity here is never an imported meaning. A
concept's identity and its candidate "names" are expressed strictly as the
concept's own dominant **Arabic** roots and lemmas and the ayah / structural
patterns they form. **No token is translated, glossed, defined, or interpreted.**
No tafsir, translation, dictionary, theology, external source, or pretrained
embedding is used. No certainty, divine origin, or human origin is claimed.
Competing identities are preserved; no single identity is forced. Phases 1–6 are
read and hashed but never rebuilt or modified.

---

## 1. The discipline of revelation-without-meaning

The integrity of the whole project rests on never importing meaning. Phase 7
therefore obeys one hard rule, enforced by the validator:

> **A candidate name must be a literal Arabic token that already appears among
> the concept's own member roots/lemmas.** It points at the dominant lexical
> anchor; it does not explain it.

So when the engine reports that `CONCEPT_007` is anchored on the lemma `ٱللَّه`
(root `اله`), it is not asserting a meaning — it is reporting that, of the
concept's 24 member roots and 326 member lemmas, the root `اله` / lemma `ٱللَّه`
carries the largest activation weight. The reader supplies any meaning; the
engine supplies only the Quran-internal evidence. The validator re-checks every
one of the candidate names against the concept's member set (3,299 checks pass).

---

## 2. Method (Phases A–G)

| Phase | Output | What it reveals (evidence only) |
|---|---|---|
| A | `concept_dossiers.json` | consolidated per-concept evidence: roots, lemmas, signature ayahs/surahs, neighbours, dependency roles, graph/activation/compression profiles |
| B | `semantic_fields.json` | member roots clustered into fields by intra-concept signature-ayah co-occurrence + Phase-2 neighbour links; lemma families grouped by shared root |
| C | `ayah_identity_profiles.json` | over top 25/50/100 signature ayahs: recurring root/lemma themes, nominal "actors" (POS N/PN/ADJ), verbal "actions" (POS V), structural "outcomes" (downstream anchors) |
| D | `root_consistency.json` | identity coherence (HHI), semantic agreement, fragmentation, ambiguity (entropy), multi-membership; a convergence verdict |
| E | `candidate_names.json` | 0–5 root-anchored Arabic candidate names per concept, with confidence + supporting roots/ayahs/propositions/neighbours |
| F | `core_revelation.json` | deep identity dossiers (hypotheses, competing hypotheses, ambiguity, evidence graph) for `CONCEPT_007/016/081`, the size-9 SCC, the top-20 |
| G | `falsification_results.json` | each proposed identity is *attacked*: contradicting roots / ayahs / neighbours / propositions; survival verdict |
| — | `identity_confidence.json` | aggregate per-concept identity tier: strong / moderate / weak / resists |

POS classes used in Phase C are Phase-1 morphology annotation — structural, not
semantic. Co-occurrence is taken over each concept's top-100 signature ayahs
(Phase-6 evidence). Everything is deterministic, pure-stdlib, byte-identically
reproducible (`validate_revelation.py --rebuild`, all checks pass).

---

## 3. Aggregate findings (no interpretation)

- **Identity tiers across 103 concepts:** **43 strong · 51 moderate · 3 weak · 6
  resist identification.** "Resist" = no member root reaches the dominance floor
  (share ≥ 0.15); these are the most lexically diffuse concepts.
- **Consistency verdicts:** 15 `coherent_single` (one root dominates), 55
  `coherent_dominant`, 33 `diffuse_unified` (one connected field, no single
  dominant root), 0 fully fragmented.
- **Competing identities are common:** 42 concepts carry ≥ 2 near-equal candidate
  names (2nd ≥ 60% of the 1st). The engine preserves them rather than forcing one.
- **Falsification:** of 97 testable identities, **94 survive** their attack and
  **3 fail** (`CONCEPT_011`, `041`, `043`) — single-anchor identities that do not
  explain a majority of their own signature ayahs.
- **Shared anchors (an honest ambiguity):** four anchors head more than one
  concept — `اله` (`CONCEPT_007`, `081`), `رسل` (`CONCEPT_061`, `085`, `088`),
  `كفي` (`009`, `067`), `قمص` (`048`, `076`). Distinct concepts can converge on
  the same dominant root; they are separated by their *other* evidence, not by it.

---

## 4. The six concepts that resist identification

| Concept | Roots | Top-root share | HHI | Verdict |
|---|---:|---:|---:|---|
| `CONCEPT_001` | 34 | 0.122 | 0.056 | diffuse_unified |
| `CONCEPT_002` | 33 | — | 0.057 | diffuse_unified |
| `CONCEPT_003` | 32 | 0.104 | 0.068 | diffuse_unified |
| `CONCEPT_004` | 31 | — | 0.065 | diffuse_unified |
| `CONCEPT_013` | 17 | — | 0.080 | diffuse_unified |
| `CONCEPT_017` | 15 | — | 0.084 | diffuse_unified |

These are the large, lexically flat concepts: no single root carries ≥ 15% of
activation weight, so no single Arabic anchor can stand for them. This is a
finding, not a failure — Monad reports that these concepts have *distributed*
identities rather than forcing a misleading single name.

---

## 5. Worked examples (evidence only)

- **`CONCEPT_081`** — anchor `ٱللَّه` / `اله`, confidence 0.629, HHI 0.442,
  `coherent_single`, survives falsification (pressure 0.01). The clearest single
  identity in the dataset.
- **`CONCEPT_053`** — competing anchors `عذب` (0.276), `كفر` (0.219), `يوم`
  (0.217), `اخر` (0.186); `competing_names = true`. Four near-equal candidates
  are preserved; none is privileged.
- **`CONCEPT_007`** — anchor `ٱللَّه` / `اله`, confidence 0.240 but high ambiguity
  (entropy 0.85): one connected diffuse field anchored on `اله`, surrounded by
  many co-equal roots. Survives falsification (only 4% of signature ayahs lack
  the anchor) yet is only `moderate` because the field is broad.

---

## 6. Outputs

`generated/revelation/`: `concept_dossiers.json`, `semantic_fields.json`,
`ayah_identity_profiles.json`, `root_consistency.json`, `candidate_names.json`,
`core_revelation.json`, `identity_confidence.json`, `falsification_results.json`,
`revelation_manifest.json`.

Tooling: `scripts/build_revelation.py` (≈ 0.4 s, pure stdlib),
`scripts/validate_revelation.py` (3,299 checks, `--rebuild` byte-identical).
Reports: `concept-identity-report.md`, `core-revelation-report.md`,
`identity-confidence-report.md`, `falsification-report.md`,
`phase7-final-report.md`, this report.

---

## 7. Limitations

- **Anchor ≠ meaning.** A candidate name is the dominant member token, nothing
  more. The reader supplies meaning; the engine never does.
- **Inherited population.** Identity rests on the Phase-3 concept set, Phase-4
  relations, and Phase-6 activation; different upstream thresholds would redraw
  every anchor.
- **Dominance floor is a deterministic choice** (root share ≥ 0.15). A different
  floor would move concepts across the resist boundary; raw shares are published.
- **POS-based actors/actions** rely on Phase-1 morphology tags only.
- **No certainty.** Confidence is a concentration statistic, not a truth value.

---

## 8. Prohibitions observed

`no tafsir · no translations · no dictionaries · no theology · no external
sources · no pretrained embeddings · no human labels · no imported interpretation
· no certainty · no divine origin · no human origin · no doctrine · no apologetics
· no single identity forced · competing identities preserved · names are
Quran-internal Arabic tokens only · prior phases never rebuilt.`

---

## 9. Reproduce

```bash
python3 scripts/build_revelation.py
python3 scripts/validate_revelation.py --rebuild
```
