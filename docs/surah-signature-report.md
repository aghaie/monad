# Surah Signature Report — Phase 6

**Status:** complete. **Date:** 2026-06-06. **Method version:**
`phase6-identification-1.0`.

This report summarises `generated/identification/surah_signatures.json`: for each
of the 103 concepts, the surahs that carry its activity, ranked three ways —
**highest activation** (raw count), **highest density** (per-ayah rate), and
**highest uniqueness** (over-representation lift). **No surah is interpreted or
assigned meaning.** Concept ids stay opaque.

---

## 1. Definitions (evidence only)

| Metric | Definition |
|---|---|
| `activating_ayahs` | distinct ayahs of the surah that activate the concept |
| `density` | `activating_ayahs / surah_ayah_count` |
| `share` | `activating_ayahs / concept's total activating ayahs` |
| `uniqueness_lift` | surah density ÷ the concept's corpus-wide activation rate; `>1` = over-represented |

Each concept exposes the top-10 surahs on each axis with `revelation_type`,
`surah_ayah_count`, `activating_ayahs`, `density`, `share`, and `uniqueness_lift`.

---

## 2. Aggregate evidence

**Surahs carrying the most concept activity** (summed activating ayahs over the
top surahs of all concepts):

| Surah | Total activations | Revelation |
|---:|---:|---|
| 2 | 1,883 | Medinan |
| 4 | 1,238 | Medinan |
| 3 | 1,157 | Medinan |
| 7 | 1,039 | Meccan |
| 9 | 839 | Medinan |
| 5 | 730 | Medinan |
| 6 | 710 | Meccan |
| 16 | 434 | Meccan |
| 26 | 427 | Meccan |
| 11 | 377 | Meccan |

Surah 2 is the top activation surah for **35 of 103 concepts** — concept
activity is heavily front-loaded into the long Medinan surahs, while uniqueness
peaks in short surahs.

**Most surah-localised concepts** (highest single-surah uniqueness lift):

| Concept | Surah | Lift | Activating ayahs |
|---|---:|---:|---:|
| `CONCEPT_102` | 49 | 346.4 | 3 |
| `CONCEPT_100` | 100 | 141.7 | 1 |
| `CONCEPT_089` | 103 | 99.0 | 1 |
| `CONCEPT_086` | 24 | 97.4 | 4 |
| `CONCEPT_068` | 33 | 85.4 | 5 |
| `CONCEPT_051` | 28 | 70.9 | 7 |
| `CONCEPT_017` | 22 | 70.0 | 14 |
| `CONCEPT_057` | 19 | 63.6 | 5 |

The rarest concepts are nearly single-surah. At the opposite extreme,
`CONCEPT_007` has **no distinctive surah** — its uniqueness lift is ≈ 1.06
everywhere, the structural signature of the dominant hub.

---

## 3. Representative surah signatures (raw evidence)

### `CONCEPT_007` (dominant hub)

- Highest activation: 2 (285) · 26 (210) · 7 (203) · 3 (199) · 4 (176) · 37 (166)
- Highest uniqueness: flat — lift ≈ 1.06 across surahs 1, 4, 5, 6, 8, …
- **Observation:** spread across the entire corpus with no concentration.

### `CONCEPT_016` (secondary core)

- Highest activation: 2 (85) · 3 (57) · 7 (54) · 5 (43) · 4 (36) · 6 (32)
- Highest uniqueness: 65 (3.03) · 13 (2.18) · 59 (2.17) · 66 (2.17) · 49 (2.02) — all Medinan
- **Observation:** broad activation but distinctively over-represented in several
  short Medinan surahs.

### `CONCEPT_021` (surah-localised)

- Top surah 12 by both count and uniqueness — concentrated in a single surah.

### `CONCEPT_102` (rarest)

- All 3 activating ayahs in surah 49 (lift 346.4) — maximally localised.

---

## 4. How to read the file

```jsonc
"CONCEPT_016": {
  "total_activating_ayahs": 1199,
  "surahs_present": 78,
  "highest_activation_surahs": [ { "surah":2, "activating_ayahs":85, "density":…, … }, … ],
  "highest_density_surahs":   [ … ],
  "highest_uniqueness_surahs":[ { "surah":65, "uniqueness_lift":3.03, … }, … ]
}
```

`density` and `uniqueness_lift` correct for surah length, so short surahs with a
few member-bearing ayahs surface as distinctive even when their raw count is
small.

---

## 5. Limitations

- Density uses total surah ayah count, including ayahs with no morphology tokens.
- Uniqueness lift is relative to the concept's own corpus-wide rate; it measures
  over-representation, not importance, and assigns no meaning.
- Meccan/Medinan labels are Phase-1 corpus metadata (revelation_type), used only
  as a structural tag — no chronological or thematic claim is made.

---

## 6. Reproduce

```bash
python3 scripts/build_identification.py
python3 scripts/validate_identification.py --rebuild
```

**No meaning assigned. Concepts remain opaque.**
