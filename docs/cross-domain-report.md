# Cross-Domain Report — Phase R (E)

**Status:** complete. **Date:** 2026-06-07. **Method version:**
`reality-discovery-1.0`.

A pattern is a *universal سنّة* only if it recurs across domains, not in one corner of
the corpus. Phase E counts, for each pattern, in how many of the ten domains the
antecedent→outcome co-occurrence is actually witnessed.

---

## 1. Domain breadth of each pattern

| Pattern | Domains witnessed (of 10) |
|---|--:|
| injustice → collapse | 10 |
| denial → collapse | 10 |
| faith → thriving | 10 |
| righteous-deed → thriving | 10 |
| guidance → thriving | 10 |
| deed → recompense | 10 |
| gratitude → thriving | 9 |
| arrogance → collapse | 9 |
| sin → collapse | 9 |
| belying → collapse | 9 |
| corruption → collapse | 8 |
| crime → collapse | 8 |
| patience → thriving | 8 |
| justice → thriving | 3 |
| transgression → collapse | 4 |

The leading domains where these co-occurrences land: **ethics, history, the human
person, nature, and society** — the Quran shows the same conduct→outcome link in the
cosmos, in the fate of peoples, and in the individual.

---

## 2. Finding

> **13 of 15 patterns recur in ≥3 domains; most in 8–10.** The Quran does not confine
> these regularities to one sphere — the *same* link between conduct and outcome is
> asserted in nature, in history, in society, and in the individual person. This is the
> structural signature of a claimed **universal سنّة** (a regularity that holds across
> domains), exactly the cross-domain unification the phase set out to test. Only
> justice→thriving (3) and transgression→collapse (4) are domain-narrow.

---

## 3. Honest boundary

"Witnessed in a domain" means the antecedent, the outcome, and a domain-phenomenon
co-occur within an ayah-window — i.e. the Quran *asserts* the pattern there. It does not
mean the pattern has been verified to operate in that domain of the real world.

---

## 4. Reproduce

```bash
python3 scripts/build_reality.py
python3 scripts/validate_reality.py --rebuild
```

Source: `generated/reality/cross_domain_patterns.json`.
