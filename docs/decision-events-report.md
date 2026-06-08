# Decision-Events Report — Phase Δ (A)

**Phase:** Δ — Quranic Decision Architecture Discovery Engine · **Method version:**
`decision-architecture-1.0` · **Date:** 2026-06-08.
The phase asks not "what does the Quran say?" but "how does it decide?" — treating the corpus as a
decision system. No human decision framework is imposed.

## 1. Objective
Locate, corpus-wide, where alternatives/choices/actions/consequences diverge — the decision events —
without predefined categories.

## 2. Method
Decision events are marked by the corpus's own structures: **conditional particles (POS = COND)** plus
a decision-vocabulary of opaque root-groups (choice/will, action, consequence, uncertainty, knowledge,
conflict, resolution, priority, evaluation). Each ayah records which decision-nodes are present and
their word order.

## 3. Results
- **1,049 COND (conditional) tokens** — the dominant structural decision marker.
- Decision-nodes appear in **2,681 ayahs** (≈ 43% of root-bearing ayahs).
- **45 candidate directed edges** among the 10 decision nodes (support ≥ 8).

## 4. Interpretation
The Quran is rich in conditional structure (1,049 COND particles — "if … then") and decision vocabulary,
so an apparent decision architecture is available to measure. Whether it is *real* (beyond frequency) or
a frequency artifact is decided by the falsification battery; this phase only inventories the events.

## 5. Falsification Attempts
None here; every candidate edge is provisional and passed to the null battery (`decision-falsification-report.md`).

## 6. Limitations
"Decision event" is operationalized via COND + a chosen decision vocabulary; a different vocabulary would
shift the node set, though the falsification logic is invariant.

## 7. Conclusion
The corpus supplies abundant decision events (1,049 conditionals; 45 candidate edges across 2,681 ayahs).
Their reality is tested downstream.

Source: `generated/decision_architecture/decision_events.json`.
