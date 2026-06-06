# Frequency Null Model Report — Phase 17

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase17-frequency-null-1.0`.

Phase 16 showed the dominant hub is largely explained by lexical frequency. Phase
17 asks the same of **every** discovery: how much of Monad's structure is genuine,
and how much is merely a consequence of the Quran's lexical frequency distribution?
Frequency is the strongest known confounder. No discovery is protected; any may
fail or survive — both are reported. No theology, tafsir, translation, meaning, or
apologetics. Deterministic, byte-identically reproducible (`validate_frequency_null.py
--rebuild`, **126 checks pass**).

> **Immutability note:** two Phase-17 report names collide with prior phases
> (`motif-survival-report.md` = Phase 9, `survivor-analysis-report.md` = Phase 11).
> The Phase-17 versions are named `motif-frequency-survival-report.md` and
> `frequency-survivor-analysis-report.md` to keep the prior reports immutable.

---

## 1. The null model (Phase A)

Two **frequency-preserving configuration nulls** were generated:

| Null | Preserves | Destroys |
|---|---|---|
| **Concept-level** (1,000 realizations) | each concept's marginal, each ayah's size | co-occurrence, verse, proposition, motif, dependency structure |
| **Root-level** (200 realizations) | each member-root's occurrence, ayah root-count | root co-occurrence (for concept clustering) |

Every discovery is recomputed on the nulls; observed values are compared via
**z-score**, **ratio**, and **structure fraction** = max(0, (observed −
null_mean)/observed). A discovery that disappears under the null was frequency; one
that exceeds it contains information beyond frequency.

---

## 2. Headline result

> **Monad is roughly one-third genuine structure, two-thirds frequency.**

| Aggregate | Value |
|---|---|
| Mean structure contribution | **~35%** |
| Mean frequency contribution | **~65%** |

But the split is **highly uneven** across discoveries — some are almost pure
structure, others almost pure frequency.

---

## 3. The structure–frequency decomposition

| Discovery | Structure % | Frequency % | Category |
|---|---:|---:|---|
| **Proposition edges** | **74.7** | 25.3 | MOSTLY STRUCTURE |
| **Strongly-connected core (SCC)** | **72.2** | 27.8 | MOSTLY STRUCTURE |
| **Strong associations (NPMI≥0.2)** | **68.7** | 31.3 | MOSTLY STRUCTURE |
| Concept clustering | 38.1 | 61.9 | MOSTLY FREQUENCY* |
| Motif distribution | 32.3 | 67.7 | MOSTLY FREQUENCY |
| Grammar transitivity | 31.3 | 68.7 | MOSTLY FREQUENCY |
| Identity anchors | 31.1 | 68.9 | MOSTLY FREQUENCY |
| Consistency | 0.0 | 100.0 | FREQUENCY ONLY |
| Grammar reciprocity | 0.0 | 100.0 | FREQUENCY ONLY |
| Hub dominance | 0.0 | 100.0 | FREQUENCY ONLY |

\* *Concept clustering's magnitude is moderate (38% of cohesion above null) but it
is hugely **significant** (z = 29.8) — it genuinely exceeds frequency; see
`concept-survival-report.md`.*

---

## 4. What survives and what disappears

**Survives frequency control (genuine structure):**
- The **proposition / co-occurrence network** — edges run **3.9×** above the
  frequency null, strong associations **3.2×**. The relational structure is real.
- The **giant SCC** — **3.6×** above null. The strongly-connected core is genuine,
  not a hub-frequency artifact.
- **Concept clustering** — member roots co-occur far more than chance (z = 29.8).

**Disappears under frequency control (was never independent structure):**
- **Hub dominance** — frequency by construction (Phase 16).
- **Consistency** — the null is *equally* consistent (0 contradictions in all
  1,000 nulls); confirms Phase 15's deflation.
- **Grammar reciprocity** — does not exceed the null.

**Mixed / mostly frequency:** identity anchors (69% are the most-frequent member
root), motif distribution (3/13 classes survive significantly), grammar
transitivity.

---

## 5. Success-criteria answers

| Question | Answer |
|---|---|
| How much of Monad is frequency? | **~65%** |
| How much is structure? | **~35%** |
| Which discoveries disappear? | hub dominance, consistency, grammar reciprocity (FREQUENCY ONLY) |
| Which survive? | proposition network, SCC, strong associations, concept clustering |
| Strongest surviving discovery | **proposition edges** (74.7% structure, 3.9× null) |

---

## 6. Outputs & reports

`generated/frequency_null/`: `null_corpora.json`, `concept_survival.json`,
`proposition_survival.json`, `motif_survival.json`, `consistency_survival.json`,
`identity_survival.json`, `scc_survival.json`, `grammar_survival.json`,
`information_decomposition.json`, `survivor_analysis.json`,
`frequency_falsification.json`, `robustness.json`, `frequency_null_manifest.json`.
Tooling: `scripts/build_frequency_null.py`, `scripts/validate_frequency_null.py`.

---

## 7. Reproduce

```bash
python3 scripts/build_frequency_null.py
python3 scripts/validate_frequency_null.py --rebuild
```
