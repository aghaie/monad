# Phase Φ — Final Report: Counterfactual Quran Discovery Engine

**Method version:** `counterfactual-discovery-1.0` · **Date:** 2026-06-08. Deterministic,
byte-identical (`validate_counterfactual.py --rebuild`). This phase measures **selection only** — never
truth, theology, revelation, or origin (divine or human).

## 1. Objective
Previous phases measured structure. Phase Φ measures **selection**: given the discovered constraints,
how large is the space of alternative Quran-like texts, and how typical is the actual one? It reframes
Phase Ψ's ~80% lexical residual as a question about the geometry of choice.

## 2. Method (summary)
The alternative space = the max-entropy set matching the constraints; its size is the typical-set
2^(N·H), computed **analytically and exactly** (better than the spec's Monte-Carlo estimate). Selection
pressure = bits removed per constraint, on two axes (co-occurrence *form* vs lexical *identity*).
Typicality = the actual Quran's position among 1,000 generated frequency-valid alternatives. Full method
in the eight companion reports.

## 3. Results (headline)
| quantity | value |
|---|--:|
| root-slots N | 44,431 |
| **alternative space (frequency-valid)** | **~2^377,803** (astronomically large) |
| frequency reduces uniform per-draw choice | 20.4% |
| structural reduction of lexical-identity freedom | ~0 bits (Phase P) |
| actual Quran — lexical typicality | **TYPICAL** |
| actual Quran — structural typicality | **z ≈ 306** (coherent outlier vs random) |
| choice-residual | 8.50 bits/draw (~80%) |
| classification | **TYPE_B — weakly constrained selection** |

---

## The seven final answers

### Q1 — How large is the structurally-valid alternative space?
**~2^377,803** frequency-valid Quran-like texts — astronomically large (beyond enumeration).

### Q2 — How much does each discovered constraint reduce it?
On **two axes**: (a) co-occurrence STRUCTURE strongly selects the coherent *form* — the actual text is
**z ≈ 306** more clustered than frequency-random text; (b) on lexical *identity*, **frequency** removes
**20.4%** (~96,851 bits) and all structural constraints remove **~0 generalizable bits** (Phase P).
Consistency, hub, and locality add no independent reduction.

### Q3 — Are the actual Quranic choices typical or atypical?
**Both, on different axes — and this must be stated as such.** **Lexically TYPICAL**: the specific word
choices are an ordinary draw from the Quran's own frequency distribution. **Structurally EXTREME**
(z ≈ 306): far more clustered than random frequency-text — i.e. it is a *coherent* text (as any real
text is), a structural outlier only among word-salad. The coherence is real (Phase 17) but
non-generalizable (Phase P).

### Q4 — Can the discovered constraints explain the actual lexical choices? (YES / NO / PARTIAL)
**NO.** The constraints leave ~80% of the lexical-identity choice free, and the actual choices are
typical within that freedom. Structure constrains *which roots cluster* (coherence), not *which specific
identity occurs*. The constraints do not derive the Quran's specific words.

### Q5 — How much choice-residual remains after all constraints?
**~8.50 bits/draw (~80% of the uniform choice).** This equals the Phase Ψ residual: the irreducible
lexical specificity *is* the free choice the constraints do not determine.

### Q6 — Is the Phase Ψ residual best described as…?
**TYPE_B — weakly constrained selection.** Frequency reduces it ~20%, structure ~0; ~80% remains free;
the actual choices are typical within that freedom. (Not TYPE_A: frequency does constrain. Not TYPE_C/D:
80% is free.)

### Q7 — The most precise measurable statement (no interpretation)
> *Two axes must be separated. **(1) Structural form:** the actual Quran is a strong structural outlier
> among frequency-random alternatives — its words co-occur z ≈ 306 more than chance (it is a coherent
> text, as any real text is). So the coherence constraint is real and strong relative to random
> word-salad. **(2) Lexical identity:** within the space of structurally-valid (coherent) texts, the
> alternative space is astronomically large (~2^377,803; ~8.50 bits of free lexical choice per
> root-slot), and the actual Quran's specific word choices are typical — a typical draw from its own
> frequency distribution. The discovered constraints reduce the lexical-identity choice only weakly:
> frequency removes ~20%, structure removes 0 generalizable bits (Phase P), because the co-occurrence
> constrains which roots cluster (form), not which identity occurs. Therefore the discovered constraints
> do **NOT** explain why the Quran contains these specific lexical choices rather than other valid
> alternatives: ~80% of the identity choice is free within the coherent space — weakly-constrained
> selection. Monad can quantify how much choice remained, and how coherent the text is, but cannot
> derive which specific words were chosen. We do not know why these specific words rather than other
> structurally-valid alternatives — only that, given the discovered constraints, the lexical choice was
> left almost entirely open.*

---

## 4. Interpretation
Phase Φ completes the arc Ω(B) → Ψ → Φ. Ω(B) measured the boundary (20% explained / 80% residual); Ψ
named the residual (irreducible lexical-referential specificity); Φ measures its selection geometry: the
residual **is the free choice** within an astronomically large space of alternatives, and the actual
choices are **typical**, not rare. The one genuinely strong selection effect — the text's coherence
(z ≈ 306) — is the generic property of being a real text and constrains form, not identity. The project
can now state precisely: the discovered constraints define a vast space of coherent alternative texts;
the Quran is one typical member; its specific lexical content is free within those constraints and is
not derivable from them.

## 5. Falsification Attempts
"The Quran's choices are rare/atypical/strongly-constrained" is falsified (lexically typical; 80% free;
TYPE_B). "Structure strongly constrains identity" is falsified (Phase P). "Structure is negligible" is
falsified on the form axis (z ≈ 306). Each claim is reported on its proper axis; nothing is overstated.

## 6. Limitations
- Alternative counts are exact in log₂; "astronomically large" is beyond physical enumeration by design.
- The form/identity split is the honest reconciliation of a strong structural z-score (coherence) with a
  zero generalizable identity reduction (Phase P).
- The phase measures selection given the *discovered* constraints; a constraint Monad has not found could
  reduce the space further — genuinely unknown.

## 7. Conclusion
**The structurally-valid alternative space is ~2^377,803; the actual Quran is a typical member on lexical
identity and a coherent outlier on form (z ≈ 306); the discovered constraints do NOT explain its specific
lexical choices (~80% free); the Phase Ψ residual is weakly-constrained free selection (TYPE_B).** Monad
measures the geometry of choice precisely and, by design, says nothing about why these choices were made —
only that, given everything discovered, they were left almost entirely open.

---

### Outputs
`generated/counterfactual/`: 8 data products + `counterfactual_manifest.json`. Tooling:
`scripts/build_counterfactual.py`, `scripts/validate_counterfactual.py`. Reports:
`constraint-inventory-report.md`, `alternative-space-report.md`, `selection-pressure-report.md`,
`rare-choice-report.md`, `local-counterfactual-report.md`, `global-counterfactual-report.md`,
`choice-residual-report.md`, `selection-classification-report.md`, this report.

### Reproduce
```bash
python3 scripts/build_counterfactual.py
python3 scripts/validate_counterfactual.py --rebuild
```

**Phase Φ complete. No further phase started automatically.**
