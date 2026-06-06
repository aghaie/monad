# Principle Discovery Report — Phase 8

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase8-principles-1.0`.

Phase 8 built the **Foundational Principle Discovery Engine**. Its purpose is to
*test* — never assume — whether the discovered Quranic structure can be explained
by a small set of foundational principles. A foundational principle is **not** a
word, root, lemma, or concept; it is a **structural pattern** capable of
explaining, generating, or constraining many discovered concepts and
propositions. Principles must emerge from the discovered structure itself; none
is invented, imported, named, translated, or interpreted. No theology, doctrine,
ontology, apologetics, or origin claim is produced. Success is not claimed before
testing, and a small principle set is not forced. Phases 1–7 are read and hashed
but never rebuilt.

---

## 1. What a principle is (operational, evidence-derived)

A principle candidate is a **maximal cohesive structural module** of the
*integrated concept graph*:

- **Nodes:** the 103 discovered concepts.
- **Edges:** undirected weight = (Phase-3 semantic overlap, min-max normalised)
  **+** (Phase-4 proposition weight, min-max normalised).
- **Discovery:** deterministic greedy modularity maximisation
  (Clauset–Newman–Moore). Modules are the principle candidates.

Each module is a higher-order pattern: it constrains the concepts it contains and
explains the propositions internal to it. Modules carry opaque ids
`PRINCIPLE_001…`; **no module is named.** This definition is forced by the
fundamental rule — a principle cannot be a concept, so it is a *pattern over*
concepts, discovered by the same community-detection family used in Phase 3,
lifted onto the combined semantic + relational graph.

Two explanatory senses are reported throughout and never conflated:

| Sense | A principle … | A relation is counted if … |
|---|---|---|
| **internal / generating** | *generates* the relation | **all** its concepts lie in the principle |
| **incidence / governing** | *governs* the relation | **≥ 1** of its concepts lies in the principle |

---

## 2. Result: 16 principles emerge

Greedy modularity discovered **16 principles** (modularity **Q = 0.294**) over the
103 concepts — a single deterministic partition, byte-identically reproducible.
The count is *discovered, not chosen*; no target number was imposed.

| Principle | Size | Concept cov. | Incident cov. | Internal cov. | Compression contrib. |
|---|---:|---:|---:|---:|---:|
| `PRINCIPLE_001` | 13 | 12.6% | 24.8% | 0.7% | 0.145 |
| `PRINCIPLE_002` | 11 | 10.7% | **36.8%** | 3.7% | 0.149 |
| `PRINCIPLE_003` | 9 | 8.7% | 21.8% | 0.6% | 0.085 |
| `PRINCIPLE_004` | 9 | 8.7% | 9.5% | 0.9% | 0.059 |
| `PRINCIPLE_005` | 8 | 7.8% | 19.6% | 0.6% | 0.076 |
| `PRINCIPLE_006` | 8 | 7.8% | 9.6% | 0.3% | 0.054 |
| `PRINCIPLE_007` | 8 | 7.8% | 18.1% | 1.0% | 0.080 |
| `PRINCIPLE_008` | 7 | 6.8% | 8.9% | 0.5% | 0.045 |
| `PRINCIPLE_009` | 6 | 5.8% | 6.4% | 0.2% | 0.036 |
| `PRINCIPLE_010` | 5 | 4.9% | 11.3% | 0.2% | 0.044 |
| `PRINCIPLE_011` | 5 | 4.9% | 28.9% | 0.6% | 0.099 |
| `PRINCIPLE_012` | 4 | 3.9% | 3.9% | 0.1% | 0.024 |
| `PRINCIPLE_013` | 3 | 2.9% | 7.3% | 0.1% | 0.027 |
| `PRINCIPLE_014` | 3 | 2.9% | 7.5% | 0.2% | 0.030 |
| `PRINCIPLE_015` | 3 | 2.9% | 14.0% | 0.3% | 0.046 |
| `PRINCIPLE_016` | 1 | 1.0% | 0.0% | 0.0% | 0.000 |

`PRINCIPLE_016` is the lone isolated concept (`CONCEPT_100`).

---

## 3. The central finding (no interpretation)

> **Only 9.9% of the 6,832 relations are internal to a single principle; 90.1%
> cross principle boundaries.**

No principle generates more than **3.7%** of the structure on its own
(`PRINCIPLE_002`). The structure is overwhelmingly **inter-principle** — relations
that no single module self-contains. This is the evidence-based answer to the
primary research question, developed fully in `principle-coverage-report.md`:
**the discovered structure is not reducible to a small set of self-contained
foundational principles.** It mirrors, one level up, the Phase-5 finding that the
concept graph is a dense relational web rather than a compressible kernel.

---

## 4. Where the prior cores landed

The Phase-5 size-9 irreducible dependency SCC (`003, 004, 034, 053, 060, 061,
084, 085, 088`) is **split across five different principles** (`002, 005, 010,
011, 015`). The dominant hub `CONCEPT_007` sits in `PRINCIPLE_001`. The modularity
modules and the dependency cycles are **orthogonal structures** — a key reason the
modules leak (see falsification). The principles are not re-discoveries of the
dependency cores; they are a different higher-order cut of the same graph.

---

## 5. Outputs

`generated/principles/`: `principle_candidates.json`, `principle_coverage.json`,
`principle_removal.json`, `principle_reconstruction.json`,
`principle_hierarchy.json`, `principle_dependencies.json`,
`irreducible_principles.json`, `principle_falsification.json`,
`principle_manifest.json`.

Tooling: `scripts/build_principles.py` (≈ 0.1 s, pure stdlib),
`scripts/validate_principles.py` (189 checks, `--rebuild` byte-identical).
Reports: this one, `principle-coverage-report.md`,
`principle-hierarchy-report.md`, `principle-falsification-report.md`,
`irreducible-principles-report.md`, `phase8-final-report.md`.

---

## 6. Limitations

- **One operational definition.** Principles are modularity modules of one
  integrated graph; a different graph weighting or community method would redraw
  them. The qualitative verdict (structure dominated by inter-principle relations)
  is robust to this — it follows from the 90% cross-boundary fraction.
- **Greedy modularity** is a deterministic heuristic, not a global optimum.
- **Inherited population.** All structure rests on the Phase-3/4 graphs with their
  fixed thresholds.
- **No meaning.** Principles are opaque structural patterns; member-concept
  anchors are listed only as discovered evidence.

---

## 7. Prohibitions observed

`no semantic meaning · no principle names · no principle translation · no theology
· no doctrine · no ontology · no apologetics · no contradiction engine · no divine
origin · no human origin · no success claimed before testing · no small principle
set forced · principles emerge from structure, never invented · prior phases never
rebuilt.`

---

## 8. Reproduce

```bash
python3 scripts/build_principles.py
python3 scripts/validate_principles.py --rebuild
```
