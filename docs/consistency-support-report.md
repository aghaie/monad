# Consistency Support Report — Phase 15 (A)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase15-consistency-propagation-1.0`.

Phase 15 investigates **how** consistency is maintained — and actively tries to
destroy it. Consistency is not assumed, not protected, not assumed special. No
theology, tafsir, translation, external logic, or imported explanation. All prior
phases are read and hashed but never rebuilt. Deterministic, byte-identically
reproducible (`validate_consistency_propagation.py --rebuild`, **81 checks pass**).

This report covers Phase A — mapping which structures support consistency.

---

## 1. Mechanical definition

All relations derive from one per-ayah concept-activation matrix M. A contradiction
is: (i) **exclusion∧positive** — a pair with co=0 (both marginals ≥ 30) that also
has co ≥ 5 (logically impossible); (ii) **C2 necessity** — a concept REQUIRES
(P(B|A) ≥ 0.9) two targets that never co-occur; (iii) **C4 strict-order** — a cycle
of strict (asymmetry ≥ 0.95) PRECEDES edges. The consistency score = number of
surviving contradictions. **Base: 0.**

---

## 2. Consistency-support weight

The **consistency-support weight** of a structure is the *increase* in contradiction
count when it is removed. Across all 103 concepts:

| Metric | Value |
|---|---|
| Maximum support weight (any single concept) | **0** |
| Concepts whose removal increases contradictions | **0 / 103** |

**No structure supports consistency.** Removing any concept — including the hub,
the SCC-9 members, the top-10 concepts — produces **0** new contradictions. There is
no structure whose presence is necessary for consistency.

---

## 3. Necessity mediation (the one structural signal)

While no structure *maintains* consistency, one structure *mediates* the
non-trivial part of it. The 100 REQUIRES (necessity) edges target:

| Target concept | REQUIRES-target count | Share |
|---|---:|---:|
| `CONCEPT_007` (hub) | 96 | **96%** |
| others | 4 | 4% |

**96% of all necessity relations point at the hub.** Because the hub appears in
96.8% of ayahs, it co-occurs with essentially everything, so a concept "requiring"
the hub can never be forced into an incompatible pair. The hub *explains why
necessity never conflicts* — but it is not *required* for consistency (see
`hub-dependence-report.md`).

---

## 4. Consistency-centrality & dependency

- **Consistency-centrality:** undefined in the usual sense — no concept is more
  "central" to consistency than any other, because consistency is not carried by a
  network position. The only centrality signal is necessity-mediation (hub 96%).
- **Consistency-dependency:** zero — consistency does not depend on any single
  structure (all support weights 0).

---

## 5. Verdict

> **No structure supports consistency.** Every consistency-support weight is 0 —
> removing any concept produces no contradiction. The only structural signal is that
> the hub *mediates* 96% of necessity relations (explaining why necessity never
> conflicts), but even the hub is not required (see Phase B). Consistency is not
> carried by any structure; it is a property of the activation matrix itself.

---

## 6. Reproduce

```bash
python3 scripts/build_consistency_propagation.py
python3 scripts/validate_consistency_propagation.py --rebuild
```

Source: `generated/consistency_propagation/consistency_support.json`.
