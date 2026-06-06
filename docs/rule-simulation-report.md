# Rule Simulation Report — Phase 12 (E)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase12-grammar-1.0`.

Phase E is the decisive test: starting from an **empty graph**, apply the
discovered rules, generate synthetic networks, and compare to the observed
network. Generation is claimed only for the properties the simulation actually
reproduces. 30 independent runs (`SEED = 20261212`); statistics reported with 95%
CIs.

---

## 1. Observed vs simulated

| Property | Observed | Simulated (mean) | 95% CI | Ratio |
|---|---:|---:|---|---:|
| **Triad-distribution cosine** | 1.000 (self) | **0.905** | [0.887, 0.922] | — |
| Motif classes | 13 | **13.0** | [13, 13] | **1.00** |
| Reciprocity | 0.612 | 0.591 | [0.555, 0.630] | 0.97 |
| Transitivity | 0.250 | 0.260 | [0.224, 0.302] | 1.04 |
| Largest SCC | 94 | 90.9 | [85.6, 96.6] | 0.97 |
| **Hub edge-share** | **0.087** | **0.034** | [0.028, 0.041] | **0.39** |

---

## 2. What the simulation generates

- **The 13-class motif vocabulary — GENERATED.** Every one of the 13 directed
  triad classes appears in every run; the full triad distribution matches the
  observed at **cosine 0.905 ± 0.010**. The motif vocabulary is a genuine
  *generative* consequence of three local rules — not an enumerated catalogue.
- **Reciprocity and transitivity — GENERATED.** Both are reproduced within ~4% of
  observed (held-in fit targets).
- **The giant SCC size — GENERATED.** The synthetic graph develops a strongly-
  connected component of ~91 nodes (ratio 0.97), emerging from reciprocity +
  density. Global connectivity is an emergent property of the local rules.

## 3. What the simulation does NOT generate

- **The hub — NOT GENERATED.** The synthetic hub reaches only edge-share 0.034 vs
  the observed 0.087 (ratio 0.39). Increasing the attachment exponent γ does not
  close the gap (it degrades the motif match instead — see
  `rule-falsification-report.md`). The observed hub (in-degree 96 of 99 possible)
  is **more extreme than any attachment rule produces** — it is an irreducible
  primitive, consistent with Phase 11 (hub SURVIVES STRONGLY) and Phase 5 (single
  dominant core).

---

## 4. Generation accuracy (success criterion)

| Question | Answer |
|---|---|
| Can the rules generate the motif vocabulary? | **Yes** — cosine 0.905, all 13 classes |
| Can the rules generate hub emergence? | **No** — only 39% of the hub's magnitude |
| Can the rules generate the giant SCC? | **Size yes** (ratio 0.97); exact membership untested |
| Can the rules generate consistency? | **No** — out of scope (topology only) |
| Fraction of observed (local) structure reproduced | **~90%** (triad cosine) |
| More efficient than the motif description? | **Yes** for local structure (2–3 rule parameters reproduce the 13-class distribution) |

---

## 5. Verdict

> **Local generation confirmed; global hub generation falsified.** Three local
> production rules generate ~90% of the local motif structure and the giant SCC
> size from an empty graph, but they do not generate the extreme hub or the
> consistency property. Generation is **partial and local** — and this is
> established by simulation, never asserted.

---

## 6. Reproduce

```bash
python3 scripts/build_grammar.py
python3 scripts/validate_grammar.py --rebuild
```

Source: `generated/grammar/rule_simulation.json`.
