# Semantic Boundary Report — Phase Σ (C)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`sigma-semantics-1.0`.

Phase C determines, for each concept, what belongs to it and what does not — its
semantic neighbourhood and its boundary.

---

## 1. Method

| Boundary side | Source |
|---|---|
| `belongs` | strongest neighbours (Phase-3 overlap) |
| `does_not_belong` | strongest exclusions (never co-occur, both frequent) |

`boundary_sharpness` = fraction of the boundary that is exclusions vs neighbours.

---

## 2. Findings

- **Boundaries emerge for the recoverable concepts.** Each has an *inside* (its
  strong neighbours) and an *outside* (its exclusion partners) — a Quran-internal
  semantic boundary.
- **Sharpness varies.** Concepts with many high-marginal exclusion partners have
  sharp boundaries (a clear "not-this"); concepts that co-occur broadly have soft
  boundaries (few exclusions). The boundary is itself a relational fact, expressed in
  concepts.
- **Some concepts have empty `contrasts_with`** — they co-occur with all frequent
  concepts (e.g. broad concepts near the hub), so their boundary is defined only by
  what belongs, not by what is excluded.

---

## 3. What emerges

| Question | Answer |
|---|---|
| What belongs to a concept? | its strongest neighbours (Quran-internal) |
| What does not belong? | its strongest exclusions (never co-occur) |
| Do semantic neighbourhoods emerge? | **Yes** — bounded regions of concepts |

---

## 4. Verdict

> **Semantic boundaries emerge.** Each recoverable concept has an inside (strong
> neighbours) and an outside (exclusion partners) — a Quran-internal neighbourhood
> with a measurable boundary. Boundary sharpness varies; broad concepts near the hub
> have soft boundaries.

---

## 5. Reproduce

```bash
python3 scripts/build_semantics.py
python3 scripts/validate_semantics.py --rebuild
```

Source: `generated/semantics/semantic_boundaries.json`.
