# Falsification Report — Phase 14 (Locality) (I)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase14-locality-1.0`.

*(Named `locality-falsification-report.md` to preserve the immutable Phase-7
`falsification-report.md`; the Phase-14 spec's generic name collided with it.)*

Phase I attacks every distributional claim. No conclusion is drawn without
measurement; failures are reported.

---

## 1. The five claims under attack

| # | Claim | Result | Evidence |
|---|---|---|---|
| 1 | Structure is uniformly distributed | **FALSIFIED** | Gini(activations) = 0.58; 17/114 surahs (15%) carry 50% of activations |
| 2 | Structure is regionally concentrated in a tiny minority | **PARTIALLY FALSIFIED** | 50% needs 17 surahs (a minority, not tiny); per-ayah density Gini = 0.275 (concentration is a length effect) |
| 3 | Distinct specialized regions exist | **WEAKLY SUPPORTED** | raw fingerprint homogeneity 0.835 (one field); 54 weak clusters (cohesion ~0.28); only motif generation is functionally specialised (to large surahs) |
| 4 | Regions are interchangeable / redundant | **SUPPORTED** | no single-region removal breaks the hub or consistency |
| 5 | Local windows reproduce global structure | **SUPPORTED at scale** | at a 10% window: motif recovery 0.94, hub rank-1 prob 1.0, consistency 1.0 (but SCC only 0.41) |

---

## 2. Reading the verdicts together

The claims partly contradict each other by design, which forces a nuanced,
evidence-based picture:

- **Not uniform, not tiny-minority:** structure is *moderately* concentrated by
  volume (Gini 0.58) but *even* by per-ayah density (Gini 0.275). Both extreme
  claims fail.
- **No strong regions:** the "specialized regions" claim is only *weakly* supported
  — the corpus is one homogeneous field with weak, size-driven clusters. The honest
  verdict is closer to *no distinct regions*.
- **Redundant and local:** regions are interchangeable (claim 4) and the core
  structure is local (claim 5) — both are well supported. The one exception is the
  giant SCC, which is global (so claim 5 is "at scale," not absolute).

---

## 3. Documented limitations / artifacts

- **Concentration is a length artifact.** The total-activation Gini (0.58) tracks
  surah length (Gini ~0.57); per-ayah density is even. Reporting only totals would
  overstate concentration — we report both.
- **Regions are weak and size-driven.** The discriminative clustering recovers real
  but shallow structure (cohesion ~0.28); it mostly groups short surahs. We do not
  claim sharp thematic regions.
- **Surahs are the corpus's own structural units** — not human-defined regions.
  Regions are clusters of fingerprints, never assigned by name or topic.

---

## 4. Verdict

> Every distributional claim was attacked and resolved by measurement: structure is
> **not uniform** (claim 1 falsified) and **not tiny-minority** (claim 2 partially
> falsified); **no strong specialized regions** exist (claim 3 only weakly
> supported); regions are **redundant/interchangeable** (claim 4) and the core
> structure is **local** (claim 5, except the global SCC).

---

## 5. Reproduce

```bash
python3 scripts/build_locality.py
python3 scripts/validate_locality.py --rebuild
```

Source: `generated/locality/falsification_results.json`.
