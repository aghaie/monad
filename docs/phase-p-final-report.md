# Phase P — Final Report: Structural Predictivity / Held-Out Information Engine

**Method version:** `predictivity-discovery-1.0` · **Date:** 2026-06-07 ·
**Verdict:** `NON_PREDICTIVE`. Deterministic, leakage-free, frequency-controlled,
pre-registered. Validator: byte-identical rebuild + leakage/fairness probes.

## 1. Objective

The first **generalization** test in Monad. Every prior phase described the full corpus.
Phase P asks the question that separates a genuine discovery from an elaborate
redescription: **does the structure Monad discovered carry predictive information about
held-out Quranic content that lexical frequency alone does not?** The answer was allowed to
be no; the design optimizes for truth, not for a positive result.

## 2. Method (summary)

Masked-unit completion under leakage-free whole-ayah holdout. A context-blind frequency
baseline (B0) is the bar; a context-aware co-occurrence model (S1) must beat it and a
frequency-preserving configuration null (N). Roots (stable, primary) and concepts (frozen
memberships, secondary). Four holdout regimes (random, contiguous, forward, length-strat),
three mask fractions, K = 30 null realizations, all in all regimes. Metrics: MRR, Hits@k,
perplexity, info-gain (bits). Fairness lock: S1 = B0 under uninformative context;
identical min-rank tie convention; λ = 1 fixed (no tuning). All §9 criteria pre-registered
and encoded before running. Full method in the eight companion reports.

## 3. Results (headline)

Primary cell (root / R1 5-fold / single, n = 43,743):

| | MRR | Hits@10 | perplexity | info-gain |
|---|--:|--:|--:|--:|
| **B0 frequency** | **0.099** | **0.199** | **354** | — |
| S1 structure | 0.087 | 0.182 | 3,522 | **−3.316 bits** [−3.391, −3.242] |
| N null structure | 0.018 | — | 4,300 | −3.617 |

Structure < frequency in **0/7 regimes**; S2 (order) worse still; degree ≈ frequency.
Concept level (secondary, confounded): S1 beats B0 on ranking (MRR 0.316→0.370) but ≈ 0 /
negative on calibrated bits and confounded by membership circularity.

---

## Question 1 — Does the discovered structure predict held-out Quranic content beyond lexical frequency?

**Answer: NO.**

At the rigorous root level, the structure model loses to the frequency baseline on every
pre-registered metric, in every regime: MRR 0.087 < 0.099, Hits@10 0.182 < 0.199,
info-gain **−3.316 bits** (CI excludes 0 negative), 0 of 7 regimes pass. The concept-level
*ranking* gain is real but **confounded** by membership circularity (concepts are
co-occurrence clusters, so predicting a concept from co-occurring concepts partly re-reads
their definition) and rests on an **untested** clustering stability (Phase-11 ARI 0.22), so
it cannot reverse the answer. **Beyond frequency, the structure does not predict.**

## Question 2 — Does the structure beat the frequency-preserving null?

**Answer: YES.**

In every regime the real structure beats the configuration null (root MRR ≈ 0.087 vs null
≈ 0.018; Δ ≈ +0.07; info-gain −3.32 vs null −3.62). The discovered co-occurrence is **real**
— not reproducible by a marginal-preserving scramble. This corroborates Phase 17's
finding that a genuine relational network survives a frequency null (D1).

## Question 3 — Is the surviving structure genuinely predictive, or merely frequency-shaped?

**Using only the pre-registered criteria:** the structure is **real but not predictive.**
It sits *between* frequency and the null — above the null (it is genuine co-occurrence),
below the frequency baseline (it adds no usable predictive information). It is **not**
"frequency-shaped" in the pre-registered sense (that category requires *beating* frequency
with a null-reproducible edge; the structure never beats frequency). It is simply
**non-predictive**: real structure, no out-of-sample predictive advantage. C2 passes (real);
C1, C3, C4, C5 fail (not useful).

## Question 4 — Final verdict

# `NON_PREDICTIVE`

(Pre-registered map: ¬C1 ⇒ NON_PREDICTIVE. C1 beats-frequency = false; only C2
beats-null = true.)

