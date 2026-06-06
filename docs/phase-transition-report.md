# Phase Transition Report — Phase 13 (H, F, I, J)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase13-evolution-1.0`.

Phase H searches for structural phase transitions; Phase F tracks identity
emergence; Phase I tests robustness across orderings; Phase J falsifies the
temporal findings. No leakage; statistics only.

---

## 1. Phase H — are there phase transitions?

Consecutive-snapshot deltas were computed for hub share, triad-class count, and
largest SCC. **No abrupt structural phase transition is found.**

| Quantity | Largest single jump | Where |
|---|---|---|
| Hub share | ≈ 0 (monotone slight decline) | — |
| Triad classes | +1 | 1% → 5% |
| Largest SCC | **+11** | 1% → 5% |

The only notable jump is the early SCC growth (+11 between 1% and 5%). Otherwise
the curves are smooth: the **growth pattern is "front-loaded"** — most structure
is present at the first snapshot and the rest fills in gradually with no critical
threshold or reorganization. There is **no hub-acceleration event** (the hub starts
at maximum and dilutes) and **no motif-stabilization event** (the vocabulary is
present from 1%).

---

## 2. Phase F — identity emergence

| Revealed | Recognizable anchor fraction |
|---:|---:|
| 1% | 0.30 |
| 20% | 0.38 |
| 50% | **0.51** |
| 100% | 0.59 |

Identity-anchor recognizability (snapshot dominant root = canonical Phase-6 anchor)
is the **one structure that grows gradually**, crossing 50% recognizable at ~50%
revealed and reaching 0.59 at 100%. (The metric is a dominant-root-by-count proxy;
the residual 41% reflects the proxy vs the weighted Phase-6 anchor, not identity
failure.) Identities become recognizable later than the hub, motifs, or
consistency — they require accumulated activation.

---

## 3. Phase I — robustness across traditions

| Finding | Canonical | Meccan/Medinan | Control | Temporally robust? |
|---|:--:|:--:|:--:|:--:|
| Hub rank-1 from start | ✓ | ✓ | ✓ | **Yes** |
| Consistency holds throughout | ✓ | ✓ | ✓ | **Yes** |
| Motif vocabulary present early | ✓ (5%) | ✓ (5%) | ✓ (1%) | **Yes** |
| High early predictability | ✓ | ✓ | ✓ | **Yes** |

Only findings holding across **both traditions AND the control** are classified
robust. All four headline findings qualify. The two traditions were analysed
separately and never merged.

---

## 4. Phase J — falsification

| Claim | Result | Evidence |
|---|---|---|
| Hub emergence is an artifact of canonical order | **FALSIFIED** | hub is rank-1 from the first snapshot even under the shuffled control — content-driven |
| Consistency is an artifact of a particular order | **FALSIFIED** | 0 exclusion/positive overlap at every snapshot under every order |
| The orderings are a verified historical chronology | **ACKNOWLEDGED LIMITATION** | no nuzul chronology exists in the corpus; canonical and Meccan/Medinan are accumulation orders, not history |

**Documented artifacts (not hidden):** canonical order is mushaf order, not
revelation order; Meccan/Medinan is a coarse 2-period proxy; the snapshot graph is
a leakage-free reconstruction (co-occurrence + positional edges), a faithful subset
of the Phase-4 graph.

---

## 5. The deeper falsification

The most important finding of Phase J is that the **naive "emergence over revelation
time" hypothesis is itself falsified.** Because the structure appears as strongly
under a **random** ordering as under the canonical one, there is no meaningful
temporal emergence to study: the hub, the motif vocabulary, and consistency are
properties of **any sufficiently large sample** of the corpus, present at all
scales. What looks like "emergence" is sampling — the content is structurally
self-similar, not sequentially built. We report this rather than narrate a
non-existent developmental story.

---

## 6. Verdict

> The network grows **front-loaded**, not through phase transitions. Hub,
> consistency, and motif vocabulary are present from the first verses under every
> order (robust, order-independent); only the SCC size and identity recognizability
> grow gradually. No historical claim is made — the orderings are structural, not
> chronological.

---

## 7. Reproduce

```bash
python3 scripts/build_evolution.py
python3 scripts/validate_evolution.py --rebuild
```

Source: `generated/evolution/phase_transitions.json`, `identity_evolution.json`.
