# Phase 17 — Final Report: Frequency Null Model Engine

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase17-frequency-null-1.0`.

Phase 16 showed the hub is largely lexical frequency. Phase 17 asks it of every
discovery: how much of Monad's structure survives after controlling for lexical
frequency? Frequency is the strongest known confounder. No discovery is protected;
any may fail or survive — both are reported. No theology, tafsir, translation,
meaning, or apologetics. All prior phases are read and hashed but never rebuilt.
Deterministic, byte-identically reproducible (`validate_frequency_null.py
--rebuild`, **126 checks pass**).

> **Immutability note:** two Phase-17 report names collide with prior phases
> (Phase 9 `motif-survival-report.md`, Phase 11 `survivor-analysis-report.md`). The
> Phase-17 versions are `motif-frequency-survival-report.md` and
> `frequency-survivor-analysis-report.md`; the prior reports are untouched.

---

## 1. Method

Two frequency-preserving configuration nulls — concept-level (1,000 realizations,
preserve concept marginals + ayah sizes) and root-level (200 realizations, preserve
root frequencies) — destroy co-occurrence/verse/proposition/motif/dependency
structure while preserving frequencies. Every discovery is recomputed on the nulls
and compared by z-score, ratio, and structure fraction = max(0, (observed −
null_mean)/observed).

---

## 2. Primary research question

> *How much of Monad's discovered structure survives after controlling for lexical
> frequency?*

**Answer: about one-third.** Monad is **~35% genuine structure, ~65% frequency**.
The survival is highly uneven: the proposition/co-occurrence network and the
strongly-connected core are genuine structure (3–4× the null), while the hub,
consistency, and grammar reciprocity carry **zero** information beyond frequency.

---

## 3. Frequency contribution table

| Discovery | Frequency % |
|---|---:|
| Consistency | 100.0 |
| Grammar reciprocity | 100.0 |
| Hub dominance | 100.0 |
| Identity anchors | 68.9 |
| Grammar transitivity | 68.7 |
| Motif distribution | 67.7 |
| Concept clustering | 61.9 |
| Strong associations | 31.3 |
| Strongly-connected core | 27.8 |
| Proposition edges | 25.3 |

## 4. Structure contribution table

| Discovery | Structure % | Survives? |
|---|---:|:--:|
| **Proposition edges** | **74.7** | ✓ (3.9× null) |
| **Strongly-connected core** | **72.2** | ✓ (3.6× null) |
| **Strong associations** | **68.7** | ✓ (3.2×, z=+19.7) |
| Concept clustering | 38.1 | ✓ significant (z=+29.8), moderate magnitude |
| Motif distribution | 32.3 | partly (3/13 classes) |
| Grammar transitivity | 31.3 | partly |
| Identity anchors | 31.1 | mostly frequency |
| Consistency | 0.0 | ✗ |
| Grammar reciprocity | 0.0 | ✗ |
| Hub dominance | 0.0 | ✗ |

---

## 5. Survival rankings

1. **Proposition edges** — 74.7% structure (strongest surviving discovery)
2. Strongly-connected core — 72.2%
3. Strong associations — 68.7%
4. Concept clustering — 38.1% (but z = 29.8)
5. Motif distribution — 32.3%
… down to consistency, grammar reciprocity, hub dominance at 0%.

## 6. Hypothesis survival table

| # | Hypothesis | Result |
|---|---|---|
| H1 | concept structure exceeds frequency | **SURVIVES** |
| H2 | proposition structure exceeds frequency | **SURVIVES** |
| H3 | motif vocabulary exceeds frequency | **SURVIVES** |
| H4 | consistency exceeds frequency | FALSIFIED |
| H5 | identity exceeds frequency | FALSIFIED (mostly) |
| H6 | grammar exceeds frequency | MIXED |
| H7 | irreducible structure remains | **SURVIVES** |

**Surviving: H1, H2, H3, H7.**

## 7. Robustness

The structure-over-null ratios are stable under ayah bootstrap (50 runs; edges
~3.9×). The survival findings are robust to resampling and to a second null
generator.

---

## 8. The honest conclusion

After the deepest available control — frequency-preserving randomization — **Monad
is part frequency, part structure**. Two-thirds of its discovered structure is a
consequence of the Quran's lexical frequency distribution: the hub, consistency,
identity anchors, and the generative grammar are largely or wholly frequency
artifacts. But **one-third is genuine structure** that no frequency null reproduces:
the **proposition/co-occurrence network** and the **strongly-connected core** are
3–4× above frequency expectation, and **concept clustering** is highly significant
(z = 29.8). Monad's genuine contribution is the discovery of a *specific relational
web* among Quranic concepts — particular concepts associating with particular others
far beyond what their frequencies predict. The deflationary findings of Phases 15–16
(consistency, hub) are confirmed and extended; but the relational structure itself
is real. No meaning or origin is claimed — only the structural fact that the
co-occurrence network carries information beyond word frequency.

---

## 9. Synthesis across phases

| Phase | Question | Verdict |
|---|---|---|
| 15 | What maintains consistency? | nothing — irreducible/generic |
| 16 | Why does the hub dominate? | lexical frequency |
| **17** | **How much of Monad is structure vs frequency?** | **~35% structure, ~65% frequency; the proposition network & SCC are genuine (3–4× null), the hub/consistency/grammar are frequency** |

---

## 10. Outputs

`generated/frequency_null/`: `null_corpora.json`, `concept_survival.json`,
`proposition_survival.json`, `motif_survival.json`, `consistency_survival.json`,
`identity_survival.json`, `scc_survival.json`, `grammar_survival.json`,
`information_decomposition.json`, `survivor_analysis.json`,
`frequency_falsification.json`, `robustness.json`, `frequency_null_manifest.json`.
Tooling: `scripts/build_frequency_null.py`, `scripts/validate_frequency_null.py`.
Reports: `frequency-null-model-report.md`, `concept-survival-report.md`,
`proposition-survival-report.md`, `motif-frequency-survival-report.md`,
`consistency-survival-report.md`, `identity-survival-report.md`,
`scc-survival-report.md`, `grammar-survival-report.md`,
`information-decomposition-report.md`, `frequency-survivor-analysis-report.md`,
this report.

---

## 11. Limitations

- **Structure% vs significance** can diverge (concept clustering: 38% magnitude but
  z = 29.8). Both are reported; neither alone is the whole story.
- **The null is a configuration model** (preserve marginals + sizes). Other nulls
  (preserving the dyad census, or a generative null) might shift the magnitudes;
  the qualitative ranking (proposition/SCC genuine; hub/consistency frequency) is
  robust to the tested nulls.
- **Concept survival** uses a cohesion proxy, not a full re-clustering of 1,000
  null corpora (computationally infeasible); the z = 29.8 result is strong evidence
  but not a full pipeline rerun.
- The structure fraction depends on the (observed − null)/observed definition; a
  different effect-size measure would rescale the percentages.

## 12. Open questions (for any future phase — not started)

1. A full Phase-2→3 re-clustering on null corpora to confirm concept survival end
   to end.
2. A dyad-census-preserving null for the motif distribution.
3. Whether the structural residue (the 3–4× proposition excess) has its own
   internal organisation worth characterising.

---

## 13. Prohibitions observed

`no theology · no tafsir · no translation · no meaning · no apologetics · no
protection of previous discoveries · no preserving desirable results · any
discovery may fail · any discovery may survive · both reported · prior phases never
rebuilt.`

---

## 14. Reproduce

```bash
python3 scripts/build_frequency_null.py
python3 scripts/validate_frequency_null.py --rebuild
```

**Phase 17 complete. No Phase 18 started.**
