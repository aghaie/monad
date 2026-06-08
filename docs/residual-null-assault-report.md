# Residual-Null-Assault Report — Phase Ψ (I)

**Phase:** Ψ · **Method version:** `residual-nature-1.0` · **Date:** 2026-06-08.

## 1. Objective
Attack every discovered residual component with strong nulls; remove anything that collapses, keep
anything that survives.

## 2. Method
The surah-topical signal is attacked with a **surah-shuffle null** (50 realizations): randomly
reassign each ayah's surah label (preserving ayah content and surah sizes), recompute the topical NLL;
the signal survives iff the real surah grouping beats the shuffle 95th percentile. Long-range and
structural components are assessed via their own profiles (long-range report, Phase P).

## 3. Results
| quantity | bits |
|---|--:|
| real surah-topical gain | −0.419 |
| null (shuffle) mean | −0.793 |
| null 95th percentile | −0.782 |

- **Surah-topical signal survives the null: YES** (−0.419 > −0.782 — real grouping is ~0.36 bits
  better than shuffled).
- Long-range "increasing" structure collapses (does not increase with distance); higher-order adds 0.

## 4. Interpretation
A **real topical signal survives**: ayahs of the same surah share characteristic vocabulary
significantly more than randomly grouped ayahs (~0.36 bits better than shuffle). But note the sign —
both real and shuffled surah models are *worse* than global frequency; the topical signal is real yet
**sub-compressing** (it cannot beat global frequency, only beat shuffling). The only components that
survive the assault are (a) this faint real topical/lexical-recurrence signal and (b) the irreducible
lexical core itself. Structural, higher-order, and increasing-long-range components do not survive.

## 5. Falsification Attempts
This report is the null assault. The topical signal survives; the structural/higher-order/increasing-
long-range components collapse and are removed.

## 6. Limitations
50 realizations give a stable null band; the surah-shuffle null tests topical coherence specifically.
Other null types (motif/dependency/grammar-preserving) were covered by Phase P (all non-predictive).

## 7. Conclusion
**Survivors of the null assault:** a faint real (sub-compressing) surah-topical/lexical-recurrence
signal, and the irreducible lexical core. Structural and higher-order components collapse.

Source: `generated/residual_nature/null_assault.json`.
