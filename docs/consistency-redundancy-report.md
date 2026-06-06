# Consistency Redundancy Report — Phase 15 (G)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase15-consistency-propagation-1.0`.

*(Named `consistency-redundancy-report.md` to preserve the Phase-14
`redundancy-report.md`; the Phase-15 spec's generic name would collide.)*

Phase G asks whether consistency is maintained through redundancy — duplicated or
parallel support structures providing backup.

---

## 1. Random half-split test

The corpus was randomly split in half (10 times); both halves were independently
checked for consistency:

| Quantity | Value |
|---|---:|
| Random half-splits | 10 |
| Both halves consistent in every split? | **Yes** |
| Splits with any contradiction | **0** |

**Every random half is independently consistent.** No matter how the corpus is
divided, each part is fully consistent on its own.

---

## 2. Is consistency maintained by redundancy?

The result superficially resembles redundancy (Phase 14 found consistency in
114/114 surahs), but it is **not** redundancy in the mechanistic sense:

- **Redundancy** would mean a structural function is *duplicated* — multiple
  independent structures each capable of providing it, so removing one leaves a
  backup.
- What is observed instead is **ubiquity of a local property**: consistency holds in
  every part because it is a per-pair property of the matrix, not a function carried
  by any structure that could be duplicated or backed up.

There are no "backup pathways" because there is no pathway; no "replacement
capacity" because nothing needs replacing. Consistency is resilient not because it
is redundantly supported but because it is **intrinsic to every measurement**.

---

## 3. Consistency resilience

| Property | Finding |
|---|---|
| Backup pathways | not applicable (no pathway) |
| Replacement capacity | not applicable (no structure to replace) |
| Resilience | total — holds in every subset and every split, because it is local |

---

## 4. Verdict

> **Consistency is not maintained by redundancy.** It holds independently in both
> halves of every random split — but this is *ubiquity of a local property*, not a
> duplicated mechanism. There is nothing to back up because consistency is intrinsic
> to every pair. Hypothesis H5 ("redundancy maintains consistency") is **falsified**
> (ubiquity, not redundancy).

---

## 5. Reproduce

```bash
python3 scripts/build_consistency_propagation.py
python3 scripts/validate_consistency_propagation.py --rebuild
```

Source: `generated/consistency_propagation/redundancy_contribution.json`.
