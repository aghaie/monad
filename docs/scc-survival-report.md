# SCC Survival Report — Phase 17 (G)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase17-frequency-null-1.0`.

Phase G re-evaluates the strongly-connected-core findings (Phase 5 SCCs, Phase 8
principle SCCs, Phase 9 SCC findings) against the concept-frequency null.

---

## 1. Result

| Quantity | Value |
|---|---|
| Observed largest SCC | **77** |
| Null largest SCC (mean) | 21 |
| **Ratio observed / null** | **3.6×** |
| Structure fraction | **72.2%** |

---

## 2. Findings

- **The giant SCC strongly survives frequency control.** The observed largest
  strongly-connected component (77 concepts) is **3.6× larger** than the frequency
  null's (~21). The strongly-connected core is **genuine structure**, not a
  hub-frequency artifact.
- This is an important, perhaps surprising, result. One might expect the SCC to be a
  consequence of the hub's ubiquity (the hub connects to everything → big SCC). The
  null *preserves* the hub's marginal, so a frequency-only SCC does form (~21), but
  the observed SCC is far larger — the additional connectivity comes from
  **specific** co-occurrence structure (the same strong associations that survive at
  3.2×), not from frequency.
- The SCC is Monad's **second-strongest** surviving discovery (72.2% structure),
  just behind the proposition edges.

---

## 3. Which cores survive?

| Core | Survival |
|---|---|
| Phase-5 giant directional SCC | **survives** (3.6× null) |
| Phase-8 principle SCC | inherits the same co-occurrence structure → survives |
| Phase-9 SCC findings | corroborated — the cyclic core exceeds frequency |

The strongly-connected core is a genuine relational structure: concepts are
mutually reachable through *specific* associations that the frequency null cannot
reproduce.

---

## 4. Verdict

> **The strongly-connected core survives frequency control** — observed SCC 3.6×
> the frequency null (72.2% structure). The giant cyclic core is genuine relational
> structure, not a hub-frequency artifact. It is Monad's second-strongest surviving
> discovery.

---

## 5. Reproduce

```bash
python3 scripts/build_frequency_null.py
python3 scripts/validate_frequency_null.py --rebuild
```

Source: `generated/frequency_null/scc_survival.json`.