## Question 5 — What should Monad do next?

**The result is negative. Per the pre-registered negative-outcome policy, Monad should
STOP launching further semantic/content phases that assume the conceptual structure carries
generalizable meaning.** Concretely:

1. **Do not build new content/semantic phases on the concept graph.** The relational
   structure (D1) is real but carries **no held-out predictive advantage over frequency**.
   Phases Q, R, X (method, sunan, epistemology) and any successor are, on this evidence,
   **frequency-mediated descriptions** of the corpus, not windows onto generalizable
   structure. They should be read with that ceiling acknowledged.
2. **The honest terminus the deflation arc pointed to (15→16→17→P) has been reached.** Most
   structure was already shown to be frequency; Phase P shows the *surviving* structure,
   though real, does not predict. There is no positive predictive discovery to strengthen.
3. **The only scientifically-warranted continuations are not "more content," but harder
   tests of the *representation itself*:** a syntactic/word-order-preserving null (would
   the structure's edge over the configuration null survive a stronger baseline?), or a
   genuinely different representation (phonological, higher-order) subjected to this same
   predictive bar. Absent such a result, the project has reached its evidential limit.

This recommendation follows the rule set before the run: a null result is reported as
prominently as a positive one and is **not** re-litigated with a weaker baseline.

## 4. Interpretation

Phase P closes the loop the project opened. Phases 16–17 showed most of Monad reduces to
lexical frequency; Phase 17 isolated a relational network that survives a frequency null
(D1) as the one robust positive. Phase P put that survivor to the decisive test —
**out-of-sample prediction** — and it failed: real co-occurrence is not the same as usable
predictive information. The structure is genuine (beats the null) but inert (loses to
frequency). One small honest qualifier: at the root level S1 slightly improves *mean
rank-percentile* (it helps mid-pack candidates) and at the concept level it improves
*ranking* — so the structure is not information-free; it is just not useful beyond
frequency on any decisive, un-confounded metric.

## 5. Falsification Attempts

The positive hypothesis was attacked from five pre-registered directions and survived only
the one (beats-null) that establishes the structure is real, not the four that would
establish it is useful. The negative result was attacked by robustness (0/7 regimes), by
the bootstrap (CI excludes 0), and by the order model (S2 worse) — it held. No baseline was
weakened and no threshold was moved after seeing results.

## 6. Limitations

- **Calibration:** λ = 1 makes the perplexity magnitude (−3.3 bits) overconfident; the
  *direction* is corroborated by the λ-invariant ranking metrics, so the verdict does not
  depend on calibration. A tuned model would narrow the bits gap but cannot make ranking
  positive.
- **Concept circularity & untested stability:** the concept-level ranking gain is
  confounded; variant 2b (per-fold re-clustering) was not implemented; the 0.9999 stability
  cosine is near-tautological and does not vindicate concept stability.
- **Null strength:** the configuration null preserves marginals but not syntax; a stronger
  (syntactic) null was out of scope and would only further reduce the structure's edge.
- **Representation scope:** Phase P tests one structure representation (pairwise
  co-occurrence / PPMI, plus directional). A negative here does not prove *no* Quran-internal
  representation could predict — only that this one, the project's surviving discovery, does
  not.

## 7. Conclusion

**`NON_PREDICTIVE`.** The structure Monad discovered is **real but not predictive**: it
beats a frequency-preserving null (genuine co-occurrence) yet loses to the frequency
baseline on every pre-registered metric, in all seven regimes. It carries no held-out
predictive information beyond lexical frequency. Monad has reached its evidential limit;
no further semantic/content phase is warranted without first finding — under this same
predictive bar — a representation that actually predicts.

---

### Outputs
`generated/predictivity/`: 9 data products + `predictivity_manifest.json` (deterministic,
byte-identical) + `run_metadata.json` (volatile provenance). Tooling:
`scripts/build_predictivity.py`, `scripts/validate_predictivity.py`. Reports: the eight
companion reports + this one + `executive-summary.md`.

### Reproduce
```bash
python3 scripts/build_predictivity.py
python3 scripts/validate_predictivity.py --rebuild
```

**Phase P complete. No further phase started automatically.**
