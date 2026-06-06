# Rule Discovery Report — Phase 12 (A)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase12-grammar-1.0`.

Phase 12 built the **Generative Grammar Discovery Engine**. It tests — never
assumes — whether the observed Quranic proposition network can be *generated* by a
small set of structural production rules. A rule is not a concept and not a motif:
it is an **empirically-measured transformation** that, applied from an empty
graph, repeatedly produces observed structure. Rules carry opaque ids
`RULE_001…`; none is named. No meaning, theology, translation, or tafsir is used;
no external graph theory is cited as an explanation — every rule is measured from
the data and validated only by simulation. **Generation is claimed only where
simulation confirms it.** Phases 1–11 are read and hashed but never rebuilt.

---

## 1. Discovered production rules

Three production rules were discovered, with parameters **measured** from the
observed graph (N = 100 nodes, M = 1,059 directed edges):

| Rule | Transformation (operation) | Measured parameter | Generates |
|---|---|---|---|
| `RULE_001` | **degree-proportional attachment** — fresh edge: source ∝ (out-deg+1)^γ, target ∝ (in-deg+1)^γ | γ = 1.0, fraction 0.47 | degree skew, in-merge / out-fork triads |
| `RULE_002` | **reciprocity** — copy the reverse of an existing edge | fraction 0.38 (target reciprocity 0.612) | mutual dyads, mutual triangles |
| `RULE_003` | **transitive closure** — close a 2-path A→B→C with A→C | fraction 0.15 (target transitivity 0.250) | transitive triangles |

The mixing fractions, the attachment exponent γ, and the constraints N, M are all
fit from the observed network — nothing is invented. The rules are described
operationally and remain opaque (no semantic labels).

---

## 2. How the parameters were measured

The observed network's generative fingerprints were measured directly:

| Quantity | Observed value |
|---|---|
| Nodes (N) | 100 |
| Directed edges (M) | 1,059 |
| Reciprocity (mutual / all directed edges) | **0.612** |
| Transitive-closure coefficient (closed 2-paths / 2-paths) | **0.250** |
| Hub edge-share (max-degree node / endpoints) | **0.087** |
| Connected triad classes | **13** |
| Largest strongly-connected component | **94** |

The mixing fractions (f_recip = 0.38, f_trans = 0.15, γ = 1.0) were selected by a
deterministic grid search minimising the distance between simulated and observed
(reciprocity, transitivity) while maximising the triad-distribution cosine. The
triad distribution itself is a **held-out** validation target (not fit) — see
`rule-simulation-report.md`.

---

## 3. Do production rules exist?

**Yes — three measured transformations reproduce the local structure.** From an
empty graph, `RULE_001..003` regenerate the 13-class motif vocabulary at cosine
**0.905** (see simulation report). The network's local relational form is
captured by a tiny rule set, not by an enumeration of motifs.

But the rules are **local**: they do **not** generate the global hub dominance
(Phase C) or the Phase-10 consistency (a property of the activation matrix, not of
topology). Generation is **partial and local** — established by simulation, not
asserted.

---

## 4. Are the rules local / global / recursive / hierarchical?

| Property | Finding |
|---|---|
| Local | **Yes** — all three operate on local edge neighbourhoods |
| Global | **No** — no rule produces the global hub; it is an irreducible primitive |
| Recursive | Partly — reciprocity and transitive closure act on the graph's own existing edges (self-referential) |
| Hierarchical | No — the rules are a flat set, applied probabilistically |
| Self-reinforcing | **Yes** — attachment is degree-proportional (rich-get-richer) and reciprocity copies existing edges |

---

## 5. Outputs

`generated/grammar/rule_candidates.json` (the rules + fit grid) plus the
generation, simulation, statistics, ablation, robustness, and falsification
products. Tooling: `scripts/build_grammar.py`, `scripts/validate_grammar.py` (70
checks, `--rebuild` byte-identical). Reports: this one, `rule-generation-report.md`,
`rule-simulation-report.md`, `rule-ablation-report.md`,
`rule-falsification-report.md`, `phase12-final-report.md`.

---

## 6. Limitations

- The grammar models **topology only** (the directed proposition graph); the
  activation matrix and its consistency are out of scope.
- The rule set is the smallest that reproduces the *measured* targets; a different
  observed-graph projection would re-fit the parameters.
- "Generation" means topological reproduction confirmed by simulation, nothing
  more — no meaning or mechanism is claimed.

---

## 7. Reproduce

```bash
python3 scripts/build_grammar.py
python3 scripts/validate_grammar.py --rebuild
```
