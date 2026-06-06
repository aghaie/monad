# Hub Dependence Report — Phase 15 (B)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase15-consistency-propagation-1.0`.

Phase B challenges `CONCEPT_007` directly: is consistency hub-dependent? The hub is
removed entirely and the contradiction count recomputed.

---

## 1. Hub removal

| Quantity | With hub | Without hub |
|---|---:|---:|
| Exclusion∧positive contradictions | 0 | **0** |
| C2 necessity contradictions | 0 | **0** |
| C4 strict-order cycles | 0 | **0** |
| **Total contradictions** | **0** | **0** |

**Consistency is fully retained without the hub.** Removing `CONCEPT_007` —
present in 96.8% of ayahs, incident to 22% of relations — produces **zero**
contradictions. Consistency is **not hub-dependent**.

---

## 2. The hub's actual role: mediation, not maintenance

The hub plays a real but different role: it **mediates necessity**. 96 of the 100
REQUIRES (necessity) edges target the hub. Because the hub co-occurs with almost
everything, a concept that "requires" the hub can never be forced into an
incompatible pair — so the hub *explains why necessity relations never conflict*.

But mediation is not maintenance:
- When the hub is removed, the 4 remaining non-hub REQUIRES edges still produce **0**
  necessity conflicts.
- The exclusion∧positive guarantee is tautological and needs no hub at all.

So the hub answers *why* necessity is conflict-free in the full graph, but its
removal does not create any conflict — the property holds without it.

---

## 3. Is consistency hub-dependent?

| Question | Answer |
|---|---|
| Does consistency survive full hub removal? | **Yes** — 0 contradictions |
| Does the hub maintain consistency? | **No** — it mediates necessity but is not required |
| Does another structure replace it on removal? | No replacement is needed — consistency never depended on it |

---

## 4. Verdict

> **Consistency is NOT hub-dependent.** It survives complete hub removal with 0
> contradictions. The hub *mediates* 96% of necessity relations (a structural
> explanation for why necessity never conflicts) but is not *required* for
> consistency — hypothesis H1 ("the hub maintains consistency") is **falsified**:
> the hub is a mediator, not a maintainer.

---

## 5. Reproduce

```bash
python3 scripts/build_consistency_propagation.py
python3 scripts/validate_consistency_propagation.py --rebuild
```

Source: `generated/consistency_propagation/hub_dependence.json`.
