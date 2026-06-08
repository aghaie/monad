# Conflict-Resolution Report — Phase Δ (E)

**Phase:** Δ · **Method version:** `decision-architecture-1.0` · **Date:** 2026-06-08.

## 1. Objective
How are conflicts (خلف/جدل/فرق — dispute, argument, division) resolved?

## 2. Method
Flow out of conflict and into resolution (حكم — judgment).

## 3. Results
- **Conflict out**: conflict → condition (159), conflict → knowledge (dir 0.59, 146),
  conflict → action (0.60, 80).
- **Resolution in**: knowledge → resolution (183), condition → resolution (171), choice → resolution (160).
- `conflict → knowledge` and `conflict → action` are bootstrap-stable.

## 4. Interpretation
The descriptive pattern is sensible: conflict flows toward **knowledge** and **action**, and resolution
(حكم) is fed by **knowledge** and **condition**. So the raw architecture suggests "conflict → seek
knowledge / judge". But under the frequency null, the explicit `conflict → resolution` edge does **not**
survive as a distinct robust component; what survives is the generic `knowledge → resolution` (judging
follows knowing) and a stable `conflict → knowledge`. So conflict-resolution, as a distinct architecture,
is mostly frequency-driven; the robust residue is "knowledge precedes judgment".

## 5. Falsification Attempts
conflict → resolution does not survive as a full-battery component; knowledge → resolution does.

## 6. Limitations
Resolution is operationalized as the حكم node; conflict via خلف/جدل/فرق.

## 7. Conclusion
**No distinct robust conflict-resolution architecture**; the surviving residue is **knowledge →
resolution** (judgment follows knowledge), and a stable conflict → knowledge.

Source: `generated/decision_architecture/conflict_resolution.json`.
