# World Model Falsification Report — Phase Ω (L, M)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`omega-world-model-1.0`.

Phase L attacks the model — searching for inconsistencies, gaps, and unexplained
regions; Phase M tests robustness. The model is not forced; it survives or fails
honestly.

---

## 1. Falsification results (Phase L)

| Target | Result | Evidence |
|---|---|---|
| Entity structure | **SURVIVES** | 83 nominal-dominant concepts emerge clearly |
| Transformation structure | **SURVIVES** | 20 verbal concepts + 720-edge transition graph |
| Causal / precedence structure | **SURVIVES (as candidates)** | consistent PRECEDES/PREDICTS direction candidates |
| Feedback structure | **SURVIVES** | 42-concept cyclic transition core |
| **State structure** | **FALSIFIED** | 0 adjective-dominant concepts — no distinct state class |
| **Knowledge model** | **FAILS TO EMERGE** | no structural extraction of knowledge semantics |
| **Society model** | **FAILS TO EMERGE** | only structural communities, not a social model |
| **History model** | **FAILS TO EMERGE** | only motif recurrence, not a historical narrative |
| **Semantic world model** | **FAILS TO EMERGE** | meaning of entities/transformations not recoverable |

**4 structural components survive; 5 semantic components fail to emerge** (including
the semantic world-model itself).

---

## 2. The gaps and unexplained regions

The honest attack reveals exactly where the model is incomplete:

- **The state layer is missing** — states and entities are grammatically
  inseparable; the model has entities and transformations but no distinct states.
- **The semantic layer is entirely absent** — knowledge, agency-as-choice, society,
  and history cannot be extracted; these are the model's largest unexplained regions.
- **Causation is unproven** — only direction candidates exist.
- **Feedback sign is invisible** — reinforcing vs correcting cannot be distinguished.

These are not hidden — they are the phase's central honest finding: the model
emerges as a structural skeleton with a missing semantic body.

---

## 3. Robustness (Phase M)

| Quantity | Bootstrap (100 runs) |
|---|---|
| Entity-class count | mean ~83 (stable) |
| Transformation-class count | mean ~20 (stable) |
| State-class count | **0 in every sample** (stably absent) |

The entity/transformation role split is bootstrap-stable, and the absence of a state
class is robust (0 in every resample). The structural model is robust; the semantic
non-emergence is **not** a sampling artifact — it is a genuine limit of structural
methods.

---

## 4. Verdict

> **The structural skeleton survives falsification; the semantic model fails to
> emerge.** Entities, transformations, precedence candidates, and feedback are robust
> structural findings. States, knowledge, society, history, and the semantic
> world-model are documented gaps — the model emerges as structure, not as meaning,
> and the gaps are reported, not concealed.

---

## 5. Reproduce

```bash
python3 scripts/build_world_model.py
python3 scripts/validate_world_model.py --rebuild
```

Source: `generated/world_model/falsification_results.json`,
`robustness_results.json`.
