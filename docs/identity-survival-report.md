# Identity Survival Report — Phase 17 (F)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase17-frequency-null-1.0`.

Phase F re-evaluates the Phase-7 identity anchors: would candidate identities emerge
from frequency alone?

---

## 1. Test

A concept's Phase-7 identity anchor is its dominant member root. If identity were
pure frequency, the anchor would simply be the **most-frequent** member root (by
corpus token count). The test counts how often anchor = most-frequent member root.

| Quantity | Value |
|---|---|
| Anchor = most-frequent member root | **71 / 103** |
| Frequency-explained fraction | **69%** |
| Structure fraction | **31%** |

---

## 2. Findings

- **Identity is MOSTLY frequency.** For **69%** of concepts, the discovered identity
  anchor is exactly the most-frequent member root — it could have been named from
  the Phase-1 token counts alone, with no relational analysis. This confirms Phase
  16's finding for the hub, generalised to all identities.
- **But ~31% is structure.** For the remaining 32 concepts, the anchor is *not* the
  most-frequent member root — the Phase-7 anchor (chosen by activation weight =
  count × membership confidence, and validated by signature-ayah coherence) reflects
  co-occurrence/coherence structure beyond raw frequency.

---

## 3. Anchor / confidence / ambiguity persistence

| Property | Reading |
|---|---|
| Anchor persistence under frequency | high (69% reproducible from frequency alone) |
| Confidence persistence | frequency-driven (dominant-root share tracks lexical frequency) |
| Ambiguity persistence | the ~31% non-frequency anchors are the more ambiguous / distributed concepts |

---

## 4. Would identities emerge from frequency alone?

| Question | Answer |
|---|---|
| Would candidate identities emerge from frequency alone? | **Mostly yes** — 69% of anchors are the most-frequent member root |
| Is identity structure or frequency? | mostly frequency (69%), with a ~31% structural residue |

**Hypothesis H5 ("identity exceeds frequency") is FALSIFIED (mostly)** — identity
is predominantly a frequency phenomenon, with a minority structural component.

---

## 5. Verdict

> **Identity is mostly frequency.** 69% of Phase-7 anchors are exactly the
> most-frequent member root — reproducible from token counts alone. ~31% reflects
> genuine co-occurrence/coherence structure. Hypothesis H5 is mostly falsified.

---

## 6. Reproduce

```bash
python3 scripts/build_frequency_null.py
python3 scripts/validate_frequency_null.py --rebuild
```

Source: `generated/frequency_null/identity_survival.json`.
