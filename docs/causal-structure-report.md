# Causal Structure Report — Phase Ω (D)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`omega-world-model-1.0`.

Phase D searches for causal patterns — not co-occurrence, but direction candidates.
Structural evidence only; no causation is claimed.

---

## 1. What is (and is not) measured

True causality cannot be established from text structure. What *can* be measured are
two Quran-internal **direction candidates**:

- **PRECEDES** — consistent positional precedence (one concept's words tend to
  appear before another's within shared ayahs, asymmetry ≥ 0.5).
- **PREDICTS** — consistent cross-ayah sequence (one concept's presence raises the
  probability of another in following ayahs).

These are **direction candidates**, explicitly **not** demonstrated causation.

---

## 2. Results

| Quantity | Value |
|---|---|
| Precedence-candidate edges | 303 (asymmetry ≥ 0.5: fewer) |
| Production-candidate (PREDICTS) edges | 547 |

Top precedence candidates and top production candidates are listed in
`causal_model.json` (opaque concept pairs with asymmetry / confidence).

---

## 3. What emerges and what does not

| Question | Answer |
|---|---|
| What consistently precedes what? | precedence candidates exist (PRECEDES) |
| What consistently produces what? | production candidates exist (PREDICTS) |
| Is this causality? | **No** — these are direction candidates, not causation |
| What consistently *destroys* what? | **Does not emerge** — "destruction" requires semantic valence (negation/loss), which is not structurally available |

---

## 4. The honest limit

The phase asked "what consistently precedes / produces / destroys what." Precedence
and production emerge as **structural candidates**. But:
- **Causation** cannot be established structurally (precedence ≠ cause).
- **Destruction** (a negative/loss transition) cannot be identified, because the
  structure has no semantic valence — it cannot tell a "producing" transition from a
  "destroying" one without interpretation.

So the causal model emerges only as a **direction-candidate graph**, not as a model
of causation.

---

## 5. Verdict

> **Causal structure emerges only as direction candidates.** Consistent precedence
> (PRECEDES) and production (PREDICTS) patterns exist, but they are not demonstrated
> causation, and "what destroys what" does not emerge (it requires semantic valence
> the structure lacks). The causal model is a candidate graph, not a causal model.

---

## 6. Reproduce

```bash
python3 scripts/build_world_model.py
python3 scripts/validate_world_model.py --rebuild
```

Source: `generated/world_model/causal_model.json`.
