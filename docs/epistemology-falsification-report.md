# Epistemology-Falsification Report — Phase X (H)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`epistemology-discovery-1.0`.

> **Filename note (immutability):** the deliverable was "falsification analysis", but
> `docs/falsification-report.md` already belongs to Phase 7 and prior outputs are never
> overwritten. This report is `epistemology-falsification-report.md`. No prior file was
> changed.

Phase H attacks every edge with its own reverse. An edge claims a *direction*
(X precedes Y). The attack: measure the reverse flow (Y precedes X). An edge survives
only if its directionality is **≥ 0.60** — i.e. the forward order is not just a bare
majority but a clear one. Bare-majority edges (0.50–0.60) are declared **non-directional**
and refuted.

---

## 1. The attack outcome

| | Count |
|---|--:|
| Edges tested (knowledge + ignorance graphs) | 89 |
| **Survive** (directionality ≥ 0.60) | **46** |
| Refuted (non-directional, 0.50–0.60) | 43 |

**Just over half (52%) of the discovered edges survive the reverse-sequence attack.**

---

## 2. The honest reading

This is **not** a clean sweep, and it is reported as it stands. Of 89 directed edges,
**43 are too weakly directional to keep** — their forward and reverse orders are nearly
balanced (e.g. observe→understanding at 0.54, observe→knowledge, self→knowledge at 0.50).
These are *associations without a reliable order*: the two nodes co-occur, but which comes
first is close to a coin-flip.

The **46 survivors** are the real directional backbone, and they are exactly the
structurally meaningful ones:

- **knowledge → certainty** (0.80) — the strongest edge in the corpus
- **travel → understanding** (0.80)
- **read → blindness** (0.76), **conjecture → lying** (0.79) — obstacle cascade
- **listen / question / compare / reflect → understanding** (0.62–0.69)
- the ignorance cascade: conjecture→lying→arrogance→deviation→forgetting

The weak/refuted edges are dominated by **observation** — confirming Phase B and E:
observation is high-*volume* but low-*direction*. Its links to knowledge and to blindness
are both near 0.50–0.55, so most of them **do not survive**. The directional epistemology
lives in the *deliberate* acts (questioning, listening, reflecting, travelling) and in the
*state gradient* (knowledge→certainty), not in raw perception.

---

## 3. What this protects against

By refusing the 43 bare-majority edges, the phase guards against reading order into mere
co-occurrence. The surviving pipeline —

```
  deliberate acts → reflection → understanding → knowledge → certainty
  (and the mirror) denial/conjecture → lying → arrogance → deviation → forgetting
```

— is what remains after the attack: a **directional skeleton**, smaller and sturdier than
the full graph.

---

## 4. Verdict

> **46 of 89 epistemic edges survive reverse-sequence falsification at margin 0.60.** The
> Quran's epistemic *direction* is real but concentrated: it is carried by the deliberate
> acts and the knowledge→certainty gradient, not by raw observation, whose links are
> high-volume but non-directional. Half the naïve graph is order-less co-occurrence and is
> discarded. The surviving skeleton is the falsification-proof epistemology.

---

## 5. Reproduce

```bash
python3 scripts/build_epistemology.py
python3 scripts/validate_epistemology.py --rebuild
```

Source: `generated/epistemology/falsification_results.json`.
