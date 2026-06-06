# Functional Meaning Report — Phase Σ (E)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`sigma-semantics-1.0`.

Phase E ignores labels and asks what *role* each concept plays — reconstructing
meaning from function.

---

## 1. The functional profile (all from concepts)

For each recoverable concept, its function is a profile of relations to other
concepts:

| Function | Source |
|---|---|
| `requires` | what it presupposes (REQUIRES) |
| `preceded_by_causes` | what antecedes it (PREDICTS-in) |
| `depends_out` | what it depends on (DEPENDS_ON) |
| `blocks_excludes` | what it never co-occurs with (exclusions) |
| `amplifies_neighbors` | what it co-occurs with strongly (overlap) |

Every entry is an opaque concept — meaning is reconstructed as a position in the
relational flow, not as a label.

---

## 2. Findings

- **Functional roles emerge for the recoverable concepts.** Each concept has a
  characteristic profile of what it requires, what precedes it, what it blocks, and
  what it amplifies — a relational signature.
- **The most common functional requirement is `CONCEPT_007`** — many concepts
  "require" the frequency hub (it co-occurs with everything). This is a frequency
  effect (Phase 16), so requiring the hub is weakly informative; the *distinctive*
  functional signal is in the non-hub requirements, contrasts, and antecedents.
- **Function distinguishes concepts that share neighbours.** Two concepts with
  similar `associated_with` sets can differ in what precedes them or what they block
  — function adds resolution beyond co-occurrence.

---

## 3. Meaning from function

| Question | Answer |
|---|---|
| What causes a concept? | its PREDICTS antecedents |
| What requires it / it requires? | REQUIRES / DEPENDS_ON profile |
| What blocks it? | its exclusion partners |
| What amplifies it? | its strong neighbours |

This is **functional/relational meaning** — a concept *is what it does* in the
network. It is genuine Quran-internal structure, but it remains relational: the
function is described in terms of other concepts, never grounded externally.

---

## 4. Verdict

> **Functional meaning emerges relationally.** Each recoverable concept has a
> characteristic role — what it requires, what precedes it, what it blocks, what it
> amplifies — all expressed in other concepts. Function adds resolution beyond mere
> co-occurrence, but it is still relational, not referential.

---

## 5. Reproduce

```bash
python3 scripts/build_semantics.py
python3 scripts/validate_semantics.py --rebuild
```

Source: `generated/semantics/functional_roles.json`.
