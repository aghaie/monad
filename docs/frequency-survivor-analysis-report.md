# Survivor Analysis Report — Phase 17 (J, K, L)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase17-frequency-null-1.0`.

*(Named `frequency-survivor-analysis-report.md` to preserve the Phase-11
`survivor-analysis-report.md`; the Phase-17 spec's generic name collides with it.)*

Phase J classifies every discovery by structure fraction; Phase K falsifies the
seven exceeds-frequency hypotheses; Phase L tests robustness.

---

## 1. Survivor classification (Phase J)

| Discovery | Structure % | Category |
|---|---:|---|
| Proposition edges | 74.7 | **MOSTLY STRUCTURE** |
| Strongly-connected core | 72.2 | **MOSTLY STRUCTURE** |
| Strong associations | 68.7 | **MOSTLY STRUCTURE** |
| Concept clustering | 38.1 | MOSTLY FREQUENCY* |
| Motif distribution | 32.3 | MOSTLY FREQUENCY |
| Grammar transitivity | 31.3 | MOSTLY FREQUENCY |
| Identity anchors | 31.1 | MOSTLY FREQUENCY |
| Consistency | 0.0 | **FREQUENCY ONLY** |
| Grammar reciprocity | 0.0 | **FREQUENCY ONLY** |
| Hub dominance | 0.0 | **FREQUENCY ONLY** |

**Tally:** 3 MOSTLY STRUCTURE · 4 MOSTLY FREQUENCY · 3 FREQUENCY ONLY · 0 STRUCTURE
ONLY · 0 MIXED. \* *Concept clustering is by-magnitude "mostly frequency" but
significantly exceeds the null (z = 29.8).*

**Strongest surviving discovery: proposition edges** (74.7% structure, 3.9× null).

---

## 2. Hypothesis survival table (Phase K)

| # | Hypothesis | Result | Evidence |
|---|---|---|---|
| H1 | concept structure exceeds frequency | **SURVIVES** | member-root cohesion z = +29.8, 1.6× null |
| H2 | proposition structure exceeds frequency | **SURVIVES** | strong associations z = +19.7, 3.2×; edges 3.9× |
| H3 | motif vocabulary exceeds frequency | **SURVIVES** | 3/13 triad classes deviate significantly (|z|≥2) |
| H4 | consistency exceeds frequency | **FALSIFIED** | the null is equally consistent (0 contradictions in 1,000 nulls) |
| H5 | identity exceeds frequency | **FALSIFIED (mostly)** | 69% of anchors are the most-frequent member root |
| H6 | grammar exceeds frequency | **MIXED** | attachment/reciprocity are frequency; transitivity ~31% structure |
| H7 | irreducible structure remains after frequency control | **SURVIVES** | proposition network, SCC, concept clustering all exceed the null (3–4×) |

**Surviving: H1, H2, H3, H7.** Falsified or mixed: H4, H5, H6.

---

## 3. Robustness (Phase L)

The structure-over-null ratios were re-measured under ayah bootstrap (50 runs)
against the concept-frequency null. The edges-over-null ratio is stable (~3.9×). The
survival findings — which discoveries exceed frequency and by how much — are robust
to resampling. A second null generator (the bootstrap itself) confirms the
proposition/SCC structure consistently exceeds the frequency baseline.

---

## 4. The strongest surviving discovery

> **The proposition / co-occurrence network is Monad's strongest genuine
> structure** — 74.7% structure, 3.9× the frequency null. After frequency is removed,
> what remains is the *specific relational web*: particular concepts associate with
> particular others far beyond what their frequencies predict. This, together with
> the strongly-connected core (72.2%) and strong associations (68.7%), is the part
> of Monad that is genuinely about Quranic *structure* rather than Quranic *word
> frequency*.

---

## 5. What disappears

Hub dominance, consistency, and grammar reciprocity are **FREQUENCY ONLY** — they
carry zero information beyond frequency and are exactly reproduced by the null.
Identity anchors and the grammar are mostly frequency. These were never independent
structural findings; they are consequences of the Quran's lexical frequency
distribution.

---

## 6. Verdict

> **Monad is ~35% structure, ~65% frequency.** Four hypotheses survive (concept,
> proposition, motif, irreducible structure); three fail or are mixed (consistency,
> identity, grammar). The strongest surviving discovery is the proposition
> network. The hub, consistency, and grammar reciprocity are frequency artifacts.

---

## 7. Reproduce

```bash
python3 scripts/build_frequency_null.py
python3 scripts/validate_frequency_null.py --rebuild
```

Source: `generated/frequency_null/survivor_analysis.json`,
`frequency_falsification.json`, `robustness.json`.
