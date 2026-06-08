# Reconstruction Report — Phase Ψ (E)

**Phase:** Ψ · **Method version:** `residual-nature-1.0` · **Date:** 2026-06-08.

## 1. Objective
Attempt to reconstruct hidden ayah content from residual structure alone (no frequency): does the
residual contain recoverable information, or only irreducible specificity?

## 2. Method
Mask each present root; predict it from context using **structure only** (PPMI evidence, no frequency
prior) vs the frequency baseline; compare Hits@10. (In-sample; the out-of-sample bound is Phase P.)

## 3. Results
| predictor | Hits@10 |
|---|--:|
| structure-only (in-sample) | 0.280 |
| frequency | 0.207 |

- In-sample, structure-only **beats** frequency (0.280 > 0.207).
- Out-of-sample (Phase P): structure does **not** beat frequency (info-gain −3.32 bits, 0/7 regimes).

## 4. Interpretation
The in-sample "recoverability" is **overfitting**: structure-only reconstruction beats frequency only
because the same specific words recur within the fitted corpus — the model is reading back the very
identities it was built from. Out-of-sample, Phase P proved this collapses. So the residual is **not
generalizably recoverable** from structure; it is **irreducible specificity** — the content can be
memorized in-sample but not derived. This is the cleanest demonstration that the residual is
referential identity, not recoverable structure.

## 5. Falsification Attempts
"The residual is recoverable from structure" survives only in-sample (overfitting) and is falsified
out-of-sample (Phase P). The honest verdict is: not recoverable.

## 6. Limitations
The reconstruction is in-sample by construction here; the decisive out-of-sample result is imported
from Phase P rather than re-run.

## 7. Conclusion
**The residual is not generalizably recoverable from structure** — in-sample recovery is overfitting;
out-of-sample it fails. It is irreducible referential specificity.

Source: `generated/residual_nature/reconstruction_results.json`.
