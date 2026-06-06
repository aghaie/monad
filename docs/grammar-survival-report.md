# Grammar Survival Report — Phase 17 (H)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase17-frequency-null-1.0`.

Phase H re-evaluates the Phase-12 grammar rules against the frequency null: are the
discovered grammar rules merely frequency artifacts?

---

## 1. Rule-by-rule survival

| Rule | Observed | Null mean | Survives frequency? | Structure % |
|---|---|---|---|---:|
| **Attachment** (degree-proportional) | degree ∝ marginal | — | **No** — IS frequency | 0% |
| **Reciprocity** | (co-occurrence symmetric) | ≈ observed | **No** — does not exceed null | 0% |
| **Transitive closure** | (2-path closure) | below observed | **partly** | 31.3% |

---

## 2. Findings

- **Attachment is frequency.** The Phase-12 attachment rule (a fresh edge attaches
  ∝ degree) is, by Phase 16, identical to frequency: degree ∝ marginal at Spearman
  0.966. Attachment carries no information beyond frequency.
- **Reciprocity is frequency-generic.** The frequency null produces the same
  reciprocity (symmetric co-occurrence is preserved when marginals are preserved).
  Reciprocity does not exceed the null — **0% structure**.
- **Transitive closure is partly structural** (~31% structure): the observed
  transitivity modestly exceeds the null, reflecting the specific association
  structure (which itself survives). But it is the weakest of the three Phase-12
  rules (Phase 12 already found it near-redundant, ablation drop 0.005).

---

## 3. Are the grammar rules frequency artifacts?

| Rule | Verdict |
|---|---|
| Attachment | **frequency artifact** (= degree ∝ frequency) |
| Reciprocity | **frequency artifact** (generic to preserved marginals) |
| Transitive closure | **partly structural** (~31%) |

The Phase-12 grammar is therefore **mostly frequency**: its two effective rules
(attachment, reciprocity) are frequency artifacts, and only the near-redundant
transitive-closure rule carries a minority of structure. **Hypothesis H6 ("grammar
exceeds frequency") is MIXED — mostly falsified.**

---

## 4. Reconciliation with Phase 12

Phase 12 found the grammar reproduces the local motif vocabulary (cosine 0.90) but
*cannot* generate the hub. Phase 17 refines: the grammar's success at reproducing
local structure is *because* its rules encode frequency (attachment) and generic
reciprocity — the very things the frequency null also reproduces. The grammar is a
faithful model of the frequency-generated structure, not of structure beyond
frequency.

---

## 5. Verdict

> **The Phase-12 grammar is mostly a frequency artifact.** Attachment is frequency
> (degree ∝ marginal); reciprocity is frequency-generic; only transitive closure
> carries a minority of structure (~31%), and it is near-redundant. Hypothesis H6 is
> mixed — mostly falsified.

---

## 6. Reproduce

```bash
python3 scripts/build_frequency_null.py
python3 scripts/validate_frequency_null.py --rebuild
```

Source: `generated/frequency_null/grammar_survival.json`.
