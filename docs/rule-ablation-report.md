# Rule Ablation Report — Phase 12 (F)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase12-grammar-1.0`.

Phase F removes each rule from the simulator, re-runs from an empty graph, and
measures what degrades. Rules are ranked by impact. 15 runs per ablation.

---

## 1. Ablation impact

Full-model triad cosine: **0.905**.

| Rank | Removed rule | Transformation | Cosine without | Cosine drop | Reciprocity without | Classes without |
|---:|---|---|---:|---:|---:|---:|
| 1 | `RULE_002` | reciprocity | 0.548 | **0.357** | 0.070 | 12.7 |
| 2 | `RULE_001` | degree-proportional attachment | 0.879 | 0.027 | 0.535 | 13.0 |
| 3 | `RULE_003` | transitive closure | 0.900 | **0.005** | 0.568 | 13.0 |

---

## 2. Findings

- **RULE_002 (reciprocity) is by far the most important rule.** Removing it
  collapses the triad cosine from 0.905 → 0.548 (drop 0.357), reciprocity from
  0.59 → 0.07, and drops a triad class. The network's local structure is
  *dominated by reciprocity* — the mutual-edge process is the engine of the motif
  vocabulary. This is consistent with Phase 9 (reciprocal/mutual triads are the
  most over-represented) and Phase 10 (symmetric `ASSOCIATES_WITH` is a large
  share of edges).
- **RULE_001 (attachment) is secondary but real.** Removing it costs 0.027 cosine
  and removes the degree skew; it still provides the edge budget.
- **RULE_003 (transitive closure) is near-redundant.** Removing it costs only
  0.005 cosine — the transitive triangles it would add are already produced by the
  attachment + reciprocity processes. The grammar barely needs it.

---

## 3. Rule importance ranking

```
RULE_002 (reciprocity)            ████████████████████  drop 0.357   ESSENTIAL
RULE_001 (attachment)             ██                    drop 0.027   contributing
RULE_003 (transitive closure)     ▏                     drop 0.005   near-redundant
```

**The minimal effective grammar is {RULE_001, RULE_002}** — attachment +
reciprocity. RULE_003 can be dropped with negligible loss (confirming the Phase-D
minimum-set result that 2 rules reach full cosine).

---

## 4. Interpretation (structural only)

The local relational structure of the Quranic proposition network is generated
predominantly by a **mutual-edge (reciprocity) process** on top of a
degree-biased edge budget. The recurring motifs are not many independent
phenomena — they are the shadow of one dominant production rule (reciprocity)
plus attachment. No meaning is attached to this; it is a generative-mechanism
finding.

---

## 5. Reproduce

```bash
python3 scripts/build_grammar.py
python3 scripts/validate_grammar.py --rebuild
```

Source: `generated/grammar/rule_ablation.json`.
