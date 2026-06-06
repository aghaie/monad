# Proposition Conflict Report — Phase 10 (B)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase10-consistency-1.0`.

Phase B searches all proposition structures for cases where one structure implies
B and another implies not-B (or equivalent incompatible outcomes). High burden of
proof; no false positives. Structural evidence only.

---

## 1. What a proposition contradiction would be

In this system, "A implies B and A implies not-B" has a precise structural form:
**A REQUIRES B and A REQUIRES D, where B and D are mutually exclusive** (never
co-occur). Then A would force two things that cannot both be present — A could
never be satisfied. This requires the NECESSITY obligation (`REQUIRES`, confidence
≥ 0.9); a TENDENCY (`DEPENDS_ON`, etc.) carries no such obligation.

---

## 2. Result: 0 genuine proposition contradictions

| Search | Result |
|---|---:|
| NECESSITY sources forcing two mutually-exclusive targets (C2) | **0** |
| `REQUIRES` edges whose recomputed `P(B|A)` falls below 0.85 | **0 / 100** |
| TENDENCY-level candidates (`DEPENDS_ON` over exclusive targets) | 39 — **all falsified** |

- **No concept REQUIRES two mutually-exclusive targets.** The 100 necessity
  relations are jointly satisfiable.
- **Every `REQUIRES` relation is verified against M:** all 100 have recomputed
  `P(B|A) ≥ 0.85` (stored threshold 0.9). The Phase-4 necessity layer is derived
  soundly from the activation matrix — no derivation inconsistency.

---

## 3. The 39 falsified tendency candidates

The engine actively surfaced the strongest *apparent* conflicts: 39 cases where a
concept `DEPENDS_ON` two targets that are mutually exclusive (e.g. `CONCEPT_002`
depends on both `CONCEPT_017` and `CONCEPT_019`, which never co-occur).

**All 39 are falsified.** `DEPENDS_ON(A,B)` asserts `P(A|B) ≥ 0.3` — that A is
*associated with* B — not that B is present whenever A. A concept may depend on B
in one set of ayahs and on an exclusive D in a different set; the two associations
are jointly true in M. No obligation is violated, so there is no contradiction.

This is the high-burden test in action: an apparent conflict pattern exists, but it
collapses under the explicit semantics of the relation. Counting these as
contradictions would be a false positive — exactly what the prohibitions forbid.

---

## 4. Why genuine proposition contradictions are absent

Because all relations derive from one consistent matrix M, a `REQUIRES(A,B)`
relation *guarantees* `co(A,B) ≈ marginal(A) > 0` — B is present with A. For A to
also require an exclusive D, `co(A,D) ≈ marginal(A)` would need D present with A
too, forcing `co(B,D) > 0` — contradicting their exclusion. The matrix simply does
not contain such a configuration: **0 of 100 necessity relations participate in
any such collision.** This is verified, not assumed.

---

## 5. Verdict

> **0 genuine proposition contradictions.** 39 tendency-level candidates were
> surfaced and falsified; the 100 necessity relations are mutually satisfiable and
> matrix-consistent.

---

## 6. Reproduce

```bash
python3 scripts/build_consistency.py
python3 scripts/validate_consistency.py --rebuild
```

Source: `generated/consistency/proposition_conflicts.json`.
