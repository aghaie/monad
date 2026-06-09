# Phase ΩΣ — Stability Report

**Method:** `foundational-questions-1.0` · corpus-only · deterministic.

## 1. Objective
Confirm that surviving findings are robust to resampling, not artifacts of the full corpus.

## 2. Method
Census ratios (Q3, Q7, Q8, Q11) are exact and need no CI. The one inferential statistic that can be
localized — the Q12 mirror-pair Jaccard — is recomputed under 80% ayah subsampling (40 replicates) and a 95%
interval reported.

## 3. Results
- Q12 mirror-pair Jaccard, 95% subsample interval: **[0.0365, 0.0412]**.
- The interval sits at/below the order-null band (null mean 0.0392, p95 0.0412) across subsamples — the
  *absence* of ring geometry is stable.
- Census ratios are invariant by construction (exact counts).

## 4. Interpretation
Both kinds of surviving conclusions are stable: the census facts trivially, and the negative geometry result
robustly (the subsample interval never clears the null). No conclusion depends on the full-corpus accident.

## 5. Falsification Attempts
Subsampling is itself a stability attack; the geometry null result withstands it.

## 6. Limitations
Only the localizable inferential statistic is subsampled; the global census ratios are exact and not
resampled.

## 7. Conclusion
**Stable.** The geometry-absence is robust under subsampling; the census ratios are exact. No surviving
finding is a sampling artifact.
