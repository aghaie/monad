# Hub Reconstruction Report — Phase 16 (C)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase16-hub-origin-1.0`.

Phase C attempts to reconstruct the hub from the remaining structure — specifically
from lexical frequency. Can `CONCEPT_007` be predicted from everything else, or is
it independent?

---

## 1. Reconstruction from lexical frequency

Each concept's **lexical frequency** is the sum of its member roots' corpus token
counts. Ranking concepts by lexical frequency alone:

| Quantity | Value |
|---|---|
| Lexical-frequency rank-1 concept | **`CONCEPT_007`** |
| Is the hub the lexical rank-1? | **Yes** |
| Spearman(activation frequency, lexical frequency) | **0.998** |

**The hub is fully reconstructible from lexical frequency.** Without using the
proposition graph, the motifs, the SCCs, or any discovered relational structure —
using *only* the corpus token frequencies of each concept's member roots — the
concept that comes out on top is exactly `CONCEPT_007`.

---

## 2. Why: the hub aggregates the most frequent lexical items

The hub's member roots include the corpus's highest-frequency roots:

| Hub member-root corpus token counts (top 6) | 2851 · 1722 · 1390 · 980 · 879 · … |
|---|---|

The single most frequent root in the entire corpus (2851 tokens) is a member of
`CONCEPT_007`. The hub is, structurally, **the concept that aggregates the head of
the lexical frequency distribution.** Because activation frequency tracks lexical
frequency at Spearman 0.998, aggregating the most frequent roots produces the
highest-activation concept — the hub.

---

## 3. Is the hub independent or predictable?

| Question | Answer |
|---|---|
| Can the hub be predicted from the rest of the structure? | **Yes** — from lexical frequency alone |
| Is the hub independent of the rest? | **No** — it is determined by which concept holds the most frequent roots |
| What does the reconstruction require? | only the corpus token frequencies (Phase-1 data), no relational structure |

The hub is **not independent**: it is a deterministic function of the lexical
frequency distribution. Given the corpus's root frequencies and the Phase-3 concept
memberships, the hub is fixed — it could be named in advance, before any
relational analysis.

---

## 4. Verdict

> **The hub is reconstructible from lexical frequency alone.** The concept with the
> highest member-root corpus token frequency is exactly `CONCEPT_007`, and
> activation frequency tracks lexical frequency at Spearman 0.998. The hub is not an
> independent emergent structure — it is the concept that aggregates the corpus's
> most frequent lexical items.

---

## 5. Reproduce

```bash
python3 scripts/build_hub_origin.py
python3 scripts/validate_hub_origin.py --rebuild
```

Source: `generated/hub_origin/hub_reconstruction.json`.
