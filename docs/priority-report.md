# Priority Report — Phase Δ (F)

**Phase:** Δ · **Method version:** `decision-architecture-1.0` · **Date:** 2026-06-08.

## 1. Objective
When multiple actions are available, how does the system prioritize (فضل/قدم — favour, precedence)?

## 2. Method
Flow out of the priority node and its position in the net-outflow ordering.

## 3. Results
- **Priority out**: priority → knowledge (99), priority → action (0.55, 64), priority → consequence
  (0.59, 27), priority → resolution (25).
- No priority edge survives the full falsification + stability battery.

## 4. Interpretation
The priority vocabulary (فضل/قدم) co-occurs with knowledge, action, and consequence, but **no priority
edge survives the controls**. The corpus does **not** robustly encode a distinct prioritization
architecture beyond frequency: preference vocabulary is present, but its directional structure collapses
under the frequency/order nulls. The honest finding is the absence of a robust priority mechanism.

## 5. Falsification Attempts
All priority edges collapse under the frequency or order null; none survives.

## 6. Limitations
Priority is operationalized via فضل/قدم; other preference markers were not included.

## 7. Conclusion
**No robust priority architecture emerges** — preference vocabulary exists but its directional structure
is frequency-driven and does not survive controls.

Source: `generated/decision_architecture/priority_architecture.json`.
