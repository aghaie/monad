# Predictability Report — Phase 13 (G)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase13-evolution-1.0`.

Phase G measures, at each snapshot, how much of the **final** network is already
implied — using only already-revealed verses (no leakage). Statistics only.

---

## 1. Composite predictability

At each snapshot the composite is the mean of five forward-looking measures of the
final structure already visible:

```
composite = mean( motif cosine-to-final,
                  hub-already-rank1 (1/0),
                  top-10 concept Jaccard-to-final,
                  consistency-holds (1/0),
                  largest-SCC fraction-of-final )
```

## 2. Trajectory (canonical)

| Revealed | Motif cosine | Hub rank-1 | Top-10 Jaccard | Consistency | SCC frac | **Composite** |
|---:|---:|:--:|---:|:--:|---:|---:|
| 1% | 0.867 | ✓ | 0.82 | ✓ | 0.44 | **0.825** |
| 5% | 0.959 | ✓ | 1.00 | ✓ | 0.56 | 0.904 |
| 10% | 0.960 | ✓ | 1.00 | ✓ | 0.67 | **0.926** |
| 20% | 0.990 | ✓ | 0.82 | ✓ | 0.75 | 0.911 |
| 30% | 0.991 | ✓ | 0.82 | ✓ | 0.84 | 0.929 |
| 50% | 0.996 | ✓ | 0.82 | ✓ | 0.93 | 0.950 |
| 70% | 0.997 | ✓ | 1.00 | ✓ | 1.00 | 0.999 |
| 100% | 1.000 | ✓ | 1.00 | ✓ | 1.00 | 1.000 |

---

## 3. Findings

- **The final structure is ~80% predictable from the first 1% of verses** and
  **~93% from 10%.** The threshold at which composite predictability first reaches
  0.80 is **1% revealed** (canonical).
- **Most predictability comes from the hub and consistency,** which are at full
  value (1.0) from the first snapshot, and the motif distribution, which is at 0.87
  cosine at 1%. The slowest-rising component is the SCC fraction (0.44 → 1.00),
  which is what keeps the composite below 1.0 early.
- **Cross-ordering:** predictability at 10% is 0.93 (canonical), 0.85 (Meccan/
  Medinan), 0.84 (control). High under every order — including the random shuffle.

---

## 4. Answering the question

| Question | Answer |
|---|---|
| Can early revelation predict later revelation? | **Yes, strongly** — ~80% of the final structure is implied by 1% of verses, ~93% by 10% |
| What is already implied early? | the hub (fully), consistency (fully), the motif distribution (cosine 0.87 at 1%), most top concepts (Jaccard 0.82 at 1%) |
| What is least predictable early? | the giant-SCC size (44% of final at 1%), which grows gradually |

---

## 5. Interpretation

The network is **highly self-similar across revelation time**: a small prefix —
even a random one — already implies almost the entire final structure. This is a
quantitative statement of the headline finding that the structure is present from
the start, not emergent over time. It holds under the random control, so it is a
property of content density, not of any particular order.

---

## 6. Reproduce

```bash
python3 scripts/build_evolution.py
python3 scripts/validate_evolution.py --rebuild
```

Source: `generated/evolution/predictability_analysis.json`.
