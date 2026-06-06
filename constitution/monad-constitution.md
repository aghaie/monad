# Monad Constitution

## Article I — Purpose

Monad exists to build a rigorous, systematic, and reproducible framework for studying the Quran as a textual corpus. The goal is to make latent structure explicit — lexical, propositional, relational — without imposing interpretation.

## Article II — Source Supremacy

1. The Quranic text as found in `corpus/quran/source/` is the ground truth. It is never modified, normalized away from its canonical form, or replaced by inference.
2. All derived data must carry a provenance reference: at minimum `sura:ayah`, ideally `sura:ayah:word:token`.
3. Data not traceable to a corpus position is not admissible as a research artifact.

## Article III — Derivation Discipline

1. Every datum in `data/` must be the output of a documented, repeatable process.
2. Processes are stored in `scripts/` or documented in `docs/`.
3. Human judgment is admissible only when documented in `journal/` with rationale.
4. Generated content in `generated/` is ephemeral and is not treated as source.

## Article IV — Epistemic Humility

1. The system distinguishes between what the text says and what it might mean.
2. Semantic analysis produces hypotheses, not conclusions.
3. Contradictions flagged in `data/contradictions/` are tensions requiring investigation, not errors in the text.
4. No theological claim is made. Analysis operates at the level of textual structure.

## Article V — Phase Separation

1. Each phase (corpus → lexical → propositional → semantic → graph → analysis) builds strictly on the output of prior phases.
2. Phase N outputs are not used as inputs to Phase N−1.
3. Cross-phase dependencies are explicitly documented.

## Article VI — Scope Boundaries

The following are explicitly outside scope:

- Tafsir-based interpretation
- Hadith corpus integration (unless explicitly initiated as a new corpus track)
- Translation evaluation or selection
- Theological argumentation
- Fatwa or ruling derivation

## Article VII — Revision

This constitution may be amended by explicit decision recorded in `journal/discovery-log.md` with date and rationale.
