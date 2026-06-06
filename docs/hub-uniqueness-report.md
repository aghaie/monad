# Hub Uniqueness Report — Phase 16 (E, H)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase16-hub-origin-1.0`.

Phase E searches for rival hubs and measures the distance between the hub and the
next-ranked concepts; Phase H assesses whether the hub function is replaceable.

---

## 1. The activation ranking

| Rank | Concept | Activation share |
|---:|---|---:|
| 1 | **`CONCEPT_007`** | **0.968** |
| 2 | `CONCEPT_081` | 0.418 |
| 3 | `CONCEPT_003` | 0.267 |
| 4 | `CONCEPT_053` | 0.207 |
| 5 | `CONCEPT_016` | 0.197 |
| 6 | `CONCEPT_061` | 0.196 |

| Quantity | Value |
|---|---|
| Hub − next gap | **0.550** |
| Next / hub ratio | **0.432** |

---

## 2. Is dominance unique?

**Yes — uniquely dominant, not "strongest among many."** The hub holds 96.8%
activation; the next concept (`CONCEPT_081`) reaches only 41.8% — **less than half**.
There is a single dominant concept separated from the field by a 0.55 share gap.
Beyond rank 2 the shares fall off smoothly (0.27, 0.21, 0.20 …), so the hub is not
one of a cluster of co-equal hubs — it is a unique outlier.

This uniqueness is itself a lexical consequence: `CONCEPT_007` aggregates the very
head of the Zipf distribution (the single most frequent root, 2,851 tokens), which
no other concept holds.

---

## 3. Redundancy (Phase H): is the hub function replaceable?

| Property | Finding |
|---|---|
| Function (a dominant connector) | **partially replaceable** — `CONCEPT_081` takes over on removal |
| Magnitude (96.8% activation) | **not replaceable** — no other concept reaches even half |
| Distributed? | in principle yes (any concept can connect), but concentrated in one lexically-heavy concept in practice |

The hub *function* is not a single point of failure (a replacement exists), but the
hub *magnitude* is unique. Removing the hub does not destroy connectivity — it just
demotes it to a much weaker concept.

---

## 4. Verdict

> **The hub is uniquely dominant.** It holds 96.8% activation versus the next
> concept's 41.8% — a 0.55 gap, less than half. It is a single outlier aggregating
> the head of the lexical distribution, not one of several comparable hubs. Its
> function is partially replaceable, but its magnitude is not.

---

## 5. Reproduce

```bash
python3 scripts/build_hub_origin.py
python3 scripts/validate_hub_origin.py --rebuild
```

Source: `generated/hub_origin/hub_uniqueness.json`, `hub_redundancy.json`.
