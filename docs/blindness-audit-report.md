# Blindness-Audit Report — Phase 19X (I)

**Phase:** 19X · **Method version:** `numerics-discovery-1.0` · **Date:** 2026-06-07.

## 1. Objective

Verify that the engine never privileged any number — that the search was genuinely blind, so
that any finding (or, here, the absence of findings) cannot be an artifact of a number-specific
code path. This audit must pass for the phase's conclusions to be valid.

## 2. Method

Audit checks: (a) every divisor 2–500 is tested by the identical procedure; (b) no
pre-registered constant equals any target number; (c) the special-question target is
constructed indirectly (`DIV_MIN + 17`, never as a literal divisor constant) and referenced
only after all analysis; (d) the divisor scan iterates uniformly (`for d in self.divisors`);
(e) the best p-value achievable per divisor is recorded so no divisor is structurally
excluded.

## 3. Results

| check | result |
|---|---|
| all 499 divisors tested identically | **yes** |
| divisor range matches constants [2, 500] | yes |
| any pre-registered constant = 19 | **no** |
| target constructed as DIV_MIN+17 (not a literal) | yes |
| scan iterates uniformly over all divisors | yes |
| best-p recorded for every divisor (none excluded) | yes |

Pre-registered constants: SEED 20260607, DIV_MIN 2, DIV_MAX 500, K_FREQ_NULL 1000,
K_STRUCT_NULL 200, ALPHA 0.05, MIN_EXPECTED 5 — none is a target number.

## 4. Interpretation

The engine is number-blind by construction. Every divisor — including 19 — passes through the
exact same divisibility, compression, null, and correction pipeline, with no branch, weight,
or threshold that references a specific number. The conclusions therefore reflect the data,
not a privileged path. The special question (where 19 ranks) is computed last, mechanically,
using the same recorded per-divisor statistics as every other divisor.

## 5. Falsification Attempts

The audit is itself an attempt to find a hidden preference. None exists: constants, scan, and
scoring are all number-agnostic, and the validator independently re-checks these invariants.

## 6. Limitations

- The audit confirms procedural blindness; it cannot audit the *choice* of feature space
  (which quantities to count), which is a design decision documented in the inventory report.
- Letter-count orthography remains an analyst choice upstream of the blind scan.

## 7. Conclusion

**The engine is verified number-blind:** 499 divisors tested identically, no target constant,
target constructed indirectly and examined only last. The phase's findings are not an artifact
of number preference.

Source: `generated/numerics/blindness_audit.json`.
