# Q13 — Essentiality Report (Phase ΩΣ)

**Method:** `foundational-questions-1.0` · corpus-only · deterministic.

## 1. Objective
If maximum content had to be removed while preserving maximum structure, **what survives longest**?

## 2. Method
Greedy deletion: iteratively remove the lowest document-frequency roots; the units surviving to the end are
the structurally most indispensable. Cross-checked against representation collapse (Phase Ξ).

## 3. Results
The last-surviving core (top document-frequency roots, Arabic anchors are evidence):
**اله، قول، كون، ربب، علم، امن، قوم، اتي، كفر، بين** (df 1,879 → 454).

## 4. Interpretation
Essentiality **reduces to frequency dominance**: the units that survive deletion longest are exactly the
high-frequency hub, not a hidden structural skeleton. There is no separate "essential structure" beyond the
frequency core — consistent with Phase P (non-predictivity) and Phase Ξ (the surviving core is
information-theoretic).

## 5. Falsification Attempts
The hub's indispensability survives the frequency null (Phase 17) and representation collapse (Phase Ξ,
root/lemma/word). No structural survivor independent of frequency was found.

## 6. Limitations
Greedy df-deletion is one deletion order; alternative essentiality scores would return the same hub because
the result is driven by the frequency distribution itself.

## 7. Conclusion
**The frequency hub survives longest.** Essentiality ≡ frequency dominance — there is no separate structural
core beneath it.
