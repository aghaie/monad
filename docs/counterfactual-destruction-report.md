# Counterfactual Destruction Report — Phase 15 (H)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase15-consistency-propagation-1.0`.

Phase H actively attempts to **destroy** consistency by three means: removing the
strongest structures, replacing the data with a null model, and directly corrupting
the matrix. This is the core falsification test — consistency is not protected.

---

## 1. Structural removal (strongest structures)

| Removed structure | Contradictions after |
|---|---:|
| The hub (`CONCEPT_007`) | **0** |
| The size-9 irreducible SCC | **0** |
| The top-10 concepts (by marginal) | **0** |
| The largest discovered region | **0** |

**No structural removal breaks consistency.** Deleting the most central, most
foundational structures in the network produces **zero** contradictions.

---

## 2. Null model (shuffle the activations)

The activation matrix was shuffled (30 times) preserving concept marginals and
ayah sizes — destroying the actual content co-occurrence while keeping the
statistical shape:

| Quantity | Value |
|---|---:|
| Null shuffles | 30 |
| Contradictions (mean / max) | **0 / 0** |
| 95% CI | **[0, 0]** |

**Random null matrices are equally consistent.** Shuffling the data into a
content-free null produces **0** contradictions in all 30 runs. Consistency is
therefore **generic** — not special to the Quran's actual structure. This is the
decisive evidence against hypothesis H6 ("consistency is emergent / special").

---

## 3. Direct data corruption (the only thing that works)

Positive co-occurrence edges were injected into exclusion pairs at increasing rates
— a direct corruption of the matrix:

| Corruption rate | Injected pairs | Contradictions |
|---:|---:|---:|
| 0% | 0 | **0** |
| 5% | 20 | 20 |
| 10% | 40 | 40 |
| 25% | 100 | 100 |
| 50% | 200 | 200 |
| 100% | 401 | **401** |

Consistency breaks **only** under direct corruption of the data, and it breaks
**proportionally** (one contradiction per injected pair). There is no threshold or
phase transition — the corruption curve is linear. This confirms consistency is a
property of the matrix's internal coherence: it can be destroyed only by falsifying
the data itself, never by removing or rearranging structure.

---

## 4. When, how, and what survives

| Question | Answer |
|---|---|
| When does consistency break? | only under direct data corruption |
| How does it break? | proportionally — 1 contradiction per injected exclusion→positive edge |
| What survives structural removal? | everything — 0 contradictions under every removal |
| What survives the null model? | everything — 0 contradictions in all shuffles |

---

## 5. Verdict

> **Consistency cannot be destroyed by removing any structure, nor by shuffling the
> data into a null model** (it is generic). It breaks **only** under direct
> corruption of the activation matrix, proportionally to the corruption. This is the
> strongest possible evidence that consistency is a property of the matrix's internal
> coherence — not maintained by any structure, and not special to this corpus.

---

## 6. Reproduce

```bash
python3 scripts/build_consistency_propagation.py
python3 scripts/validate_consistency_propagation.py --rebuild
```

Source: `generated/consistency_propagation/counterfactual_destruction.json`.
