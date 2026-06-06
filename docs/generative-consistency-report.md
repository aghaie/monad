# Generative Consistency Report — Phase 15 (I)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase15-consistency-propagation-1.0`.

Phase I tests whether the Phase-12 generative grammar can produce or test
consistency, or whether consistency is an independent property.

---

## 1. The grammar's scope

The Phase-12 grammar generates **graph topology** — directed edges via three rules:
degree-proportional attachment, reciprocity, and transitive closure. It produces a
directed proposition-style graph from an empty graph.

| Property | Value |
|---|---|
| Grammar models the activation matrix M? | **No** |
| Grammar produces exclusion / positive layers? | **No** |
| Consistency generable by the grammar? | **No** |

---

## 2. Why consistency is out of grammar scope

Consistency is a property of the **activation matrix** M — the disjointness of the
exclusion (co = 0) and positive (co ≥ 5) layers, and the necessity structure. The
grammar models only **topology** (which concept points to which), not
**co-occurrence counts**. It has no notion of:

- exclusion (pairs that never co-occur),
- positive co-occurrence support,
- conditional probabilities (necessity).

A synthetic graph from the grammar therefore has no consistency property to
evaluate — there is nothing in it that could be consistent or inconsistent in the
Phase-10 sense. Phase 12 already reported consistency as "out of scope (a property
of the activation matrix, not topology)"; this phase confirms it.

---

## 3. Can consistency emerge from the grammar?

**No** — and not because the grammar fails, but because consistency lives at a
different level. The grammar operates on topology; consistency operates on the
count matrix. They are **orthogonal**. Consistency is therefore an **independent
property** — it cannot be generated, explained, or destroyed by the topological
grammar.

This is consistent with the broader Phase-15 finding: consistency is not maintained
by any structure (hub, core, SCC, motif) — and it is likewise not produced by the
generative process. It is a matrix-level property, separate from the network's
topology and its generative rules.

---

## 4. Verdict

> **Consistency is independent of the generative grammar.** The grammar models
> topology and has no exclusion/positive layers, so it can neither generate nor test
> consistency. Consistency is a property of the activation matrix, orthogonal to the
> topological grammar — confirming it is independent and irreducible.

---

## 5. Reproduce

```bash
python3 scripts/build_consistency_propagation.py
python3 scripts/validate_consistency_propagation.py --rebuild
```

Source: `generated/consistency_propagation/generative_consistency.json`.
