# Divisibility Report — Phase 19X (B)

**Phase:** 19X · **Method version:** `numerics-discovery-1.0` · **Date:** 2026-06-07.

## 1. Objective

Scan every divisor 2–500 against every numerical feature for divisibility, remainder
structure, and multiple-density — blind to any target number — producing the raw findings
that the controls then filter.

## 2. Method

For each divisor d ∈ [2,500]:
- **scalar divisibility:** which of the 10 totals are ≡ 0 mod d (a deterministic fact).
- **sequence divisibility-count:** how many elements of each sequence are ≡ 0 mod d (vs the
  1/d expectation).
- **sequence residue-uniformity:** χ² of the residue histogram mod d (where n/d ≥ 5).

## 3. Results

- The divisibility scan produced **5,380 sequence tests** plus 499 scalar-compression
  tests. Under a naïve **uniform-integer** null, ~1,800 sequence tests appeared
  "significant."
- **That naïve significance is an artifact and is NOT carried forward** (see Method/§4 and
  `frequency-null-report.md`): natural Quranic quantities (root and word frequencies, ayah
  lengths) are **Zipfian / clustered, not uniform**, so their residues mod d are non-uniform
  for ordinary distributional reasons, not numerical design.
- The well-posed family — **scalar joint-divisibility** — is reported in
  `compression-report.md`; its strongest raw finding is d = 86 (p = 0.0057, uncorrected).

## 4. Interpretation

The central lesson of the scan is **why most apparent divisibility findings are not real**:
divisibility and residue of a sequence are properties of its **value multiset**, which for
the Quran's frequencies is a natural skewed distribution. Comparing such a multiset to
*uniform random integers* trivially yields tiny p-values that say nothing about design. The
correct null (frequency-preserving) reproduces these residues, so the real data is typical.
Only **scalar totals** — single integers — admit a clean divisibility test (against the 1/d
prior and random integers of matched magnitude), and that family is analysed under full
correction in the significance and frequency-null reports.

## 5. Falsification Attempts

The naïve sequence "findings" were attacked by the frequency-preserving null
(`frequency-null-report.md`) and the structure null (`structure-null-report.md`): both show
the residue structure is reproduced by chance / is invariant to arrangement. They do not
survive and are excluded.

## 6. Limitations

- Residue-uniformity uses the χ² approximation (valid only where n/d ≥ 5); small-count cells
  are excluded.
- The scan is exhaustive over 2–500 but a single integer is divisible by ~7 divisors in that
  range by chance, so raw divisibility counts are expected, not surprising.

## 7. Conclusion

The blind divisibility scan finds abundant *raw* divisibility, but almost all of it is the
expected behaviour of natural integer distributions. Only the scalar-total family is
well-posed; it is carried to the controls. No finding is accepted from this phase alone.

Source: `generated/numerics/divisibility_scan.json`.
