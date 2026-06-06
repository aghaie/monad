# Hub Simulation Report — Phase 16 (F)

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase16-hub-origin-1.0`.

Phase F attempts to *generate* a hub synthetically. Can a hub be created by
frequency/activation rules? Can it be created by topology rules? 20 simulation runs
each.

---

## 1. Three generative regimes

| Regime | Rule | Max concept activation share |
|---|---|---:|
| **Frequency (Zipfian roots)** | sample roots ∝ corpus frequency, activate member concepts | **0.877** [CI 0.87, 0.88] |
| Uniform roots | sample roots ∝ 1 | **0.208** |
| **Topology grammar (Phase 12)** | attachment + reciprocity + transitive closure | **0.034** (reference) |
| Observed | — | 0.968 |

---

## 2. Findings

- **Frequency rules reproduce the hub.** Sampling roots by their real (Zipfian)
  corpus frequencies yields a dominant concept at **~88% activation** — close to the
  observed 96.8%. A hub is the natural output of frequency-weighted activation.
- **Uniform rules do not.** Flatten the frequencies and the maximum concept share
  drops to ~21% — no hub.
- **Topology rules cannot.** The Phase-12 generative grammar — which builds the
  proposition graph from attachment, reciprocity, and transitive closure — produces
  a hub of only ~3.4% edge-share. As Phase 12 reported, super-linear attachment does
  not close the gap. **Topology cannot manufacture the hub.**

---

## 3. The reconciliation with Phase 12

Phase 12 found the hub "not generable by the grammar" and called it an irreducible
primitive. Phase 16 locates *why*: the grammar models **topology**, but the hub's
origin is **lexical frequency**, which the topology grammar does not represent.

| Source | Can it generate the hub? |
|---|:--:|
| Graph topology (Phase-12 grammar) | **No** (~3.4%) |
| Lexical frequency (this phase) | **Yes** (~88%) |

The hub is irreducible *relative to topology* but fully *reducible to frequency*.
Phase 16 finds the origin Phase 12 could not: the heavy lexical tail.

---

## 4. Verdict

> **The hub is generable — by frequency, not by topology.** Frequency-weighted
> activation reproduces a ~88% hub; uniform activation does not (~21%); the
> topology grammar cannot (~3.4%). The hub's origin is the corpus's Zipfian lexical
> frequency distribution, not its relational structure.

---

## 5. Reproduce

```bash
python3 scripts/build_hub_origin.py
python3 scripts/validate_hub_origin.py --rebuild
```

Source: `generated/hub_origin/hub_simulation.json`.
