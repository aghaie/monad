# Rule Falsification Report — Phase 12 (G, H)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase12-grammar-1.0`.

Phase H attacks every generation claim; Phase G tests rule robustness under
perturbation. Only claims confirmed by simulation survive; failures are
documented.

---

## 1. Phase H — falsification of generation claims

| Claim | Result | Evidence |
|---|---|---|
| Rules generate the **13-class motif vocabulary** | **SURVIVES** | all 13 classes reproduced; triad cosine 0.905 |
| Rules generate the **observed hub dominance** | **FALSIFIED** | simulated hub share 0.034 vs observed 0.087; super-linear attachment does not close the gap |
| Rules generate the **exact giant SCC** | **PARTIAL** | SCC *size* ~91 vs 94 (ratio 0.97); membership untested |
| Rules generate **Phase-10 consistency** | **FALSIFIED (out of scope)** | consistency is a property of the activation matrix, not topology |

**1 claim survives, 2 falsified, 1 partial.** The grammar's generative power is
**local**: the motif vocabulary survives every test; the global hub and the
consistency property cannot be generated and are explicitly reported as failures /
scope boundaries — not hidden.

---

## 2. Why the hub claim fails (the key falsification)

The observed hub `CONCEPT_007` has in-degree 96 of 99 possible — it connects to
almost every node. No attachment rule reproduces this:

| Attachment exponent γ | Simulated hub share | Triad cosine |
|---:|---:|---:|
| 1.0 | 0.036 | 0.898 |
| 1.5 | 0.042 | 0.878 |
| 2.0 | 0.040 | 0.693 |
| 2.5 | 0.033 | 0.306 |
| 3.0 | 0.031 | 0.081 |

Increasing γ does **not** raise the hub share toward 0.087 — and it destroys the
motif match. The hub is **not** a product of preferential attachment; it is an
**irreducible primitive**, exactly as Phase 11 found (hub SURVIVES STRONGLY,
share invariant at 0.968 across all perturbations). The grammar cannot generate
it, and we say so.

---

## 3. Phase G — robustness of the rules

Rule parameters re-measured under 10–20% edge removal of the observed graph (8
runs each):

| Parameter | Observed | Under perturbation (mean) | 95% CI |
|---|---:|---:|---|
| Hub share | 0.087 | 0.088 | [0.085, 0.091] |
| Reciprocity | 0.612 | 0.520 | [0.479, 0.563] |
| Transitivity | 0.250 | 0.214 | [0.192, 0.233] |

- **Hub share is perfectly stable** (0.088, tight CI) — the hub parameter does not
  move under perturbation (it just isn't *generable*).
- **Reciprocity and transitivity fall modestly** under edge removal (expected:
  deleting edges breaks reciprocal pairs and 2-paths), but stay well above zero
  and within a narrow band. The rules' parameters are robust to perturbation.

**Verdict:** the discovered rules are robust — their measured parameters are
stable across perturbation regimes.

---

## 4. Documented failures (no hiding)

1. **Hub generation FAILS** — the central global feature is not reproduced.
2. **Consistency generation is out of scope** — topology cannot encode it.
3. **Transitive closure (RULE_003) is near-redundant** — it survives as a rule but
   contributes almost nothing (ablation drop 0.005).
4. **Exact SCC membership is untested** — only its size is reproduced.

---

## 5. Verdict

> **Generation is PARTIAL and LOCAL.** The motif vocabulary is generated and
> robust; the hub and consistency are not generated. Every failure is documented;
> no generation is claimed beyond what simulation confirms.

---

## 6. Reproduce

```bash
python3 scripts/build_grammar.py
python3 scripts/validate_grammar.py --rebuild
```

Source: `generated/grammar/rule_falsification.json`, `rule_robustness.json`.
