# State Model Report — Phase Ω (B)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`omega-world-model-1.0`.

Phase B searches for recurring states — conditions entities can occupy. Structural
evidence only; the model must emerge or fail to emerge.

---

## 1. Grammatical state class

A state-class concept would be **adjective-dominant** (POS ADJ) — the grammatical
signal for a condition rather than a thing or an action.

| Quantity | Value |
|---|---|
| Adjective-dominant concepts | **0 / 103** |

**A distinct state class does NOT emerge.** No concept is adjective-dominant; states
and entities are not grammatically separable. Roots manifest as nominal or verbal,
not as a distinct stative class.

---

## 2. Structural state candidates (alternative)

If "state" is operationalized not grammatically but structurally — as a **transition
sink** (a concept that is reached by transformations more than it initiates them) —
some candidates appear (high in-degree − out-degree in the transition graph). These
are reported as a structural role, **not** as a discovered state ontology:

| Structural state candidate | Anchor | In-deg | Out-deg |
|---|---|---:|---:|
| (top sinks) | … | … | … |

(Full list in `state_model.json`.) But this is a *role* (being a target), not a
distinct *kind* of concept.

---

## 3. What emerges and what does not

| Question | Answer |
|---|---|
| Do recurring states emerge as a distinct class? | **No** — 0 adjective-dominant concepts |
| How many states exist? | undefined — states are not structurally separable from entities |
| Is there a structural state-role? | yes (transition sinks), but it is a role, not a kind |

---

## 4. Verdict

> **The state model FAILS TO EMERGE.** No distinct state class exists grammatically
> (0 adjective-dominant concepts); states and entities are not structurally
> separable. The only state-like signal is the structural role of being a transition
> sink — a role, not a discovered kind. The phase honestly reports non-emergence
> rather than forcing a state taxonomy.

---

## 5. Reproduce

```bash
python3 scripts/build_world_model.py
python3 scripts/validate_world_model.py --rebuild
```

Source: `generated/world_model/state_model.json`.
