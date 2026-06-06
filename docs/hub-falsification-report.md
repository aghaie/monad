# Hub Falsification Report — Phase 16 (I)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase16-hub-origin-1.0`.

Phase I attacks every explanatory hypothesis for hub dominance. The hub is not
protected; only hypotheses that survive falsification are explanatory.

---

## 1. Hypothesis survival table

| # | Hypothesis | Result | Evidence |
|---|---|---|---|
| **H1** | The hub is frequency-driven | **SURVIVES** | frequency predicts degree (Spearman 0.966); the hub is rank-1 on activation, degree, and lexical frequency |
| **H2** | The hub is motif-driven | **FALSIFIED** | motif participation is a *consequence* of frequency (a frequent concept joins most triads); motifs cannot make a concept frequent |
| **H3** | The hub is grammar-driven | **FALSIFIED** | the Phase-12 topology grammar produces only ~3.4% hub share; topology cannot generate the observed 0.968 |
| **H4** | The hub is SCC-driven | **FALSIFIED** | SCC membership is a consequence of high co-occurrence (itself a consequence of frequency); the SCC does not create frequency |
| **H5** | The hub is activation-driven | **SURVIVES (= H1)** | activation frequency *is* the driver; it tracks lexical frequency at Spearman 0.998; frequency-simulation reproduces the hub (~0.88) |
| **H6** | The hub is an irreducible primitive | **FALSIFIED** (at the structural level) | the hub reduces to lexical frequency — reconstructible, simulatable, inevitable from frequency; irreducible only in that lexical frequencies are the input data |

**Surviving hypotheses: H1 and H5** (which are the same — frequency = activation).

---

## 2. The chain of causation

The evidence assembles into a single causal chain, each link tested:

```
Zipfian root frequencies  (lexical, Phase-1 input data)
        │  (necessary; uniform frequencies → no hub)
        ▼
CONCEPT_007 aggregates the head of the distribution
        │  (Spearman 0.998: activation ← lexical frequency)
        ▼
Highest activation frequency (96.8%)
        │  (Spearman 0.966: degree ← frequency)
        ▼
Highest degree, REQUIRES-in, motif participation, SCC membership
        │
        ▼
"Hub dominance" (one cause, many axes)
```

Every downstream form of dominance (H2 motif, H4 SCC, and the connectivity behind
H3) is a *consequence* of the frequency at the top of this chain — none is an
independent cause, and none can produce the frequency.

---

## 3. Why H6 (irreducible) fails

The hub is irreducible only *relative to graph topology* (Phase 12). At the level of
the activation matrix it is fully reducible: it is the concept aggregating the
corpus's most frequent roots. It is reconstructible (lexical rank-1 = CONCEPT_007),
simulatable (~88% from frequency rules), unique (gap 0.55), necessary (Zipf
required), and inevitable (rank-1 from 1%). The only sense in which it is irreducible
is that the corpus's lexical frequencies are the *input data*, not a discovered
structure — which is not structural irreducibility.

---

## 4. Verdict

> **The hub is FREQUENCY-DRIVEN** (H1/H5 survive). H2 (motif), H3 (grammar), H4
> (SCC), and H6 (irreducible-structural) are **falsified** — all are consequences
> of, or cannot produce, the hub's frequency. The hub's origin is the corpus's
> Zipfian lexical frequency distribution. The "irreducible primitive" framing is
> deflated: the hub is the concept that aggregates the most frequent lexical items.

---

## 5. Reproduce

```bash
python3 scripts/build_hub_origin.py
python3 scripts/validate_hub_origin.py --rebuild
```

Source: `generated/hub_origin/hub_falsification.json`.
