# Decision-Triggers Report — Phase Δ (B)

**Phase:** Δ · **Method version:** `decision-architecture-1.0` · **Date:** 2026-06-08.

## 1. Objective
For each decision event, identify the preceding structures: what most frequently triggers decisions?
Classes emerge from data only.

## 2. Method
Directed flow into the condition and action nodes (within-ayah order + cross-ayah adjacency); rank
sources by support.

## 3. Results
- Into **condition**: conflict → condition (dir 0.53, support 159).
- Into **action**: choice → action (411), condition → action (dir 0.61, 384), consequence → action (117),
  conflict → action (80).

## 4. Interpretation
On the raw graph, decisions (actions) are most triggered by **choice** and **conditional** structure —
"if/when … [then] act". This is the descriptively expected decision trigger. But these raw flows are
dominated by frequency; only `condition→choice`/`condition→action`-type edges survive the controls (see
falsification). The robust trigger is the **conditional structure preceding choice/action**.

## 5. Falsification Attempts
Most trigger edges are frequency artifacts (see `decision-falsification-report.md`); the conditional
trigger (condition→choice) is among the few survivors.

## 6. Limitations
Triggers are measured as directed precedence; semantic content of triggers is not inferred (forbidden).

## 7. Conclusion
**Decisions are triggered by conditional structure** ("if … then choose/act") — the one trigger pattern
that survives controls; other triggers are frequency-driven.

Source: `generated/decision_architecture/decision_triggers.json`.
