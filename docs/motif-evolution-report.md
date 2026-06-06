# Motif Evolution Report — Phase 13 (C, E)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase13-evolution-1.0`.

Phase C tracks the motif vocabulary's emergence; Phase E tracks SCC growth. No
leakage; statistics only.

---

## 1. Motif vocabulary trajectory (canonical)

| Revealed | Triad classes | Cosine to final |
|---:|---:|---:|
| 1% | 12 | 0.867 |
| 5% | 13 | **0.959** |
| 10% | 12 | 0.960 |
| 20% | 13 | 0.990 |
| 50% | 12 | 0.996 |
| 100% | 12 | 1.000 |

**Vocabulary stabilization threshold (cosine ≥ 0.9): 5% revealed.**

---

## 2. Findings

- **The motif vocabulary is essentially complete from 1% revealed** — 12 of the
  final 12 triad classes appear in the first snapshot (292 ayahs), and the triad
  *distribution* matches the final at cosine 0.87, rising to 0.96 by 5%.
- **Stabilization is extremely early:** by **5% of revealed verses** the
  distribution is within cosine 0.96 of the final and never drops below 0.96
  thereafter. The vocabulary does not accumulate over revelation time — it is
  present at small scale.
- **Cross-tradition / control:** stabilization (cosine ≥ 0.9) is reached by 5%
  (canonical, Meccan/Medinan) and 1% (control). All three orderings reach the full
  class set by 10–20%.

---

## 3. SCC evolution (Phase E)

| Revealed | Largest SCC | Fraction of final |
|---:|---:|---:|
| 1% | 40 | 0.44 |
| 5% | 51 | 0.56 |
| 10% | 61 | 0.67 |
| 30% | 76 | 0.84 |
| 50% | 85 | 0.93 |
| 70% | 91 | 1.00 |
| 100% | 91 | 1.00 |

- **The giant SCC is born immediately** (size 40 at 1% revealed — already ≥ 9, the
  Phase-5 core size) and **grows gradually** to its final size of 91 by ~70%
  revealed. The SCC is the one *topological* structure that exhibits genuine
  gradual growth (the largest single jump is +11 between 1% and 5%).
- Unlike the hub and motifs, the SCC **does** accumulate — but it starts large (44%
  of final at 1%) and saturates well before 100%.

---

## 4. Answering the questions

| Question | Answer |
|---|---|
| At what stage does the motif vocabulary stabilize? | **~5% revealed** (cosine ≥ 0.9) |
| First appearance of classes | 12 classes at the **first** snapshot (1%) |
| SCC birth | **1%** (size 40, already ≥ Phase-5 core size) |
| SCC growth | gradual, saturating ~70% revealed |

---

## 5. Reproduce

```bash
python3 scripts/build_evolution.py
python3 scripts/validate_evolution.py --rebuild
```

Source: `generated/evolution/motif_evolution.json`, `scc_evolution.json`.
