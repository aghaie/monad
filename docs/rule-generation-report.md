# Rule Generation Report — Phase 12 (B, C, D)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase12-grammar-1.0`.

Phase B measures **local** generation (motifs, chains, local structure); Phase C
measures **global** generation (hub, SCC, compression, consistency); Phase D finds
the **minimum rule sets**. All claims are simulation-confirmed.

---

## 1. Phase B — local generation

| Property | Result |
|---|---|
| Triad-distribution cosine | **0.905** |
| Motif classes reproduced | **13 / 13** |
| Reciprocity reproduced | 0.591 (obs 0.612) |
| Transitivity reproduced | 0.260 (obs 0.250) |

**Verdict: GENERATED.** The local relational structure — the motif vocabulary,
reciprocity, and transitivity — is reproduced by `RULE_001..003` from an empty
graph. The rules that generate motif recurrence are **reciprocity (RULE_002)** and
**degree-proportional attachment (RULE_001)**; transitive closure (RULE_003)
contributes marginally (see ablation).

---

## 2. Phase C — global generation

| Property | Observed | Simulated | Generated? |
|---|---:|---:|:--:|
| Hub edge-share | 0.087 | 0.034 | **No** |
| Largest SCC | 94 | 91 | **Size yes** |
| Compression behaviour | (Phase 5) | — | inherited, not re-derived |
| Consistency | 0 contradictions | — | **No (out of scope)** |

**Verdict: NOT generated (hub / consistency).** The extreme hub is not an emergent
product of the local rules — it is an irreducible primitive. The giant SCC's
*size* emerges from reciprocity + density (ratio 0.97), but its exact membership
is not tested. Consistency is a property of the activation matrix M, not of graph
topology, so a topological grammar cannot generate it — this is a scope boundary,
not a rule failure.

**Which rules generate what (secondary questions):**

| Phenomenon | Generating rule(s) |
|---|---|
| Motif recurrence | RULE_002 (reciprocity) + RULE_001 (attachment) |
| Dependency formation (local) | RULE_001 (attachment) |
| Hub emergence | **none** — irreducible primitive |
| SCC formation (size) | RULE_002 + density (emergent) |
| Consistency preservation | **none** — out of topological scope |

---

## 3. Phase D — minimum rule sets

Reproduction measured as triad-distribution cosine vs observed; rules added
cumulatively (attachment provides the edge budget and is mandatory).

| Rule set | Triad cosine | Fraction of full |
|---|---:|---:|
| `RULE_001` (attachment only) | 0.595 | 0.66 |
| `RULE_001 + RULE_002` (+ reciprocity) | **0.901** | **1.00** |
| `RULE_001 + RULE_002 + RULE_003` (+ transitive closure) | 0.901 | 1.00 |

| Target (of full) | Rules required |
|---:|---:|
| 50% | 1 |
| 60% | 1 |
| 70% | **2** |
| 80% | **2** |
| 90% | **2** |
| 95% | **2** |

**Two rules — attachment + reciprocity — reproduce ~100% of the achievable local
structure.** Transitive closure (RULE_003) adds essentially nothing to the cosine
(it is near-redundant; confirmed by ablation). The minimal generative grammar is
therefore **{attachment, reciprocity}**.

---

## 4. Efficiency vs the motif description

The Phase-9 motif description enumerates 13 triad classes with their frequencies.
The grammar reproduces that entire distribution (cosine 0.90) from **2 rules with
~3 measured parameters** (f_recip, γ, and the M/N constraints). The grammar is
therefore a **more compressive account of the local structure** than the motif
catalogue — for local structure. It does not subsume the global hub or
consistency, which the motif/consistency descriptions cover and the grammar does
not.

---

## 5. Reproduce

```bash
python3 scripts/build_grammar.py
python3 scripts/validate_grammar.py --rebuild
```

Source: `generated/grammar/rule_generation.json`, `rule_statistics.json`.
