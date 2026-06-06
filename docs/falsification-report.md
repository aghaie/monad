# Falsification Report — Phase 7

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase7-revelation-1.0`.

Phase G *attacks* every proposed identity. For each concept's top candidate
anchor it searches the concept's own Quran-internal evidence for contradiction —
member roots that do not fit, signature ayahs the anchor does not explain,
neighbours and dependency partners that pull elsewhere. An identity that cannot
be falsified by its own evidence survives; one that can does not. **No identity is
defended; each is tested. No meaning is assigned at any step.**

---

## 1. Method

For a concept's top candidate (anchor root **R**):

| Contradiction probe | Definition |
|---|---|
| **contradicting roots** | member roots with activation share ≥ 0.05 and ~0 Phase-2 neighbour link to R |
| **contradicting ayahs** | signature ayahs (top-50) in which R does **not** fire |
| **contradicting neighbours** | closest concepts whose own anchor root has ~0 neighbour link to R |
| **contradicting propositions** | DEPENDS_ON / REQUIRES partners whose anchor root is unlinked to R |

```
falsification_pressure = mean( contradicting_ayah_fraction,
                               contradicting_root_fraction )
survives  ⇔  falsification_pressure < 0.5
```

"~0 link" uses the Phase-2 minimum-confidence floor (0.05). The probe is purely
structural — it never consults meaning.

---

## 2. Results

| Outcome | Count |
|---|---:|
| Identities tested | 97 |
| **Survive** | **94** |
| **Falsified** | **3** |
| Not tested (resist identification) | 6 |

The single-anchor identity is robust for 94 of 97 concepts: the dominant Arabic
anchor is present in a majority of the concept's signature ayahs and coheres with
its co-member roots.

---

## 3. The three falsified identities

These concepts have a leading root, but it fails to explain the majority of their
own signature ayahs — their identity is genuinely multi-anchored or distributed,
and the single-anchor hypothesis is rejected.

### `CONCEPT_011` — anchor `نصح` (falsified, pressure 0.51)

- **78%** of signature ayahs do not contain `نصح`.
- Contradicting member roots: `لوح` (0.159), `غضب` (0.137), `اسف` (0.132),
  `نسخ` (0.106) — none neighbour-linked to `نصح`.
- Contradicting ayahs: 7:150, 7:154, 20:86, 7:133, 7:176.

### `CONCEPT_041` — anchor `حدب` (falsified, pressure 0.67)

- **83%** of signature ayahs lack `حدب`.
- Contradicting roots: `قصم` (0.141), `نون` (0.124), `نفح` (0.122).
- Contradicting ayahs: 21:30, 21:79, 21:11, 21:87, 21:46.

### `CONCEPT_043` — anchor `رفد` (falsified, pressure 0.60)

- **86%** of signature ayahs lack `رفد`.
- Contradicting roots: `حنذ` (0.142), `زري` (0.142).
- Contradicting ayahs: 11:44, 11:31, 11:69, 11:74, 11:105.

In all three, the engine reports the leading anchor *and* the evidence that
refutes it as the sole identity — the competing roots are preserved, not hidden.

---

## 4. Near-miss survivors

Six identities survive but with high falsification pressure (0.42–0.46) — their
single anchor explains barely over half their evidence:

| Concept | Anchor | Pressure |
|---|---|---:|
| `CONCEPT_022` | `لعن` | 0.462 |
| `CONCEPT_027` | `ربو` | 0.460 |
| `CONCEPT_015` | `سال` | 0.450 |
| `CONCEPT_018` | `روح` | 0.447 |
| `CONCEPT_037` | `قمر` | 0.420 |
| `CONCEPT_031` | `رفت` | 0.417 |

These are flagged as moderate identities with real competing anchors — candidates
for distributed rather than single identity.

---

## 5. What falsification reveals (evidence only)

- The 43 `strong` identities all survive with low pressure — their anchor is
  present across most signature ayahs and coheres with co-members.
- Falsification, not naming, is what separates a genuine single identity from a
  superficially dominant root: `CONCEPT_053`'s `عذب` survives (it returns
  competing anchors), whereas `CONCEPT_011`'s `نصح` does not.
- No identity is asserted beyond what its own evidence supports; three are
  explicitly rejected.

---

## 6. Reproduce

Source: `generated/revelation/falsification_results.json`, built by
`scripts/build_revelation.py`, validated by
`scripts/validate_revelation.py --rebuild`.

```bash
python3 scripts/build_revelation.py
python3 scripts/validate_revelation.py --rebuild
```

**Identities are attacked, not defended. No meaning, certainty, or origin is
claimed.**
