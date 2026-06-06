# Hub Evolution Report — Phase 13 (B)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase13-evolution-1.0`.

Phase B tracks `CONCEPT_007` and every competing hub candidate over revelation
time, across both traditions and the control. No leakage; statistics only.

---

## 1. Hub trajectory (canonical order)

| Revealed | Ayahs | Hub share | Hub rank | Top-3 concepts |
|---:|---:|---:|---:|---|
| 1% | 292 | **1.000** | **1** | 007, 081, 003 |
| 5% | 491 | 1.000 | 1 | 007, … |
| 10% | 667 | 1.000 | 1 | 007, … |
| 20% | 1,232 | 0.998 | 1 | 007, … |
| 30% | 1,898 | 0.996 | 1 | 007, … |
| 50% | 3,148 | 0.991 | 1 | 007, … |
| 80% | 4,931 | 0.981 | 1 | 007, … |
| 100% | 6,101 | **0.968** | 1 | 007, 081, 003 |

---

## 2. Findings

- **The hub is present from the very first snapshot.** `CONCEPT_007` is the rank-1
  concept at 1% revealed — and its share is **1.000** (it appears in *every* active
  ayah of the opening surahs).
- **The hub does not "emerge" — it dilutes.** Its share *decreases* monotonically
  from 1.000 (1%) to 0.968 (100%) as more diverse content arrives. Far from growing
  into dominance, it starts at total saturation and is slightly diluted. This is the
  opposite of a gradual-emergence narrative.
- **No competing hub ever appears.** Across all 12 snapshots and all three
  orderings, `CONCEPT_007` is rank-1 at every step; `CONCEPT_081` is a distant
  second throughout.

---

## 3. Robustness across orderings

| Ordering | Hub rank-1 from start? | Share at 1% |
|---|:--:|---:|
| `TRADITION_CANONICAL` | **Yes** | 1.000 |
| `TRADITION_MECCAN_MEDINAN` | **Yes** | 1.000 |
| `CONTROL` (shuffle) | **Yes** | 1.000 |

The hub is rank-1 from the first snapshot **even under a random shuffle of
surahs**. Its dominance is therefore **content-driven, not order-driven**.

---

## 4. Answering the questions

| Question | Answer |
|---|---|
| Was the hub present early? | **Yes** — from 1% revealed, at maximal share |
| Did it emerge gradually? | **No** |
| Did it emerge suddenly? | **No** — it is present from the start and only dilutes |

---

## 5. Connection to prior phases

This corroborates and sharpens Phase 11 (hub SURVIVES STRONGLY, share 0.968 ±
0.002 under all perturbation) and Phase 12 (the hub is an irreducible primitive no
generative rule produces). Here it is shown to be present from the earliest verses
under any order — a primitive of the content, not an emergent or order-dependent
feature.

---

## 6. Reproduce

```bash
python3 scripts/build_evolution.py
python3 scripts/validate_evolution.py --rebuild
```

Source: `generated/evolution/hub_evolution.json`.
