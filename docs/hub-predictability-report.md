# Hub Predictability Report — Phase 16 (G)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase16-hub-origin-1.0`.

Phase G uses only partial structure (1–20% of ayahs) to predict final hub
dominance — how early hub inevitability appears.

---

## 1. Hub trajectory over partial corpus

| Revealed | Hub rank | Hub share |
|---:|---:|---:|
| 1% | **1** | ~0.97 |
| 5% | **1** | ~0.97 |
| 10% | **1** | ~0.97 |
| 20% | **1** | ~0.97 |

**The hub is rank-1 from the first 1% of ayahs**, with a share already near its
final value. Hub inevitability appears immediately.

---

## 2. Why the hub is inevitable early

Because the hub aggregates the corpus's most frequent lexical items, it dominates
*any* sample: even a 1% slice of ayahs contains the high-frequency roots that make
`CONCEPT_007` activate nearly every verse. There is no accumulation period — the hub
is present at full strength from the start.

This corroborates Phase 13 (the hub is present from the first verses under any
ordering) and locates the cause: it is a sampling consequence of the lexical
frequency distribution. A frequent lexical item appears frequently in any sample,
so the concept that aggregates frequent items is dominant in any sample.

---

## 3. How early does inevitability appear?

| Question | Answer |
|---|---|
| Earliest snapshot where the hub is rank-1 | **1%** (the first measured) |
| Does hub dominance grow into place? | **No** — present at full share from the start |
| Is hub dominance predictable from a small sample? | **Yes** — fully, from 1% |

---

## 4. Verdict

> **Hub inevitability is immediate.** The hub is rank-1 from the first 1% of ayahs,
> at near-final share. Because it aggregates the most frequent lexical items, it
> dominates any sample — its dominance is predictable from the smallest slice and
> requires no accumulation.

---

## 5. Reproduce

```bash
python3 scripts/build_hub_origin.py
python3 scripts/validate_hub_origin.py --rebuild
```

Source: `generated/hub_origin/hub_predictability.json`.
