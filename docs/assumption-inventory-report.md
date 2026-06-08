# Assumption-Inventory Report — Phase Ξ (B)

**Phase:** Ξ · **Method version:** `foundation-audit-1.0` · **Date:** 2026-06-08.

## 1. Objective
Make every foundational assumption explicit — no assumption may remain implicit.

## 2. Method
Enumerate the assumptions the Phase-2–4 chain rests on, each with the phases it underwrites and a concrete
removal test.

## 3. Results
- **A1** — roots are the meaningful unit (test: rebuild at lemma/word).
- **A2** — semantic similarity (PPMI co-occurrence) captures structure (test: vs frequency/null).
- **A3** — clustering boundaries (concepts) are meaningful, not arbitrary (test: Phase-11 cross-method ARI).
- **A4** — proposition edges reflect real relations (test: Phase-17 frequency null).
- **A5** — the graph representation is the appropriate model (test: Phase-P held-out prediction).

## 4. Interpretation
These five assumptions generate essentially the whole project. Each already has a measured verdict from a
prior phase: A3 is method-relative (Phase 11, ARI 0.22); A4 is 65% frequency (Phase 17); A5 fails held-out
prediction (Phase P). So the audit does not need to speculate — the assumptions have been tested.

## 5. Falsification Attempts
Each assumption is given a concrete removal experiment (`assumption-removal-report.md`).

## 6. Limitations
Five assumptions are the load-bearing set; finer modelling assumptions exist but reduce to these.

## 7. Conclusion
Five explicit assumptions (A1–A5) underwrite the project; each has a measured removal test, and A3/A4/A5
already have adverse verdicts from prior phases.

Source: `generated/foundation_audit/assumption_inventory.json`.
