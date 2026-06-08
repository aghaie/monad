# Decision-Falsification Report — Phase Δ (J)

**Phase:** Δ · **Method version:** `decision-architecture-1.0` · **Date:** 2026-06-08.
(Named distinctly: Phase 7 owns `falsification-report.md`.)

## 1. Objective
Attack every candidate decision edge with nulls; remove anything that collapses.

## 2. Method
Each of the 45 candidate edges faces a **frequency** configuration null (K=100; preserve node df + ayah
sizes, destroy co-occurrence — exists beyond frequency?) and a **mushaf-order** null (K=100; word + ayah
order shuffled — directional beyond order?).

## 3. Results
| metric | value |
|---|--:|
| candidate edges | 45 |
| **exist beyond the frequency null** | **4 / 45 (8.9%)** |
| directional beyond the order null | 14 / 45 |

**The 4 edges existing beyond frequency:** condition→choice (support 861, dir 0.60), knowledge→uncertainty
(114, 0.69), consequence→action (117, 0.57 — fails the order null), knowledge→resolution (183, 0.56).

## 4. Interpretation
**91% of candidate decision edges are frequency artifacts** — they do not exist beyond the frequency
null. The apparent decision architecture is overwhelmingly a frequency shadow. Only 4 edges are real
associations, and of those one (consequence→action) fails the order null. This is the decisive
deflation: there is no broadly real decision structure, only a handful of genuine edges.

## 5. Falsification Attempts
This report is the attack: 41 of 45 edges fail the frequency null. No threshold was relaxed.

## 6. Limitations
Node-level frequency null; a stricter (root-level / syntactic) null would only remove more.

## 7. Conclusion
**Only 4 of 45 decision edges exist beyond frequency (8.9%).** The decision architecture is overwhelmingly
frequency-driven; a coherent architecture does not emerge.

Source: `generated/decision_architecture/decision_falsification.json`.
