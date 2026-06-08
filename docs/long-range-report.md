# Long-Range Report — Phase Ψ (B)

**Phase:** Ψ · **Method version:** `residual-nature-1.0` · **Date:** 2026-06-08.

## 1. Objective
Test whether the residual contains long-range structure: does a root recur at increasing distances
more than chance, and does predictive power grow with distance or stay flat?

## 2. Method
Root recurrence-lift at ayah distances {1,2,5,10,25,50,100,global} within surahs: lift(d) =
P(root recurs at distance d | present) / base density.

## 3. Results
| distance | 1 | 2 | 5 | 10 | 25 | 50 | 100 | global |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| recurrence-lift | 27.8 | 23.8 | 20.3 | 19.3 | 18.3 | 19.5 | 20.9 | 16.0 |

- Lift is **high at every distance** (16–28× chance) — roots recur far above base rate throughout a
  surah.
- Lift **decays** from distance 1 (27.8) to ~25 (18.3), then plateaus; it does **not increase** with
  distance.

## 4. Interpretation
There **is** substantial long-range lexical **recurrence** — characteristic vocabulary repeats
across a surah at 16–28× chance, even 100 ayahs apart. But this is **lexical cohesion** (the same
specific words recur), not an *increasing structural* long-range dependency: the lift decays with
distance and is strongest locally. So "long-range structure" exists only in the weak sense that a
surah keeps using its own words — a manifestation of the lexical specificity itself, not a separate
predictive constraint (and per Phase P it does not predict held-out content).

## 5. Falsification Attempts
"Predictive power increases with distance" is falsified (lift decays). "There is no long-range
recurrence at all" is also falsified (lift stays ~20× far apart). Both horns reported → PARTIAL.

## 6. Limitations
Recurrence-lift measures same-root repetition, not full cross-root long-range prediction; the latter
was shown non-generalizable in Phase P.

## 7. Conclusion
**Long-range structure: PARTIAL.** Real long-range lexical recurrence exists (16–28× chance at all
distances) but decays with distance and is lexical, not an increasing structural dependency.

Source: `generated/residual_nature/long_range_results.json`.
