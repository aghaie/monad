# Dependency-Map Report — Phase Ξ (A)

**Phase:** Ξ — Foundation Audit & Representation Collapse Engine · **Method version:**
`foundation-audit-1.0` · **Date:** 2026-06-08.
Nothing is protected: every discovery must re-earn survival when the original representation is removed.

## 1. Objective
Map which discoveries depend on which foundational assumptions, so the blast radius of removing each
assumption is explicit.

## 2. Method
For each of 20 major discoveries, record the foundational assumptions (A1–A5) it depends on, forming a
discovery→assumption dependency graph.

## 3. Results
- **A1 (roots are the unit)** and **A3 (concept clustering is meaningful)** are the most load-bearing:
  almost every conceptual discovery depends on them.
- The conceptual edifice — concepts, propositions, compression, identities, principles, grammar,
  semantics, world-model, methodology, decision architecture — chains off A2/A3/A4 (Phases 2–4).
- A small set depends on **no** Phase-2–4 assumption: frequency dominance, scale-invariance.

## 4. Interpretation
The project is a tree rooted in Phases 2–4. Cutting A3 (concept clustering) severs the entire conceptual
canopy; cutting A1 (roots) forces a representation rebuild. Only the information-theoretic facts hang
outside the tree. This map predicts the collapse pattern the later phases measure.

## 5. Falsification Attempts
The dependency map is the target enumeration; collapse is measured in `assumption-removal-report.md` and
`collapse-analysis-report.md`.

## 6. Limitations
Dependencies are at the assumption level; finer (parameter-level) dependencies are not traced.

## 7. Conclusion
Almost every discovery depends on A1 (roots) and/or A3 (concept clustering); only the information-theoretic
core hangs outside the Phase-2–4 dependency tree.

Source: `generated/foundation_audit/discovery_dependency_graph.json`.
