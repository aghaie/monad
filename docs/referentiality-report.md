# Referentiality Report — Phase Ψ (C)

**Phase:** Ψ · **Method version:** `residual-nature-1.0` · **Date:** 2026-06-08.

## 1. Objective
Determine whether the residual is carried by specific **lexical** choices (which words) or by
**structural** patterns (how arranged).

## 2. Method
Compare the information carried by lexical identity vs structure: (a) preserve structure, randomize
lexical identity → does the residual collapse? (b) preserve lexical identity, destroy structure →
does it survive? Structural information is measured as the generalizable co-occurrence gain (Phase
P) and the in-sample association mass (mean PPMI).

## 3. Results
| carrier | information |
|---|--:|
| lexical identity | 8.50 bits/root (= the whole residual) |
| structural (in-sample association) | 1.72 bits (real but non-generalizable) |
| structural (generalizable, Phase P) | 0 bits |

- Destroy structure / preserve lexical → residual **preserved** (it is the per-ayah root multiset).
- Randomize lexical / preserve structure → residual **collapses** (identity carries the information).
- **Carrier = lexical.**

## 4. Interpretation
The residual is carried by **lexical identity, not structure.** Knowing the arrangement/co-occurrence
adds no generalizable information (Phase P); knowing which specific roots are present *is* the
residual. The in-sample association (1.72 bits) is real but, per Phase P, predicts nothing held-out —
so it is not an explanatory structure but a by-product of the same words recurring. The residual is
**referential/lexical**: the specific identity of what each ayah contains.

## 5. Falsification Attempts
"The residual is structural" is falsified (structure carries 0 generalizable information; destroying
it preserves the residual). "The residual is lexical" survives (randomizing identity collapses it).

## 6. Limitations
"Lexical vs structural" is measured at the co-occurrence level; a representation that fuses them
differently is untested, but Phase P bounds the structural contribution at 0.

## 7. Conclusion
**The residual is lexical/referential** — carried by which specific root/concept occurs, not by
structure. Structure adds no generalizable information.

Source: `generated/residual_nature/referentiality_results.json`.
