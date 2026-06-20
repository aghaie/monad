# Robustness / Falsification Report (L2 & L3)

- **Purpose:** test whether the L2 and L3 self-prediction signals are **real** or
  artifacts of method / frequency / leakage — before building further layers on them.
- **Source:** `generated/monad.db`, `generated/layers/L2_names/`.
- **Reproducibility:** deterministic (fixed RNG, seed 12345). Output: `generated/layers/robustness/robustness.json`.

## Tests and results

### A. L2 permutation null — *is the content→name structure real?*

Shuffle the (content → sealing-name) labels and re-run the held-out predictor.

| | top-1 |
|---|---:|
| Real | **31.18%** |
| Permuted null (50×) | 4.10% ± 1.08% (max 6.86%) |

Empirical p = 0.020; real > every null. **There IS genuine content→name
structure** — destroying the label–content link collapses accuracy to ~4%.

### B. L2 leakage test — *how much of that is the name's own root repeating?*

Remove the sealing name's **own root** from the ayah content, then re-predict.

| | top-1 |
|---|---:|
| Real (with the name's own root) | 31.18% |
| Without the name's own root | **16.13%** |
| (L2 frequency baseline, for reference) | 21.64% |

**This is the sobering finding.** ~Half of the headline accuracy was the name's
own root appearing elsewhere in the ayah (e.g. رحمة → رحیم). With that trivial
cue removed, the residual content signal is **16.1%, which falls *below* the
21.6% most-frequent-name baseline.** So once root-repetition is excluded, ayah
content does **not** pinpoint the exact sealing name better than simply guessing
the commonest name. (Part of this is that synonymous names — the mercy family
رحیم/غفور/رؤوف — are mutually confusable, so even genuine thematic coherence does
not single out one name.)

### C. L3 mismatched-context null — *is masked-root recovery genuinely contextual?*

Predict each masked root from a **random other ayah's** context.

| | top-1 |
|---|---:|
| Real (matched context, single split) | **4.93%** |
| Mismatched-context null (20×) | 0.18% ± 0.06% (max 0.30%) |

Empirical p = 0.048; real ≫ null. **L3's signal is robust** — the true context
predicts a masked root vastly better than a random one. (The 4.93% here is a
single 80/20 split; the 5-fold headline was 9.70%.)

## Verdict and consequences

- **L3 (root recovery): confirmed real.** Genuinely contextual; safe to build on.
- **L2 (content → name): partially real but its headline was inflated ~2× by
  root-repetition leakage.** Real structure exists (Test A), but the clean
  content→*exact*-name signal is weak (≈ at/below the frequency baseline). The
  earlier "thesis supported at 30.9%" claim is **downgraded**: it is evidence
  that content coheres with the name *family/space*, not that content pinpoints
  the specific name once trivial cues are removed.

**Action:** the L2 report and thesis claim are corrected (see
`docs/L2-names-report.md`). The proper test of "concepts cohere with the names"
should be made at the name-*family* / ayah level (L6) with leakage controls
built in from the start. This is the falsification discipline working as intended
— catching an inflated result before it propagated.
