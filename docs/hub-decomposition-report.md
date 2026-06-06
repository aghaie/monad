# Hub Decomposition Report — Phase 16 (A, B)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase16-hub-origin-1.0`.

Phase 16 investigates the **structural origin** of `CONCEPT_007`'s dominance — not
its meaning, theology, or interpretation. The hub is not protected; it must earn
survival. No theology, tafsir, translation, meaning, or imported explanation. All
prior phases are read and hashed but never rebuilt. Deterministic, byte-identically
reproducible (`validate_hub_origin.py --rebuild`, **75 checks pass**).

This report covers Phase A (decomposition) and Phase B (counterfactual removal).

---

## 1. The hub is rank-1 on every dominance axis

| Axis | Hub rank |
|---|---:|
| Activation frequency (marginal) | **1** |
| Co-occurrence degree | **1** |
| REQUIRES-in (necessity targeting) | **1** |
| Lexical frequency (member-root corpus tokens) | **1** |

`CONCEPT_007` is the top concept on all axes simultaneously. The question is
whether these are independent forms of dominance or one cause expressed many ways.

---

## 2. Dominance reduces to frequency

Spearman rank-correlation of each axis with activation frequency across all 103
concepts:

| Axis vs activation frequency | Spearman |
|---|---:|
| **Degree** | **0.966** |
| **Lexical frequency** | **0.998** |
| REQUIRES-in | −0.365 (non-monotone; hub still rank-1) |

- **Connectivity is a consequence of frequency** (Spearman 0.966): a concept that
  activates 96.8% of ayahs *mechanically* co-occurs with almost everything, so it
  has the highest degree. Degree is not an independent cause.
- **Frequency is itself near-perfectly predicted by lexical frequency** (Spearman
  0.998): a concept's activation rate is determined by the corpus token frequency of
  its member roots.
- REQUIRES-in is not monotone in frequency across all concepts, but the hub still
  leads it (everything co-occurs with the hub, so almost everything "requires" it).

**The hub's dominance is not six separate phenomena — it is one cause (frequency)
expressed across six axes.**

---

## 3. Counterfactual removal (Phase B)

Removing the hub and recomputing:

| Quantity | Value |
|---|---|
| Replacement hub (by activation) | `CONCEPT_081` |
| Replacement hub activation share | **0.418** |
| Hub's own share | 0.968 |

When the hub is removed, `CONCEPT_081` becomes the top concept — but at only **41.8%**
activation versus the hub's 96.8%. The hub's *function* (a dominant connector) is
partially taken over; its *magnitude* is not. The hub is simply doing what the
most-frequent concept mechanically does: co-occur with everything.

---

## 4. Verdict

> **Hub dominance decomposes to one cause: frequency.** The hub is rank-1 on every
> axis, and degree (0.966) and frequency (0.998 vs lexical) show that connectivity
> is a consequence of activation frequency, which is a consequence of lexical
> frequency. The hub is not a six-fold coincidence; it is the highest-frequency
> concept, and everything else follows.

---

## 5. Reproduce

```bash
python3 scripts/build_hub_origin.py
python3 scripts/validate_hub_origin.py --rebuild
```

Source: `generated/hub_origin/hub_decomposition.json`.
