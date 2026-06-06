# Semantic Primitives Report — Phase Σ (G)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`sigma-semantics-1.0`.

Phase G asks whether many concepts can be reconstructed from a smaller set of
**semantic** primitives — concepts that appear in (help define) many others. Unlike
Phase 8's structural principles, these are semantic; their existence is tested, not
assumed.

---

## 1. Method

A semantic primitive is a concept that appears in many other concepts'
neighbourhoods (definitions). Greedy set-cover over "which concepts each primitive
helps define" gives the minimum primitive sets.

| Target (of 89 defined concepts) | Primitives required |
|---:|---:|
| 50% | **6** |
| 70% | 10 |
| 80% | 13 |
| 90% | 18 |

---

## 2. Findings

- **A small semantic core covers most definitions.** Six primitives cover half the
  defined concepts; 13 cover 80%. The semantic layer is partly compressible to a
  small definitional core.
- **The primitive core is mixed.** Top primitives include `CONCEPT_001` (`يسر`),
  `CONCEPT_007` (`اله`), `CONCEPT_027` (`ربو`), `CONCEPT_005` (`نشا`), `CONCEPT_080`
  (`غلب`). Some are frequency hubs (`CONCEPT_007`), some are low-frequency genuine
  semantic anchors (`CONCEPT_027`, marginal 52). So the compression is **partly
  frequency, partly genuine semantic structure**.
- **This is consistent with Phase 17** (~35% structure / ~65% frequency): the
  definitional core's frequency component is the hub's ubiquity; its genuine
  semantic component is the low-frequency, high-residual anchors (see
  `semantic-anchor-report.md`).

---

## 3. Honest reading

A small primitive set covers most definitions, but **not all of that compression is
semantic** — much of it is the hub appearing in everyone's neighbourhood by
frequency. The genuinely *semantic* primitives are the high-residual anchors
(low-frequency concepts that define many others). The semantic core exists but is
smaller than the raw primitive count suggests.

---

## 4. Verdict

> **A small semantic core partly compresses the semantic layer** (6 primitives →
> 50%, 13 → 80% of definitions). But the core is mixed: part is frequency (the hub),
> part is genuine semantic anchoring (low-frequency high-residual concepts). The
> compression is real but not purely semantic.

---

## 5. Reproduce

```bash
python3 scripts/build_semantics.py
python3 scripts/validate_semantics.py --rebuild
```

Source: `generated/semantics/semantic_primitives.json`.
