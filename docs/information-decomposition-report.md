# Information Decomposition Report — Phase 17 (I)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase17-frequency-null-1.0`.

Phase I partitions every major discovery into a frequency-explained component and a
structure-explained component.

---

## 1. Decomposition

`structure % = max(0, (observed − null_mean) / observed)`; `frequency % = 100 −
structure %`.

| Discovery | Structure % | Frequency % |
|---|---:|---:|
| Proposition edges | **74.7** | 25.3 |
| Strongly-connected core (SCC) | **72.2** | 27.8 |
| Strong associations | **68.7** | 31.3 |
| Concept clustering | 38.1 | 61.9 |
| Motif distribution | 32.3 | 67.7 |
| Grammar transitivity | 31.3 | 68.7 |
| Identity anchors | 31.1 | 68.9 |
| Consistency | 0.0 | 100.0 |
| Grammar reciprocity | 0.0 | 100.0 |
| Hub dominance | 0.0 | 100.0 |
| **Mean** | **~35** | **~65** |

---

## 2. The structure spectrum

The ten discoveries fall into three bands:

**High structure (60–75%)** — the relational network:
- proposition edges, SCC, strong associations. These are Monad's genuine
  contribution: specific co-occurrence/association structure that no frequency null
  reproduces (3–4× above null).

**Moderate structure (31–38%)** — the partly-structural layer:
- concept clustering (significant, z = 29.8, but moderate magnitude), motif
  distribution (3/13 classes survive), grammar transitivity, identity anchors. These
  contain real structure but are dominated by the frequency baseline.

**Zero structure (0%)** — the frequency layer:
- consistency, grammar reciprocity, hub dominance. These carry no information beyond
  frequency; the null reproduces them exactly.

---

## 3. Frequency contribution vs structure contribution

| Aggregate | Value |
|---|---|
| **Mean frequency contribution** | **~65%** |
| **Mean structure contribution** | **~35%** |

Two-thirds of Monad's discovered structure is a consequence of the Quran's lexical
frequency distribution. One-third is genuine relational structure — concentrated in
the proposition/co-occurrence network and the strongly-connected core.

---

## 4. Caveat on the two measures

Structure % (magnitude) and z-score (significance) can diverge. Concept clustering
has only 38% structure% yet z = +29.8 — it is *significantly* above frequency but
its *magnitude* is mostly the frequency baseline. The decomposition reports
magnitude; the survival reports (`concept-survival-report.md` etc.) report
significance. Both are honest and both are needed.

---

## 5. Verdict

> **Monad is ~35% structure, ~65% frequency.** The genuine structure (60–75%) is
> the proposition network, the SCC, and the strong associations; the moderate layer
> (31–38%) is concept clustering, motifs, and identity; the frequency-only layer
> (0%) is consistency, hub dominance, and grammar reciprocity.

---

## 6. Reproduce

```bash
python3 scripts/build_frequency_null.py
python3 scripts/validate_frequency_null.py --rebuild
```

Source: `generated/frequency_null/information_decomposition.json`.
