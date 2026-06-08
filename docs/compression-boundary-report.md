# Compression-Boundary Report — Phase Ψ (G)

**Phase:** Ψ · **Method version:** `residual-nature-1.0` · **Date:** 2026-06-08.

## 1. Objective
Measure the residual's compression boundary: what is the shortest description of the residual — can it
be compressed, or is it largely incompressible?

## 2. Method
The best available compressor of the residual is surah-topical (per-surah) conditioning; measure how
much it reduces the residual's description length below global frequency.

## 3. Results
- Surah-topical conditioning: **−0.42 bits** (it does not reduce the description length — it increases
  it).
- **Residual compressible fraction ≈ 0%; incompressible ≈ 100%.**

## 4. Interpretation
The residual is **largely incompressible.** The strongest conditioning Monad can apply (surah-topic)
does not shorten its description below global frequency; co-occurrence/motif/grammar add no
generalizable compression (Phase P). So the ~80% residual approximates an incompressible core: the
specific lexical identity of each ayah cannot be derived from a shorter rule. This is the
information-theoretic signature of irreducible specificity.

## 5. Falsification Attempts
"The residual is compressible" is falsified — no available conditioning compresses it.

## 6. Limitations
Compression is measured against the conditioning models Monad has; a Kolmogorov-optimal compressor is
uncomputable, so "incompressible" means "incompressible by all discovered structure," not provably
algorithmically random.

## 7. Conclusion
**The residual is largely incompressible** — no discovered conditioning shortens its description. It
is an irreducible lexical-specificity core.

Source: `generated/residual_nature/compression_boundary.json`.
