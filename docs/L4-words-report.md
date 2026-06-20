# L4 — Word / Form Meaning Report

- **Layer:** L4 (Monad v2), built on the relational foundation (Charter Article B-3).
- **Question:** does morphological form (pattern/wazn, derivation, voice, participle) carry meaning beyond the bare root?
- **Source:** `generated/monad.db`. Outputs: `generated/layers/L4_words/`.
- **Reproducibility:** `validate_L4_words.py` passes 8/8, byte-identical re-run.

## Deliverables

- **word_lexicon.json** — 4,627 lemmas, each with its root, morphological
  pattern, attestation tier (763 قوی / 1,194 محتمل / 2,670 abstain), and top
  associated roots (PPMI, own root excluded).
- **pattern_stats.json** — 68 distinct morphological patterns. Most common:
  N (2,008), ACT-PCPL active participle (358), V-IMPF-ACT (346), V-PERF-ACT
  (239), ADJ (198), PASS-PCPL passive participle (122). The pattern layer is
  cleanly extracted from the morphology.

## Self-prediction — does form carry meaning beyond root?

**Task (leakage-controlled by design):** hold the root FIXED and predict *which
form/lemma of that root* is used, from context. Because every candidate shares
the root, the root can never be the cue — this isolates the form's contribution.
41,035 instances over 923 polysemous roots, held-out 5-fold. Two context
instruments, in fairness:

| Predictor | top-1 |
|-----------|------:|
| Model — ayah-bag context | 59.79% |
| Model — local ±4 window | 57.64% |
| Baseline — most frequent form of the root | **62.13%** |

**Verdict: no improvement over baseline.** Neither the coarse (ayah-bag) nor the
appropriate (local window) instrument beats simply guessing the root's dominant
form — the local window is in fact slightly worse. **Which specific word-form of
a root appears is not recoverable from context; it is governed by the
dominant-form prior.**

## What this means — the emerging coherent picture

Across the pipeline, the relational meaning signal is **concentrated at the root
level**:

| Layer | Unit | Relational signal |
|-------|------|-------------------|
| L1 | letters | none (structural only) |
| **L3** | **roots** | **strong, robust** (masked-root recovery beats null) |
| L4 | word-forms | none beyond the root (this report) |
| L2 | divine names as axes | not supported (two fair tests) |

So in this corpus, at ayah/word granularity, **the root is the locus of
relational meaning.** Letters below it and word-forms above it do not add
context-distinguishable signal, and the divine names are not privileged axes.
The word lexicon here is therefore a useful *descriptive* artifact, but form is
not a meaning-multiplier over the root.

## Prohibitions observed

No external glosses, dictionaries, tafsir, translations, or pretrained models.
Built entirely from the corpus, on the relational foundation.
