# Agency Report — Phase Ω (F)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`omega-world-model-1.0`.

Phase F asks who can act, what actions exist, and what constrains action. Structural
evidence only.

---

## 1. What can be measured structurally

| Structural proxy | Measure |
|---|---|
| **Initiation** (structural agency) | out-degree in the transition graph |
| **Actions** | transformation-class (verbal) concepts — 20 |
| **Constraint** | REQUIRES-gated transitions |

Top structural initiators (high out-degree) and the 20 action concepts are listed
in `agency_model.json`.

---

## 2. What emerges and what does not

| Question | Answer |
|---|---|
| Is there a structural initiation hierarchy? | **Yes** — concepts differ in out-degree (initiation) |
| What actions exist? | the 20 verbal (transformation) concepts |
| WHO can act? | **Does not emerge** — agent *identity* requires interpretation |
| Is action free or constrained? | **Does not emerge** — freedom/choice is a semantic notion, not structural |

- A structural **initiation hierarchy** emerges: some concepts initiate more
  transitions than others (out-degree). This is the closest structural analogue of
  "agency."
- But **agency in any meaningful sense** — choice, freedom, responsibility, who is an
  agent — does **not** emerge. Determining whether a concept "can act" or "chooses"
  requires importing a model of agency the phase forbids.

---

## 3. Verdict

> **Only structural initiation emerges; the agency model does not.** Concepts differ
> in transition out-degree (a structural initiation hierarchy), and 20 verbal
> concepts are "actions." But who can act, and whether action is free or
> constrained, cannot be established structurally — the semantic agency model does
> not emerge.

---

## 4. Reproduce

```bash
python3 scripts/build_world_model.py
python3 scripts/validate_world_model.py --rebuild
```

Source: `generated/world_model/agency_model.json`.
