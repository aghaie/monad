# Semantic Recoverability Report — Phase Σ (A)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`sigma-semantics-1.0`.

Phase Σ tests a new hypothesis: the Quran may define its own meanings internally.
Meaning is allowed; **external** meaning is forbidden. Everything emerges from the
corpus and prior Monad outputs — no dictionary, tafsir, translation, lexicon,
embedding, or imported label. This is the distributional theory of meaning applied
Quran-internally: a concept is defined only by its relations to **other opaque
concepts**; Arabic anchors are evidence labels, never glossed. Deterministic,
byte-identically reproducible (`validate_semantics.py --rebuild`, **344 checks
pass**).

This report covers Phase A — semantic recoverability.

---

## 1. Recoverability criterion (Quran-internal)

A concept is **RECOVERABLE** only if independent Quranic evidence converges:
- a falsification-surviving identity anchor (Phase 7 tier strong/moderate),
- a distinctive neighbourhood (Phase 6 top-neighbour weight ≥ 0.15),
- and contrasts (exclusion partners).

No external definition is used; recoverability means "the Quran's own relational
evidence converges on a stable position for this concept."

---

## 2. Result

| Class | Count |
|---|---:|
| **RECOVERABLE** | **77** |
| PARTIALLY_RECOVERABLE | 12 |
| NON_RECOVERABLE | 14 |

**77 of 103 concepts are relationally recoverable.** A clear majority of the
discovered concepts have convergent internal evidence — a stable anchor, a
distinctive neighbourhood, and contrasts — sufficient to define them *in terms of
other concepts*.

---

## 3. What recoverability does and does not mean

| Claim | Status |
|---|---|
| The concept has a stable *relational* position (neighbours, contrasts, role) | **Yes** for the 77 |
| The concept's *referent* (what it denotes in the world) is recovered | **No** — that is referential meaning (Phase Ω limit) |

Recoverability here is **relational/distributional**: the Quran's evidence fixes
*where a concept sits* in the network of other concepts, not *what it points to*.
The 14 non-recoverable concepts are the resist-identification and diffuse concepts
(Phase 7) — their internal evidence does not converge.

---

## 4. Verdict

> **Relational meaning is recoverable for the majority.** 77 of 103 concepts have
> convergent Quran-internal evidence (anchor + distinctive neighbourhood + contrasts)
> sufficient to define them relationally; 14 are non-recoverable (diffuse). This is
> distributional meaning, not referential meaning.

---

## 5. Reproduce

```bash
python3 scripts/build_semantics.py
python3 scripts/validate_semantics.py --rebuild
```

Source: `generated/semantics/recoverability.json`.
