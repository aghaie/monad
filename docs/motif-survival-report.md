# Motif Survival Report — Phase 9 (E, F)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase9-motifs-1.0`.

Do motifs survive concept replacement (Phase E) and hub removal (Phase F)? A
genuine structural motif should recur independently of any particular concept.
Structural counts only; no meaning.

---

## 1. Phase E — concept replacement test

Motifs are isomorphism classes and are therefore concept-agnostic by
construction. The meaningful test is **recurrence across many distinct concepts
with no single concept dominating** (≥ 10 distinct concepts and max single-concept
share < 50%).

| Motif | Descriptor | Distinct concepts | Max single-concept share | Survives replacement |
|---|---|---:|---:|:--:|
| `MOTIF_001` | mutual-path | 91 | **0.742** (`CONCEPT_007`) | ✗ |
| `MOTIF_002` | in-merge | 99 | 0.257 | ✓ |
| `MOTIF_003` | in-merge | high | < 0.5 | ✓ |
| `MOTIF_004` | chain | high | < 0.5 | ✓ |
| `MOTIF_005` | out-fork | 91 | < 0.5 | ✓ |
| `MOTIF_007` | cyclic-mixed triangle | — | ≥ 0.5 | ✗ |
| `MOTIF_009` | fully-mutual triangle | — | ≥ 0.5 | ✗ |

**11 of 15 motifs survive replacement.** They recur across 90+ distinct concepts
with no concept dominating — they are genuine structural patterns, not artefacts
of specific concepts. The exceptions are revealing: the **most common motif**,
`MOTIF_001` (mutual-path), is **concept-bound** — 74% of its instances pass
through the hub `CONCEPT_007`. The fully-mutual and cyclic triangle motifs are
likewise hub-concentrated.

---

## 2. Phase F — hub removal test

Removing `CONCEPT_007` and recomputing the full triad census:

- **Triads with hub: 17,345 → without hub: 12,494.** Only **28.0% of triads are
  lost**; **72% of all triadic structure survives** the removal of the dominant
  hub.
- **Per-motif status:** 10 of 13 triad motifs **survive** (retain ≥ 50% of
  instances); 3 are **weakened** (`MOTIF_001` mutual-path, `MOTIF_007`
  cyclic-mixed, `MOTIF_009` fully-mutual) — exactly the hub-concentrated motifs;
  **0 collapse entirely.**
- **Emergent motifs:** 8 motifs become *relatively* more common after hub removal
  (`MOTIF_003, 004, 006, 011, 012, 013, 014, 015`) — the chain, fork, and
  transitive-triangle patterns, which the hub had been masking.

| Outcome | Motifs |
|---|---|
| survive (≥ 50% retained) | 10 triad motifs (paths, forks, transitive triangles) |
| weakened (hub-concentrated) | `MOTIF_001`, `MOTIF_007`, `MOTIF_009` |
| collapse (≈ 0 retained) | none |

**Answer — do motifs survive hub removal? Yes, overwhelmingly.** The motif
vocabulary is a distributed property of the network; the hub amplifies a few
reciprocal/triangle motifs but does not create the motif structure. Without the
hub, the same patterns persist and the chain/fork/transitive patterns become
relatively more prominent.

---

## 3. Synthesis

| Property | Result |
|---|---|
| Motifs recurring across many concepts | 11 / 15 survive replacement |
| Motifs surviving hub removal | 10 / 13 survive, 0 collapse, 72% of triads retained |
| Hub-bound motifs | `MOTIF_001`, `007`, `009` (reciprocal / fully-mutual) |
| Emergent on hub removal | chains, forks, transitive triangles |

The motif structure is robust: it does not depend on any single concept, and it
does not collapse when the dominant hub is removed. The one caveat — that the
single *most frequent* motif is hub-driven — is recorded, not hidden.

---

## 4. Limitations

- Hub removal recomputes the census on the induced subgraph; it does not re-derive
  Phase-4 relations from the corpus.
- Replacement is assessed by concept-distribution of instances, not by literal
  re-instantiation.

---

## 5. Reproduce

```bash
python3 scripts/build_motifs.py
python3 scripts/validate_motifs.py --rebuild
```
