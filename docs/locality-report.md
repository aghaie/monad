# Locality Report — Phase 14 (H)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase14-locality-1.0`.

Phase H determines how *local* the discovered structure is: do random local windows
reproduce the global structure, or does the structure require corpus-scale
integration? Random contiguous windows of increasing size (1–50% of ayahs, 40
samples each) are measured against the global graph.

---

## 1. Structure recovery by window size

| Window | Motif-class recovery | Hub rank-1 prob. | Consistency recovery | SCC recovery |
|---:|---:|---:|---:|---:|
| 1% | 0.50 | **1.00** | **1.00** | 0.11 |
| 5% | 0.88 | **1.00** | **1.00** | 0.28 |
| 10% | 0.94 | **1.00** | **1.00** | 0.41 |
| 20% | 1.00 | **1.00** | **1.00** | 0.62 |
| 50% | 1.00 | **1.00** | **1.00** | 0.84 |

---

## 2. Findings — a locality gradient

The discovered structures differ sharply in how local they are:

| Structure | Locality | Evidence |
|---|---|---|
| **Hub** | **fully local** | rank-1 in 100% of windows, even at 1% |
| **Consistency** | **fully local** | recovered in 100% of windows, even at 1% |
| **Motif vocabulary** | **mostly local** | 50% at 1%, 88% at 5%, 94% at 10%, full by 20% |
| **Giant SCC** | **global** | 11% at 1%, 41% at 10%, 84% at 50% — needs corpus-scale integration |

- **Hub and consistency are entirely local properties** — any sufficiently small
  window already exhibits them in full. They are intensive (per-sample) properties.
- **The motif vocabulary is mostly local** — it is essentially complete by a 10–20%
  window. The recurring relational shapes are reproduced at modest scale.
- **The giant SCC is the one genuinely global structure** — it requires integrating
  a large fraction of the corpus; a 10% window recovers only 41% of it, and even a
  50% window only 84%. Global connectivity is an extensive property that needs
  corpus-scale assembly.

---

## 3. Answering the questions

| Question | Answer |
|---|---|
| How local is the discovered structure? | The hub, consistency, and (largely) the motif vocabulary are **local** — reproduced by small windows |
| How global is it? | The **giant SCC** is global — it requires corpus-scale integration |
| Do local windows reproduce global structure? | **Mostly yes** (hub, consistency, motifs); **no** for the SCC |

---

## 4. Connection to Phase 13

This corroborates Phase 13 (the structure is present at all scales / self-similar):
the hub, consistency, and motif vocabulary are scale-invariant local properties,
which is *why* they appeared from the first 1% of verses under any ordering. The
SCC, by contrast, is the structure that grew gradually in Phase 13 — because it is
the one extensive, global property.

---

## 5. Verdict

> The Quranic structure is **mostly local**: the hub and consistency are fully
> local (any window has them), the motif vocabulary is mostly local (complete by a
> 10–20% window), and only the giant SCC is genuinely global (needs corpus-scale
> integration).

---

## 6. Reproduce

```bash
python3 scripts/build_locality.py
python3 scripts/validate_locality.py --rebuild
```

Source: `generated/locality/locality_analysis.json`.
