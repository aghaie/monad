# Compression Analysis Report — Phase 5 (B, D, G)

**Date:** 2026-06-06. **Method version:** `phase5-compression-1.0`. **Status:**
complete.

This report answers the **primary research question**: *can the proposition
graph be reconstructed from a substantially smaller subset of concepts?* It
combines the iterative removal experiments (Phase B), the minimum reconstruction
sets (Phase D), and the compression curve (Phase G). All quantities are
combinatorial. No concept is named, translated, or interpreted.

A concept set **reconstructs** a relation iff every participating concept is in
the set. Recovered structure = fraction of the 6,832 Phase-4 relations so
covered.

---

## 1. Headline answer

**Partially compressible — and provably so.** The structure does **not** reduce
to a small core under strict reconstruction:

| Recovered structure | Concepts required | Compression ratio |
|---:|---:|---:|
| 50% | 39 | 0.379 |
| 60% | 45 | 0.437 |
| 70% | 51 | 0.495 |
| 80% | **59** | **0.573** |
| 90% | 69 | 0.670 |
| 95% | 76 | 0.738 |

(Deterministic greedy maximum-coverage; sizes are upper bounds on the true
minimum. Source: `reconstruction_sets.json`.)

Recovering 80% of the discovered structure still requires **57% of the
concepts**. The system is *compressible at the margin* (a single concept buys
22%) but **not reducible to a small foundational kernel**.

---

## 2. Why not (the structural reason)

The proposition structure is a **dense relational web, not a star**. Because
every binary relation needs *both* endpoints and every triadic relation needs
*all three*, a concept contributes covered relations only once its partners are
already present. The compression curve is therefore **convex early**:

| Concepts (greedy) | Recovered |
|---:|---:|
| 10 | 4.7% |
| 20 | 18.2% |
| 30 | 35.6% |
| 40 | 53.1% |
| 50 | 69.0% |
| 60 | 81.8% |
| 70 | 91.4% |
| 80 | 96.9% |
| 90 | 99.4% |

The first 10 concepts — including the dominant hub — close under 5% of complete
relations, because their many partners are still missing. Coverage accelerates
only once a critical mass of mutually-related concepts co-exists. This convexity
is the formal signature of **low compressibility**.

- Greedy-coverage AUC: **0.612** · foundationality-order AUC: 0.602 · dependency
  AUC: 0.544 (all on `[0,1]²`).
- **Knee** (max distance above the diagonal chord): greedy at **k = 66**
  (88.1% recovered); foundationality at k = 64 (85.6%). The "elbow" sits at
  roughly two-thirds of the concept set — late, confirming weak compressibility.

---

## 3. Iterative removal experiments (Phase B)

Removing the top-*k* most foundational concepts (Phase A order):

| k removed | Prop. retention | Dep. retention | Graph integrity | Largest component | Recoverability |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.778 | 0.662 | — | 94 / 102 | high |
| 3 | 0.537 | 0.542 | — | 90 / 100 | high |
| 5 | 0.409 | 0.472 | — | 88 / 98 | high |
| 10 | 0.192 | 0.285 | — | 80 / 93 | mid |
| 20 | 0.054 | 0.158 | — | 54 / 83 | falling |
| 30 | 0.028 | 0.106 | — | 28 / 73 | low |
| 50 | 0.008 | 0.049 | — | 5 / 53 | collapsed |

Full per-row metrics (graph integrity, component counts, recoverability):
`compression_statistics.json :: removal_experiments`.

**Reading:** the structure is concentrated but not single-point. The first
concept carries 22% of relations; the top-5 carry ~59%; the top-20 carry ~95%.
Connectivity degrades gradually until ~top-20, then the largest component
fractures rapidly (54 → 28 → 5 across top-20/30/50). There is a **dense
foundational band of ~15–20 concepts**, not a 1–3 concept axis.

---

## 4. Secondary questions answered

| Question | Answer |
|---|---|
| Core–periphery structure? | **Yes** — a ~15–20 concept core, a long periphery (see §3). |
| Multiple independent cores? | **No** — one dominant node plus a single tightly-linked secondary band. |
| Single dominant core? | **Yes** — `CONCEPT_007` (see `hub-removal-report.md`). |
| Hierarchical dependency layers? | **Yes** — 8 levels (see `dependency-layer-report.md`). |
| Recursive dependency layers? | **Yes** — 7 irreducible cycles (see `irreducibility-report.md`). |
| Irreducible subgraphs? | **Yes** — strongly-connected cores that resist any compression. |
| Can a small subset explain most structure? | **No** — 80% needs 57% of concepts. |

---

## 5. Limitations

- **Strict reconstruction.** Full-membership coverage is conservative; partial
  or weighted recovery would report higher compressibility. The choice is
  stated, not hidden.
- **Greedy ≈ optimum, not exact.** Greedy maximum-coverage is a (1−1/e)
  approximation; reported set sizes are deterministic upper bounds. True minima
  could be marginally smaller but cannot change the qualitative verdict.
- **Population = Phase-4 relations** with their fixed thresholds and the
  per-ayah activation-union rule. A different relation population would redraw
  the curve.
- **No meaning.** Concept ids and relation types remain opaque.

---

## 6. Reproduce

```bash
python3 scripts/build_compression.py
python3 scripts/validate_compression.py --rebuild
```
