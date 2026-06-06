# Consistency Core Report — Phase 15 (C)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase15-consistency-propagation-1.0`.

Phase C searches for the smallest structure capable of preserving consistency — a
"consistency core." Equivalently, it searches for the smallest subset that is
*inconsistent*.

---

## 1. Subset consistency

Random subsets of the ayahs were tested for contradictions (10 samples per size):

| Subset fraction | Contradictions (mean) | 95% CI |
|---:|---:|---|
| 10% | 0 | [0, 0] |
| 25% | 0 | [0, 0] |
| 50% | 0 | [0, 0] |
| 75% | 0 | [0, 0] |

**Every subset is fully consistent** — down to 10% of the ayahs, no random subset
produces a single contradiction.

---

## 2. Does a consistency core exist?

| Question | Answer |
|---|---|
| Smallest structure preserving 50% of consistency | the empty set (consistency holds for any subset) |
| Smallest structure preserving 95% of consistency | the empty set |
| Smallest inconsistent subset found | **none** |
| Does a consistency core exist? | **No** |

There is **no minimal supporting structure** for consistency. A "core" would be a
small structure whose retention preserves consistency while the rest could be
discarded — but here consistency is preserved by *every* part and requires *no*
particular structure. The core size is effectively **0**: consistency needs
nothing in particular.

---

## 3. Why no core exists

Consistency is a **local property of every concept pair**: a pair either co-occurs
(positive) or never co-occurs (exclusion) — never both, in any subset. The
necessity guarantee is likewise carried by the hub's ubiquity, which is present in
any subset. There is no concentrated "consistency-maintaining kernel" because the
property is distributed over (indeed *intrinsic to*) every part of the matrix.

---

## 4. Verdict

> **No consistency core exists.** Every subset of the corpus — down to 10% of ayahs
> — is fully consistent. Consistency has no minimal supporting structure; it is a
> property of every part, not of a core. Hypothesis H2 ("a small core maintains
> consistency") is **falsified**.

---

## 5. Reproduce

```bash
python3 scripts/build_consistency_propagation.py
python3 scripts/validate_consistency_propagation.py --rebuild
```

Source: `generated/consistency_propagation/consistency_core.json`.
