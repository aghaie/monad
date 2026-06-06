# Consistency Survival Report — Phase 17 (E)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase17-frequency-null-1.0`.

Phase E re-evaluates the Phase-10 / Phase-15 consistency finding against the
frequency null: does consistency exceed null expectation?

---

## 1. Result

| Quantity | Value |
|---|---|
| Observed contradictions | **0** |
| Null contradictions (1,000 realizations) | **0** (mean 0, std 0, max 0) |
| Consistency exceeds null? | **No** |
| Structure fraction | **0%** |

---

## 2. Findings

- **Consistency does NOT exceed the frequency null.** Every one of the 1,000
  frequency-preserving null corpora is *equally* consistent — 0 contradictions. The
  observed consistency is exactly what a frequency-shuffled corpus produces.
- This is a **direct corroboration of Phase 15**, which found consistency to be
  irreducible, generic, and partly tautological. Phase 17 confirms it at the null
  level: consistency carries **0% information beyond frequency**.
- The reason is structural-definitional: the exclusion∧positive guarantee is
  tautological (a pair cannot have co = 0 and co ≥ 5), and necessity-consistency is
  carried by the hub's ubiquity (preserved in the null). Both survive any
  frequency-preserving shuffle.

---

## 3. Does consistency survive frequency control?

| Question | Answer |
|---|---|
| Does consistency exceed the null? | **No** — the null is equally consistent |
| Is consistency a structural achievement? | **No** — it is generic to frequency-preserving data |
| Structure fraction | **0%** (FREQUENCY ONLY) |

**Hypothesis H4 ("consistency exceeds frequency") is FALSIFIED.**

---

## 4. Verdict

> **Consistency does not survive frequency control — it is FREQUENCY ONLY.** All
> 1,000 frequency-preserving nulls are equally consistent (0 contradictions).
> Consistency carries no information beyond frequency; it is generic and partly
> tautological, exactly as Phase 15 found. Hypothesis H4 is falsified.

---

## 5. Reproduce

```bash
python3 scripts/build_frequency_null.py
python3 scripts/validate_frequency_null.py --rebuild
```

Source: `generated/frequency_null/consistency_survival.json`.
