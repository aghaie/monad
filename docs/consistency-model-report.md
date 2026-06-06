# Consistency Model Report — Phase 10 (A)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase10-consistency-1.0`.

Phase 10 built the **Contradiction & Consistency Discovery Engine** to test —
never assume — whether the discovered Quranic structure contains internal
contradictions. This report documents the **formal consistency model** (Phase A):
every rule is explicit, no assumption is hidden, the contradiction threshold is
high, and false positives are unacceptable. No theology, tafsir, translation,
external logic, or philosophical assumption is used. Phases 1–9 are read and
hashed but never rebuilt.

---

## 1. The ground truth: one count matrix

All Phase-4 relations are **monotone functions of a single per-ayah
concept-activation matrix M**, reconstructed here by the exact Phase-4/6 rule (an
ayah activates a concept iff any of its word tokens carries a member root/lemma).
The reconstruction is verified: **6,101 active ayahs** — byte-for-byte the Phase-4
active-ayah population.

This is decisive for contradiction analysis: two structures derived from one
consistent matrix can contradict **only** if each asserts a *universal obligation*
that M cannot jointly satisfy. The model therefore classifies every relation by
its obligation strength.

---

## 2. Obligation classes (explicit)

| Class | Definition | Obligating? |
|---|---|:--:|
| **NECESSITY** | `REQUIRES`, confidence ≥ 0.90 — B present whenever A | **yes** (universal) |
| **STRICT ORDER** | `PRECEDES`, asymmetry ≥ 0.95 — A before B, never B before A | **yes** (universal) |
| **EXCLUSION** | `co(A,B) = 0` with both marginals ≥ 30 — A,B never co-occur | **yes** (universal-negative) |
| **TENDENCY** | `DEPENDS_ON`, `PREDICTS`, `CO_OCCURS`, `ASSOCIATES_WITH`, `MEDIATES`, `CONDITIONAL_EMERGES`, weak `PRECEDES` | **no** (statistical) |

The critical distinction: a **TENDENCY cannot, alone, produce a contradiction.**
`DEPENDS_ON(A,B)` asserts `P(A|B) ≥ 0.3` — that A is *lifted* by B, not that B is
present whenever A. A may associate with two mutually-exclusive things in
*different* ayahs without any contradiction.

---

## 3. Contradiction rules (explicit, high burden)

A contradiction exists **only** when one of these fires:

| Rule | Condition |
|---|---|
| **C1 necessity–exclusion** | `A REQUIRES B` and `(A,B)` is EXCLUSION |
| **C2 double-necessity–exclusion** | `A REQUIRES B` and `A REQUIRES D` and `(B,D)` is EXCLUSION |
| **C3 strict-order antisymmetry** | strict `PRECEDES(A,B)` and strict `PRECEDES(B,A)` |
| **C4 strict-order cycle** | a directed cycle of **strict** `PRECEDES` edges (intransitive strict order) |
| **C5 self-negating recursion** | a dependency cycle containing an internal EXCLUSION pair |
| **C6 identity inversion** | a concept whose defining anchor appears in **0%** of its own activating ayahs |

---

## 4. Explicit non-contradiction clauses

The model **forbids** counting the following as contradictions (per the
prohibitions):

- **TENDENCY conflicts** — e.g. `A DEPENDS_ON B` and `A DEPENDS_ON D` with B,D
  exclusive. `DEPENDS_ON` asserts association, not co-presence; no obligation is
  violated.
- **Cycles / mutual dependency** — consistency loops, not contradictions, unless
  self-negating (C5).
- **Multiple or overlapping identities, shared anchors, ambiguity, complexity,
  motif diversity** — none is a contradiction.

---

## 5. The matrix landscape

| Quantity | Value |
|---|---|
| Active ayahs (M) | 6,101 |
| Concept marginals | 103 |
| Co-occurring concept pairs | 2,698 |
| **Strong EXCLUSION pairs** (co = 0, both marginals ≥ 30) | **401** |
| Strong negative-association pairs (NPMI ≤ −0.3) | 401 |

The structure contains a large, explicit *negative* layer — 401 concept pairs
that never co-occur. This is the raw material against which every positive
obligation is tested. The central question is whether any positive obligation
collides with this negative layer.

---

## 6. How the model is applied

Phases B–E search each conflict class; Phase F scores per-concept consistency;
Phase G classifies recursive structures; Phase H surfaces every candidate, attaches
evidence, and attempts an explicit disproof. A candidate is a genuine
contradiction **only if no disproof succeeds**. Results are in the companion
reports and `phase10-final-report.md`.

---

## 7. Outputs

`generated/consistency/consistency_model.json` (this model) plus the eight
conflict/score/candidate products. Tooling: `scripts/build_consistency.py`,
`scripts/validate_consistency.py` (585 checks, `--rebuild` byte-identical).

---

## 8. Reproduce

```bash
python3 scripts/build_consistency.py
python3 scripts/validate_consistency.py --rebuild
```
