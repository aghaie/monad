# Dependency Analysis Report — Phase 4

**Date:** 2026-06-06. **Source:** `generated/propositions/dependency_candidates.json`,
`proposition_candidates.json`.

This report covers the directional dependency layer of Phase 4: `DEPENDS_ON`
and `REQUIRES` candidates plus the hierarchical chains they form. All ids stay
opaque; no semantic claim is attached.

---

## 1. Definitions

| Relation | Direction | Test | Strength |
|---|---|---|---|
| `DEPENDS_ON(A → B)` | A depends on B | `P(A\|B) ≥ 0.30 ∧ lift = P(A\|B)/P(A) ≥ 2.0 ∧ support ≥ 5` | `confidence = P(A\|B)`, `lift` |
| `REQUIRES(A → B)` | A nearly never appears without B | `P(B\|A) ≥ 0.90 ∧ support ≥ 5` | `confidence = P(B\|A)` |
| Chain (hierarchical) | `REQUIRES → REQUIRES` of length 3 | structural | n/a |

Every edge carries `stability_score` (0 / 0.5 / 1) under support ± 1 and up
to five `(surah, ayah)` evidence tuples.

---

## 2. Population

| Quantity | Value |
|---|---:|
| `DEPENDS_ON` edges | **184** |
| `REQUIRES` edges | **100** |
| Hierarchical chains (length 3) | **4** |
| Mean stability of dependency edges | 0.94 |

---

## 3. Top DEPENDS_ON by lift

Highest-lift directed dependencies (small-support fixations included, but
each passes support ≥ 5 and confidence ≥ 0.30):

| src → tgt | lift | confidence | support | stability |
|---|---:|---:|---:|---:|
| `CONCEPT_076 → CONCEPT_048` | 305.05 | 0.600 | 6 | 1.0 |
| `CONCEPT_058 → CONCEPT_077` | 189.47 | 0.714 | 5 | 0.5 |
| `CONCEPT_039 → CONCEPT_048` | 187.72 | 0.800 | 8 | 1.0 |
| `CONCEPT_039 → CONCEPT_089` | 134.09 | 0.571 | 12 | 1.0 |
| `CONCEPT_039 → CONCEPT_076` | 117.33 | 0.500 | 6 | 1.0 |
| `CONCEPT_073 → CONCEPT_074` | 104.67 | 0.824 | 28 | 1.0 |

## 4. Top DEPENDS_ON by confidence (strong but not boutique)

| src → tgt | conf | lift | support |
|---|---:|---:|---:|
| `CONCEPT_002 → CONCEPT_091` | 0.949 | 10.53 | 75 |
| `CONCEPT_002 → CONCEPT_090` | 0.905 | 10.04 | 76 |
| `CONCEPT_002 → CONCEPT_035` | 0.879 |  9.75 | 51 |
| `CONCEPT_018 → CONCEPT_063` | 0.843 | 23.27 | 59 |
| `CONCEPT_004 → CONCEPT_090` | 0.798 |  4.84 | 67 |
| `CONCEPT_021 → CONCEPT_039` | 0.769 | 33.52 | 20 |

## 5. Top REQUIRES by support (pervasive dependence)

| src → tgt | conf | support | surahs covered (evidence span) |
|---|---:|---:|---:|
| `CONCEPT_081 → CONCEPT_007` | 1.000 | 2,553 | 99 |
| `CONCEPT_003 → CONCEPT_007` | 0.988 | 1,608 | 99 |
| `CONCEPT_053 → CONCEPT_007` | 0.990 | 1,252 | 94 |
| `CONCEPT_061 → CONCEPT_007` | 0.988 | 1,180 | — |
| `CONCEPT_016 → CONCEPT_007` | 0.983 | 1,179 | 97 |
| `CONCEPT_084 → CONCEPT_007` | 0.996 | 1,170 | — |
| `CONCEPT_088 → CONCEPT_007` | 0.989 | 1,114 | — |
| `CONCEPT_004 → CONCEPT_007` | 0.979 |   984 | 91 |
| `CONCEPT_034 → CONCEPT_007` | 0.994 |   888 | — |
| `CONCEPT_085 → CONCEPT_007` | 0.984 |   875 | — |

Of 100 `REQUIRES` edges, **96** target `CONCEPT_007`. The four exceptions
form the secondary hierarchy below.

## 6. Non-`CONCEPT_007` REQUIRES edges

| src → tgt | conf | support |
|---|---:|---:|
| `CONCEPT_090 → CONCEPT_002` | 0.905 | 76 |
| `CONCEPT_091 → CONCEPT_002` | 0.949 | 75 |
| `CONCEPT_029 → CONCEPT_081` | 1.000 | 14 |
| `CONCEPT_068 → CONCEPT_081` | 1.000 |  5 |

## 7. Hierarchical chains (`REQUIRES → REQUIRES`, depth 3)

All four discovered chains terminate at `CONCEPT_007`:

```
CONCEPT_029 → CONCEPT_081 → CONCEPT_007
CONCEPT_068 → CONCEPT_081 → CONCEPT_007
CONCEPT_090 → CONCEPT_002 → CONCEPT_007
CONCEPT_091 → CONCEPT_002 → CONCEPT_007
```

These describe a two-level requirement: a peripheral concept requires an
intermediate concept which itself requires `CONCEPT_007`. No interpretation
is attached.

## 8. Dependency hubs (concepts with most outgoing dependencies)

| concept | out-degree (`DEPENDS_ON`) |
|---|---:|
| `CONCEPT_004` | 29 |
| `CONCEPT_002` | 13 |
| `CONCEPT_085` | 11 |
| `CONCEPT_016` | 11 |
| `CONCEPT_088` | 10 |
| `CONCEPT_034` |  9 |
| `CONCEPT_001` |  8 |
| `CONCEPT_061` |  8 |
| `CONCEPT_053` |  7 |
| `CONCEPT_084` |  7 |

These ten concepts originate **123 of 184** outgoing `DEPENDS_ON` edges
(66.8%). The dependency structure is sparse on most concepts and concentrated
on a small set of hubs.

---

## 9. Evidence (structural, no interpretation)

Each emitted dependency edge stores up to five `(surah, ayah)` tuples
sampled in `ayah_sequential` order from the joint co-activation set. They
are listed verbatim in `dependency_candidates.json` and serve only as
pointers to where the pattern can be observed — never as a basis for
meaning.

---

## 10. Limitations

- `REQUIRES` toward `CONCEPT_007` reflects its overwhelming activation
  fraction (~ majority of ayahs). The relation is statistically real but
  structurally degenerate: it tells us little beyond "this concept is
  near-ubiquitous."
- Lift can be very large when both concepts have low marginal probability;
  small-support, high-lift edges should be read with the support column.
- `DEPENDS_ON(A → B)` and `DEPENDS_ON(B → A)` are both emitted whenever both
  directions pass the thresholds — co-restricted pairs may appear twice in
  the table.
- The 4-chain depth-3 hierarchy almost certainly under-counts longer
  hierarchies: a deeper sweep with a relaxed `REQUIRES_CONF_MIN` would yield
  more chains.

---

## 11. Open questions (not answered here)

- Does a `REQUIRES` mass detached from `CONCEPT_007` exist if we remove
  `CONCEPT_007` from the activation matrix and re-run?
- Are the four exceptional chains stable under perturbation of
  `REQUIRES_CONF_MIN ∈ {0.85, 0.95}`?
- How do dependency hubs overlap with Phase-3 concept hubs?
