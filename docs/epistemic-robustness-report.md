# Epistemic-Robustness Report — Phase X (I)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`epistemology-discovery-1.0`.

Phase I tests whether the knowledge pipeline is an artefact of one part of the corpus. It
recomputes every knowledge-graph edge **separately on the Meccan and Medinan halves** and
asks: does the forward direction hold in *both*?

---

## 1. Cross-corpus stability

| | Value |
|---|--:|
| Knowledge-graph edges | 74 |
| **Stable** (forward in BOTH Meccan and Medinan) | **57** |
| Stable fraction | **0.77** |

---

## 2. Finding

> **77% of the epistemic pipeline holds in both the Meccan and the Medinan corpus.** The
> direction of knowing — acts → reflection → understanding → knowledge → certainty — is
> **not** a feature of one revelation period; it reproduces across the corpus's two
> independently-datable halves. An epistemology that appeared only in Meccan or only in
> Medinan surahs would be suspect; this one is stable across both.
>
> The 23% that drift are the weaker, lower-support edges — the same near-0.50 links the
> falsification phase already flagged. The **robust core is the directional backbone**;
> the unstable margin is the order-less co-occurrence.

---

## 3. Convergence of the two attacks

Phases H and I attack the graph from different angles and converge on the same survivors:

| Edge type | Reverse attack (H) | Corpus split (I) |
|---|---|---|
| deliberate acts → understanding | survive | stable |
| knowledge → certainty | survive (0.80) | stable |
| ignorance cascade | survive | stable |
| **observation → knowledge/blindness** | **refuted** (≈0.5) | **drifts** |

The same edges that fail the reverse test also fail the corpus-split test. This
double-failure of the observation edges is itself a robust finding: **raw perception is
genuinely non-directional in the Quran's epistemology**, by two independent measures.

---

## 4. Verdict

> **The epistemic pipeline is robust** — 77% of its edges keep direction across both
> revelation halves, and the robust edges are exactly the ones that survived
> reverse-sequence falsification. The discovered epistemology is a stable property of the
> whole Quran, not of one period or one rhetorical mode.

---

## 5. Reproduce

```bash
python3 scripts/build_epistemology.py
python3 scripts/validate_epistemology.py --rebuild
```

Source: `generated/epistemology/robustness_results.json`.
