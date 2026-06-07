# Holdout-Design Report — Phase P (B)

**Phase:** P · **Method version:** `predictivity-discovery-1.0` · **Date:** 2026-06-07.

## 1. Objective

Specify and verify the **leakage-free** holdout used to test generalization, and the
multiple regimes that cross-check the result. Leakage-freedom is the supreme invariant: if
a test ayah influences the statistics used to predict it, any positive result is an
artifact. Multiple regimes guard against a result that holds only under one split.

## 2. Method

**Whole-ayah holdout.** Test ayahs are entirely excluded from all statistic-building.
Per fold, B0/B1/S1/S2 statistics (df, co-occurrence, PPMI, degree) are rebuilt from
**training ayahs only**. The masked unit's own test-ayah occurrence never enters any
count. The context is observed from the test ayah; every context→unit association is
learned from training. OOV masked units (absent from a fold's training vocabulary) are
excluded **symmetrically** for all predictors and counted as coverage.

**Regimes.**
- **R1 — random k-fold:** k = 5 (primary) and k = 10 (robustness), seed 20260607.
- **R2 — contiguous blocks:** 5 folds of contiguous `ayah_sequential` ranges (whole
  surahs/regions held out) — probes local-context leakage; cross-checks Phase-14
  homogeneity.
- **R3 — forward/temporal:** train on the first {25, 50, 75}% by mushaf order, predict the
  rest — directional generalization; cross-checks Phase-13 scale-invariance.
- **R4 — length-stratified:** 5 folds balanced on distinct-root count — removes the
  Phase-14 length→density confound.

**Mask fractions.** single (leave-one-unit-out), 25%, 50%. Ayahs with < 2 units (no
context) are excluded.

## 3. Results

Validator-verified leakage controls (all pass):
- For R1 (k=5), R2, and R4: every fold has **train ∩ test = ∅** and **train ∪ test = all
  6,214 ayahs**; the k test sets **partition** the corpus.
- Coverage per cell ≥ 0.95 (root level); OOV masked units excluded symmetrically and
  counted (e.g. 523/44,266 at root single-mask R1).

Instance counts (root, single-mask): R1-5 43,743 · R1-10 43,812 · R2 43,577 · R3-fwd25
26,831 · R3-fwd50 16,696 · R3-fwd75 5,894 · R4 43,746.

## 4. Interpretation

The four regimes triangulate the result. R1 gives the primary estimate; R2 tests whether
prediction depends on contiguous-context leakage; R3 tests forward generalization (the
hardest, most realistic direction); R4 removes length effects. Agreement across regimes
means a result is a property of the corpus, not of one split.

## 5. Falsification Attempts

The leakage-freedom claim is attacked directly by the validator's partition probes
(train/test disjoint and exhaustive, per fold, per regime) — all pass. R2 and R3
additionally attack the *possibility* of hidden local leakage by holding out contiguous
and forward blocks; if prediction depended on adjacency leakage, R2/R3 would diverge
sharply from R1 (they do not — see `root-predictivity-report.md`).

## 6. Limitations

- Forward regimes (R3) train on smaller/earlier vocabularies, raising OOV (coverage 0.95
  at fwd25) — reported, not hidden.
- The "orderings" are accumulation orders (mushaf), not external chronology (same caveat
  as Phase 13).
- Concept-level folds reuse the same partitions but with frozen memberships (definitional
  caveat carried in the concept report).

## 7. Conclusion

A leakage-free whole-ayah holdout with four independent regimes and three mask fractions is
constructed and validator-verified. The predictive comparison runs on this scaffold.

Source: `generated/predictivity/holdout_folds.json`.
